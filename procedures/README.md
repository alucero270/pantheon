# Procedures

## Purpose

This folder contains cross-system procedures, runbooks, validation checklists, recovery guides, and operational workflows for Pantheon.

Procedures must be executable, testable, and clear about risk.

## Current Procedures

- [[procedures/atlas-recovery]]
- [[procedures/atlas-share-audit]]
- [[procedures/branch-validation]]
- [[procedures/chatgpt-obsidian-mcp-setup]]
- [[procedures/network-rebuild]]
- [[procedures/nextcloud-deployment]]
- [[procedures/nextcloud-ext-storage-validation]]
- [[procedures/nextcloud-external-storage]]
- [[procedures/nextcloud-migration]]
- [[procedures/prometheus-ai-stack-initialization]]
- [[procedures/prometheus-reverse-proxy]]
- [[procedures/prometheus_ollama_model_management_procedure]]
- [[procedures/rebuild-network]]

## Templates

- Folder-local template: [[procedures/procedures-template]]
- Shared fallback templates: [[templates/README]]

## Rules

- Include prerequisites, commands, expected results, validation, and rollback or recovery notes.
- Do not include destructive commands without warnings.
- Do not assume live state without evidence.
- Do not mix architecture decisions into procedure steps.

## Needs Validation

- `prometheus_ollama_model_management_procedure.md` should be reviewed for kebab-case normalization.
- Links to `prometheus-ai-stack-bringup` need validation against existing procedure names.
