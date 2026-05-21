# Portainer Config

## Purpose

This folder tracks sanitized Portainer config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/ssd/services/portainer/data` | Portainer app state | Do not Git-track |

## Status

No Git-backed sanitized config documented yet.

Validation is tracked by issue #112.

## Rules

- Do not commit Portainer databases, credentials, tokens, or Docker access material.
