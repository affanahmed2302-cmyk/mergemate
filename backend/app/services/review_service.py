from __future__ import annotations

import re
from typing import List, Optional, Tuple
from uuid import uuid4

from app.core.store import store
from app.integrations.ai import get_ai_provider
from app.integrations.github import GitHubClient, parse_pr_url
from app.schemas.common import FindingSource, ReviewStatus, Severity, VerificationStatus
from app.schemas.findings import Evidence, Finding
from app.schemas.reviews import (
    PRInfo,
    ReviewResponse,
    RiskFactor,
    RiskSummary,
    Scorecard,
    TestSuggestion,
)
from app.services.prooflayer import validate_all

# --- Deterministic rule library (few strong detectors, evidence-first) ---
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)
BARE_EXCEPT_RE = re.compile(r"except\s*:\s*(#.*)?$", re.MULTILINE)
EVAL_RE = re.compile(r"\beval\s*\(")
EXEC_RE = re.compile(r"\bexec\s*\(")
PICKLE_RE = re.compile(r"\bpickle\.loads\s*\(")
SUBPROCESS_SHELL_RE = re.compile(r"subprocess\.[a-zA-Z_]+\([^)]*shell\s*=\s*True")
YAML_LOAD_RE = re.compile(r"\byaml\.load\s*\(")


def _line_from_patch(patch: str, match_start: int) -> Optional[int]:
    """Best-effort new-file line number from a unified diff patch."""
    if not patch:
        return None
    pos = 0
    current_new = 0
    for line in patch.splitlines():
        if line.startswith("@@"):
            m = re.search(r"\+(\(d+)(?:,(\(d+))?", line.replace("(", ""))
            # fallback parse
            m = re.search(r"\+(\\d+)", line)
            if m:
                current_new = int(m.group(1)) - 1
            continue
        line_start = pos
        line_end = pos + len(line) + 1
        if line.startswith("+"):
            current_new += 1
            if line_start <= match_start < line_end or (match_start >= line_start and match_start < line_end):
                return current_new
        elif line.startswith("-"):
            pass
        else:
            current_new += 1
        pos = line_end
    return None


def _line_for_match(patch: str, matched: str) -> Optional[int]:
    idx = patch.find(matched)
    if idx < 0:
        return None
    new_line = 0
    cursor = 0
    for line in patch.splitlines(keepends=True):
        if line.startswith("@@"):
            m = re.search(r"\+(\\d+)", line)
            if m:
                new_line = int(m.group(1)) - 1
            cursor += len(line)
            continue
        if line.startswith("+"):
            new_line += 1
            if cursor <= idx < cursor + len(line):
                return new_line
        elif not line.startswith("-"):
            new_line += 1
        cursor += len(line)
    return None


def _add(
    findings: List[Finding],
    *,
    title: str,
    category: str,
    severity: Severity,
    file_path: str,
    excerpt: str,
    explanation: str,
    impact: str,
    fix: str,
    confidence: float,
    patch: str,
) -> None:
    start = _line_for_match(patch, excerpt) or _line_for_match(patch, excerpt.split("\n")[0])
    findings.append(
        Finding(
            id=str(uuid4()),
            title=title,
            category=category,
            severity=severity,
            file_path=file_path,
            evidence=Evidence(excerpt=excerpt[:160], start_line=start, end_line=start, notes="Anchored from unified diff when possible"),
            explanation=explanation,
            potential_impact=impact,
            suggested_fix=fix,
            confidence=confidence,
            source=FindingSource.DETERMINISTIC,
        )
    )


