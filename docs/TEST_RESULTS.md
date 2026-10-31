# Automated test results

**Executed:** 2026-10-31 (pre-submission verification)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3
collected 7 items

tests/test_demo_pipeline.py::test_demo_end_to_end PASSED
tests/test_demo_pipeline.py::test_invalid_url PASSED
tests/test_demo_pipeline.py::test_report_markdown PASSED
tests/test_health.py::test_health PASSED
tests/test_prooflayer.py::test_deterministic_with_evidence_supported PASSED
tests/test_prooflayer.py::test_ai_always_unverified PASSED
tests/test_prooflayer.py::test_bad_path_rejected PASSED

======================== 7 passed, 2 warnings in 0.53s =========================
```

## Demo rehearsal (same session)

| Check | Result |
|-------|--------|
| GET /health | 200 ok |
| GET / (SPA) | 200 HTML |
| GET /prooflayer | 200 SPA fallback |
| POST demo review | completed, 3 findings |
| Deterministic → supported_by_static_check | yes (2) |
| AI → unverified | yes (1) |
| ProofLayer steps per finding | 5 |
| Markdown report | 200 |
| Invalid non-github URL | 400 |

**Command to re-run:**
```bash
cd backend && source .venv/bin/activate && pytest tests/ -v
```
