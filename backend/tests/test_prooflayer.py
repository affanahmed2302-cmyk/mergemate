from app.schemas.common import FindingSource, Severity, VerificationStatus
from app.schemas.findings import Evidence, Finding
from app.services.prooflayer import validate_finding
from uuid import uuid4

def _f(**kw):
    base = dict(id=str(uuid4()), title="t", category="c", severity=Severity.MEDIUM,
                evidence=Evidence(), explanation="e", source=FindingSource.DETERMINISTIC)
    base.update(kw)
    return Finding(**base)

def test_deterministic_with_evidence_supported():
    files = [{"filename": "a.py", "patch": "+API_KEY = \"secretvalue123\"\n"}]
    f = _f(file_path="a.py", evidence=Evidence(excerpt='API_KEY = "secretvalue123"'),
           source=FindingSource.DETERMINISTIC)
    out = validate_finding(f, files)
    assert out.verification_status == VerificationStatus.SUPPORTED_BY_STATIC_CHECK
    assert len(out.proof_steps) == 5

def test_ai_always_unverified():
    files = [{"filename": "a.py", "patch": "+x = 1\n"}]
    f = _f(file_path="a.py", source=FindingSource.AI,
           evidence=Evidence(excerpt="(AI observation – no concrete excerpt extracted)"))
    out = validate_finding(f, files)
    assert out.verification_status == VerificationStatus.UNVERIFIED

def test_bad_path_rejected():
    files = [{"filename": "a.py", "patch": "+x\n"}]
    f = _f(file_path="missing.py", source=FindingSource.DETERMINISTIC,
           evidence=Evidence(excerpt="x"))
    out = validate_finding(f, files)
    assert out.verification_status == VerificationStatus.REJECTED
