# Procedure — Deploy Reverse Proxy (Traefik) on Prometheus

This document is the operational runbook for rebuilding or auditing the Traefik ingress layer.

This procedure assumes:

- Prometheus is Ubuntu Server
- Docker + Docker Compose are installed
- Prometheus IP is 192.168.60.103
- Atlas IP is 192.168.60.102

---

## Phase 1 — Prepare Directory Structure (Prometheus)

Create base structure:

/opt/traefik
/opt/traefik/config
/opt/traefik/dynamic
/opt/traefik/certs
/opt/traefik/logs
/opt/traefik/acme

Ensure permissions allow Docker to read config and certs.

---

## Phase 2 — Create Docker Network (if not existing)

Ensure a shared Docker network named:

proxy

This network will be used by Traefik and future Prometheus services.

---

## Phase 3 — Static Configuration

File:
/opt/traefik/config/traefik.yml

Define:

EntryPoints:

- web → :80

- websecure → :443

- websecure-mgmt → :8443

- traefik → :8080


Providers:

- Docker (unix:///var/run/docker.sock)

- File (/dynamic)


Enable dashboard (api.dashboard = true).
Disable insecure dashboard.

---

## Phase 4 — Generate Internal TLS Certificate

Location:
/opt/traefik/certs

Generate self-signed certificate for:

- proxy.home.arpa

- nextcloud.home.arpa

- *.home.arpa


Files created:

- homelab-tls.crt

- homelab-tls.key


---

## Phase 5 — TLS Store Configuration

File:
/opt/traefik/dynamic/tls.yml

Define default TLS store pointing to:
/certs/homelab-tls.crt
/certs/homelab-tls.key

Restart Traefik and verify no TLS load errors in logs.

---

## Phase 6 — Middleware Definitions

File:
/opt/traefik/dynamic/middlewares.yml

Define:

- HTTP → HTTPS redirect middleware

- Security headers middleware (optional but recommended)


---

## Phase 7 — Dashboard Router (MGMT Only)

File:
/opt/traefik/dynamic/dashboard.yml

Route:

- Host: proxy.home.arpa

- EntryPoint: websecure-mgmt (:8443)

- Service: api@internal

- TLS enabled


Validate:
Access [https://proxy.home.arpa:8443/dashboard/](https://proxy.home.arpa:8443/dashboard/)

---

## Phase 8 — Nextcloud Router (Atlas Backend)

File:
/opt/traefik/dynamic/nextcloud.yml

Define:
HTTP router (web) → redirect middleware
HTTPS router (websecure)
Backend service URL:
[http://192.168.60.102:8080](http://192.168.60.102:8080/)

Validate locally on Prometheus using curl with Host header.

---

## Phase 9 — Configure Nextcloud Proxy Settings (Atlas)

Inside Nextcloud container:

Set:

- trusted_domains

- trusted_proxies = 192.168.60.103

- overwriteprotocol = https

- overwritehost = nextcloud.home.arpa

- overwrite.cli.url = [https://nextcloud.home.arpa](https://nextcloud.home.arpa/)


Confirm values using occ config:system:get

---

## Phase 10 — DNS Configuration (Cerberus)

Services → Unbound DNS → Overrides → Hosts

Add:

- proxy.home.arpa → 192.168.60.103

- nextcloud.home.arpa → 192.168.60.103


Validate from client VLAN:

nslookup nextcloud.home.arpa 192.168.20.1

---

## Phase 10.5 - Trust the Internal TLS Certificate on Windows Clients

Pantheon currently uses a self-signed `home.arpa` certificate for internal
Traefik routes. Each Windows client must trust the public certificate before
the Nextcloud desktop client can connect without TLS errors.

### Export and verify on Prometheus

The public certificate is:

`/opt/traefik/certs/homelab-tls.crt`

Never copy `/opt/traefik/certs/homelab-tls.key` to a client. Verify the public
certificate before transferring it:

```bash
openssl x509 -in /opt/traefik/certs/homelab-tls.crt \
  -noout -subject -issuer -dates -fingerprint -sha256 -ext subjectAltName
```

Confirm that:

- The certificate is currently valid.
- The SAN list contains `nextcloud.home.arpa` (or `*.home.arpa`).
- The SHA-256 fingerprint matches the transferred certificate.
- The transferred file contains `BEGIN CERTIFICATE`, never `PRIVATE KEY`.

### Import for the current Windows user

1. Open `certmgr.msc` as the user who runs Nextcloud.
2. Open **Trusted Root Certification Authorities > Certificates**.
3. Select **All Tasks > Import**.
4. Select the transferred public certificate. Use the **All files** filter if
   the file does not have a `.cer` or `.crt` extension.
5. Place it in **Trusted Root Certification Authorities** and complete the
   import.

The current `home.arpa` certificate is self-signed (its subject and issuer are
the same) and has the CA basic constraint, so it belongs in the Trusted Root
store. Do not place it in Intermediate Certification Authorities merely to
mirror an older client configuration.

### Configure and validate Nextcloud

1. Fully exit and restart the Nextcloud desktop client.
2. Connect to `https://nextcloud.home.arpa`.
3. Use normal Nextcloud account authentication.

Do not choose **Connect without TLS** or **Use client certificate**. The latter
expects a PKCS#12 client identity and is unrelated to trusting Traefik's server
certificate.

Validate from the client:

```powershell
Resolve-DnsName nextcloud.home.arpa
Test-NetConnection nextcloud.home.arpa -Port 443
curl.exe -I https://nextcloud.home.arpa
```

If TCP 443 is unreachable, fix the Cerberus client-VLAN-to-Traefik access path
before troubleshooting certificates. A trusted certificate cannot bypass a
firewall block.

When the internal certificate is rotated, redistribute and trust the new
public certificate, validate all clients, and then remove the expired
certificate from their trust stores.

---

## Phase 11 — Validation Checklist

From USER VLAN:

- [https://nextcloud.home.arpa](https://nextcloud.home.arpa/) loads

- HTTP automatically redirects to HTTPS


From MGMT VLAN:

- [https://proxy.home.arpa:8443/dashboard/](https://proxy.home.arpa:8443/dashboard/) loads


From USER VLAN:

- 8443 should eventually be blocked by firewall (future step)


---

## Phase 12 - Current Prometheus-Hosted Routes

Current live Docker-provider routes observed on 2026-05-17:

| Hostname | Backend | Status |
|---|---|---|
| `openwebui.home.arpa` | OpenWebUI container port 8080 | Active |
| `comfy.home.arpa` | ComfyUI container port 8188 | Active |
| `searxng.home.arpa` | SearXNG container port 8080 | Active |
| `ollama.home.arpa` | Ollama container port 11434 | Live drift; needs decision |

`ollama.home.arpa` conflicts with [[decisions/ADR-007-centralized-ingress-on-prometheus]], which says Ollama remains internal-only and is not routed. Do not treat that route as approved until the ADR is explicitly revisited or the live route is removed.

---

## Phase 13 — Operational Rules

All new services must:

1. Not publish ports externally

2. Join the proxy Docker network

3. Be exposed via Traefik only

4. Use host-based routing


Atlas services must never be directly accessed by client VLANs.

---

## Recovery Procedure

If dashboard unavailable:

- Verify DNS resolution

- Verify Traefik container running

- Verify entrypoints bound (80, 443, 8443)

- Inspect dynamic config inside container

- Inspect Traefik logs


If Nextcloud redirect loop occurs:

- Verify trusted_proxies

- Verify overwriteprotocol

- Confirm backend URL is [http://Atlas:8080](http://atlas:8080/)


---

This document is authoritative for rebuilding ingress from scratch.
