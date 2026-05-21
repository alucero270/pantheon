# qBittorrent Config

## Purpose

This folder tracks sanitized qBittorrent config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/torrents/config` | qBittorrent app config | Sanitized notes only |
| `/opt/torrents/downloads` | Download staging | Do not commit |

## Status

No Git-backed sanitized config documented yet.

## Rules

- Do not commit credentials, cookies, private tracker data, torrent files, or downloads.
- Downloads remain Prometheus-local staging, not authoritative storage.
