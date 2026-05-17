# Ingress Flow - Internal

## Current State (Internal Only)

Client (USER VLAN)
  -> DNS resolution (.home.arpa)
  -> Prometheus IP
  -> HTTPS :443
  -> Traefik
  -> HTTP to target service

Examples:

nextcloud.home.arpa
  -> Atlas:8080

openwebui.home.arpa
  -> Prometheus container

comfy.home.arpa
  -> Prometheus container

searxng.home.arpa
  -> Prometheus container

ollama.home.arpa
  -> Prometheus container (live route observed; needs decision because [[decisions/ADR-007-centralized-ingress-on-prometheus]] keeps Ollama internal-only)

Future:
jellyfin.home.arpa
  -> Prometheus container

## Security Boundaries

- USER VLAN -> SERVERS VLAN allowed only on intended ingress ports.
- Atlas is not directly reachable for application ports.
- Only Prometheus serves 80/443.
- Traefik dashboard and admin entrypoints must remain MGMT-only.

## Enforcement Principle

All services must be behind:
  Prometheus -> Traefik -> Service

Direct access to:
  Atlas:8080
  Prometheus container ports

should be restricted at firewall level.
