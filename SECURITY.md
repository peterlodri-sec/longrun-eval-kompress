# Security Policy

## Supported Versions

This is an open-source academic research repository. The manuscript (LaTeX),
baseline scripts, marimo notebook, and MCP server are all in active
development on `main`.

| Version | Supported |
|---------|-----------|
| main    | yes       |
| tags    | yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in the code (baseline scripts, MCP
server, or notebook), please report it privately:

1. **Do not open a public issue.**
2. Email: contact via https://pocoo.vaked.dev (use the chat link for initial contact)
3. Or use GitHub's private security advisory feature:
   https://github.com/peterlodri-sec/longrun-eval-kompress/security/advisories/new

You will receive a response within 72 hours. If the vulnerability is
confirmed, a fix will be prioritized and a security advisory published.

## Scope

**In scope:**
- `baselines/run_baselines.py` — if it can be made to execute arbitrary code
- `mcp_server/server.py` — if it exposes filesystem or command injection
- `notebook.py` — if it can be made to execute arbitrary code

**Out of scope:**
- The LaTeX manuscript (static text, no executable code)
- `LINKS.txt`, `robots.txt`, `AGENTS.md`, `README.md` (static text)
- The `paper/` directory in general (LaTeX source only)

## Data Privacy

This repository contains no personal data. The `ultrawhale-dogfood` dataset
(HuggingFace) enforces `pii_scrubbed=true` on every record. See
`paper/disclaimer_legal_privacy.tex` §A.2 for the full PII policy.

## License

All code is Apache 2.0. Security fixes are released under the same license.
