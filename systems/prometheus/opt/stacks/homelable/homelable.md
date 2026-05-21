---
type: service
service_name: homelable
status: active
last_updated: 2026-05-18
---

# Homelable

## Purpose

Homelable provides an interactive infrastructure visualization and monitoring dashboard for Pantheon. It maps devices and services on a drag-and-drop canvas with live node status checks (ping, HTTP, TCP, SSH), network scanning via nmap, and hardware spec tracking.

It is not authoritative storage.

## Hosting

- System: [[systems/prometheus]]
- Runtime: Docker Compose (built from source)
- Compose path: `/opt/homelable/docker-compose.yml`
- Source path: `/opt/homelable/` (full git clone)
- Upstream: `https://github.com/Pouzor/homelable.git`
- Live version: v1.13.0 (untagged; built from source on or before 2026-05-09)
- Containers:
  - `homelable-backend-1`
  - `homelable-frontend-1`
  - `homelable-mcp-1`
- Images: Built locally from `Dockerfile.backend`, `Dockerfile.frontend`, `mcp/Dockerfile.mcp`

## Data Classification

- Authoritative: no
- Runtime: yes
- Disposable: SQLite database and imported scan data are runtime state; the node/edge topology can be recreated

## Storage Paths

| Path | Read/Write | Description |
|------|-----------|-------------|
| `/opt/homelable/docker-compose.yml` | R | Live compose file |
| `/opt/homelable/.env` | R | Local environment file; contains default secrets that must be changed |
| `/opt/homelable/` (full source tree) | R | Git clone of upstream repository; includes Dockerfiles and config |
| `homelable_backend_data` Docker volume | RW | SQLite database at `/app/data/homelab.db` |

## Configuration

Validated live settings on 2026-05-18:

- Build method: Source (uses `build:` directives in compose, not prebuilt images)
- Network: `homelable` bridge network (172.23.0.0/16)
- CORS_ORIGINS: `["http://localhost:5173","http://localhost:3000"]`
- SCANNER_RANGES: `["192.168.20.0/24","192.168.30.0/24","192.168.40.0/24","192.168.50.0/24","192.168.60.0/24","192.168.99.0/24"]`
- STATUS_CHECKER_INTERVAL: 60 seconds
- Backend health: `GET /api/v1/health` returns 200

### Secrets Requiring Action

All authentication keys are set to default/placeholder values:

| Secret | Live Value | Action |
|--------|-----------|--------|
| `SECRET_KEY` | `change_me_in_production` | Change before exposing beyond SERVERS VLAN |
| `AUTH_USERNAME` | `admin` | Change to unique username |
| `AUTH_PASSWORD_HASH` | Default bcrypt hash for `admin` | Regenerate with `passlib` bcrypt |
| `MCP_API_KEY` | `mcp_sk_changeme` | Generate random token if MCP is used |
| `MCP_SERVICE_KEY` | `svc_changeme` | Generate random token if MCP is used |

Generate a new password hash:

```bash
docker compose exec backend python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('yourpassword'))"
```

## Access

Validated live state on 2026-05-18:

- Ports:
  - `0.0.0.0:3000 -> 80/tcp` (frontend)
  - `0.0.0.0:8001 -> 8001/tcp` (MCP server)
  - `8000/tcp` (backend, internal to Docker network only)
- Traefik route: None configured (direct host port exposure)
- Default login: `admin` / `admin`
- Docker IP: `172.23.0.2` (frontend), `172.23.0.3` (backend)

Validated from Prometheus:

```bash
curl -s http://localhost:3000 | head -5
```

## Security Notes

- Direct host port exposure (`0.0.0.0:3000`) circumvents the Traefik-only access model. `homelable.home.arpa` should be routed through Traefik and the host port removed, following `Phase 13` in [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]].
- Default admin credentials are still active. Change `AUTH_USERNAME` and `AUTH_PASSWORD_HASH` in `.env` and restart.
- `MCP_API_KEY` and `MCP_SERVICE_KEY` are set to placeholder values. If MCP integration is used, generate random tokens.
- Network scanning uses nmap with `NET_RAW` capability. Scanner ranges cover all Pantheon VLANs.
- `.env` must stay local to Prometheus and never be committed.

## Network Scanning

Homelable scans all Pantheon VLANs for device discovery:

- `192.168.20.0/24` (USER)
- `192.168.30.0/24` (IOT)
- `192.168.40.0/24` (GUEST)
- `192.168.50.0/24` (CAMERA)
- `192.168.60.0/24` (SERVERS)
- `192.168.99.0/24` (MGMT)

Trigger a scan from the Homelable UI sidebar or via the API.

## MCP Server Integration

The MCP server is running on port `8001` but is not yet integrated with any AI client:

- MCP endpoint: `http://192.168.60.103:8001/mcp`
- `MCP_API_KEY` and `MCP_SERVICE_KEY` are placeholder values
- Integration with Claude, Open WebUI, or other MCP-compatible clients is `Needs decision`

## Backup Strategy

- Back up the sanitized compose file and `.env` template only.
- Do not commit `.env` with secrets.
- The SQLite database (`homelable_backend_data` volume) contains runtime topology data and is disposable.
- Restoration requires rebuilding images from source and re-importing topology.
- Restore test status: Needs validation.

## Monitoring & Health

Container state:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep homelable
```

Backend health:

```bash
curl -sf http://localhost:8000/api/v1/health
# Expected: {"status":"ok"}
```

Logs:

```bash
docker logs --tail=50 homelable-backend-1
docker logs --tail=50 homelable-frontend-1
```

## Upgrade Strategy

- Currently built from source using `build:` directives in compose.
- Upstream recommends re-running `install.sh` or pulling prebuilt images.
- To switch to prebuilt images:
  1. Replace compose file with `docker-compose.prebuilt.yml`
  2. Update `.env` as needed
  3. `docker compose pull && docker compose up -d`
- Pin a specific version tag before automation is considered complete.
- Test rollback by keeping the current compose file until upgrade is validated.

## Known Issues

- Default credentials are still active; secrets have not been rotated.
- No Traefik route configured — direct host port exposure needs remediation.
- CORS_ORIGINS does not include `homelable.home.arpa` — accessing via Traefik would require updating CORS settings.
- MCP server is running but not connected to any AI client.
- Built from source (not prebuilt) — rebuild time is longer and version pinning is manual.
- Container names suggest the project was started from the clone root rather than a named project directory (`docker compose -p homelable` would be preferred for clarity).

## Related Docs

- Services: [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
- Architecture: [[systems/prometheus/architecture/compose-registry]]
- Procedures: [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]], [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker Compose with source build (frontend, backend, MCP) |
| Source of truth | `/opt/homelable/docker-compose.yml`; `/opt/homelable/.env`; upstream at `Pouzor/homelable` |
| Config path | `/opt/homelable/.env` |
| Data path | `homelable_backend_data` Docker volume (SQLite) |
| Secret requirements | Rotate all default secrets before network exposure beyond SERVERS VLAN |
| Network ports | `3000/tcp` host (frontend), `8001/tcp` host (MCP), `8000/tcp` internal (backend) |
| Dependencies | Docker, nmap (included in backend image), Traefik (if routed) |
| Backup requirement | Sanitized compose and `.env.example`; SQLite data is disposable |
| Validation command | `curl -sf http://localhost:8000/api/v1/health` |
| Recovery procedure | Re-clone upstream, copy compose and `.env`, rebuild, restore topology manually |
| Automation classification | Needs validation until secrets are rotated and Traefik routing is implemented |
| Preferred automation tool | Ansible candidate after Traefik route and secrets model are documented |
