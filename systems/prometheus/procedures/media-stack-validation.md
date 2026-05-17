---
type: procedure
risk_level: low
last_tested: 2026-05-16
---

# Media Stack Validation

## Purpose

Validate the Prometheus media stack without deleting data, pruning Docker objects, changing VPN secrets, exposing new services, or deploying Jellyfin.

## Preconditions

- Access required: SSH to `alex@prometheus`
- Systems impacted: [[systems/prometheus]], [[systems/atlas]]
- Live compose path: `/opt/vpn/docker-compose.yml`
- Approved restart scope, if needed: Gluetun, qBittorrent, Prowlarr, Radarr, Sonarr only
- Test downloads must be legal/public test content only

## Steps

1. Confirm host identity.

```bash
hostname
```

Expected output:

```text
prometheus
```

2. Confirm the live media compose file exists.

```bash
test -f /opt/vpn/docker-compose.yml && echo "media compose present"
```

3. Validate the active containers and exposure.

```bash
docker ps --filter name=gluetun --filter name=qbittorrent --filter name=prowlarr --filter name=radarr --filter name=sonarr --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

Expected current-state exposure:

- qBittorrent WebUI: `127.0.0.1:8080:8080` through Gluetun
- Prowlarr: `0.0.0.0:9696`
- Radarr: `0.0.0.0:7878`
- Sonarr: `0.0.0.0:8989`

The Prowlarr/Radarr/Sonarr broad binds are temporary current state.

4. Validate mounts without printing secrets.

```bash
docker inspect gluetun qbittorrent prowlarr radarr sonarr --format '{{.Name}} {{range .Mounts}}{{.Source}}:{{.Destination}};{{end}}'
```

Expected media mounts:

- `/opt/vpn/gluetun:/gluetun`
- `/opt/torrents/config:/config`
- `/opt/torrents/downloads:/downloads`
- `/opt/arr/prowlarr:/config`
- `/opt/arr/radarr:/config`
- `/mnt/atlas/managed-media/movies:/movies`
- `/opt/arr/sonarr:/config`
- `/mnt/atlas/managed-media/tv:/tv`

5. Confirm Atlas NFS mounts.

```bash
findmnt -no SOURCE,TARGET,FSTYPE /mnt/atlas/managed-media /mnt/atlas/shared-media
```

Expected sources:

- `192.168.60.102:/mnt/user/managed-media`
- `192.168.60.102:/mnt/user/shared-media`

6. Confirm Atlas downloads is not an active export.

```bash
findmnt -no SOURCE,TARGET,FSTYPE /mnt/atlas/downloads || echo "no active /mnt/atlas/downloads mount"
```

Expected result:

- No active `/mnt/atlas/downloads` mount.

7. Confirm Radarr/Sonarr NFS write posture with UID/GID `1000:1000`.

```bash
sudo -u '#1000' test -w /mnt/atlas/managed-media/movies && echo "movies writable"
sudo -u '#1000' test -w /mnt/atlas/managed-media/tv && echo "tv writable"
```

Expected result:

- `movies writable`
- `tv writable`

8. Validate application settings in the UIs or APIs.

qBittorrent:

- Default save path: `/downloads`
- Category `radarr`: `/downloads/radarr`
- Category `sonarr`: `/downloads/sonarr`
- Category `mam`: `/downloads/mam`
- Category `manual`: `/downloads/manual`

Radarr:

- Root folder: `/movies`
- qBittorrent host: `gluetun`
- qBittorrent port: `8080`
- qBittorrent category: `radarr`

Sonarr:

- Root folder: `/tv`
- qBittorrent host: `gluetun`
- qBittorrent port: `8080`
- qBittorrent category: `sonarr`

Prowlarr:

- Radarr URL: `http://radarr:7878`
- Sonarr URL: `http://sonarr:8989`

9. If testing downloads, use legal/public test content only.

Expected result:

- qBittorrent stages downloads under `/downloads`.
- Radarr imports movies into `/movies`.
- Sonarr imports TV into `/tv`.
- No download path uses `/mnt/atlas/downloads`.

## Validation

- `docker ps` shows the five media stack containers running.
- qBittorrent remains localhost-only.
- Prowlarr/Radarr/Sonarr exposure is documented as temporary.
- Atlas managed/shared media mounts are active.
- `/mnt/atlas/downloads` is not active.
- `SKIP_CHOWN=true` is present for Radarr and Sonarr in the compose model before service restart.
- `/opt/vpn/.env` may be permission-protected from normal `alex` reads; do not loosen permissions just to run `docker compose config` unless secret handling is explicitly approved.
- Radarr/Sonarr root folders, qBittorrent clients, qBittorrent categories, and Prowlarr app links were validated on 2026-05-16.
- qBittorrent Web/API version `v5.1.4` was validated on 2026-05-16.
- Radarr and Sonarr qBittorrent download-client tests passed on 2026-05-16.
- Legal qBittorrent transport test was validated on 2026-05-16 using the official Debian `debian-13.4.0-amd64-netinst.iso` torrent. The test torrent downloaded to `/downloads/test` and was stopped, not deleted.
- Prowlarr LinuxTracker indexer was configured and validated on 2026-05-16 for legal Linux distribution searches. Internet Archive indexer setup timed out and remains `Needs validation`.
- End-to-end Radarr/Sonarr import testing is still `Needs validation`.

## Rollback

If an approved media-stack config edit fails:

1. Revert only the media-stack change in `/opt/vpn/docker-compose.yml`.
2. Restart only the approved affected service:

```bash
docker compose -f /opt/vpn/docker-compose.yml up -d gluetun qbittorrent prowlarr radarr sonarr
```

3. Re-run the validation steps above.

## Warnings

- Do not delete containers.
- Do not delete images.
- Do not delete volumes.
- Do not delete media data.
- Do not modify VPN secrets.
- Do not expose new WAN/public services.
- Do not deploy Jellyfin from this procedure.
- Unknown containers and volumes must be classified before cleanup.

## Automation Potential

- Can this be scripted? Yes, as read-only validation under `pantheonctl` or Ansible.
- If not, why? UI/API validation needs credential handling and secret policy before automation.

## Related Docs

- Systems: [[systems/prometheus]], [[systems/atlas]]
- Services:
  - [[systems/prometheus/services/gluetun]]
  - [[systems/prometheus/services/qbittorrent]]
  - [[systems/prometheus/services/prowlarr]]
  - [[systems/prometheus/services/radarr]]
  - [[systems/prometheus/services/sonarr]]
  - [[systems/prometheus/services/jellyfin]]
- Architecture: [[architecture/media-architecture]]
