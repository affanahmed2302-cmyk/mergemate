# Demo script (live, ~3 minutes)

## Setup before stage

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --port 8000
# other terminal
cd frontend && python3 -m http.server 3000
```

Open http://localhost:3000  
Zoom browser to ~125% if projector is far.

## Sequence

1. **Landing (15s)**  
   Read headline: “AI code reviews. Backed by evidence.”  
   Point at ProofLayer explainer statuses.

2. **Run labelled demo (10s)**  
   Click **Explore labelled demo**.  
   Wait for results. Note the yellow “Labelled demo data” badge.

3. **Scorecard + risk (20s)**  
   Show Evidence coverage / Unverified ratio.  
   Show risk formula and disclaimer — “heuristic, not probability of failure.”

4. **Static finding + Review Replay (40s)**  
   Expand “Possible hardcoded secret”.  
   Open **ProofLayer — Review Replay**.  
   Walk steps 1→5. Status: **Static-supported**.

5. **AI finding (25s)**  
   Filter **Unverified AI** or open the AI finding.  
   Status: **Unverified**. Say: “We refuse to mark this verified.”

6. **False-accusation avoidance (15s)**  
   Mention the correct `add()` helper was not flagged.

7. **Export (15s)**  
   Download Markdown. Optional: click Useful/Incorrect feedback.

8. **Close (10s)**  
   Deliver the one-liner.

## Fallback

If network/API fails: keep the landing ProofLayer diagram visible and narrate the pipeline from `docs/PITCH.md`. Demo mode is offline once the backend is local.
