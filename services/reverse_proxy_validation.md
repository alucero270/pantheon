# Reverse Proxy (Traefik) — Validation Checklist

This document is a repeatable validation checklist to confirm the reverse proxy is operating correctly.

Use this:
- after config changes
- after upgrades
- after restores
- before adding a new service behind Traefik
- before enabling VPN-based access

It is not a rebuild guide. See the procedure/runbook for rebuild steps.

---

## A. DNS Validation (Client-Side)

Goal: all service hostnames resolve to Prometheus (the ingress point).

From a USER VLAN client (example DNS = 192.168.20.1):
- nextcloud.home.arpa resolves to 192.168.60.103
- proxy.home.arpa resolves to 192.168.60.103

From a MGMT VLAN client (MGMT DNS resolver):
- nextcloud.home.arpa resolves to 192.168.60.103
- proxy.home.arpa resolves to 192.168.60.103

Pass criteria:
- No client relies on local hosts file entries for these names.
- Both names resolve consistently across VLANs.

---

## B. Port Exposure (Prometheus)

Goal: Prometheus is listening only on intended ingress ports.

On Prometheus:
- TCP 80 is listening (Traefik web)
- TCP 443 is listening (Traefik websecure)
- TCP 8443 is listening (Traefik websecure-mgmt)

Optional:
- TCP 18080 bound to 127.0.0.1 only (if enabled)

Pass criteria:
- No unexpected published ports for internal services.
- 8443 will later be firewall-restricted to MGMT VLAN only.

---

## C. Traefik Health (Prometheus)

Goal: Traefik is running and providers are loaded.

Checks:
- Container is running
- Logs show no repeating provider errors
- File provider is reading dynamic configs
- Docker provider is available (even if no labeled services yet)

Pass criteria:
- No repeating error loops in logs.
- Dashboard API returns JSON successfully.

---

## D. TLS Sanity (Prometheus)

Goal: Traefik is serving TLS with the expected internal certificate.

Checks:
- Certificate is loaded (no “failed to load X509 key pair” errors)
- HTTPS connections complete

Pass criteria:
- TLS handshake succeeds for nextcloud.home.arpa and proxy.home.arpa.
- Certificate CN/SAN covers:
  - proxy.home.arpa
  - nextcloud.home.arpa
  - *.home.arpa

---

## E. Dashboard Access Pattern

Goal: dashboard is accessible only via the MGMT entrypoint.

Expected behavior:
- https://proxy.home.arpa:8443/dashboard/ is reachable (MGMT VLAN)
- proxy.home.arpa on 443 is not used for dashboard

Notes:
- Some curl HEAD requests may return 405 for dashboard/API; use GET when validating.

Pass criteria:
- Dashboard works on :8443.
- Dashboard is not exposed through :443.

---

## F. Nextcloud Routing (End-to-End)

Goal: nextcloud.home.arpa routes through Traefik to the Atlas container correctly.

Expected flow:
Client → HTTPS 443 (Prometheus) → HTTP 8080 (Atlas Nextcloud container)

Pass criteria:
- nextcloud.home.arpa loads the Nextcloud login page
- No redirect loops
- No exposure of Unraid web UI

Failure signatures:
- ERR_TOO_MANY_REDIRECTS
  - Nextcloud overwrite* or trusted_proxies misconfigured
- Seeing Unraid login page
  - Traefik backend URL points to Atlas base web UI instead of Nextcloud container port

---

## G. Nextcloud Proxy Configuration (Atlas)

Goal: Nextcloud is configured to behave correctly behind TLS termination.

Check the following values:

trusted_domains includes:
- localhost
- nextcloud.home.arpa

trusted_proxies includes:
- 192.168.60.103

overwriteprotocol:
- https

overwritehost:
- nextcloud.home.arpa

overwrite.cli.url:
- https://nextcloud.home.arpa

Pass criteria:
- All values are present and correct.

---

## H. Backend Reachability (Prometheus → Atlas)

Goal: Prometheus can reach Atlas Nextcloud backend on port 8080.

Pass criteria:
- Prometheus can connect to 192.168.60.102:8080
- No timeouts or connection refused

---

## I. Security Intent Verification (High-Level)

Goal: validate that current state matches the intended security model.

Intended policy:
- USER VLAN can reach 443 on Prometheus
- USER VLAN should not reach 8443 on Prometheus (enforced later via firewall)
- MGMT VLAN can reach 8443
- Only Prometheus should reach Atlas:8080 (enforced later via firewall)

Pass criteria:
- Documented intent matches reality once firewall rules are implemented.

---

## J. Change Control (Minimum)

After any change:
- Update reverse-proxy.md if architecture changes
- Update procedure doc if rebuild steps change
- Update this validation checklist if expected outputs change
- Commit changes with a message tied to the relevant issue

---

## Quick Outcome

If A–H pass:
- Ingress is healthy and safe to extend with the next service.

If any section fails:
- Stop and resolve before adding new routes/services.

