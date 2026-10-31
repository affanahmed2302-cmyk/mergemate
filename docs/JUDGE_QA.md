# Judge Q&A preparation

**What makes MergeMate different?**  
We optimise for *trust*, not finding count. ProofLayer independently validates every finding and refuses to mark AI-only claims as verified.

**How does ProofLayer work?**  
Five steps: source recorded → file reference → evidence assessed → support assessment (text ≠ defect) → final status. Statuses: `supported_by_static_check`, `unverified`, `needs_human_review`, `rejected`. `test_confirmed` is reserved and never assigned because we do not execute repository code.

**How are false positives handled?**  
Developers can mark findings useful / incorrect / disputed. Feedback is stored on the review. We do **not** claim the model auto-learns from this in the current MVP.

**What if evidence is unavailable?**  
Finding is `needs_human_review` or `unverified`. We never invent surrounding code to make evidence look complete.

**Prompt injection?**  
PR content is treated as untrusted data for pattern matching and structured AI prompts. We do not execute repo code. AI output is schema-constrained and still forced through ProofLayer.

**AI vs test-confirmed?**  
AI findings remain `unverified` unless a deterministic rule independently supports them. `test_confirmed` would require real test execution — intentionally out of scope; we never run untrusted code.

**Limitations?**  
Pattern-based static rules (not full SAST). Mock AI by default. In-memory store. No auth. Public GitHub rate limits without a token. Heuristic risk score is not a calibrated failure probability.

**Scale?**  
Stateless workers, queue PR jobs, persist reviews, add GitHub App webhooks, optional real providers behind the same AI interface, keep ProofLayer as the trust boundary.

**Why Developer Productivity?**  
Time saved is time not spent chasing unsupported AI comments — and avoiding false accusations on correct code.
