---
type: service
service_name: sonarr
status: active
last_updated: 2026-05-16
---

# Sonarr

## Purpose

Sonarr manages TV automation for the Prometheus media stack and writes final TV libraries to Atlas.

## Hosting

- System: [[systems/prometheus]]
- Container / VM: `sonarr`
- Runtime: Docker Compose
- Live compose path: `/opt/vpn/docker-compose.yml`

## Data Classification

- Authoritative: TV library on [[systems/atlas]]
- Runtime: `/opt/arr/sonarr`
- Disposable: imports from `/opt/torrents/downloads`

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/arr/sonarr` | RW | Sonarr configuration and application database. |
| `/opt/torrents/downloads` | RW | Prometheus-local download staging mounted as `/downloads`. |
| `/mnt/atlas/managed-media/tv` | RW | Atlas authoritative TV library mounted as `/tv`. |

## Configuration

- Environment variables: `PUID=1000`, `PGID=1000`, `TZ`, `SKIP_CHOWN=true`
- Volumes:
  - `/opt/arr/sonarr:/config`
  - `/opt/torrents/downloads:/downloads`
  - `/mnt/atlas/managed-media/tv:/tv`
- Ports: `0.0.0.0:8989`
- Root folder: `/tv`
- Download client:
  - Host: `gluetun`
  - Port: `8080`
  - Category: `sonarr`

## Access

- URL: `http://prometheus:8989` or direct host/IP equivalent
- Auth method: Needs validation
- Roles: administrator only

## Security Notes

- Current broad bind is temporary and must not be treated as the final ingress model.
- Do not expose Sonarr to WAN/public networks.
- `SKIP_CHOWN=true` is required for LinuxServer Sonarr against Atlas NFS mounts.
- Sonarr may write final media to Atlas but does not own Atlas storage authority.

## Backup Strategy

- What is backed up: Sonarr config/database if needed for service continuity; TV library is authoritative on Atlas
- Frequency: Needs validation
- Restore test status: Needs validation

## Monitoring & Health

- Health checks: container running, UI reachable, qBittorrent client connected, `/tv` writable by UID/GID `1000:1000`
- Metrics: Needs validation

## Upgrade Strategy

- Manual image tag update in compose
- Downtime expectations: imports and automation pause during restart

## Known Issues

- `/mnt/atlas/downloads` is not an active Atlas export. Downloads remain local at `/opt/torrents/downloads`.
- Live SSH validation succeeded on 2026-05-16.
- Root folder and qBittorrent client are configured. End-to-end import testing is still Needs validation.

## Related Docs

- Procedures: [[systems/prometheus/procedures/media-stack-validation]]
- ADRs: [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
- Stack scaffold: [[systems/prometheus/automation/docker/stacks/media/README]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker Compose service |
| Source of truth | Live `/opt/vpn/docker-compose.yml`; sanitized scaffold documented at [[systems/prometheus/automation/docker/stacks/media/README]] |
| Config path | `/opt/arr/sonarr` |
| Data path | `/mnt/atlas/managed-media/tv` authoritative on Atlas; `/opt/torrents/downloads` local staging |
| Secret requirements | API keys and download-client credentials stay outside Git |
| Network ports | `0.0.0.0:8989` temporary current state |
| Dependencies | Gluetun/qBittorrent, Prowlarr, Atlas NFS mount |
| Backup requirement | Config/database backup needs validation; media library protected by Atlas policy |
| Validation command | [[systems/prometheus/procedures/media-stack-validation]] |
| Recovery procedure | Needs validation |
| Automation classification | Documentation/scaffold ready; mutating automation needs approval |
| Preferred automation tool | Ansible candidate after recovery is documented |
