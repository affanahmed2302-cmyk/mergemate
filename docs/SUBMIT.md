# Submission pack — DevForge finals

## Public repository
https://github.com/affanahmed2302-cmyk/mergemate

## Licence
MIT

## Run (one command origin for site + API)
```bash
git clone https://github.com/affanahmed2302-cmyk/mergemate.git
cd mergemate/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn app.main:app --port 8000
```
Open **http://localhost:8000**

## Demo path for judges
1. Landing `/`
2. `/prooflayer`
3. `/demo` or `/app/review` → **Run labelled demo**
4. Open Review Replay on a static-supported finding
5. Show AI finding remains **unverified**
6. Export Markdown

## AI tools disclosure
Built with assistance from **Grok (xAI)**. Product AI findings are always labelled and never presented as verified without evidence.

## Pitch materials
- `docs/PITCH.md`
- `docs/DEMO_SCRIPT.md`
- `docs/JUDGE_QA.md`
- `docs/PITCH_DECK.md` + `MergeMate_Pitch_Deck.pptx`
