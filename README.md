# MergeMate

**Evidence-first AI Pull Request Intelligence**

> *No finding should be presented as verified without supporting evidence.*

**DevForge × Hacktoberfest 2026 · Bengaluru**  
Theme: **Developer Productivity**  
Licence: **MIT**  
Repo: https://github.com/affanahmed2302-cmyk/mergemate

---

## Hackathon submission (judges)

| Item | Link / command |
|------|----------------|
| Public repo | https://github.com/affanahmed2302-cmyk/mergemate |
| OSI licence | [MIT LICENSE](LICENSE) |
| Submission notes | [docs/HACKATHON_SUBMISSION.md](docs/HACKATHON_SUBMISSION.md) |
| Test results | [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md) — **7/7 passed** |
| Pitch / Q&A | [docs/PITCH.md](docs/PITCH.md) · [docs/JUDGE_QA.md](docs/JUDGE_QA.md) · [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) |
| Pitch deck | Download `MergeMate_Pitch_Deck.pptx` from team share, or generate (see below) |

### One-command run (website + API)

```bash
git clone https://github.com/affanahmed2302-cmyk/mergemate.git
cd mergemate/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn app.main:app --port 8000
```

Open **http://localhost:8000** — public site and `/app` on the same origin.

### 3-minute demo

1. Click **Explore labelled demo** (or open `/demo`)
2. Show static-supported vs **unverified** AI findings
3. Open **ProofLayer — Review Replay**
4. Export Markdown

> We didn’t build another AI code reviewer. We built a way to check whether an AI review deserves to be trusted.

### AI tools disclosure

Built with assistance from **Grok (xAI)**. Critical paths are covered by automated tests. In-product AI findings are always labelled and never presented as verified without evidence.

---

## The problem we are solving

AI code reviewers are fast and persuasive. They can also be wrong.

A typical AI review might say:

> “This function is missing null checks on line 47.”

If the line numbers are invented, the file path is wrong, or the claim is pure speculation, developers still have to spend time verifying it.

**MergeMate was built for that gap** — an independent evidence layer called **ProofLayer** so AI-assisted review can be trusted.

---

## What MergeMate is

1. Accepts a real GitHub Pull Request URL  
2. Retrieves metadata, changed files and patches via the GitHub REST API  
3. Runs deterministic static checks with concrete evidence  
4. Optionally runs an AI reviewer (mock by default)  
5. Passes **every** finding through **ProofLayer**  
6. Labels verification status honestly  
7. Surfaces risk indicators and test suggestions without over-claiming  
8. Exports Markdown / JSON reports  

### ProofLayer statuses

| Status | Meaning |
|--------|---------|
| `supported_by_static_check` | Deterministic rule + real evidence |
| `unverified` | AI observation without independent proof |
| `needs_human_review` | Incomplete or ambiguous evidence |
| `rejected` | Invalid path or unsupported reference |
| `test_confirmed` | Reserved — never assigned (no code execution) |

---

## Product surface

**Public website:** `/` `/about` `/features` `/prooflayer` `/how-it-works` `/docs` `/demo`  
**Application:** `/app` `/app/review` `/app/review/[id]` `/app/findings` `/app/prooflayer` `/app/intelligence` `/app/tests` `/app/history` `/app/reports` `/app/settings`

---

## Features

- Real GitHub PR ingest (public; optional token)
- Deterministic rules (secrets, bare except) with evidence
- Provider-agnostic AI adapter (mock default)
- ProofLayer + Review Replay (5-step chain)
- Intelligence Scorecard + explainable risk heuristic
- Test suggestions marked **not executed**
- Feedback: useful / incorrect / disputed
- Labelled offline demo
- Markdown + JSON export

---

## Environment

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | No | Higher rate limits / private repos |
| `AI_PROVIDER` | No | Default `mock` |
| `CORS_ORIGINS` | No | Defaults include localhost |
| `MAX_FILES_PER_REVIEW` | No | Default 40 |

**Never commit real secrets.**

---

## Pitch deck (8 slides)

If `docs/MergeMate_Pitch_Deck.pptx` is not in the clone:

```bash
cd docs
npm install pptxgenjs   # once
node generate_pitch_deck.js   # if present in docs/
```

Or use the PPTX shared with the team for stage.

---

## Security & limitations (honest)

- No repository code execution on the server  
- Only `github.com` PR URLs  
- AI findings stay `unverified` without independent support  
- Pattern-based static rules (not full SAST)  
- In-memory store (cleared on restart)  
- No API auth in this release  

See [docs/SECURITY.md](docs/SECURITY.md).

---

## Licence

MIT — [LICENSE](LICENSE)

**Built for DevForge × Hacktoberfest 2026 · Bengaluru**  
Theme: **Developer Productivity**