def _deterministic_scan(files: List[dict]) -> List[Finding]:
    findings: List[Finding] = []
    for f in files:
        fname = f.get("filename") or ""
        patch = f.get("patch") or ""
        # Only scan added lines for some rules
        for m in SECRET_RE.finditer(patch):
            _add(
                findings,
                title="Possible hardcoded secret",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                excerpt=m.group(0)[:120],
                explanation="A pattern resembling a hardcoded credential was found in the diff.",
                impact="Credentials in source can leak via repository history.",
                fix="Move secrets to environment variables or a secrets manager.",
                confidence=0.88,
                patch=patch,
            )
        for m in BARE_EXCEPT_RE.finditer(patch):
            _add(
                findings,
                title="Bare except clause",
                category="reliability",
                severity=Severity.MEDIUM,
                file_path=fname,
                excerpt=m.group(0).strip(),
                explanation="A bare except: catches all exceptions, including KeyboardInterrupt and SystemExit.",
                impact="Errors may be silently swallowed, making debugging harder.",
                fix="Catch specific exception types instead of a bare except.",
                confidence=0.9,
                patch=patch,
            )
        for m in EVAL_RE.finditer(patch):
            _add(
                findings,
                title="Use of eval()",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                excerpt=m.group(0),
                explanation="eval() executes arbitrary expressions and is a common injection sink.",
                impact="Attacker-controlled input could lead to remote code execution.",
                fix="Avoid eval; use ast.literal_eval or explicit parsing.",
                confidence=0.9,
                patch=patch,
            )
        for m in EXEC_RE.finditer(patch):
            _add(
                findings,
                title="Use of exec()",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                excerpt=m.group(0),
                explanation="exec() runs dynamic code and should almost never appear in application logic.",
                impact="Code injection risk if input is not fully trusted.",
                fix="Remove exec() or isolate in a tightly controlled sandbox.",
                confidence=0.9,
                patch=patch,
            )
        for m in PICKLE_RE.finditer(patch):
            _add(
                findings,
                title="Unsafe pickle.loads",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                excerpt=m.group(0),
                explanation="pickle.loads can execute arbitrary code during deserialization.",
                impact="Untrusted pickle data can compromise the process.",
                fix="Use a safe format (JSON) or cryptographic integrity with a trusted producer.",
                confidence=0.92,
                patch=patch,
            )
        for m in SUBPROCESS_SHELL_RE.finditer(patch):
            _add(
                findings,
                title="subprocess with shell=True",
                category="security",
                severity=Severity.HIGH,
                file_path=fname,
                excerpt=m.group(0)[:120],
                explanation="shell=True enables shell injection if arguments include untrusted input.",
                impact="Command injection leading to system compromise.",
                fix="Pass argument lists with shell=False and validate inputs.",
                confidence=0.87,
                patch=patch,
            )
        for m in YAML_LOAD_RE.finditer(patch):
            _add(
                findings,
                title="Unsafe yaml.load",
                category="security",
                severity=Severity.MEDIUM,
                file_path=fname,
                excerpt=m.group(0),
                explanation="yaml.load without SafeLoader can construct arbitrary Python objects.",
                impact="Deserialization attacks from untrusted YAML.",
                fix="Use yaml.safe_load or SafeLoader explicitly.",
                confidence=0.85,
                patch=patch,
            )
    return findings


def _clean_paths(files: List[dict], findings: List[Finding]) -> List[str]:
    """Paths scanned with no deterministic findings — false-accusation avoidance."""
    flagged = {f.file_path for f in findings if f.file_path}
    return sorted({(f.get("filename") or "") for f in files if f.get("filename") and f.get("filename") not in flagged})


def _risk(findings: List[Finding]) -> RiskSummary:
    weights = {
        Severity.CRITICAL: 1.0,
        Severity.HIGH: 0.7,
        Severity.MEDIUM: 0.4,
        Severity.LOW: 0.2,
        Severity.INFO: 0.05,
    }
    factors: List[RiskFactor] = []
    total = 0.0
    for sev, w in weights.items():
        count = sum(
            1
            for f in findings
            if f.severity == sev and f.verification_status != VerificationStatus.REJECTED
        )
        if count:
            contrib = min(1.0, count * w * 0.25)
            total += contrib
            factors.append(
                RiskFactor(
                    name=f"{sev.value}_findings",
                    weight=w,
                    contribution=round(contrib, 3),
                    explanation=f"{count} {sev.value} finding(s) contributed {contrib:.2f}",
                )
            )
    unverified = sum(1 for f in findings if f.verification_status == VerificationStatus.UNVERIFIED)
    if unverified:
        contrib = min(0.3, unverified * 0.08)
        total += contrib
        factors.append(
            RiskFactor(
                name="unverified_ai",
                weight=0.3,
                contribution=round(contrib, 3),
                explanation=f"{unverified} unverified AI finding(s) add uncertainty",
            )
        )
    score = round(min(1.0, total), 3)
    level = "high" if score >= 0.6 else "medium" if score >= 0.3 else "low"
    return RiskSummary(
        score=score,
        level=level,
        formula="min(1.0, Σ(count_sev × weight_sev × 0.25) + unverified_penalty)",
        factors=factors,
        disclaimer="Heuristic indicator only — not a calibrated probability of production failure.",
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
        disclaimer="Scorecard measures evidence labelling, not correctness of the underlying code.",
    )


