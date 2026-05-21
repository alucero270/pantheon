# SearXNG Config

## Purpose

This folder tracks sanitized SearXNG config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/ssd/ai/services/searxng/searxng/settings.yml` | SearXNG settings | Sanitized Git candidate |
| `/mnt/local/ssd/ai/services/searxng/.env` | Local env and secrets | Do not commit |

## Status

No Git-backed sanitized SearXNG config has been committed here yet.

## Snapshot Pattern

```bash
cp /mnt/local/ssd/ai/services/searxng/searxng/settings.yml \
  /mnt/local/ssd/ai/services/searxng/searxng/settings.yml.$(date +%F-%H%M%S).bak
```

## Related Procedure

- [[systems/prometheus/opt/stacks/ai/searxng/procedures/searxng-openwebui-integration]]

## Rules

- Do not commit `.env` or `server.secret_key`.
- Sanitize settings before adding examples to Git.
