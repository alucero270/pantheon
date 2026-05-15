# References

## Repository Navigation

- [[README]] - root project overview.
- [[AGENTS]] - agent operating guide and routing table.
- [[procedures/branch-validation]] - branch validation queue.

## Architecture

- [[architecture/overview]]
- [[architecture/network-architecture]]
- [[architecture/vlan-design]]
- [[architecture/security-model]]
- [[architecture/data-strategy]]
- [[architecture/dns-plan]]
- [[architecture/network-Ingress-Flow]]
- [[architecture/media-architecture]]
- [[architecture/second-brain-chatgpt-obsidian]]

## Systems

- [[systems/cerberus-opensense]]
- [[systems/axon-cisco-sg350]]
- [[systems/atlas-unraid]]
- [[systems/prometheus-ubuntu]]
- [[systems/access-points]]
- [[systems/prometheus-services-inventory]]

## Services

Root `services/` is transitional during migration. System-owned service docs should move under `systems/<system>/services/` during Pass 2 after validation.

- [[services/ai]]
- [[services/comfyui]]
- [[services/databases]]
- [[services/media-architecture]]
- [[services/next-cloud-reverse-proxy]]
- [[services/nextcloud]]
- [[services/ollama]]
- [[services/openwebui]]
- [[services/redis]]
- [[services/reverse-proxy]]
- [[services/reverse_proxy_validation]]
- [[services/tailscale_remote_access_architecture]]

## Procedures

- [[procedures/atlas-recovery]]
- [[procedures/atlas-share-audit]]
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

## Decisions

- [[decisions/ADR-001-zero-trust-lite]]
- [[decisions/ADR-002-atlas-as-storage]]
- [[decisions/ADR-003-disposable-compute-prometheus]]
- [[decisions/ADR-004-nextcloud-migration]]
- [[decisions/ADR-005-atlas-share-storage-model]]
- [[decisions/ADR-006-comfyui-storage-constraints]]
- [[decisions/ADR-007-centralized-ingress-on-prometheus]]
- `decisions/ADR-008 — AI Runtime Network Segmentation.md` - Needs validation before link normalization.
- `decisions/ADR-009 — Docker DNS Resolution Strategy.md` - Needs validation before link normalization.

## Templates And Tooling

- [[templates/README]]
- `.obsidian/templates.json`
- `.github/ISSUE_TEMPLATE/custom.md`
