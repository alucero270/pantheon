---
type: procedure
risk_level: medium
last_tested: 2026-05-17
---

# SearXNG and OpenWebUI Integration

## Purpose

Document the current SearXNG deployment on [[systems/prometheus]] and the steps required to make it useful as the OpenWebUI web-search backend.

This procedure is partly validated:

- SearXNG JSON search through Traefik was validated from Prometheus on 2026-05-17.
- SearXNG JSON search over Docker DNS was validated from inside the OpenWebUI container on 2026-05-17.
- OpenWebUI integration is not live because `ENABLE_WEB_SEARCH=false`.
- Client validation from Nomad is still `Needs validation`.

## Preconditions

- SSH access to Prometheus as the non-root admin user.
- Docker and Docker Compose installed on Prometheus.
- [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] running.
- DNS for `searxng.home.arpa` pointing to Prometheus.
- Approval before changing live compose or OpenWebUI configuration.

## Current Live Paths

| Purpose | Path |
|---|---|
| Compose root | `/mnt/local/ssd/ai/services/searxng` |
| Compose file | `/opt/stacks/ai/searxng/compose.yml` |
| Local env file | `/mnt/local/ssd/ai/services/searxng/.env` |
| SearXNG config mount | `/mnt/local/ssd/ai/services/searxng/searxng` |
| Settings file | `/mnt/local/ssd/ai/services/searxng/searxng/settings.yml` |

## Current Live Services

| Container | Image | Role |
|---|---|---|
| `searxng` | `searxng/searxng:latest` | SearXNG application |
| `searxng-redis` | `redis:7-alpine` | Dedicated Redis cache/backend |

## Read-Only Validation

Run on Prometheus:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "^searxng|^searxng-redis"
```

Expected:

- `searxng` is running.
- `searxng-redis` is running.
- No host ports are published for either container.

Validate Traefik JSON search from Prometheus:

```bash
curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"
```

Expected:

- HTTP `200`
- `Content-Type: application/json`
- JSON response includes `query` and `results`

Check live settings without exposing secrets:

```bash
sed -E 's/(secret_key:).*/\1 REDACTED/' /mnt/local/ssd/ai/services/searxng/searxng/settings.yml
```

## OpenWebUI Integration Target

Current live OpenWebUI environment has:

```text
ENABLE_WEB_SEARCH=false
```

To make SearXNG useful from OpenWebUI, the live OpenWebUI configuration must be changed with approval to enable web search and point it at SearXNG.

Candidate target values:

```text
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=searxng
SEARXNG_QUERY_URL=https://searxng.home.arpa/search?q=<query>&format=json
```

Alternative internal Docker-network target if OpenWebUI resolves `searxng` on `ai_ai_internal`:

```text
SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>&format=json
```

This internal Docker-network target was validated from inside the OpenWebUI container on 2026-05-17 and is preferred while Traefik uses a self-signed certificate.

The HTTPS Traefik target failed from inside OpenWebUI because the container does not trust the current self-signed certificate:

```text
certificate verify failed: self-signed certificate
```

Use the exact environment variable names expected by the installed OpenWebUI version before changing live compose. Do not guess or apply until validated against OpenWebUI documentation or the live container.

## Known-Good SearXNG Settings

Current live settings include:

```yaml
use_default_settings: true

server:
  base_url: https://searxng.home.arpa/
  public_instance: false
  limiter: false
  bind_address: "0.0.0.0"
  image_proxy: true

redis:
  url: redis://searxng-redis:6379/0

search:
  safe_search: 1
  default_lang: "en"
  method: "GET"
  formats:
    - html
    - json
```

Do not copy the live `secret_key` into Git.

## Known Failure Modes

### Browser or JSON Search Returns 403

Possible causes:

- Traefik IP allowlist does not include the client source range.
- SearXNG limiter/bot-detection settings reject the request.
- A specific upstream engine blocks SearXNG.

Validation:

```bash
curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"
docker logs --tail=100 searxng
```

### Missing limiter.toml Warning

Live logs show:

```text
missing config file: /etc/searxng/limiter.toml
```

Current live settings set `server.limiter=false`. This warning is not currently blocking JSON search from Prometheus, but it should be resolved before considering the service cleanly recovered.

### Invalid limiter.toml Schema

If a limiter file is added, validate it against the installed SearXNG version before redeploying. Earlier notes in issue #72 mention invalid limiter schema attempts.

### Redis Deprecation Warning

Live logs warn that `redis.url` is deprecated in favor of `valkey.url`. This is not currently blocking service operation.

## Rollback

If OpenWebUI search configuration is changed and breaks the UI:

1. Revert the OpenWebUI environment changes in `/opt/stacks/ai/core/compose.yml`.
2. Redeploy only the AI stack with explicit approval.
3. Confirm OpenWebUI loads at `https://openwebui.home.arpa`.
4. Leave SearXNG running if its independent validation still passes.

If SearXNG compose/settings are changed and search breaks:

1. Restore the previous `settings.yml` and compose file from backup or Git/sanitized notes.
2. Redeploy only the SearXNG stack with explicit approval.
3. Re-run the JSON validation command.

## Warnings

- Do not commit `.env` or `server.secret_key`.
- Do not expose SearXNG publicly.
- Do not loosen the Traefik IP allowlist without updating the security model.
- Do not run mutating Docker Compose commands without explicit approval.

## Automation Potential

This can become Ansible-managed after:

- image tags are pinned
- secrets handling is decided
- the OpenWebUI integration is validated
- client access from Nomad is validated
- rollback is tested

## Related Docs

- Systems: [[systems/prometheus]]
- Services: [[systems/prometheus/opt/stacks/ai/searxng/searxng]], [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
- Architecture: [[systems/prometheus/architecture/compose-registry]], [[systems/prometheus/architecture/storage-authority-map]]
