# Radarr Config

## Purpose

This folder tracks sanitized Radarr config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/arr/radarr` | Radarr config and database state | Sanitized notes only |
| `/mnt/atlas/managed-media/movies` | Final movie library | Atlas authoritative, not Git |

## Status

No Git-backed sanitized config documented yet.

## Rules

- Do not commit API keys, indexer credentials, cookies, database dumps, or media files.
- Atlas movie library is authoritative storage, not Prometheus config.
