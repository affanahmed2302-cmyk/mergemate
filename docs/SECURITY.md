# Security notes

- Only `github.com` PR URLs are accepted (SSRF protection via strict URL parser).
- Repository code is **never executed** on the MergeMate server.
- AI findings are always labelled `unverified` unless independently corroborated by deterministic evidence.
- Secrets must live in environment variables (`.env`); never commit tokens.
- In-memory store — reviews disappear on process restart (intentional MVP).
- No authentication on the API in this release — treat as a local/demo tool.
- Report exports contain only analysis results, not repository secrets (excerpts may still show patterns that matched secret detectors; redact before sharing externally if needed).
