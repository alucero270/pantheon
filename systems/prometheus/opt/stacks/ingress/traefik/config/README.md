# Traefik Config

## Purpose

This folder tracks sanitized Traefik config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/traefik/config/traefik.yml` | Static Traefik config | Sanitized Git candidate |
| `/opt/traefik/dynamic` | Dynamic routers, middlewares, transports, TLS store | Sanitized Git candidate |
| `/opt/traefik/certs` | TLS cert/key material | Do not commit private keys |
| `/opt/traefik/acme` | ACME state if used | Do not commit secrets |

## Status

No Git-backed sanitized Traefik config has been committed here yet.

## Snapshot Pattern

```bash
cp /opt/traefik/config/traefik.yml \
  /opt/traefik/config/traefik.yml.$(date +%F-%H%M%S).bak
```

## Related Procedures

- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]]
- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]]

## Rules

- Do not commit private keys, dashboard credentials, or secrets.
- Do not weaken MGMT-only or ingress boundary constraints.
