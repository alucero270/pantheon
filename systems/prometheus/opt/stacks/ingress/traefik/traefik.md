---
type: service
service_name: reverse-proxy
status: active
last_updated: 2026-05-17
---
# Reverse Proxy (Traefik)

## Purpose

Provide a single ingress point for internal services with:

- HTTPS termination on Prometheus
- Hostname-based routing to services running on Prometheus and Atlas
- HTTP → HTTPS redirect
- A separate admin entrypoint for dashboards (MGMT-only)

This design aligns with:

- [[systems/network/architecture/network-architecture]]
- [[systems/atlas/architecture/data-strategy]]
- security-model.md

## Hosting

- System: Prometheus (Ubuntu)
- Container / VM: Docker container (Traefik)
- Runtime: Docker Compose
- Image: `traefik:v3.6.1`
- Compose path: `/opt/traefik/docker-compose.yml`
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
- traefik: :8080 (published as `127.0.0.1:18080 -> 8080`)

Notes:

- A localhost-only bind for the internal Traefik port may exist during bootstrap (127.0.0.1:18080 → 8080), but the long-term pattern is dashboard on :8443.

## Access

Internal user-facing ingress (`.home.arpa` — LAN only):

- [https://nextcloud.home.arpa](https://nextcloud.home.arpa) (443)
- [https://openwebui.home.arpa](https://openwebui.home.arpa) (443)
- [https://comfy.home.arpa](https://comfy.home.arpa) (443)
- [https://searxng.home.arpa](https://searxng.home.arpa) (443)

Public ingress via Cloudflare Tunnel (`loosearrowlabs.com` — Cloudflare Access gated):

- [https://chat.loosearrowlabs.com](https://chat.loosearrowlabs.com) → openwebui:8080
- [https://comfy.loosearrowlabs.com](https://comfy.loosearrowlabs.com) → comfyui:8188
- [https://search.loosearrowlabs.com](https://search.loosearrowlabs.com) → searxng:8080

Public routes are defined in `/opt/traefik/dynamic/loosearrow-public.yml` and are only reachable via the Cloudflare Tunnel. See [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/cloudflare-tunnel]].

Live route needing decision:

- [https://ollama.home.arpa](https://ollama.home.arpa) (443)

`ollama.home.arpa` exists in live Traefik labels as of 2026-05-17, but [[decisions/ADR-007-centralized-ingress-on-prometheus]] says Ollama remains internal-only and is not routed.

Admin surface:

- [https://proxy.home.arpa:8443/dashboard/](https://proxy.home.arpa:8443/dashboard/)

Auth method:

- Traefik dashboard: no auth configured yet (must be protected by MGMT-only firewall policy)

## Security Notes

- Cerberus (OPNsense) enforces VLAN policy; Traefik provides ingress.
- Dashboard and admin surfaces must not be available from USER VLAN.
- Services behind Traefik should not publish ports to LAN (prefer internal Docker networks + Traefik routing).
- Backend-only services should not be routed unless an ADR or service-specific decision allows it.
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
	- systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-traefik-install.md (create)
    - systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-traefik-update.md (create)
- Validation:
    - [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]]
- ADRs:
    - decisions/ADR-007-centralized-ingress-on-prometheus.md (create)

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker reverse proxy / ingress runtime |
| Source of truth | [[decisions/ADR-007-centralized-ingress-on-prometheus]] and [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]] |
| Config path | `/opt/traefik/config/traefik.yml`, `/opt/traefik/dynamic` |
| Data path | `/opt/traefik/config`, `/opt/traefik/dynamic`, `/opt/traefik/certs`, `/opt/traefik/logs`, `/opt/traefik/acme` |
| Secret requirements | Do not commit TLS secrets or credentials |
| Network ports | `0.0.0.0:80`, `0.0.0.0:443`, `0.0.0.0:8443`, `127.0.0.1:18080 -> 8080` |
| Dependencies | Cerberus DNS/firewall policy, Docker network, backend services |
| Backup requirement | Git-backed configuration and recovery procedure required |
| Validation command | [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]] |
| Recovery procedure | [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]] |
| Automation classification | Ansible candidate after compose inventory |
| Preferred automation tool | Ansible |
