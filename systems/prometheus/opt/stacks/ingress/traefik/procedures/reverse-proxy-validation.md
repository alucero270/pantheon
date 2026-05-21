# Reverse Proxy (Traefik) - Validation Checklist

This document is a repeatable validation checklist to confirm the reverse proxy is operating correctly.

Use this:

- after config changes
- after upgrades
- after restores
- before adding a new service behind Traefik
- before enabling VPN-based access

It is not a rebuild guide. See [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]] for rebuild steps.

## A. DNS Validation

Goal: all service hostnames resolve to Prometheus, the ingress point.

Expected records:

| Hostname | Target |
|---|---|
| `proxy.home.arpa` | Prometheus |
| `nextcloud.home.arpa` | Prometheus |
| `openwebui.home.arpa` | Prometheus |
| `comfy.home.arpa` | Prometheus |
| `searxng.home.arpa` | Prometheus |
| `ollama.home.arpa` | Prometheus in live state, but route needs decision |

Pass criteria:

- No client relies on local hosts file entries for these names.
- Names resolve consistently across intended VLANs.
- `ollama.home.arpa` is either explicitly approved by a decision or removed from live routing.

## B. Port Exposure

Goal: Prometheus is listening only on intended ingress ports.

On Prometheus:

- TCP 80 is listening for Traefik `web`.
- TCP 443 is listening for Traefik `websecure`.
- TCP 8443 is listening for Traefik `websecure-mgmt`.
- TCP 18080 is bound to `127.0.0.1` only for the Traefik API/dashboard service port.

Pass criteria:

- No unexpected published ports for internal services.
- 8443 is restricted to MGMT VLAN by firewall policy.
- Backend containers prefer Docker-network-only exposure.

## C. Traefik Health

Goal: Traefik is running and providers are loaded.

Checks:

- Container `traefik` is running.
- Image is documented.
- Logs show no repeating provider errors.
- File provider is reading dynamic configs.
- Docker provider is available.

Pass criteria:

- No repeating error loops in logs.
- Dashboard/API works through the documented MGMT-only path.

## D. TLS Sanity

Goal: Traefik is serving TLS with the expected internal certificate.

Checks:

- Certificate is loaded.
- HTTPS connections complete.

Pass criteria:

- TLS handshake succeeds for service hostnames.
- Certificate CN/SAN covers the required `.home.arpa` names or wildcard.

## E. Dashboard Access Pattern

Goal: dashboard is accessible only via the MGMT entrypoint.

Expected behavior:

- `https://proxy.home.arpa:8443/dashboard/` is reachable from MGMT VLAN.
- `proxy.home.arpa` on 443 is not used for the dashboard.

Notes:

- Some curl HEAD requests may return 405 for dashboard/API; use GET when validating.

## F. Nextcloud Routing

Goal: `nextcloud.home.arpa` routes through Traefik to the Atlas container correctly.

Expected flow:

Client -> HTTPS 443 on Prometheus -> Traefik -> HTTP 8080 on Atlas Nextcloud container

Pass criteria:

- `nextcloud.home.arpa` loads the Nextcloud login page.
- No redirect loops.
- No exposure of the Unraid web UI.

Failure signatures:

- `ERR_TOO_MANY_REDIRECTS`: Nextcloud `overwrite*` or `trusted_proxies` is misconfigured.
- Seeing Unraid login page: Traefik backend URL points to Atlas base web UI instead of Nextcloud container port.

## G. AI and Search Routes

Goal: AI user-facing routes are reachable through Traefik and backend-only routes are not accidentally approved.

Expected routes:

- `openwebui.home.arpa` routes to OpenWebUI container port 8080.
- `comfy.home.arpa` routes to ComfyUI container port 8188.
- `searxng.home.arpa` routes to SearXNG container port 8080.

Validation from Prometheus:

```bash
curl -k --resolve openwebui.home.arpa:443:127.0.0.1 https://openwebui.home.arpa/
curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/
curl -k --resolve searxng.home.arpa:443:127.0.0.1 "https://searxng.home.arpa/search?q=test&format=json"
```

Pass criteria:

- OpenWebUI returns an HTTP success or login page.
- ComfyUI returns an HTTP success page.
- SearXNG returns HTTP 200 with JSON when `format=json` is requested.

Decision drift:

- `ollama.home.arpa` exists in live labels as of 2026-05-17 but conflicts with [[decisions/ADR-007-centralized-ingress-on-prometheus]], which says Ollama remains internal-only.

## H. Nextcloud Proxy Configuration

Goal: Nextcloud is configured to behave correctly behind TLS termination.

Check the following values on Atlas:

- `trusted_domains` includes `localhost` and `nextcloud.home.arpa`.
- `trusted_proxies` includes `192.168.60.103`.
- `overwriteprotocol` is `https`.
- `overwritehost` is `nextcloud.home.arpa`.
- `overwrite.cli.url` is `https://nextcloud.home.arpa`.

## I. Backend Reachability

Goal: Prometheus can reach Atlas Nextcloud backend on port 8080.

Pass criteria:

- Prometheus can connect to `192.168.60.102:8080`.
- No timeouts or connection refused.

## J. Security Intent Verification

Goal: validate that current state matches the intended security model.

Intended policy:

- USER VLAN can reach 443 on Prometheus.
- USER VLAN should not reach 8443 on Prometheus.
- MGMT VLAN can reach 8443.
- Only Prometheus should reach Atlas:8080.
- Backend-only services such as Ollama should not be routed unless explicitly approved.

Pass criteria:

- Documented intent matches reality once firewall rules are implemented.
- Any drift is captured in [[systems/prometheus/inventory]] and tracked by an issue.

## K. Change Control

After any change:

- Update [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] if architecture or access changes.
- Update [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]] if rebuild steps change.
- Update this validation checklist if expected outputs change.
- Update [[systems/prometheus/inventory]] and [[systems/prometheus/architecture/compose-registry]] if live routes, ports, or compose paths change.

## Quick Outcome

If A through I pass:

- Ingress is healthy enough to extend with the next service.

If any section fails:

- Stop and resolve before adding new routes/services.
