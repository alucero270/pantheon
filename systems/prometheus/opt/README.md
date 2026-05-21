# /opt

## Purpose

This folder mirrors `/opt` on [[systems/prometheus]].

`/opt` is the Prometheus area for stack definitions, app-owned source trees, operator paths, and current service roots.

## Current Live Paths

| Live path | Documentation | Role |
|---|---|---|
| `/opt/traefik` | [[systems/prometheus/opt/stacks/ingress/traefik/README]] | Current Traefik stack and ingress config root |
| `/opt/vpn` | [[systems/prometheus/opt/stacks/media/vpn/README]] | Current media/VPN egress compose root |
| `/opt/homelable` | [[systems/prometheus/opt/stacks/homelable/README]] | Current Homelable source and compose root |
| `/opt/arr` | [[systems/prometheus/opt/arr/README]] | Current Arr service config parent |
| `/opt/torrents` | [[systems/prometheus/opt/torrents/README]] | qBittorrent config and download staging |
| `/opt/containerd` | [[systems/prometheus/opt/containerd/README]] | Containerd install-looking path; role requires validation |
| `/opt/media-staging` | [[systems/prometheus/opt/media-staging/README]] | Media staging path |

## Desired Normalized Path

`/opt/stacks` is the desired normalized home for Docker Compose stack definitions. It is documentation target state until live migration is approved and completed.
