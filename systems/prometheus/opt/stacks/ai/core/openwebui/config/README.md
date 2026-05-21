# OpenWebUI Config

## Purpose

This folder tracks sanitized OpenWebUI config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/ssd/ai/projects/openwebui` | OpenWebUI app state | Do not Git-track without sanitization |

## Status

No Git-backed sanitized config documented yet.

## Rules

- Do not commit user uploads, chats, prompts, API keys, tokens, or generated user data.
- Revisit backup posture if OpenWebUI becomes multi-user or production-facing.
