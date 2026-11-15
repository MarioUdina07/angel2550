# Angel2500 AI Core v5 (recovery)

A deliberately limited, **non-trading** recovery of Angel2500. This branch removes the unsafe process-control/web endpoints from the runtime and provides an authenticated text-only API.

## Security incident — immediate action

The public Git history contains credentials, including a GitHub personal access token and exchange credentials. **Revoke/rotate all exposed credentials immediately**, inspect exchange activity and permissions, and migrate funds if a real wallet private key was exposed. Removing files from the latest commit **does not erase Git history**. Do not reuse any exposed credential. Coordinate history cleanup after rotation; history rewriting may disrupt clones and does not undo prior disclosure.

## Setup

Python 3.11+:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set new secrets in environment or secret manager. The application intentionally **does not load .env automatically**; export variables securely (e.g. `set -a; . ./.env; set +a` in a trusted local shell). Never expose .env publicly.

```bash
python webserver.py
python -m unittest discover -s tests -v
```

GET /health is unauthenticated. POST /api/chat requires `Authorization: Bearer <ANGEL_API_TOKEN>` and JSON `{"message":"hello"}`. Keep the server bound to localhost; for remote use place behind HTTPS reverse proxy with rate limiting and access controls.

## Scope

No exchange SDKs, no trading, no wallet operations, no Telegram execution, no shell or filesystem command execution, no autonomous self-training. This is a safe starting point, **not a production-ready trading bot**. Tests mock OpenAI and make no external trades or API requests.
