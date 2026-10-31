# Contributing

## Team access
Repo owner invites collaborators via GitHub Settings → Collaborators.  
See [docs/COLLABORATORS.md](docs/COLLABORATORS.md).

## Local setup
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn app.main:app --reload --port 8000
```

## Principles
- Never present an AI finding as verified without evidence
- Never execute untrusted repository code
- Prefer labelled demo reliability over fragile live dependencies
