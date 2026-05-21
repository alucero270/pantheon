---
type: service
service_name: radarr
status: active
last_updated: 2026-05-16
---

# Radarr

## Purpose

Radarr manages movie automation for the Prometheus media stack and writes final movie libraries to Atlas.

## Hosting

- System: [[systems/prometheus]]
- Container / VM: `radarr`
- Runtime: Docker Compose
- Live compose path: `/opt/vpn/docker-compose.yml`

## Data Classification

- Authoritative: movie library on [[systems/atlas]]
- Runtime: `/opt/arr/radarr`
- Disposable: imports from `/opt/torrents/downloads`

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/arr/radarr` | RW | Radarr configuration and application database. |
| `/opt/torrents/downloads` | RW | Prometheus-local download staging mounted as `/downloads`. |
| `/mnt/atlas/managed-media/movies` | RW | Atlas authoritative movie library mounted as `/movies`. |

## Configuration

- Environment variables: `PUID=1000`, `PGID=1000`, `TZ`, `SKIP_CHOWN=true`
- Volumes:
  - `/opt/arr/radarr:/config`
  - `/opt/torrents/downloads:/downloads`
  - `/mnt/atlas/managed-media/movies:/movies`
- Ports: `0.0.0.0:7878`
- Root folder: `/movies`
- Download client:
  - Host: `gluetun`
  - Port: `8080`
  - Category: `radarr`

## Access

- URL: `http://prometheus:7878` or direct host/IP equivalent
- Auth method: Needs validation
- Roles: administrator only

## Security Notes

- Current broad bind is temporary and must not be treated as the final ingress model.
- Do not expose Radarr to WAN/public networks.
- `SKIP_CHOWN=true` is required for LinuxServer Radarr against Atlas NFS mounts.
- Radarr may write final media to Atlas but does not own Atlas storage authority.

## Backup Strategy

- What is backed up: Radarr config/database if needed for service continuity; movie library is authoritative on Atlas
- Frequency: Needs validation
- Restore test status: Needs validation

## Monitoring & Health

- Health checks: container running, UI reachable, qBittorrent client connected, `/movies` writable by UID/GID `1000:1000`
- Metrics: Needs validation

## Upgrade Strategy

- Manual image tag update in compose
- Downtime expectations: imports and automation pause during restart

## Known Issues

- `/mnt/atlas/downloads` is not an active Atlas export. Downloads remain local at `/opt/torrents/downloads`.
- Live SSH validation succeeded on 2026-05-16.
- Root folder and qBittorrent client are configured. End-to-end import testing is still Needs validation.

## Related Docs

- Procedures: [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]]
- ADRs: [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
- Stack scaffold: [[systems/prometheus/automation/docker/stacks/media/README]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker Compose service |
| Source of truth | Live `/opt/vpn/docker-compose.yml`; sanitized scaffold documented at [[systems/prometheus/automation/docker/stacks/media/README]] |
| Config path | `/opt/arr/radarr` |
| Data path | `/mnt/atlas/managed-media/movies` authoritative on Atlas; `/opt/torrents/downloads` local staging |
| Secret requirements | API keys and download-client credentials stay outside Git |
| Network ports | `0.0.0.0:7878` temporary current state |
| Dependencies | Gluetun/qBittorrent, Prowlarr, Atlas NFS mount |
| Backup requirement | Config/database backup needs validation; media library protected by Atlas policy |
| Validation command | [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]] |
| Recovery procedure | Needs validation |
| Automation classification | Documentation/scaffold ready; mutating automation needs approval |
| Preferred automation tool | Ansible candidate after recovery is documented |
