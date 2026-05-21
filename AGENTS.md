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

# Live Infrastructure Exception Protocol

Pantheon is documentation-first, but some troubleshooting and configuration work may require touching live infrastructure. Live changes are allowed only when the user explicitly asks for live work in the current task.

When live infrastructure work is explicitly approved:

- Confirm the owning system, service, live host path, tracking issue, and expected success criteria before changing anything.
- Read the relevant service doc, `config/README.md`, procedure folder, architecture docs, and tracking issue before the first live command.
- Capture read-only current state first: service status, active config path, relevant logs, exposed ports, mounted paths, and current Git status.
- Create a timestamped rollback snapshot beside any live config before editing it.
- Never move secrets, private keys, tokens, transcripts, recordings, private voice samples, generated user data, or host-only sensitive values into Git.
- Make one live change at a time. Validate it before making the next change.
- Update the owning service doc, `config/README.md`, procedure, or tracking issue at each meaningful step with:
  - command or file changed
  - host path
  - reason for the change
  - validation result
  - rollback path
  - remaining `Needs validation` items
- Do not stack multiple patches, service restarts, config rewrites, or dependency changes without a documentation checkpoint.
- Stop immediately if the observed state diverges from the documented plan in a way that could weaken security, break rollback, or risk authoritative data.
- At a stopping point, leave a clean handoff: Git status, live service status, validation result, rollback snapshot name, updated docs/issues, and next safe action.

## Git Checkpoints for Live Work

Git should be used as the safety rail for documented state, not as a dumping ground for live secrets or machine-local residue.

- Commit or open a PR only when the user asks, or when the task explicitly includes publishing the live-work checkpoint.
- Before any commit or PR, ensure the repo contains only sanitized docs, sanitized config examples, procedures, and validation notes.
- Keep live rollback snapshots on the host unless a sanitized version is intentionally promoted to Git.
- Prefer small commits at completed experiments or safe stopping points: one coherent config/procedure change plus its validation notes.
- Do not commit partially validated live changes as final state. Use `Needs validation` and link the tracking issue.

---

# Investigation Hygiene and Cleanup

Pantheon troubleshooting should leave a usable trail, not an archaeological dig.

- Do not create loose temporary scripts, benchmark files, logs, patches, or generated artifacts at the repository root.
- Put exploratory artifacts under a clearly named folder near the owning system, such as `systems/<system>/procedures/<topic>-artifacts/`, or under an existing test/validation folder when one exists.
- Name investigation files for the question being tested, not for the tool that created them. Prefer names like `tts-latency-profile.py` over `tmp_patch3.py`.
- Before starting a new troubleshooting direction, write down the current hypothesis, command or script, observed result, and next decision in the relevant procedure, runbook, or issue.
- Keep one reusable validation script when possible. Remove or consolidate superseded scratch scripts before handing work back.
- If root-level scratch files are discovered, stop and classify them before continuing: preserve useful evidence in the owning system folder, summarize findings in docs or the tracking issue, and remove only files that are clearly disposable and not user-authored.
- Do not mark a service as deployed or validated because a component test passed. Use `Needs validation` until the documented end-to-end success criteria are met.
- For latency or performance work, record baseline numbers, changed variables, and before/after measurements. Do not stack multiple patches without a checkpoint.
- If live-host changes were made during troubleshooting, document the exact host path, process or service name, command used, rollback path, and validation status.
- End each investigation with a cleanup pass: `git status --short`, root artifact check, doc consistency check, and a short summary of what is known, unknown, and next.

---

# Routing Table

| Task | Go to | Read First | Template Source | Notes |
|---|---|---|---|---|
| Change cross-domain architecture, data strategy, or security model | owning domain `systems/<domain>/architecture/` and/or `/decisions` | `[[systems/README]]`, `[[REFERENCES]]`, relevant domain architecture doc, relevant ADRs | folder-local template, then `/templates` fallback | Pantheon does not use a root `/architecture` folder. Cross-domain rules should be captured as ADRs when they lock constraints. |
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
