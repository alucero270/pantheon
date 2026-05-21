# Sonarr Config

## Purpose

This folder tracks sanitized Sonarr config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/arr/sonarr` | Sonarr config and database state | Sanitized notes only |
| `/mnt/atlas/managed-media/tv` | Final TV library | Atlas authoritative, not Git |

## Status

No Git-backed sanitized config documented yet.

## Rules

- Do not commit API keys, indexer credentials, cookies, database dumps, or media files.
- Atlas TV library is authoritative storage, not Prometheus config.
