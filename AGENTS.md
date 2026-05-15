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
| Change architecture, VLANs, data strategy, security model, ingress, DNS, or remote access | `/architecture` | `[[architecture/README]]`, `[[architecture/REFERENCES]]`, relevant architecture doc | folder-local template, then `/templates` fallback | Architecture changes may require an ADR. |
| Record or update a locked decision | `/decisions` | `[[decisions/README]]`, `[[decisions/REFERENCES]]`, existing ADRs | folder-local ADR template | Do not change ADR status without approval. |
| Write a cross-system SOP, runbook, validation checklist, or recovery guide | `/procedures` | `[[procedures/README]]`, `[[procedures/REFERENCES]]` | folder-local procedure template | Procedures must be executable and testable. |
| Document a host, switch, firewall, NAS, workstation, or infrastructure device | `/systems/<system>` | `[[systems/README]]`, `[[systems/REFERENCES]]` | folder-local system template | Keep system responsibilities explicit. |
| Document a system-owned service | `/systems/<system>/services` | system README, system REFERENCES, service folder README | folder-local service template | Include hosting, ports, data paths, dependencies, backup posture, and validation. |
| Document a system-specific procedure | `/systems/<system>/procedures` | system README, system REFERENCES, procedure folder README | procedure template | Keep host-specific operations near the owning system. |
| Create or update shared templates | `/templates` | `[[templates/README]]`, `[[templates/REFERENCES]]`, `.obsidian/templates.json` | existing shared templates | Do not invent templates without approval. |
| Normalize wiki links | relevant folder | AGENTS.md, folder README, folder REFERENCES | existing docs | Use `[[folder/doc]]` links without `.md`. |
| Inventory branches for later validation | `/procedures` | `[[procedures/README]]`, `[[procedures/REFERENCES]]` | procedure template | Do not merge branches. Create/update `[[procedures/branch-validation]]`. |
| Prepare Ansible automation | `/automation/ansible` | `[[automation/README]]`, `[[automation/ansible/README]]` | automation template if present | Documentation and scaffolding only unless explicitly instructed. |
| Prepare Terraform automation | `/automation/terraform` | `[[automation/README]]`, `[[automation/terraform/README]]` | automation template if present | Do not create live state or apply infrastructure changes. |
