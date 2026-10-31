"""Property: AI findings can never become supported_by_static_check."""
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.common import FindingSource, VerificationStatus
from app.schemas.findings import Evidence, Finding
from app.services.prooflayer import validate_finding
from uuid import uuid4

client = TestClient(app)


def test_ai_cannot_be_static_supported():
    files = [{"filename": "a.py", "patch": "+x = 1\n"}]
    f = Finding(
        id=str(uuid4()),
        title="Invented issue",
        category="correctness",
        file_path="a.py",
        evidence=Evidence(excerpt="x = 1"),
        explanation="AI claim",
        source=FindingSource.AI,
        confidence=0.99,
    )
    out = validate_finding(f, files)
    assert out.verification_status == VerificationStatus.UNVERIFIED
    assert out.source == FindingSource.AI


def test_demo_ai_stays_unverified():
    r = client.post("/api/v1/reviews", json={"pr_url": "demo", "demo": True})
    assert r.status_code == 200
    data = r.json()
    ai = [f for f in data["findings"] if f["source"] == "ai"]
    assert ai, "expected at least one AI finding in demo"
    for f in ai:
        assert f["verification_status"] == "unverified"


def test_demo_has_clean_path_message():
    r = client.post("/api/v1/reviews", json={"pr_url": "demo", "demo": True})
    data = r.json()
    assert "helpers" in (data.get("executive_summary") or "").lower() or "clean" in (data.get("executive_summary") or "").lower()
