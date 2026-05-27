# Cloudflare Tunnel Config

## Purpose

This folder holds sanitized reference copies of the cloudflared and Traefik configs for the public tunnel.

Do not store tunnel tokens, API tokens, or credentials JSON here.

## Live Config Paths on Prometheus

| Live path | Purpose | Git posture |
|---|---|---|
| `/etc/cloudflared/config.yml` | Tunnel ingress rules | Sanitized Git candidate (no secrets) |
| `/opt/traefik/dynamic/loosearrow-public.yml` | Traefik public hostname routers | Sanitized Git candidate |

## /etc/cloudflared/config.yml

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

The tunnel token is injected at service install time via `cloudflared service install <token>` and stored in the systemd unit file. It is not in this config file.

## /opt/traefik/dynamic/loosearrow-public.yml

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

## Rules

- Do not commit the tunnel token (lives in the systemd unit file on prometheus)
- Do not commit API tokens or credentials JSON
- When adding a new public route, update both files above and this README
