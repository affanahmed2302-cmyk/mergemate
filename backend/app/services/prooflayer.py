from __future__ import annotations
from typing import Dict, List, Set
from app.schemas.common import FindingSource, VerificationStatus
from app.schemas.findings import Finding, ProofStep


def _file_set(files: List[dict]) -> Set[str]:
    return {f.get("filename") or f.get("path") or "" for f in files if f}


def _patch_map(files: List[dict]) -> Dict[str, str]:
    return {
        (f.get("filename") or ""): (f.get("patch") or "")
        for f in files
        if f and f.get("filename")
    }


def validate_finding(finding: Finding, files: List[dict]) -> Finding:
    """Run ProofLayer validation and attach evidence chain (Review Replay steps)."""
    steps: List[ProofStep] = []
    file_paths = _file_set(files)
    patches = _patch_map(files)

    # Step 1 — source recorded
    steps.append(ProofStep(
        step=1,
        name="Source recorded",
        status="passed",
        detail=f"Finding originated from {finding.source.value} analysis",
    ))

    # Step 2 — file reference
    file_ok = bool(finding.file_path) and finding.file_path in file_paths
    if not finding.file_path:
        steps.append(ProofStep(step=2, name="File reference checked", status="failed",
                               detail="No file path provided"))
    elif file_ok:
        steps.append(ProofStep(step=2, name="File reference checked", status="passed",
                               detail=f"Path '{finding.file_path}' exists in PR changed files"))
    else:
        steps.append(ProofStep(step=2, name="File reference checked", status="failed",
                               detail=f"Path '{finding.file_path}' not found in PR changed files"))

    # Step 3 — evidence / excerpt
    excerpt = (finding.evidence.excerpt or "").strip()
    evidence_ok = False
    if excerpt and finding.file_path:
        patch = patches.get(finding.file_path, "")
        # Soft match: excerpt fragment appears in patch or is a labelled deterministic snippet
        if excerpt in patch or excerpt.startswith("+") or "(AI observation" in excerpt:
            evidence_ok = "(AI observation" not in excerpt
            steps.append(ProofStep(
                step=3,
                name="Evidence assessed",
                status="passed" if evidence_ok else "partial",
                detail="Concrete excerpt located in diff" if evidence_ok else "AI observation without concrete excerpt",
            ))
        else:
            steps.append(ProofStep(step=3, name="Evidence assessed", status="partial",
                                   detail="Excerpt provided but not located verbatim in available patch"))
    else:
        steps.append(ProofStep(step=3, name="Evidence assessed", status="failed",
                               detail="No usable evidence excerpt"))

    # Step 4 — support assessment (existence of text ≠ proof of defect)
    steps.append(ProofStep(
        step=4,
        name="Support assessment",
        status="passed",
        detail="Evidence presence is recorded; existence of text does not prove a defect",
    ))

    # Final status assignment — never claim AI findings as verified
    if finding.source == FindingSource.AI:
        status = VerificationStatus.UNVERIFIED
        final_detail = "AI-generated finding remains unverified (no independent deterministic proof)"
    elif finding.source == FindingSource.DETERMINISTIC and file_ok and evidence_ok:
        status = VerificationStatus.SUPPORTED_BY_STATIC_CHECK
        final_detail = "Deterministic rule matched concrete evidence in the diff"
    elif finding.source == FindingSource.DETERMINISTIC and file_ok:
        status = VerificationStatus.NEEDS_HUMAN_REVIEW
        final_detail = "Deterministic signal with incomplete evidence — needs human review"
    elif not file_ok:
        status = VerificationStatus.REJECTED
        final_detail = "File reference invalid — finding rejected"
    else:
        status = VerificationStatus.NEEDS_HUMAN_REVIEW
        final_detail = "Insufficient evidence for automatic verification"

    steps.append(ProofStep(step=5, name="Final decision", status="passed", detail=final_detail))

    finding.verification_status = status
    finding.proof_steps = steps
    return finding


def validate_all(findings: List[Finding], files: List[dict]) -> List[Finding]:
    return [validate_finding(f, files) for f in findings]
