---
type: service
service_name: gluetun
status: active
last_updated: 2026-05-16
---

# Gluetun

## Purpose

Gluetun provides the VPN network boundary for the Prometheus media stack.

## Hosting

- System: [[systems/prometheus]]
- Container / VM: `gluetun`
- Runtime: Docker Compose
- Live compose path: `/opt/vpn/docker-compose.yml`

## Data Classification

- Authoritative: none
- Runtime: `/opt/vpn/gluetun`
- Disposable: container image and recreated runtime state

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/opt/vpn/gluetun` | RW | Gluetun runtime configuration. Secrets must not be committed. |

## Configuration

- Environment variables: VPN provider, VPN type, WireGuard credentials, region selection
- Volumes: `/opt/vpn/gluetun:/gluetun`
- Ports:
  - `127.0.0.1:8080:8080` for qBittorrent WebUI through Gluetun

## Access

- URL: `http://127.0.0.1:8080` for qBittorrent WebUI through Gluetun
- Auth method: qBittorrent auth
- Roles: administrator only

## Security Notes

- Do not commit VPN secrets.
- Do not modify VPN secrets without explicit approval.
- qBittorrent uses `network_mode: service:gluetun`.
- Do not expose the qBittorrent WebUI beyond localhost without a documented ingress/security decision.

## Backup Strategy

- What is backed up: sanitized compose scaffold and non-secret configuration notes
- Frequency: Git-tracked docs/scaffold
- Restore test status: Needs validation

## Monitoring & Health

- Health checks: container running, VPN health/status, qBittorrent WebUI reachable on localhost
- Metrics: Needs validation

## Upgrade Strategy

- Manual image tag update in compose
- Downtime expectations: restarts affect qBittorrent network access

## Known Issues

- Live SSH validation succeeded on 2026-05-16.

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
| Config path | `/opt/vpn/gluetun` |
| Data path | None authoritative |
| Secret requirements | VPN secrets stay local and outside Git |
| Network ports | `127.0.0.1:8080` for qBittorrent WebUI through Gluetun |
| Dependencies | Docker, VPN provider credentials, media stack |
| Backup requirement | Sanitized config in Git; local secret recovery process needs validation |
| Validation command | [[systems/prometheus/procedures/media-stack-validation]] |
| Recovery procedure | Needs validation |
| Automation classification | Documentation/scaffold ready; mutating automation needs approval |
| Preferred automation tool | Ansible candidate after secrets policy is finalized |
