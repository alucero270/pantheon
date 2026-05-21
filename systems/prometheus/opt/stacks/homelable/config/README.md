# Homelable Config

## Purpose

This folder tracks sanitized Homelable config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/opt/homelable/.env` | Runtime env and secrets | Do not commit |
| `/opt/homelable/.env.example` | Sanitized env example | Git candidate |
| Docker volume `homelable_backend_data` | Backend app data | Needs validation before backup stance |

## Status

No Git-backed sanitized Homelable config has been committed here yet.

## Rules

- Do not commit default secrets, runtime credentials, tokens, or database dumps.
- Rotate default secrets before treating recovery docs as complete.
