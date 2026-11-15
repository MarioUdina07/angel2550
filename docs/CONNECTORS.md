# Connecting external services safely

Angel2500 v5 provides a generic **read-only** HTTPS connector interface.
It does not automatically inherit ChatGPT's installed plugins or OAuth grants.
Every service must explicitly authorize access, and some services require
their own OAuth integration rather than a static token.

## Configure secrets (never paste them into chat)

In your hosting platform's **Secrets / Environment Variables** page set:
- `ANGEL_API_TOKEN`: a new random API access token for the Angel2500 server
- `OPENAI_API_KEY`: a new OpenAI API key (not an exposed old key)
- `ANGEL_CONNECTORS`: comma-separated identifiers, e.g. `inventory`
- `ANGEL_CONNECTOR_INVENTORY_URL`: approved HTTPS GET endpoint
- `ANGEL_CONNECTOR_INVENTORY_TOKEN`: optional token for that endpoint

Connector identifiers use letters, digits and underscore, beginning with a letter or underscore.
Only explicitly named connectors are accessible. Connectors reject non-HTTPS URLs,
non-standard ports, and resolved non-global IP addresses; redirects are disabled.
**Security note:** DNS rebinding is not fully mitigated by pre-request DNS checks.
For production, also enforce outbound network egress allowlists/proxy and prevent
connections to internal networks at the infrastructure layer.

## Task API

POST `/api/tasks` with `Authorization: Bearer <ANGEL_API_TOKEN>` and JSON
`{"goal":"Summarize inventory from the inventory connector"}`.

GET `/api/tasks/<task_id>` returns a stored result. Task execution is
synchronous and limited to five model iterations, with at most three read
calls per iteration. It does not promise continuous background execution.

## Extending to more apps

Implement each integration with least-privilege OAuth or scoped API keys,
explicit user approval for writes, timeouts, audit logs and idempotency.
Never expose raw generic shell or unrestricted HTTP write tools to the model.
