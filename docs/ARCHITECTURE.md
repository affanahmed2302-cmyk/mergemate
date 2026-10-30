# Architecture

MergeMate = FastAPI backend + static frontend + ProofLayer.

## Pipeline
1. Validate PR URL (github.com only)
2. Fetch metadata + files + patches (GitHub REST)
3. Deterministic rules → findings with evidence
4. AI provider (mock by default) → additional findings
5. ProofLayer validates path + evidence → verification status
6. Risk heuristic + test suggestions
7. Report (Markdown / JSON)

## ProofLayer statuses
- `supported_by_static_check` — deterministic rule + matching evidence
- `unverified` — AI-only
- `needs_human_review` / `rejected` — missing or mismatched evidence
- `test_confirmed` — never assigned (no code execution)

## Storage
In-memory for the MVP.
