# MergeMate

**Evidence-first AI Pull Request Intelligence**

> No finding should be presented as verified without supporting evidence.

MergeMate analyses GitHub pull requests, combines deterministic static checks with optional AI review, and runs every finding through **ProofLayer** — an independent evidence-validation engine.

**Theme:** Developer Productivity (also pairs with AI for Open Source)

## Features

- Real GitHub PR ingestion (public repos; token optional)
- Diff extraction and deterministic rules (secrets, bare except, …)
- AI review via provider-agnostic adapter (mock by default for reliable demos)
- **ProofLayer**: validates file paths + evidence; AI-only findings stay `unverified`
- Transparent risk heuristic (formula exposed, never claimed as calibrated probability)
- Test suggestions clearly marked as not executed
- Markdown + JSON report export
- Labelled demo mode that works offline

## Quick start

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
python3 -m http.server 3000
```
Open http://localhost:3000

### Demo (no GitHub required)
Click **“Run labelled demo”** in the UI, or:
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"pr_url":"demo","demo":true}'
```

### Live public PR
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"pr_url":"https://github.com/octocat/Hello-World/pull/1"}'
```

## Tests
```bash
cd backend && source .venv/bin/activate && pytest tests/ -v
```

## Environment
Copy `.env.example` to `.env`.  
`GITHUB_TOKEN` is optional for public repos.  
`AI_PROVIDER=mock` by default — no paid keys required.

## AI tools used in development
This project was built with assistance from **Grok (xAI)**. All critical paths are covered by automated tests. AI findings in the product itself are always labelled and never presented as verified without evidence.

## Licence
MIT — see [LICENSE](LICENSE).

## Credits
- FastAPI, Pydantic, httpx, tenacity
- Tailwind CSS (CDN for the demo UI)
- GitHub REST API
