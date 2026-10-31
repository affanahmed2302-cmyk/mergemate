from __future__ import annotations
import re
from typing import List
from uuid import uuid4
from app.core.exceptions import ValidationError
from app.core.store import store
from app.integrations.ai import get_ai_provider
from app.integrations.github import GitHubClient, parse_pr_url
from app.schemas.common import FindingSource, ReviewStatus, Severity, VerificationStatus
from app.schemas.findings import Evidence, Finding
from app.schemas.reviews import (
    PRInfo, ReviewResponse, RiskFactor, RiskSummary, Scorecard, TestSuggestion,
)
from app.services.prooflayer import validate_all

SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)
BARE_EXCEPT_RE = re.compile(r"except\s*:\s*(#.*)?$", re.MULTILINE)


def _deterministic_scan(files: List[dict]) -> List[Finding]:
    findings: List[Finding] = []
    for f in files:
        fname = f.get("filename") or ""
        patch = f.get("patch") or ""
        for m in SECRET_RE.finditer(patch):
            findings.append(Finding(
                id=str(uuid4()),
                title="Possible hardcoded secret",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                evidence=Evidence(excerpt=m.group(0)[:120]),
                explanation="A pattern resembling a hardcoded credential was found in the diff.",
                potential_impact="Credentials in source can be leaked via the repository history.",
                suggested_fix="Move secrets to environment variables or a secrets manager.",
                confidence=0.85,
                source=FindingSource.DETERMINISTIC,
            ))
        for m in BARE_EXCEPT_RE.finditer(patch):
            findings.append(Finding(
                id=str(uuid4()),
                title="Bare except clause",
                category="reliability",
                severity=Severity.MEDIUM,
                file_path=fname,
                evidence=Evidence(excerpt=m.group(0).strip()),
                explanation="A bare except: catches all exceptions, including KeyboardInterrupt and SystemExit.",
                potential_impact="Errors may be silently swallowed, making debugging harder.",
                suggested_fix="Catch specific exception types instead of a bare except.",
                confidence=0.9,
                source=FindingSource.DETERMINISTIC,
            ))
    return findings


def _risk(findings: List[Finding]) -> RiskSummary:
    weights = {Severity.CRITICAL: 1.0, Severity.HIGH: 0.7, Severity.MEDIUM: 0.4, Severity.LOW: 0.2, Severity.INFO: 0.05}
    factors: List[RiskFactor] = []
    total = 0.0
    for sev, w in weights.items():
        count = sum(1 for f in findings if f.severity == sev and f.verification_status != VerificationStatus.REJECTED)
        if count:
            contrib = min(1.0, count * w * 0.25)
            total += contrib
            factors.append(RiskFactor(
                name=f"{sev.value}_findings",
                weight=w,
                contribution=round(contrib, 3),
                explanation=f"{count} {sev.value} finding(s) contributed {contrib:.2f}",
            ))
    unverified = sum(1 for f in findings if f.verification_status == VerificationStatus.UNVERIFIED)
    if unverified:
        contrib = min(0.3, unverified * 0.08)
        total += contrib
        factors.append(RiskFactor(
            name="unverified_ai",
            weight=0.3,
            contribution=round(contrib, 3),
            explanation=f"{unverified} unverified AI finding(s) add uncertainty",
        ))
    score = round(min(1.0, total), 3)
    level = "high" if score >= 0.6 else "medium" if score >= 0.3 else "low"
    return RiskSummary(
        score=score,
        level=level,
        formula="min(1.0, Σ(count_sev × weight_sev × 0.25) + unverified_penalty)",
        factors=factors,
    )


def _scorecard(findings: List[Finding]) -> Scorecard:
    total = len(findings)
    static = sum(1 for f in findings if f.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK)
    unverified = sum(1 for f in findings if f.verification_status == VerificationStatus.UNVERIFIED)
    human = sum(1 for f in findings if f.verification_status == VerificationStatus.NEEDS_HUMAN_REVIEW)
    with_evidence = sum(1 for f in findings if f.evidence and f.evidence.excerpt)
    return Scorecard(
        evidence_coverage=round(with_evidence / total, 2) if total else 1.0,
        static_analysis_coverage=round(static / total, 2) if total else 1.0,
        unverified_ratio=round(unverified / total, 2) if total else 0.0,
        total_findings=total,
        static_supported=static,
        ai_unverified=unverified,
        needs_human_review=human,
    )


def _test_suggestions(findings: List[Finding]) -> List[TestSuggestion]:
    suggestions: List[TestSuggestion] = []
    for f in findings:
        if f.category == "security" and f.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK:
            suggestions.append(TestSuggestion(
                title="Assert no secrets in committed files",
                rationale=f"Related to finding: {f.title}",
                related_finding_id=f.id,
                executed=False,
            ))
        if "except" in f.title.lower():
            suggestions.append(TestSuggestion(
                title="Unit test that exceptions are not silently swallowed",
                rationale=f"Related to finding: {f.title}",
                related_finding_id=f.id,
                executed=False,
            ))
    if not suggestions:
        suggestions.append(TestSuggestion(
            title="Add regression coverage for the changed paths",
            rationale="General suggestion — no specific defect-linked tests required",
            executed=False,
        ))
    return suggestions


