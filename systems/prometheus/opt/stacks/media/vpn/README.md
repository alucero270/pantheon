# /opt/stacks/media/vpn

## Purpose

This folder documents the media VPN/egress stack.

| Field | Value |
|---|---|
| Current live path | `/opt/stacks/media/vpn` |
| Current compose file | `/opt/stacks/media/vpn/compose.yml` |
| Legacy compatibility path | `/opt/vpn/docker-compose.yml` symlink |
| Runtime/config paths | `/opt/vpn`, `/opt/torrents`, `/opt/arr`, `/mnt/atlas/managed-media` |
| Status | Active live stack; normalized on 2026-05-21 |

## Services

- [[systems/prometheus/opt/stacks/media/vpn/gluetun/gluetun]]
- [[systems/prometheus/opt/stacks/media/vpn/qbittorrent/qbittorrent]]
- [[systems/prometheus/opt/stacks/media/vpn/prowlarr/prowlarr]]
- [[systems/prometheus/opt/stacks/media/vpn/radarr/radarr]]
- [[systems/prometheus/opt/stacks/media/vpn/sonarr/sonarr]]

## Stack Procedures

- [[systems/prometheus/opt/stacks/media/vpn/procedures/media-stack-validation]]
- [[systems/prometheus/opt/stacks/procedures/stack-source-normalization-2026-05-21]]
