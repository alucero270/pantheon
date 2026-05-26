---
type: service
service_name: prowlarr
status: active
last_updated: 2026-05-16
---

# Prowlarr

## Purpose

Prowlarr manages indexer integration for the Prometheus media automation stack.

## Hosting

- System: [[systems/prometheus]]
- Container / VM: `prowlarr`
- Runtime: Docker Compose
- Live compose path: `/opt/stacks/media/vpn/compose.yml`
- Legacy compose path: `/opt/vpn/docker-compose.yml` symlink

## Data Classification

- Authoritative: none
- Runtime: `/opt/arr/prowlarr`
- Disposable: container image and recreated runtime state

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/arr/prowlarr` | RW | Prowlarr configuration and application database. |

## Configuration

- Environment variables: `PUID=1000`, `PGID=1000`, `TZ`
- Volumes: `/opt/arr/prowlarr:/config`
- Ports: `0.0.0.0:9696`
- App links:
  - Radarr URL: `http://radarr:7878`
  - Sonarr URL: `http://sonarr:8989`

## Access

- URL: `http://prometheus:9696` or direct host/IP equivalent
- Auth method: Needs validation
- Roles: administrator only

## Security Notes

- Current broad bind is temporary and must not be treated as the final ingress model.
- Do not expose Prowlarr to WAN/public networks.
- Indexer API keys and app API keys must not be committed.

## Backup Strategy

- What is backed up: Prowlarr config/database if needed for service continuity
- Frequency: Needs validation
- Restore test status: Needs validation

## Monitoring & Health

- Health checks: container running, UI reachable, Radarr/Sonarr app sync succeeds
- Metrics: Needs validation

## Upgrade Strategy

- Manual image tag update in compose
- Downtime expectations: indexer sync unavailable during restart

## Known Issues

- Live SSH validation succeeded on 2026-05-16.
- Radarr and Sonarr app links are configured.
- LinuxTracker public torrent indexer was configured and validated for legal Linux distribution searches on 2026-05-16.
- Internet Archive indexer creation timed out during validation and remains Needs validation.
- Media-specific indexers for Radarr/Sonarr acquisition remain Needs validation and must be lawful/approved sources.

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
| Config path | `/opt/arr/prowlarr` |
| Data path | None authoritative |
| Secret requirements | API keys stay outside Git |
| Network ports | `0.0.0.0:9696` temporary current state |
| Dependencies | Radarr, Sonarr, Docker network, configured indexers |
| Backup requirement | Config/database backup needs validation |
| Validation command | [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]] |
| Recovery procedure | Needs validation |
| Automation classification | Documentation/scaffold ready; mutating automation needs approval |
| Preferred automation tool | Ansible candidate after secrets policy is finalized |
