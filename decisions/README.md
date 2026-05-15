# Decisions

## Purpose

This folder contains Architecture Decision Records for Pantheon.

ADRs capture locked or important design decisions, the context for those decisions, and the conditions under which they may be revisited.

## Current Decisions

- [[decisions/ADR-001-zero-trust-lite]]
- [[decisions/ADR-002-atlas-as-storage]]
- [[decisions/ADR-003-disposable-compute-prometheus]]
- [[decisions/ADR-004-nextcloud-migration]]
- [[decisions/ADR-005-atlas-share-storage-model]]
- [[decisions/ADR-006-comfyui-storage-constraints]]
- [[decisions/ADR-007-centralized-ingress-on-prometheus]]
- `ADR-008 — AI Runtime Network Segmentation.md` - Needs validation before link normalization.
- `ADR-009 — Docker DNS Resolution Strategy.md` - Needs validation before link normalization.

## Templates

- Shared ADR template: [[templates/adr]]

## Rules

- Do not change ADR status without approval.
- Do not rewrite locked decisions during documentation normalization.
- If an architecture change affects VLANs, storage authority, management access, ingress, or security boundaries, create or update an ADR only with approval.

## Needs Validation

- ADR filenames with spaces and dash punctuation should be reviewed for kebab-case normalization during Pass 2.
- ADR-008 and ADR-009 candidate files exist on `codex/deferred-local-changes` and require validation before adoption.
