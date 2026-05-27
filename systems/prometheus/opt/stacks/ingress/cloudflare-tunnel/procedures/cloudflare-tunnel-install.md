# Procedure — Install Cloudflare Tunnel on Prometheus

This document is the authoritative runbook for installing and configuring the Cloudflare Tunnel (`cloudflared`) on Prometheus from scratch.

Assumptions:

- Prometheus is running Ubuntu Server
- Traefik is already installed and running at `/opt/traefik`
- You have a Cloudflare account with `loosearrowlabs.com` as a managed zone
- You are logged into prometheus as `alex` with sudo access

---

## Phase 1 — Install cloudflared

```bash
curl -L --output /tmp/cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i /tmp/cloudflared.deb
cloudflared --version
```

---

## Phase 2 — Create a Cloudflare API Token

1. Go to [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click **Create Token** → **Create Custom Token**
3. Configure:
   - Name: `prometheus-tunnel`
   - Permissions: **Account** → **Cloudflare Tunnel** → **Edit**
   - Permissions: **Zone** → **DNS** → **Edit**
   - Account Resources: your account
   - Zone Resources: `loosearrowlabs.com`
4. Create and copy the token — it is only shown once

---

## Phase 3 — Create the Tunnel via API

Replace `<API_TOKEN>` with your token. Run from any machine with curl/PowerShell.

Get your account and zone IDs:

```bash
# Get zone + account ID
curl -s -H "Authorization: Bearer <API_TOKEN>" \
  "https://api.cloudflare.com/client/v4/zones?name=loosearrowlabs.com" \
  | python3 -m json.tool | grep -E '"id"|"name"'
```

Create the tunnel (replace `<ACCOUNT_ID>`):

```bash
curl -s -X POST \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  --data '{"name":"prometheus","tunnel_secret":"<32-byte-base64-secret>"}' \
  "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/cfd_tunnel"
```

Note the `id` field in the response — this is your **tunnel ID**.

Get the tunnel token (replace `<ACCOUNT_ID>` and `<TUNNEL_ID>`):

```bash
curl -s -H "Authorization: Bearer <API_TOKEN>" \
  "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/cfd_tunnel/<TUNNEL_ID>/token"
```

Note the token from `result` — this is your **tunnel token**.

---

## Phase 4 — Write Config and Install Service

On prometheus, create the config directory and write the ingress config:

```bash
sudo mkdir -p /etc/cloudflared
```

Write `/etc/cloudflared/config.yml`:

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

Install as a systemd service with the tunnel token:

```bash
sudo cloudflared service install <TUNNEL_TOKEN>
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

The service is set to start automatically on boot (`enabled` by default after install).

---

## Phase 5 — Create DNS Records

For each public hostname, create a Cloudflare-proxied CNAME pointing to the tunnel:

```bash
# Target: <TUNNEL_ID>.cfargotunnel.com
# Zone ID: 78f191635403160f16b6bd4c7237bde3

for sub in chat comfy search app; do
  curl -s -X POST \
    -H "Authorization: Bearer <API_TOKEN>" \
    -H "Content-Type: application/json" \
    --data "{\"type\":\"CNAME\",\"name\":\"$sub\",\"content\":\"<TUNNEL_ID>.cfargotunnel.com\",\"proxied\":true}" \
    "https://api.cloudflare.com/client/v4/zones/78f191635403160f16b6bd4c7237bde3/dns_records"
done
```

---

## Phase 6 — Add Traefik Dynamic Config

Write `/opt/traefik/dynamic/loosearrow-public.yml`:

```yaml
http:
  routers:
    chat-public:
      rule: 'Host(`chat.loosearrowlabs.com`)'
      entryPoints:
        - websecure
      service: openwebui-public
      tls: {}

    search-public:
      rule: 'Host(`search.loosearrowlabs.com`)'
      entryPoints:
        - websecure
      service: searxng-public
      tls: {}

    comfy-public:
      rule: 'Host(`comfy.loosearrowlabs.com`)'
      entryPoints:
        - websecure
      service: comfyui-public
      tls: {}

  services:
    openwebui-public:
      loadBalancer:
        servers:
          - url: "http://openwebui:8080"

    searxng-public:
      loadBalancer:
        servers:
          - url: "http://searxng:8080"

    comfyui-public:
      loadBalancer:
        servers:
          - url: "http://comfyui:8188"
```

Traefik picks up the file automatically via its file provider watcher. Verify no errors appear in `docker logs traefik`.

---

## Phase 7 — Configure Cloudflare Access (REQUIRED)

Without this step, all public hostnames are reachable by anyone on the internet.

For each subdomain:

1. Go to **Cloudflare Zero Trust → Access → Applications**
2. Click **Add an Application → Self-hosted**
3. Set:
   - Application name: e.g., `Open WebUI`
   - Application domain: e.g., `chat.loosearrowlabs.com`
4. Under **Policies**, add a policy:
   - Policy name: `Owner only`
   - Action: **Allow**
   - Include rule: **Emails** → `A.lucero2892@gmail.com`
5. Save

Repeat for each subdomain.

---

## Phase 8 — Validation

Run the validation checklist:

[[systems/prometheus/opt/stacks/ingress/cloudflare-tunnel/procedures/cloudflare-tunnel-validation]]

---

## Recovery Notes

If the tunnel goes down:

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -n 50
```

If the tunnel token is lost, get a new one from the Cloudflare API (Phase 3) and reinstall the service:

```bash
sudo cloudflared service uninstall
sudo cloudflared service install <NEW_TOKEN>
sudo systemctl start cloudflared
```

If the tunnel needs to be deleted and recreated, delete it in Zero Trust → Networks → Tunnels and repeat from Phase 3.
