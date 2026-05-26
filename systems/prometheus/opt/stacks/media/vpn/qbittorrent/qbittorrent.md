---
type: service
service_name: qbittorrent
status: active
last_updated: 2026-05-16
---

# qBittorrent

## Purpose

qBittorrent provides download staging for the Prometheus media automation stack.

## Hosting

- System: [[systems/prometheus]]
- Container / VM: `qbittorrent`
- Runtime: Docker Compose
- Live compose path: `/opt/stacks/media/vpn/compose.yml`
- Legacy compose path: `/opt/vpn/docker-compose.yml` symlink

## Data Classification

- Authoritative: none
- Runtime: `/opt/torrents/config`
- Disposable: `/opt/torrents/downloads`

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/torrents/config` | RW | qBittorrent service configuration. |
| `/opt/torrents/downloads` | RW | Prometheus-local download staging mounted as `/downloads`. |
| `/opt/torrents/downloads/radarr` | RW | qBittorrent `radarr` category path. |
| `/opt/torrents/downloads/sonarr` | RW | qBittorrent `sonarr` category path. |
| `/opt/torrents/downloads/mam` | RW | qBittorrent `mam` category path for manual MaM/freeleech testing and future Readarr use. |
| `/opt/torrents/downloads/manual` | RW | qBittorrent `manual` category path for non-automated downloads. |

## Configuration

- Environment variables: `PUID=1000`, `PGID=1000`, `WEBUI_PORT=8080`, `TZ`
- Volumes:
  - `/opt/torrents/config:/config`
  - `/opt/torrents/downloads:/downloads`
- Ports:
  - WebUI is exposed through Gluetun as `127.0.0.1:8080:8080`
- Network:
  - `network_mode: service:gluetun`

## Access

- URL: `http://127.0.0.1:8080`
- Auth method: qBittorrent WebUI authentication
- Roles: administrator only

## Security Notes

- qBittorrent must remain behind Gluetun.
- WebUI is localhost-only.
- Downloads are local staging and must not be treated as authoritative media.
- Test downloads must be legal/public test content only.

## Backup Strategy

- What is backed up: config only if needed for service continuity
- Frequency: Needs validation
- Restore test status: Needs validation

## Monitoring & Health

- Health checks: container running, WebUI reachable on localhost, client usable by Radarr/Sonarr
- Metrics: Needs validation

## Upgrade Strategy

- Manual image tag update in compose
- Downtime expectations: active downloads pause during restart

## Known Issues

- `/mnt/atlas/downloads` is not an active Atlas export. Do not configure qBittorrent to use it.
- Live SSH validation succeeded on 2026-05-16.
- qBittorrent is currently usable through a generated WebUI credential found in container logs; rotate to a documented local secret before relying on long-term operations.
- Legal download transfer testing succeeded on 2026-05-16 using the official Debian `debian-13.4.0-amd64-netinst.iso` torrent. The test torrent was stopped after transport validation and not deleted.
- qBittorrent Web/API version `v5.1.4` was validated on 2026-05-16.
- Categories `radarr`, `sonarr`, `mam`, and `manual` were validated on 2026-05-16.

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
| Source of truth | Live `/opt/stacks/media/vpn/compose.yml`; sanitized scaffold documented at [[systems/prometheus/automation/docker/stacks/media/README]] |
| Config path | `/opt/torrents/config` |
| Data path | `/opt/torrents/downloads` local staging |
| Secret requirements | WebUI credentials must not be committed |
| Network ports | `127.0.0.1:8080` through Gluetun |
| Dependencies | Gluetun, Docker, local staging path |
| Backup requirement | Config backup needs validation; downloads are disposable staging |
| Validation command | [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]] |
| Recovery procedure | Needs validation |
| Automation classification | Documentation/scaffold ready; mutating automation needs approval |
| Preferred automation tool | Ansible candidate after media stack recovery is documented |
