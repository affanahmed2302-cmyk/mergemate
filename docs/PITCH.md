# MergeMate — 3-minute pitch

## Opening (20s)

AI code reviewers are fast and persuasive. They can also be wrong.

A typical AI comment says: *“Missing null check on line 47.”*
If the line is invented or the claim is speculation, developers still waste time verifying it.

**MergeMate was built for that gap.**

## Problem (30s)

Existing AI review tools optimise for finding more issues.
They rarely optimise for *whether those findings deserve trust*.

Unsupported suggestions create noise, false accusations, and review fatigue.

## Solution (40s)

MergeMate is an evidence-first Pull Request intelligence platform.

1. Paste a real GitHub PR URL  
2. We fetch the actual diff  
3. Deterministic checks produce findings with concrete evidence  
4. An AI reviewer may add observations — always labelled  
5. **ProofLayer** validates every finding independently  

AI-only findings stay **unverified**.  
Deterministic matches with evidence are **supported_by_static_check**.  
We never present a finding as verified without support.

## Demo (60s)

*Run labelled demo.*

- Summary cards: static-supported vs unverified AI  
- Open ProofLayer **Review Replay** on a static finding — five validation steps  
- Open an AI finding — status is clearly **unverified**  
- Correct code is not falsely flagged  
- Export Markdown report  

## Why it matters (20s)

Developer productivity is not “more AI comments.”  
It is less time spent chasing claims that were never supported.

## Close (10s)

> We didn’t build another AI code reviewer.  
> We built a way to check whether an AI review deserves to be trusted.

**MergeMate. Evidence-first. ProofLayer.**
