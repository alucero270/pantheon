# Pantheon

Pantheon documents a self-hosted homelab infrastructure and services repository focused on reproducibility, security, clarity, operational recovery, and future automation.

The repository describes a segmented home network built around centralized storage, dedicated compute, explicit security boundaries, rebuild procedures, and architecture decisions. The goal is not experimentation for its own sake. The goal is documented, rebuildable, secure infrastructure.

## Core Principles

- Network security, storage, and compute are separated.
- VLAN boundaries are explicit and enforced by Cerberus.
- Atlas is the authoritative storage system.
- Prometheus is disposable compute.
- Infrastructure management is restricted to management paths.
- Changes that alter architecture require a decision record.
- Future automation must follow documented system ownership boundaries.

## Core Systems

| System | Role | Evidence |
|---|---|---|
| Cerberus | OPNsense firewall, router, DNS, DHCP, inter-VLAN enforcement | [[systems/cerberus-opensense]] |
| Axon | Cisco SG350 Layer-2 core switch | [[systems/axon-cisco-sg350]] |
| Atlas | Unraid NAS and authoritative storage system | [[systems/atlas-unraid]] |
| Prometheus | Ubuntu compute, virtualization, containers, AI workloads | [[systems/prometheus-ubuntu]] |
| Access points | Wireless VLAN access | [[systems/access-points]] |
| Ares | Daily workstation | Existing root README; Needs validation |
| Nomad | Mobile client | Existing root README; Needs validation |

## Documentation Map

| Area | Purpose |
|---|---|
| [[architecture/README|Architecture]] | Cross-system architecture, security, VLANs, data ownership, ingress, DNS, and remote access design. |
| [[decisions/README|Decisions]] | Architecture Decision Records and locked constraints. |
| [[procedures/README|Procedures]] | Cross-system SOPs, runbooks, validation checklists, recovery guides, and branch validation. |
| [[systems/README|Systems]] | Infrastructure hosts, network devices, storage systems, compute nodes, and access devices. |
| `services/` | Transitional service documentation. System-owned service docs should move under owning systems in Pass 2. |
| [[templates/README|Templates]] | Shared and folder-local documentation templates. |
| `second-brain/` | Obsidian and ChatGPT-connected second brain support files. |

## Current Status

Repository evidence currently documents:

- Network v1.0 as stable.
- Atlas as authoritative storage.
- Nextcloud as operational.
- Prometheus as disposable compute and AI/runtime host.
- Prometheus initialization as in progress.
- Nextcloud as user-facing service with authoritative data on Atlas.
- Reverse proxy and Tailscale-domain documentation from recent merged PRs.
- VPN / external access as deferred in the existing root README.
- Future automation as not yet implemented.

Items requiring validation are tracked in [[procedures/branch-validation]] and in the Pass 1 migration notes from this work.

## Automation Position

Pantheon is preparing for future Ansible and Terraform/OpenTofu automation. Automation is documentation/scaffold-only until explicitly approved.

Initial safe automation target:

- [[systems/prometheus-ubuntu|Prometheus]]

Protected areas:

- Cerberus firewall behavior
- Axon switch configuration
- Atlas authoritative storage configuration
- Secrets and live infrastructure state

## Second Brain Workflow

Pantheon also acts as the starting Obsidian vault for a ChatGPT-connected second brain workflow.

- Architecture: [[architecture/second-brain-chatgpt-obsidian]]
- Setup procedure: [[procedures/chatgpt-obsidian-mcp-setup]]
- Local registry example: `second-brain/vaults.example.json`
- ChatGPT operating prompt: `second-brain/system-prompt.md`
- Capture templates: `templates/second-brain-capture.md`, `templates/second-brain-synthesis.md`, `templates/second-brain-source.md`

The workflow starts with Pantheon as the authoritative infrastructure vault and attaches other vaults through an allowlisted MCP vault registry.

## Operating Notes

- Use repository evidence only.
- Use `TBD`, `Unknown`, or `Needs validation` where evidence is missing.
- Use Obsidian wiki links for internal documentation references.
- Do not merge or delete branches during documentation normalization.
- Do not modify live infrastructure from this repository.

See [[AGENTS]] for the agent operating guide.

## License

Internal / personal use. Documentation may be reused with attribution.
