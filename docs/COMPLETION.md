# MergeMate — Live Completion Checklist

> Updated for DevForge code freeze readiness. Only mark TESTED after running the relevant test.

## Core product

| Item | Status |
|------|--------|
| Website (MergeMate is the product UI) | IMPLEMENTED |
| GitHub PR URL ingest (public) | IMPLEMENTED |
| Diff / file extraction | IMPLEMENTED |
| Deterministic static checks (secrets, bare except) | IMPLEMENTED |
| AI reviewer (mock provider) | IMPLEMENTED |
| ProofLayer validation | IMPLEMENTED |
| Findings explorer with severity / source / status | IMPLEMENTED |
| Risk indicator with visible formula | IMPLEMENTED |
| Test suggestions (explicitly not executed) | IMPLEMENTED |
| Markdown + JSON report export | IMPLEMENTED |
| Labelled offline demo mode | IMPLEMENTED |
| Executive summary | IMPLEMENTED |
| Intelligence Scorecard | IMPLEMENTED |
| Review Replay / Evidence chain (proof_steps) | IMPLEMENTED |
| False-positive feedback (useful / incorrect / disputed) | IMPLEMENTED |
| Automated tests (health, ProofLayer, demo pipeline) | IMPLEMENTED |
| README + architecture + security docs | IMPLEMENTED |
| MIT licence, no committed secrets | IMPLEMENTED |

## Intentionally not built (scope control)

| Item | Reason |
|------|--------|
| Auth / teams / billing | Out of scope for 12h hackathon |
| Real test execution (`test_confirmed`) | We never execute repo code |
| Live model fine-tuning from feedback | Feedback is recorded only |
| GitHub App / webhooks | REST read-only is enough for demo |
| Public cloud deployment | Requires explicit approval |

## How to verify before demo

```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn app.main:app --port 8000
# other terminal:
cd frontend && python3 -m http.server 3000
# open http://localhost:3000 → Run labelled demo
```
