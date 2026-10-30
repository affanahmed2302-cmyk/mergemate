# Security

- Repository content is untrusted.
- No repository code is ever executed on the server.
- Only github.com host is accepted (SSRF protection).
- Secrets only via environment variables; never committed.
- AI findings are never marked verified without independent evidence.

## Known limitations
- No API authentication (hackathon MVP).
- In-memory store.
- Deterministic rules are pattern-based.
