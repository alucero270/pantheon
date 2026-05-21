# /opt/stacks/media/vpn

## Purpose

This folder documents the media VPN/egress stack currently deployed from `/opt/vpn/docker-compose.yml`.

| Field | Value |
|---|---|
| Current live path | `/opt/vpn` |
| Current compose file | `/opt/vpn/docker-compose.yml` |
| Desired normalized path | `/opt/stacks/media/vpn` |
| Status | Active live stack; desired path is not yet implemented |

## Services

- [[systems/prometheus/opt/stacks/media/vpn/gluetun/gluetun]]
- [[systems/prometheus/opt/stacks/media/vpn/qbittorrent/qbittorrent]]
- [[systems/prometheus/opt/stacks/media/vpn/prowlarr/prowlarr]]
- [[systems/prometheus/opt/stacks/media/vpn/radarr/radarr]]
- [[systems/prometheus/opt/stacks/media/vpn/sonarr/sonarr]]

## Stack Procedures

- [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]]
