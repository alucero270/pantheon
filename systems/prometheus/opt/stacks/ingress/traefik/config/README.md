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

## Live Change Notes

### 2026-05-28 llama-swap-http router: drop HTTP→HTTPS redirect, preserve IP allowlist

Live path: `/opt/traefik/dynamic/llama-swap.yml`

Rollback snapshot created on Prometheus:

- `/opt/traefik/dynamic/llama-swap.yml.bak-2026-05-28T175304Z`

Rollback command:

```bash
sudo cp -p /opt/traefik/dynamic/llama-swap.yml.bak-2026-05-28T175304Z \
  /opt/traefik/dynamic/llama-swap.yml
```

Hypothesis:

- Clients sending `Authorization: Bearer LOCAL` to `http://llama-swap.home.arpa` were getting `401` despite [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] documenting Bearer as the supported auth header.
- The `llama-swap-http` router was applying `redirect-to-https@file`, returning `301` to `https://llama-swap.home.arpa`. HTTP clients (PowerShell `Invoke-RestMethod`, Rust `reqwest`, and curl ≥ 7.86) strip the `Authorization` header on cross-scheme redirect per RFC 7235 guidance, so the second-leg HTTPS request reached llama-swap with no credentials.
- `X-API-Key: LOCAL` worked because it is a custom header not in the auth-strip list.

Change:

- Edited `/opt/traefik/dynamic/llama-swap.yml`. In the `llama-swap-http` router (the `web` entrypoint), replaced the single middleware `redirect-to-https@file` with `ollama-allowlist@file`. The `llama-swap-https` router on `websecure` is unchanged.
- The allowlist swap is mandatory: the prior redirect implicitly funneled all traffic through the `websecure` router where `ollama-allowlist@file` was applied. Removing the redirect without adding the allowlist would have left HTTP wide open.
- Exact edit (idempotent and symmetric):

```bash
sudo sed -i 's|- redirect-to-https@file|- ollama-allowlist@file|' \
  /opt/traefik/dynamic/llama-swap.yml
```

Validation:

- Direct llama-swap probe via `172.17.0.1:8085` with `Authorization: Bearer LOCAL` returned `200` before and after the change, confirming the gap was in Traefik, not llama-swap.
- After the change, `curl -H 'Authorization: Bearer LOCAL' http://llama-swap.home.arpa/v1/models` from Prometheus returned `200`.
- After the change, the same probe from the Windows workstation via `Invoke-RestMethod` returned `200` with 18 model entries in `data[]`.
- `noauth http://llama-swap.home.arpa/v1/models` still returns `401`, confirming llama-swap's `apiKeys` check is still enforced on the HTTP path.
- Traefik file provider reloaded automatically within ~5 seconds; no service restart required.

Result:

- `Authorization: Bearer LOCAL` now works against `http://llama-swap.home.arpa/v1/models` end-to-end from both Prometheus and the Windows workstation.
- HTTPS path is unchanged and still works with Bearer or X-API-Key.
- IP allowlist coverage on the HTTP path is restored.

Decision:

- Keep. The `redirect-to-https@file` middleware was load-bearing only for HTTPS-only browser ergonomics; for LAN-only `.home.arpa` AI control endpoints behind an IP allowlist with a self-signed `home.arpa` cert, forcing HTTPS provided no trust gain while breaking standard HTTP auth-header semantics for non-browser clients.

Needs validation:

- Off-allowlist client (a source IP outside `127.0.0.1/32`, `172.20.0.1/32`, `100.64.0.0/10`, `192.168.{1,60,99}.0/24`) is still blocked by `ollama-allowlist@file` on the HTTP path. Not testable from Prometheus itself.
- The same redirect-strip-auth issue applies to `anemoi.home.arpa` via `/opt/traefik/dynamic/anemoi.yml`. Apply the same single-line swap in a separate live-change iteration before any caller uses Bearer against the anemoi route.

Tracking issue: TBD — open one if validation of the off-allowlist block or the parallel anemoi-router patch is needed.

Content note:

- Root cause was a generic Traefik + HTTP-client interaction, not specific to llama-swap. Worth a public-facing writeup for anyone reverse-proxying an OpenAI-compatible API behind a `redirect-to-https` middleware and wondering why Bearer dies but `X-API-Key` does not.

## Related Procedures

- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]]
- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]]

## Rules

- Do not commit private keys, dashboard credentials, or secrets.
- Do not weaken MGMT-only or ingress boundary constraints.
