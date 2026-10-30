# MergeMate

**Evidence-first AI Pull Request Intelligence**

> *No finding should be presented as verified without supporting evidence.*

---

## The problem we are solving

AI code reviewers are fast and persuasive. They can also be wrong.

A typical AI review might say:

> “This function is missing null checks on line 47.”

If the line numbers are invented, the file path is wrong, or the claim is pure speculation, developers still have to spend time verifying it. The more confident the language, the more dangerous the false positive.

**MergeMate was built for that gap.**

It does not try to replace human judgment. It tries to make AI-assisted review *trustworthy* by forcing every finding through an independent evidence layer called **ProofLayer**.

---

## What MergeMate is

MergeMate is an open-source pull-request analysis tool that:

1. Accepts a real GitHub Pull Request URL  
2. Retrieves actual metadata, changed files and patches via the GitHub REST API  
3. Runs deterministic static checks that produce findings with concrete evidence  
4. Optionally runs an AI reviewer (provider-agnostic; mock by default)  
5. Passes **every** finding through **ProofLayer**  
6. Labels each finding with an honest verification status  
7. Surfaces risk indicators and test suggestions without over-claiming  
8. Exports a clean Markdown or JSON report  

The product is deliberately designed so that an AI-only observation can never be shown as “verified” or “test-confirmed” unless the supporting evidence actually exists.

### Signature technology: ProofLayer

ProofLayer is the core differentiator.

For every finding it performs:

| Stage | What it checks |
|-------|----------------|
| Schema | Required fields present |
| File validation | Path exists in the PR’s changed files |
| Line / evidence validation | Excerpt can be located in the available patch |
| Support assessment | Existence of an excerpt ≠ proof of a defect |
| Status assignment | One of the five honest statuses below |

**Verification statuses**

| Status | Meaning |
|--------|---------|
| `supported_by_static_check` | Deterministic rule matched real evidence in the diff |
| `unverified` | AI or heuristic observation with no independent proof |
| `needs_human_review` | Evidence incomplete or ambiguous |
| `rejected` | Invalid path or unsupported reference |
| `test_confirmed` | Reserved for real test execution (never assigned in the current MVP because we never execute repository code) |

This is the product promise in one sentence:

> **We built a way to check whether an AI review deserves to be trusted.**

---

## Why this matters for developers

- Reduces noise from confident but incorrect AI comments  
- Makes the source of every finding explicit (deterministic vs AI)  
- Prevents false accusations on correct code  
- Gives reviewers a clear “human review needed” signal  
- Keeps the entire pipeline free of secret leakage and code execution on the server  

MergeMate is aimed at the **Developer Productivity** theme: tools that save developers time and frustration while remaining honest about their limits.

---

## Features at a glance

- **Real GitHub integration** — public PRs work with no token; private repos supported when a read-only token is supplied  
- **Diff & context engine** — extracts additions/deletions and preserves evidence excerpts  
- **Deterministic analysis** — practical rules (hardcoded-secret patterns, bare `except`, …) that always carry evidence  
- **AI review adapter** — provider-independent interface; ships with a reliable mock provider so demos never depend on paid keys  
- **ProofLayer** — independent verification of every finding  
- **Risk intelligence** — transparent weighted heuristic with the formula and contributing factors exposed (never presented as a calibrated failure probability)  
- **Test intelligence** — suggests missing test scenarios and clearly marks them as *not executed*  
- **Reports** — one-click Markdown and JSON export  
- **Labelled demo mode** — works fully offline so judges always see a complete flow  

---

## Architecture (high level)

```
User → Frontend (static UI)
         ↓
      FastAPI backend
         ↓
   ┌─────┴─────────────────────┐
   │                           │
GitHub Client            AI Provider
(read-only)              (mock / configurable)
   │                           │
   └─────┬─────────────────────┘
         ↓
   Finding Normaliser
         ↓
      ProofLayer
         ↓
   Risk + Test Intelligence
         ↓
   Structured Report (JSON / Markdown)
```