def _executive_summary(pr_info: PRInfo | None, findings: List[Finding], is_demo: bool) -> str:
    if is_demo:
        return (
            "Demo review of a synthetic pull request containing deliberate defects "
            "(hardcoded secret, bare except) plus one correct change that is not flagged. "
            "One AI observation is present and correctly labelled unverified."
        )
    title = pr_info.title if pr_info else "PR"
    static = sum(1 for f in findings if f.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK)
    ai = sum(1 for f in findings if f.source == FindingSource.AI)
    return (
        f"Review of '{title}'. "
        f"{len(findings)} finding(s): {static} supported by static checks, {ai} AI observation(s) marked unverified. "
        f"No finding is presented as verified without evidence."
    )


def create_demo_review() -> ReviewResponse:
    review = store.create("demo", is_demo=True)
    review.status = ReviewStatus.ANALYZING
    review.progress_message = "Running labelled demo analysis"
    store.update(review)

    demo_files = [
        {"filename": "app/auth.py", "patch": "+API_KEY = \"sk-live-abc123secret\"\n+password = \"hunter2pass\"\n"},
        {"filename": "app/utils.py", "patch": "+try:\n+    do_work()\n+except:\n+    pass\n"},
        {"filename": "app/helpers.py", "patch": "+def add(a, b):\n+    return a + b\n"},
    ]

    findings = [
        Finding(
            id=str(uuid4()),
            title="Possible hardcoded secret",
            category="security",
            severity=Severity.HIGH,
            file_path="app/auth.py",
            evidence=Evidence(excerpt='API_KEY = "sk-live-abc123secret"'),
            explanation="Hardcoded API key pattern detected in the diff.",
            potential_impact="Credential exposure via repository history.",
            suggested_fix="Load from environment variable.",
            confidence=0.9,
            source=FindingSource.DETERMINISTIC,
        ),
        Finding(
            id=str(uuid4()),
            title="Bare except clause",
            category="reliability",
            severity=Severity.MEDIUM,
            file_path="app/utils.py",
            evidence=Evidence(excerpt="except:"),
            explanation="Bare except catches all exceptions including system-exiting ones.",
            potential_impact="Silent failure and harder debugging.",
            suggested_fix="Catch specific exception types.",
            confidence=0.92,
            source=FindingSource.DETERMINISTIC,
        ),
        Finding(
            id=str(uuid4()),
            title="Possible missing edge-case validation",
            category="correctness",
            severity=Severity.LOW,
            file_path="app/helpers.py",
            evidence=Evidence(excerpt="(AI observation – no concrete excerpt extracted)"),
            explanation="AI suggests the helper may lack edge-case checks. This has not been independently verified.",
            potential_impact="Unexpected inputs could produce incorrect results.",
            suggested_fix="Add explicit checks for None and boundary values.",
            confidence=0.4,
            source=FindingSource.AI,
        ),
    ]

    findings = validate_all(findings, demo_files)

    review.pr_info = PRInfo(
        owner="mergemate", repo="demo", number=1,
        title="Demo: secrets + bare except + correct helper",
        author="demo", state="open", base_branch="main", head_branch="demo",
        html_url="https://github.com/mergemate/demo/pull/1",
        changed_files=3, additions=8, deletions=0,
    )
    review.findings = findings
    review.risk = _risk(findings)
    review.test_suggestions = _test_suggestions(findings)
    review.scorecard = _scorecard(findings)
    review.executive_summary = _executive_summary(review.pr_info, findings, True)
    review.status = ReviewStatus.COMPLETED
    review.progress_message = "Demo analysis complete"
    return store.update(review)


async def run_review(pr_url: str, *, demo: bool = False) -> ReviewResponse:
    if demo or pr_url.strip().lower() in {"demo", "demo://local"}:
        return create_demo_review()

    owner, repo, number = parse_pr_url(pr_url)
    review = store.create(pr_url, is_demo=False)
    review.status = ReviewStatus.FETCHING
    review.progress_message = f"Fetching {owner}/{repo}#{number}"
    store.update(review)

    try:
        client = GitHubClient()
        pr = await client.get_pr(owner, repo, number)
        files = await client.get_pr_files(owner, repo, number)

        review.status = ReviewStatus.ANALYZING
        review.progress_message = "Running deterministic + AI analysis"
        review.pr_info = PRInfo(
            owner=owner, repo=repo, number=number,
            title=pr.get("title") or "",
            author=(pr.get("user") or {}).get("login") or "",
            state=pr.get("state") or "",
            base_branch=(pr.get("base") or {}).get("ref") or "",
            head_branch=(pr.get("head") or {}).get("ref") or "",
            html_url=pr.get("html_url") or pr_url,
            changed_files=pr.get("changed_files") or len(files),
            additions=pr.get("additions") or 0,
            deletions=pr.get("deletions") or 0,
        )
        store.update(review)

        det = _deterministic_scan(files)
        ai = await get_ai_provider().review(review.pr_info.title, files, det)
        findings = validate_all(det + ai, files)

        review.status = ReviewStatus.VALIDATING
        review.progress_message = "ProofLayer validation complete"
        review.findings = findings
        review.risk = _risk(findings)
        review.test_suggestions = _test_suggestions(findings)
        review.scorecard = _scorecard(findings)
        review.executive_summary = _executive_summary(review.pr_info, findings, False)
        review.status = ReviewStatus.COMPLETED
        review.progress_message = "Analysis complete"
        return store.update(review)
    except Exception as exc:
        review.status = ReviewStatus.FAILED
        review.error = str(exc)
        review.progress_message = "Analysis failed"
        store.update(review)
        raise
