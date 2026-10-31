from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_demo_end_to_end():
    r = client.post("/api/v1/reviews", json={"pr_url": "demo", "demo": True})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "completed"
    assert data["is_demo"] is True
    findings = data["findings"]
    assert len(findings) >= 3

    statuses = {f["verification_status"] for f in findings}
    assert "supported_by_static_check" in statuses
    assert "unverified" in statuses

    # AI findings must never be marked supported_by_static_check
    for f in findings:
        if f["source"] == "ai":
            assert f["verification_status"] == "unverified"
        # every finding has ProofLayer steps (Review Replay)
        assert len(f.get("proof_steps") or []) >= 4

    assert data.get("scorecard") is not None
    assert data.get("risk") is not None
    assert data.get("executive_summary")

def test_invalid_url():
    r = client.post("/api/v1/reviews", json={"pr_url": "https://evil.example/x"})
    assert r.status_code in (400, 422)

def test_report_markdown():
    r = client.post("/api/v1/reviews", json={"pr_url": "demo", "demo": True})
    rid = r.json()["id"]
    md = client.get(f"/api/v1/reviews/{rid}/report.md")
    assert md.status_code == 200
    assert "ProofLayer" in md.text or "Verification" in md.text or "supported" in md.text
