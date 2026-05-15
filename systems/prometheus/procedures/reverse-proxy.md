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

## Phase 11 — Validation Checklist

From USER VLAN:

- [https://nextcloud.home.arpa](https://nextcloud.home.arpa/) loads
    
- HTTP automatically redirects to HTTPS
    

From MGMT VLAN:

- [https://proxy.home.arpa:8443/dashboard/](https://proxy.home.arpa:8443/dashboard/) loads
    

From USER VLAN:

- 8443 should eventually be blocked by firewall (future step)
    

---

## Phase 12 — Operational Rules

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