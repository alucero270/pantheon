# ADR-007: Centralized Ingress on Prometheus

## Status

Accepted

## Context

The homelab architecture defines:

- Cerberus (OPNsense) as the enforcement plane (routing, firewall, DNS)
- Atlas (Unraid) as authoritative storage and backend service host
- Prometheus (Ubuntu) as compute/services node and disposable runtime per the data strategy

Nextcloud is hosted on Atlas (container published on port 8080). The homelab requires a production-grade ingress point that:

- Terminates HTTPS
- Routes to Atlas-hosted services and Prometheus-hosted services
- Remains internal-only initially
- Is compatible with later VPN-based remote access
- Avoids port sprawl on the host

Additionally, Prometheus now hosts AI services (Ollama, OpenWebUI, ComfyUI) that must integrate cleanly with the ingress model.

---

## Decision

Run the reverse proxy (Traefik) on Prometheus as the single ingress point for internal services.

Use separate entrypoints:

- 443 for user-facing service ingress
- 8443 for MGMT-only dashboards and admin surfaces

Do not run the reverse proxy on Cerberus.

Expose application services using the Traefik Docker provider with labels instead of publishing host ports.

---

## Routing Model

### Atlas-Hosted Backends

Example:

- nextcloud.home.arpa → Traefik (Prometheus) → [http://192.168.60.102:8080](http://192.168.60.102:8080)

Atlas remains backend-only. It does not expose services directly to clients.

### Prometheus-Hosted Services (Docker Provider Pattern)

Services such as:

- OpenWebUI
- ComfyUI

Attach to the external `proxy` Docker network and are exposed using Traefik labels.

They:

- Do not publish ports to the host
- Are reachable only via hostname-based routing through Traefik

Backend-only services (e.g., Ollama) remain internal and are not routed publicly.

---

## Network Model

Docker networks:

- `proxy` (external) → shared with Traefik for routed services
- `ai_internal` (internal) → isolates backend AI components

This ensures:

- Only services explicitly labeled are exposed
- Internal model-serving components are not externally reachable

---

## Rationale

- Preserves role separation: Cerberus remains a security appliance, not an application host.
- Aligns with the data strategy: Prometheus is disposable; ingress configuration is version-controlled and rebuildable.
- Aligns with the security model: admin surfaces are restricted to MGMT via a dedicated port and firewall policy.
- Prevents port sprawl by eliminating direct host exposure of services.
- Scales cleanly: host-based routing supports many services without additional IPs or port allocations.

---

## Consequences

### Positive

- Consistent ingress pattern for all services
- Centralized TLS management
- Clear separation between user access and admin access paths
- Reduced attack surface through label-based exposure
- Future VPN can provide secure remote access without exposing WAN ingress

### Negative / Tradeoffs

- Requires careful firewall policy (MGMT vs USER)
- Requires internal certificate trust strategy (self-signed now; improve later)
- Adds a critical service on Prometheus (mitigated by reproducible config and backups)
- Requires discipline in Docker labeling to avoid accidental exposure

---

## Implementation Notes

### DNS

- home.arpa names are resolved via Cerberus Unbound host overrides to Prometheus.

### EntryPoints

- web (:80) → HTTP redirect
- websecure (:443) → user services
- websecure-mgmt (:8443) → admin dashboards

### Atlas Backends

- nextcloud.home.arpa → [http://192.168.60.102:8080](http://192.168.60.102:8080)
- Configure Nextcloud trusted_proxies and overwrite values to prevent redirect loops.

### AI Services

- OpenWebUI and ComfyUI use Traefik Docker labels.
- Ollama remains internal-only and is not routed.

### Dashboard

- Expose Traefik dashboard only on :8443 via proxy.home.arpa using api@internal.
- Enforce MGMT-only access using firewall rules (not hostname rules).

---

## Alignment

This ADR governs:

- Reverse proxy placement
- Port separation strategy
- Docker-provider exposure pattern
- Backend routing discipline

All future services must conform to this ingress model.