---
type: service
service_name: cloudflare-tunnel
status: active
last_updated: 2026-05-27
---

# Cloudflare Tunnel (cloudflared)

## Purpose

Provide authenticated public access to selected Prometheus services via a Cloudflare Tunnel, without exposing the home network IP or opening any inbound ports on the router.

The tunnel runs on Prometheus and makes an outbound-only QUIC connection to Cloudflare's edge. Cloudflare proxies inbound requests through the tunnel to Traefik, which routes them to the appropriate backend service.

This design:

- Keeps the home IP completely hidden from the internet
- Requires no router port forwarding or firewall changes
- Uses Cloudflare Access to gate all public routes to the owner's identity only
- Integrates cleanly with the existing [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] ingress layer

## Hosting

- System: [[systems/prometheus]]
- Runtime: systemd service (`cloudflared.service`)
- Binary: `/usr/bin/cloudflared`
- Version at install: `2026.5.1`
- Config path: `/etc/cloudflared/config.yml`
- Service installed via: `cloudflared service install <tunnel-token>`

## Tunnel Details

| Field | Value |
|---|---|
| Tunnel name | `prometheus` |
| Tunnel ID | `bef05e7e-45a0-4f10-a2d6-b93b228102f2` |
| Cloudflare account | A.lucero2892@gmail.com |
| Domain | `loosearrowlabs.com` |
| Auth method | API token (Cloudflare Tunnel Edit + Zone DNS Edit) |

## Traffic Flow

```
Browser (you, anywhere)
  → Cloudflare Access (identity gate — your email only)
    → Cloudflare Edge (TLS termination)
      → cloudflared tunnel (outbound QUIC from prometheus)
        → Traefik :443 (internal TLS, noTLSVerify)
          → Docker service container
```

Your home IP is never in this path. No inbound ports are opened.

## Public Routes

| Public Hostname | Backend | Via | Notes |
|---|---|---|---|
| `chat.loosearrowlabs.com` | `openwebui:8080` | Traefik | Open WebUI |
| `comfy.loosearrowlabs.com` | `comfyui:8188` | Traefik | ComfyUI (add when container is running) |
| `search.loosearrowlabs.com` | `searxng:8080` | Traefik | SearXNG |
| `app.loosearrowlabs.com` | `localhost:3000` | Direct | Homelable frontend |

DNS CNAMEs for all four subdomains point to `bef05e7e-45a0-4f10-a2d6-b93b228102f2.cfargotunnel.com` (Cloudflare-proxied).

## Configuration Files

### /etc/cloudflared/config.yml (on prometheus)

```yaml
ingress:
  - hostname: chat.loosearrowlabs.com
    service: https://localhost:443
    originRequest:
      noTLSVerify: true
  - hostname: comfy.loosearrowlabs.com
    service: https://localhost:443
    originRequest:
      noTLSVerify: true
  - hostname: search.loosearrowlabs.com
    service: https://localhost:443
    originRequest:
      noTLSVerify: true
  - hostname: app.loosearrowlabs.com
    service: http://localhost:3000
  - service: http_status:404
```

`noTLSVerify: true` is required because Traefik uses an internal self-signed certificate. Cloudflare handles real TLS externally.

### /opt/traefik/dynamic/loosearrow-public.yml (on prometheus)

See [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/config/README]] for the sanitized copy.

## Security Notes

- **Cloudflare Access must be configured** for each public subdomain or traffic is open to the internet. See [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/procedures/cloudflare-tunnel-install]] Phase 5.
- The API token used during setup should be rotated after initial install (it was entered interactively and is sensitive).
- Do not commit the tunnel token or API token to Git.
- `noTLSVerify: true` is acceptable here because the connection is localhost-only between cloudflared and Traefik on the same host.
- Ollama is intentionally not routed publicly. Expose Open WebUI instead.

## Adding a New Public Route

1. Add the hostname to `/etc/cloudflared/config.yml` before the catch-all `http_status:404` line.
2. Add a router and service entry to `/opt/traefik/dynamic/loosearrow-public.yml`.
3. Create the DNS CNAME in Cloudflare (or run `cloudflared tunnel route dns prometheus <hostname>`).
4. Add a Cloudflare Access policy for the new hostname.
5. Test: `curl -sk -H "Host: <hostname>" https://localhost:443/ -o /dev/null -w "%{http_code}"` on prometheus.

## Monitoring & Health

Service status:

```bash
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -n 50
```

Connectivity check from prometheus:

```bash
curl -sk -H "Host: chat.loosearrowlabs.com" https://localhost:443/ -o /dev/null -w "%{http_code}\n"
curl -sk -H "Host: search.loosearrowlabs.com" https://localhost:443/ -o /dev/null -w "%{http_code}\n"
```

Tunnel health in Cloudflare dashboard: Zero Trust → Networks → Tunnels → prometheus → should show **Healthy**.

## Upgrade Strategy

cloudflared is installed as a `.deb` package. To upgrade:

```bash
curl -L --output /tmp/cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i /tmp/cloudflared.deb
sudo systemctl restart cloudflared
```

## Known Issues

- ComfyUI (`comfy.loosearrowlabs.com`) DNS and Traefik config are in place but the container was not running at setup time. Route will 502 until ComfyUI is started and the container name `comfyui` is confirmed.
- Cloudflare Access policies must be created manually in the dashboard — no API automation is set up for this yet.
- API token used during tunnel creation should be rotated.

## Related Docs

- [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
- [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/procedures/cloudflare-tunnel-install]]
- [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/procedures/cloudflare-tunnel-validation]]
- [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/config/README]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | systemd service |
| Source of truth | `/etc/cloudflared/config.yml` and `/opt/traefik/dynamic/loosearrow-public.yml` |
| Config path | `/etc/cloudflared/` |
| Data path | n/a (stateless tunnel) |
| Secret requirements | Do not commit tunnel token, API token, or credentials JSON |
| Network ports | No inbound ports. Outbound QUIC to Cloudflare edge. |
| Dependencies | cloudflared binary, Traefik, Cloudflare account, loosearrowlabs.com DNS zone |
| Backup requirement | Config is Git-backed (sanitized). Token must be stored in secrets manager separately. |
| Validation command | `sudo systemctl status cloudflared` |
| Recovery procedure | [[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/procedures/cloudflare-tunnel-install]] |
| Automation classification | Ansible candidate |
| Preferred automation tool | Ansible |
