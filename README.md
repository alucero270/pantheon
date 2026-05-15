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
| Network | Firewall, switching, access points, VLANs, DNS, DHCP, ingress, and remote access | [[systems/network]] |
| Atlas | Unraid NAS and authoritative storage system | [[systems/atlas]] |
| Prometheus | Ubuntu compute, virtualization, containers, AI workloads | [[systems/prometheus]] |
| Ares | Daily workstation | Existing root README; Needs validation |
| Nomad | Mobile client | Existing root README; Needs validation |

## Documentation Map

| Area | Purpose |
|---|---|
| [[systems/README|Systems]] | Pantheon-wide architecture, security, and data ownership constraints. |
| [[decisions/README|Decisions]] | Architecture Decision Records and locked constraints. |
| [[systems/README|System Procedures]] | Cross-system SOPs, runbooks, validation checklists, recovery guides, and branch validation. |
| [[systems/README|Systems]] | Network, Atlas, Prometheus, and their local architecture, services, procedures, and devices. |
| [[TODO]] | Branch validation queue and remaining local validation work. |
| [[templates/README|Templates]] | Shared documentation templates. |
| Second brain docs | Needs validation; candidate files exist on `codex/deferred-local-changes`. |

## Current Status

Repository evidence currently documents:

- Network v1.0 as stable.
- Atlas as authoritative storage.
- Nextcloud as operational.
- Prometheus as disposable compute and AI/runtime host.
- Prometheus initialization as in progress.
- Nextcloud as user-facing service with authoritative data on Atlas.
- Reverse proxy and Tailscale-domain documentation from recent merged PRs.
- Remote access has mixed evidence: the original root README described VPN / external access as deferred, while [[systems/network/procedures/tailscale-remote-access]] documents a current Tailscale baseline. This needs validation before automation.
- Future automation as not yet implemented.

Items requiring validation are tracked in [[TODO]] and in the Pass 1 migration notes from this work.

## Automation Position

Pantheon is preparing for future documentation-driven automation. Automation is documentation/scaffold-only until explicitly approved.

The automation model is:

1. Markdown and wiki-linked documentation define intent.
2. [[automation/pantheonctl/README|pantheonctl]] validates docs and generates safe inputs.
3. Domain-owned automation lives under `systems/<domain>/automation/`.
4. Ansible configures safe host targets, beginning with Prometheus.
5. Pulumi C# is preferred for future API-backed infrastructure.
6. Terraform/OpenTofu is optional and deferred unless clearly justified.

Initial safe automation target:

- [[systems/prometheus|Prometheus]]

Protected areas:

- Network firewall, switch, DNS, DHCP, and remote access behavior
- Atlas authoritative storage configuration
- Secrets and live infrastructure state

Automation policy starts at [[automation/README]].

## Second Brain Workflow

Pantheon also acts as the starting Obsidian vault for a ChatGPT-connected second brain workflow.

- Architecture: Needs validation
- Setup procedure: Needs validation
- Local registry example: Needs validation
- ChatGPT operating prompt: Needs validation
- Capture templates: Needs validation

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
