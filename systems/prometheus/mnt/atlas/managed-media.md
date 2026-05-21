# /mnt/atlas/managed-media

## Purpose

Prometheus mount for Atlas-managed media.

| Field | Value |
|---|---|
| Current live mount | `/mnt/atlas/managed-media` |
| Source | `192.168.60.102:/mnt/user/managed-media` |
| Filesystem | NFSv4 |
| Authority | Authoritative on Atlas |

## Known Children

- `/mnt/atlas/managed-media/movies`
- `/mnt/atlas/managed-media/tv`
- `/mnt/atlas/managed-media/music`
- `/mnt/atlas/managed-media/video`

## Related Services

- [[systems/prometheus/opt/stacks/media/vpn/radarr/radarr]]
- [[systems/prometheus/opt/stacks/media/vpn/sonarr/sonarr]]