def _test_suggestions(findings: List[Finding]) -> List[TestSuggestion]:
    suggestions: List[TestSuggestion] = []
    for f in findings:
        if f.category == "security" and f.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK:
            suggestions.append(
                TestSuggestion(
                    title="Assert no secrets in committed files",
                    rationale=f"Related to finding: {f.title}",
                    related_finding_id=f.id,
                    executed=False,
                )
            )
        if "except" in f.title.lower():
            suggestions.append(
                TestSuggestion(
                    title="Unit test that exceptions are not silently swallowed",
                    rationale=f"Related to finding: {f.title}",
                    related_finding_id=f.id,
                    executed=False,
                )
            )
        if "eval" in f.title.lower() or "exec" in f.title.lower():
            suggestions.append(
                TestSuggestion(
                    title="Forbid dynamic code execution in CI lint",
                    rationale=f"Related to finding: {f.title}",
                    related_finding_id=f.id,
                    executed=False,
                )
            )
    if not suggestions:
        suggestions.append(
            TestSuggestion(
                title="Add regression coverage for the changed paths",
                rationale="General suggestion — no specific defect-linked tests required",
                executed=False,
            )
        )
    return suggestions


def _executive_summary(
    pr_info: PRInfo | None,
    findings: List[Finding],
    is_demo: bool,
    clean: List[str] | None = None,
) -> str:
    clean = clean or []
    if is_demo:
        base = (
            "Demo review of a synthetic pull request containing deliberate defects "
            "(hardcoded secret, bare except) plus one correct change that is not flagged. "
            "One AI observation is present and correctly labelled unverified."
        )
        if clean:
            base += f" Clean paths (no deterministic flag): {', '.join(clean)}."
        return base
    title = pr_info.title if pr_info else "PR"
    static = sum(1 for f in findings if f.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK)
    ai = sum(1 for f in findings if f.source == FindingSource.AI)
    msg = (
        f"Review of '{title}'. "
        f"{len(findings)} finding(s): {static} supported by static checks, {ai} AI observation(s) marked unverified. "
        f"No finding is presented as verified without evidence."
    )
    if clean:
        msg += f" Scanned without deterministic flags: {', '.join(clean[:5])}{'…' if len(clean) > 5 else ''}."
    return msg


def create_demo_review() -> ReviewResponse:
    review = store.create("demo", is_demo=True)
    review.status = ReviewStatus.ANALYZING
    review.progress_message = "Running labelled demo analysis"
    store.update(review)

    demo_files = [
        {"filename": "app/auth.py", "patch": "@@ -1,0 +1,2 @@\n+API_KEY = \"sk-live-abc123secret\"\n+password = \"hunter2pass\"\n"},
        {"filename": "app/utils.py", "patch": "@@ -1,0 +1,4 @@\n+try:\n+    do_work()\n+except:\n+    pass\n"},
        {"filename": "app/helpers.py", "patch": "@@ -1,0 +1,2 @@\n+def add(a, b):\n+    return a + b\n"},
        {"filename": "app/legacy.py", "patch": "@@ -1,0 +1,1 @@\n+result = eval(user_expr)\n"},
    ]

    findings = _deterministic_scan(demo_files)
    # AI observation on clean helper — must stay unverified after ProofLayer
    findings.append(
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
        )
    )

    findings = validate_all(findings, demo_files)
    clean = _clean_paths(demo_files, [f for f in findings if f.source == FindingSource.DETERMINISTIC])

    review.pr_info = PRInfo(
        owner="mergemate",
        repo="demo",
        number=1,
        title="Demo: secrets + bare except + eval + correct helper",
        author="demo",
        state="open",
        base_branch="main",
        head_branch="demo",
        html_url="https://github.com/mergemate/demo/pull/1",
        changed_files=4,
        additions=9,
        deletions=0,
    )
    review.findings = findings
    review.risk = _risk(findings)
    review.test_suggestions = _test_suggestions(findings)
    review.scorecard = _scorecard(findings)
    review.executive_summary = _executive_summary(review.pr_info, findings, True, clean)
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
            owner=owner,
            repo=repo,
            number=number,
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
        clean = _clean_paths(files, det)

        review.status = ReviewStatus.VALIDATING
        review.progress_message = "ProofLayer validation complete"
        review.findings = findings
        review.risk = _risk(findings)
        review.test_suggestions = _test_suggestions(findings)
        review.scorecard = _scorecard(findings)
        review.executive_summary = _executive_summary(review.pr_info, findings, False, clean)
        review.status = ReviewStatus.COMPLETED
        review.progress_message = "Analysis complete"
        return store.update(review)
    except Exception as exc:
        review.status = ReviewStatus.FAILED
        review.error = str(exc)
        review.progress_message = "Analysis failed"
        store.update(review)
        raise
