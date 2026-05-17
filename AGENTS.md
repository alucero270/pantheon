# AGENTS.md

# Identity

You are helping document and maintain Pantheon: a self-hosted homelab infrastructure and services repository focused on reproducibility, security, clarity, operational recovery, and future automation.

Pantheon documents architecture, systems, services, SOPs, runbooks, templates, references, automation readiness, and architecture decisions for a segmented home network.

The goal is not experimentation for its own sake. The goal is a documented, rebuildable, secure infrastructure.

---

# Operating Principles

- Use repository evidence only.
- Preserve existing constraints.
- Preserve existing terminology unless clearly inconsistent.
- Use Obsidian wiki links for internal documentation references.
- Prefer folder-local templates when present.
- Do not convert future plans into implemented facts.
- Use `TBD`, `Unknown`, or `Needs validation` instead of guessing.
- When adding or discovering a new `Needs validation` item, create or update a GitHub issue that tracks the validation work, unless an existing issue already clearly covers it.
- Do not delete content.
- Do not weaken security constraints.
- Do not modify locked decisions without approval.
- Do not merge branches during documentation normalization.
- Do not modify live infrastructure.
- Keep documentation useful to both humans and agents.

---

# Routing Table

| Task | Go to | Read First | Template Source | Notes |
|---|---|---|---|---|
| Change Pantheon-wide architecture, data strategy, or security model | `/architecture` | `[[systems/README]]`, `[[REFERENCES]]`, relevant architecture doc | folder-local template, then `/templates` fallback | Architecture changes may require an ADR. |
| Change network architecture, VLANs, ingress, DNS, DHCP, firewall model, switch model, or remote access | `/systems/network/architecture` | `[[systems/network]]`, `[[systems/network/REFERENCES]]`, relevant network architecture doc | folder-local template, then `/templates` fallback | Network changes may require an ADR and must not weaken management boundaries. |
| Record or update a locked decision | `/decisions` | `[[decisions/README]]`, `[[decisions/REFERENCES]]`, existing ADRs | folder-local ADR template | Do not change ADR status without approval. |
| Write a system SOP, runbook, validation checklist, or recovery guide | owning system procedure folder | `[[systems/README]]`, owning system README, owning system REFERENCES | folder-local procedure template | Procedures must be executable and testable. |
| Document a system domain such as Network, Atlas, or Prometheus | `/systems/<system>` | `[[systems/README]]`, `[[systems/REFERENCES]]` | folder-local system template | Keep system responsibilities explicit. |
| Document a network device such as Cerberus, Axon, or access points | `/systems/network/devices` | `[[systems/network]]`, `[[systems/network/devices/README]]` | folder-local system template | Keep device responsibilities subordinate to the Network system. |
| Document a system-owned service | `/systems/<system>/services` | system README, system REFERENCES, service folder README | folder-local service template | Include hosting, ports, data paths, dependencies, backup posture, and validation. |
| Document a system-specific procedure | `/systems/<system>/procedures` | system README, system REFERENCES, procedure folder README | procedure template | Keep host-specific operations near the owning system. |
| Create or update shared templates | `/templates` | `[[templates/README]]`, `[[templates/REFERENCES]]`, `.obsidian/templates.json` | existing shared templates | Do not invent templates without approval. |
| Normalize wiki links | relevant folder | AGENTS.md, folder README, folder REFERENCES | existing docs | Use Obsidian wiki links without `.md` when the target exists. |
| Inventory branches for later validation | `/TODO.md` | `[[TODO]]`, `[[REFERENCES]]` | procedure template | Do not merge branches. Keep the branch validation queue current. |
| Prepare repo-wide automation validation or orchestration | `/automation/pantheonctl` | `[[automation/README]]`, `[[automation/pantheonctl/README]]`, `[[automation/policies/README]]` | existing automation docs | `pantheonctl` starts read-only / generate-only. Do not implement mutating commands without approval. |
| Prepare shared Ansible roles or collections | `/automation/shared/ansible` | `[[automation/shared/ansible/README]]`, `[[automation/policies/README]]` | automation docs | Shared assets only. Domain playbooks stay under the owning system. |
| Prepare Prometheus Ansible automation | `/systems/prometheus/automation/ansible` | `[[systems/prometheus/automation/ansible/README]]`, `[[systems/prometheus]]` | automation docs | Documentation and scaffolding only unless explicitly instructed. Do not run Ansible without approval. |
| Prepare Pulumi automation | relevant domain or `/automation/shared/pulumi` | `[[automation/shared/pulumi/README]]`, domain automation README | automation docs | Pulumi C# is for future API-backed resources. Do not run `pulumi up`. |
| Prepare Terraform/OpenTofu automation | `/automation/shared/terraform` or justified domain folder | `[[automation/shared/terraform/README]]`, `[[automation/policies/state-policy]]` | automation docs | Optional fallback only. Do not create production state or run apply. |
