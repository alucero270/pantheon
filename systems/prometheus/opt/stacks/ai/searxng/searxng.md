---
type: service
service_name: searxng
status: active
last_updated: 2026-05-17
---

# SearXNG

## Purpose

SearXNG provides a local metasearch service for Pantheon-hosted AI tooling, especially future OpenWebUI web-search integration.

It is not authoritative storage.

## Hosting

- System: [[systems/prometheus]]
- Runtime: Docker Compose
- Compose path: `/opt/stacks/ai/searxng/compose.yml`
- Legacy compose path: `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` symlink
- Containers:
  - `searxng`
  - `searxng-redis`
- Images:
  - `searxng/searxng:latest`
  - `redis:7-alpine`

## Data Classification

- Authoritative: no
- Runtime: yes
- Disposable: cache and Redis data are disposable
- Persistent runtime config: yes

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/stacks/ai/searxng/compose.yml` | R | Live compose file |
| `/mnt/local/ssd/ai/services/searxng/.env` | R | Local environment file; contains secrets; do not commit |
| `/mnt/local/ssd/ai/services/searxng/searxng/settings.yml` | RW | SearXNG settings mounted at `/etc/searxng` |
| Docker anonymous volume for `/var/cache/searxng` | RW | SearXNG cache |
| Docker anonymous volume for `/data` | RW | Redis data path; Redis is configured without persistence in compose |

## Configuration

Validated live settings on 2026-05-17:

- `server.base_url=https://searxng.home.arpa/`
- `server.public_instance=false`
- `server.limiter=false`
- `server.image_proxy=true`
- `search.formats` includes `html` and `json`
- `redis.url=redis://searxng-redis:6379/0`

The live compose file joins these Docker networks:

- `searxng_internal`
- `proxy`
- `ai_ai_internal`

## Access

Live state observed on 2026-05-17:

- Host port: none published
- Container port: `8080/tcp`
- Traefik route: `https://searxng.home.arpa`
- Traefik target port: `8080`
- Traefik middleware: `searxng-ipallow`
- Allowed source ranges in live labels:
  - `127.0.0.1/32`
  - `172.20.0.0/16`
  - `192.168.60.0/24`
  - `192.168.10.0/24`
  - `192.168.1.0/24`

Validated from Prometheus:

```bash
curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"
```

This returned HTTP `200` with JSON results on 2026-05-17.

## OpenWebUI Integration State

OpenWebUI web search is not enabled in the live OpenWebUI environment as of 2026-05-17:

- `ENABLE_WEB_SEARCH=false`

This is why SearXNG is not currently useful as an OpenWebUI tool even though the SearXNG HTTP JSON endpoint works.

Validated from inside the OpenWebUI container on 2026-05-17:

- `http://searxng:8080/search?q=test&format=json` returns HTTP `200` with JSON.
- `https://searxng.home.arpa/search?q=test&format=json` fails certificate validation because the current Traefik certificate is self-signed and not trusted inside the OpenWebUI container.

Prefer the Docker-network URL for OpenWebUI integration unless the container trust store is intentionally updated.

See [[systems/prometheus/opt/stacks/ai/searxng/procedures/searxng-openwebui-integration]].

## Security Notes

- `server.secret_key` is a secret and must stay out of Git.
- `.env` must stay local to Prometheus.
- SearXNG is private (`public_instance=false`).
- Access is limited through Traefik IP allowlist labels plus Cerberus firewall policy.
- Bot detection limiter is disabled in current live settings; do not assume public-instance hardening.

## Backup Strategy

- Back up sanitized compose and `settings.yml` only.
- Do not commit `.env` or secret values.
- Redis data and SearXNG cache are disposable by current design.
- Restore test status: Needs validation.

## Monitoring & Health

Container state:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "^searxng|^searxng-redis"
```

Ingress JSON validation:

```bash
curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"
```

Logs:

```bash
docker logs --tail=100 searxng
```

## Upgrade Strategy

- Current image tag is floating `latest`.
- Pin a known-good version before automation or repeatable recovery is considered complete.
- Redeploy with Docker Compose only after validating settings and rollback.

## Known Issues

- OpenWebUI web search is disabled, so SearXNG is not currently wired into the main AI UI.
- OpenWebUI can reach SearXNG over `http://searxng:8080`; HTTPS via `searxng.home.arpa` fails from inside OpenWebUI until internal certificate trust is handled.
- Logs show `missing config file: /etc/searxng/limiter.toml` even though `server.limiter=false`.
- Logs show several engines disabled or failing at startup, including historical `wikidata` HTTP 403 during init.
- `redis.url` emits a deprecation warning; SearXNG now recommends `valkey.url`.
- Validation from a separate client named Nomad was requested in issue #72 but has not been proven by this repo or the 2026-05-17 Prometheus-only validation run.

## Related Docs

- Services: [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]], [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]]
- Procedures: [[systems/prometheus/opt/stacks/ai/searxng/procedures/searxng-openwebui-integration]]
- Architecture: [[systems/prometheus/architecture/compose-registry]], [[systems/prometheus/architecture/storage-authority-map]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker metasearch service plus Redis |
| Source of truth | `/opt/stacks/ai/searxng/compose.yml`; issue #72 |
| Config path | `/mnt/local/ssd/ai/services/searxng/searxng/settings.yml`; `/mnt/local/ssd/ai/services/searxng/.env` |
| Data path | Anonymous Docker volumes for cache and Redis data |
| Secret requirements | Do not commit `.env` or `server.secret_key` |
| Network ports | Container `8080/tcp`; Traefik route `searxng.home.arpa`; no host port |
| Dependencies | Docker, Redis container, Traefik, DNS, OpenWebUI integration if used as a tool |
| Backup requirement | Sanitized config backup needed; cache and Redis are disposable |
| Validation command | `curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"` |
| Recovery procedure | [[systems/prometheus/opt/stacks/ai/searxng/procedures/searxng-openwebui-integration]] |
| Automation classification | Needs validation until OpenWebUI integration and client access are confirmed |
| Preferred automation tool | Ansible candidate after config/secrets model is documented |
