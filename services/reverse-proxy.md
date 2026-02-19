---
type: service
service_name: reverse-proxy
status: active
last_updated: 2026-02-19
---
# Reverse Proxy (Traefik)

## Purpose

Provide a single ingress point for internal services with:

- HTTPS termination on Prometheus
- Hostname-based routing to services running on Prometheus and Atlas
- HTTP → HTTPS redirect
- A separate admin entrypoint for dashboards (MGMT-only)

This design aligns with:

- architecture/network-architecture.md
- architecture/data-strategy.md
- security-model.md

## Hosting

- System: Prometheus (Ubuntu)
- Container / VM: Docker container (Traefik)
- Runtime: Docker Compose
- Deploy path: /opt/traefik

## Data Classification

- Authoritative: none
- Runtime: Traefik configuration, logs
- Disposable: the host (Prometheus) is rebuildable; all config must live in Git

## Storage Paths

|Path|Read/Write|Description|
|---|---|---|
|/opt/traefik/config/|R|Static Traefik config (entrypoints, providers)|
|/opt/traefik/dynamic/|R|Dynamic routers/middlewares/TLS store|
|/opt/traefik/certs/|R|Internal TLS certificate/key (self-signed for now)|
|/opt/traefik/logs/|RW|Access logs (and any future logs)|
|/opt/traefik/acme/|RW|Reserved for later ACME automation (not used yet)|

## Configuration

- Static config: /opt/traefik/config/traefik.yml
- Dynamic config dir: /opt/traefik/dynamic
- Providers:
    - Docker (label discovery; exposedByDefault=false)
    - File (infra routers: dashboard, Atlas backends)

Ports / EntryPoints:

- web: :80 (redirect to HTTPS)
- websecure: :443 (user-facing services)
- websecure-mgmt: :8443 (admin dashboards)

Notes:

- A localhost-only bind for the internal Traefik port may exist during bootstrap (127.0.0.1:18080 → 8080), but the long-term pattern is dashboard on :8443.

## Access

User-facing ingress:

- [https://nextcloud.home.arpa](https://nextcloud.home.arpa) (443)
- [https://openwebui.home.arpa](https://openwebui.home.arpa) (443)
- [https://comfy.home.arpa](https://comfy.home.arpa) (443)

Admin surface:

- [https://proxy.home.arpa:8443/dashboard/](https://proxy.home.arpa:8443/dashboard/)

Auth method:

- Traefik dashboard: no auth configured yet (must be protected by MGMT-only firewall policy)

## Security Notes

- Cerberus (OPNsense) enforces VLAN policy; Traefik provides ingress.
- Dashboard and admin surfaces must not be available from USER VLAN.
- Services behind Traefik should not publish ports to LAN (prefer internal Docker networks + Traefik routing).
- Internal TLS is currently self-signed; plan an internal trust strategy (import CA/cert into clients) before relying on it widely.

## Backup Strategy

- What is backed up:
    - /opt/traefik/config
    - /opt/traefik/dynamic
    - /opt/traefik/certs (if self-signed is being used long-term)
- Frequency: via repo (Git) + periodic snapshot/export if needed
- Restore test status: manual restore validated during initial build

## Monitoring & Health

- Health checks:
    - Container running: docker ps
    - Router visibility: GET [https://proxy.home.arpa:8443/api/overview](https://proxy.home.arpa:8443/api/overview)
- Metrics: not enabled yet

## Upgrade Strategy

- Manual upgrade via Docker image tag (Traefik)
- Expected downtime: brief (container restart)

## Known Issues

- curl -I sends HEAD and may return 405 for dashboard/API routes; use GET for validation.
- Mispointing backend URLs can route to Atlas Unraid UI instead of the service container port.

## Related Docs

- Procedures:
	- procedures/reverse-proxy-traefik-install.md (create)
    - procedures/reverse-proxy-traefik-update.md (create)
- Validation:
    - services/reverse-proxy-validation.md
- ADRs:
    - architecture/adr/ADR-007-centralized-ingress-prometheus.md (create)