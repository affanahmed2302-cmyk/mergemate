# DevForge × Hacktoberfest 2026 — Submission

## Project
**MergeMate** — Evidence-first AI Pull Request Intelligence  
Theme: **Developer Productivity** (also AI for Open Source)

## Public repository (required)
https://github.com/affanahmed2302-cmyk/mergemate

## OSI licence (required)
MIT — see [LICENSE](../LICENSE)

## How to run (judges)
```bash
git clone https://github.com/affanahmed2302-cmyk/mergemate.git
cd mergemate/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v          # expect 7 passed
uvicorn app.main:app --port 8000
```
Open **http://localhost:8000**

## Demo (3 minutes)
1. Landing → **Explore labelled demo** (or `/demo`)
2. Show static-supported vs **unverified** AI findings
3. Open **ProofLayer — Review Replay** (5 steps)
4. Correct code not falsely flagged
5. Export Markdown report

Closing line:  
*We didn’t build another AI code reviewer. We built a way to check whether an AI review deserves to be trusted.*

## AI tools disclosure (required)
Built with assistance from **Grok (xAI)**. All critical paths covered by automated tests. In-product AI findings are always labelled and never presented as verified without evidence.

## Pitch deck
```bash
cd docs && bash assemble_pitch_deck.sh
# opens MergeMate_Pitch_Deck.pptx (8 slides)
```
Or download the assembled deck from the team if parts are present under `docs/deck_b64/`.

## What is implemented
- Public website routes: `/` `/about` `/features` `/prooflayer` `/how-it-works` `/docs` `/demo`
- App routes: `/app` and nested review, findings, prooflayer, intelligence, tests, history, reports, settings
- Real GitHub public PR analysis + labelled offline demo
- ProofLayer evidence validation
- Scorecard, risk heuristic, test suggestions, feedback, exports

## Tests
See [TEST_RESULTS.md](TEST_RESULTS.md) — **7/7 passed** on last verification run.

## Security limits (honest)
- No repository code execution
- Only github.com PR URLs
- Secrets only via environment variables
- In-memory store (session lifetime)
