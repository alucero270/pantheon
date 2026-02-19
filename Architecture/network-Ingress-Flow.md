# Ingress Flow — Internal

## Current State (Internal Only)

Client (USER VLAN)
  ↓ DNS resolution (.home.arpa)
  ↓
Prometheus IP
  ↓ HTTPS :443
Traefik
  ↓ HTTP
Target Service

Examples:

nextcloud.home.arpa
  → Atlas:8080

Future:
openwebui.home.arpa
  → Prometheus container

---

## Security Boundaries

- USER VLAN → SERVERS VLAN allowed only on 443
- Atlas not directly reachable for application ports
- Only Prometheus serves 80/443

---

## Enforcement Principle

All services must be behind:
  Prometheus → Traefik → Service

Direct access to:
  Atlas:8080
  Prometheus container ports

should be restricted at firewall level.