- **Backend**: Python, FastAPI, Pydantic  
- **Frontend**: Single-page professional dark UI (Tailwind via CDN)  
- **Storage**: In-memory for the MVP (no database required)  
- **Security**: Only `github.com` host accepted, no repository code execution, secrets only via environment variables  

More detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Quick start

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `curl http://localhost:8000/health`

### 2. Frontend

```bash
cd frontend
python3 -m http.server 3000
```

Open **http://localhost:3000**

### 3. Run the labelled demo (recommended for judges)

In the UI click **“Run labelled demo”**, or:

```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"pr_url":"demo","demo":true}'
```

Poll `GET /api/v1/reviews/{id}` until `status` is `completed`.

You will see:

- Two deterministic findings marked `supported_by_static_check`  
- One AI finding marked `unverified`  
- One correct change that is **not** incorrectly flagged  

### 4. Analyse a real public PR

```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"pr_url":"https://github.com/octocat/Hello-World/pull/1"}'
```

---

## Environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | No | Optional classic PAT (read-only) for higher rate limits / private repos |
| `AI_PROVIDER` | No | Defaults to `mock`. Real providers can be wired later |
| `CORS_ORIGINS` | No | Defaults to `http://localhost:3000` |
| `MAX_FILES_PER_REVIEW` | No | Safety bound (default 40) |

**Never commit real API keys or tokens.**

---

## Tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Critical paths covered:

- Health endpoint  
- GitHub URL validation (accept / reject)  
- Full demo pipeline including ProofLayer status assignment  
- Report export  

---

## Demo script for judges (≈ 3 minutes)

See [`docs/DEMO.md`](docs/DEMO.md) for the full script.

1. Open the UI and click **Run labelled demo**  
2. Show the summary cards (findings, static-supported, unverified AI, risk)  
3. Expand a deterministic finding → point at the evidence excerpt and `supported_by_static_check`  
4. Expand the AI finding → show it is clearly labelled `unverified`  
5. Show the “Correct change – no issue found” entry (false-accusation avoidance)  
6. Export Markdown / JSON  

**One-liner to leave the judges with:**

> “We didn’t build another AI code reviewer. We built a way to check whether an AI review deserves to be trusted.”

---

## Project structure

```
mergemate/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── core/          # config, exceptions, store
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # review orchestration + ProofLayer
│   │   └── integrations/  # GitHub client + AI provider
│   ├── tests/
│   └── requirements.txt
├── frontend/              # Professional dark single-page UI
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md
│   └── DEMO.md
├── .env.example
├── LICENSE                # MIT
└── README.md
```

---

## Security & limitations (honest)

- Repository content is treated as untrusted  
- **No repository code is ever executed** on the application server  
- Only `github.com` hosts are accepted (SSRF protection)  
- AI findings remain `unverified` unless independently corroborated  
- Deterministic rules are pattern-based (not a full static-analysis engine)  
- In-memory store — reviews are lost on restart (intentional for the MVP)  
- No API authentication in the current release  

Full notes: [`docs/SECURITY.md`](docs/SECURITY.md)

---

## AI tools used in development

This project was built with assistance from **Grok (xAI)**.

All critical product paths are covered by automated tests. Inside the product itself, AI-generated findings are always labelled and never presented as verified without evidence.

---

## Licence

MIT — see [LICENSE](LICENSE).

## Credits

- [FastAPI](https://fastapi.tiangolo.com/) · [Pydantic](https://docs.pydantic.dev/) · [httpx](https://www.python-httpx.org/) · [tenacity](https://tenacity.readthedocs.io/)
- Tailwind CSS (CDN) for the demo UI
- GitHub REST API

---

**Built for DevForge × Hacktoberfest 2026 · Bengaluru**  
Theme: **Developer Productivity**
