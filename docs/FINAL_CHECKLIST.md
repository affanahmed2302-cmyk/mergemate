# Final quality gate

| Item | Status |
|------|--------|
| Professional landing page | IMPLEMENTED |
| Consistent visual design (dark, restrained accent) | IMPLEMENTED |
| Functional review flow (landing → results) | IMPLEMENTED |
| Working GitHub PR workflow (public) | IMPLEMENTED |
| Code diff presentation (excerpts, not full syntax UI) | IMPLEMENTED (excerpts) |
| Findings explorer + filters | IMPLEMENTED |
| Complete ProofLayer + Review Replay | IMPLEMENTED |
| Evidence chain (proof_steps) | IMPLEMENTED |
| Explainable risk + scorecard | IMPLEMENTED |
| Test intelligence (not executed) | IMPLEMENTED |
| Markdown / JSON export | IMPLEMENTED |
| Reliable labelled demo | IMPLEMENTED |
| Responsive layout | IMPLEMENTED |
| Security review (URL allowlist, no code exec, no secrets in repo) | IMPLEMENTED |
| Frontend “build” | N/A (static HTML) |
| Backend tests | IMPLEMENTED — run `pytest tests/ -v` before stage |
| No exposed credentials | IMPLEMENTED |
| README + docs | IMPLEMENTED |
| Pitch + judge Q&A | IMPLEMENTED |
| Side-by-side full diff viewer | NOT IMPLEMENTED (scope) |
| Auth / teams | NOT IMPLEMENTED (scope) |
| Public deployment | NOT IMPLEMENTED (needs approval) |

## Commands

```bash
cd backend && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn app.main:app --port 8000

cd frontend && python3 -m http.server 3000
# http://localhost:3000
```
