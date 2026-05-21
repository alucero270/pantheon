# Gluetun Config

## Purpose

This folder tracks sanitized Gluetun config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/vpn/gluetun` | Gluetun runtime config | Sanitized notes only |
| `/opt/vpn/.env` | VPN credentials and stack env | Do not commit |

## Status

No Git-backed sanitized config documented yet.

## Rules

- Do not commit VPN credentials, keys, tokens, or provider secrets.
- Preserve qBittorrent's VPN network boundary.
