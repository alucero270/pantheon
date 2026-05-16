# Automation

## Purpose

This folder contains repo-wide automation tooling, shared automation assets, and automation safety policies for Pantheon.

Domain-specific automation belongs under the owning domain in `systems/<domain>/automation/`.

## Automation Model

Pantheon uses a layered automation model:

| Layer | Tool | Purpose |
|---|---|---|
| Documentation source of truth | Markdown / wiki links | Defines intended state and constraints |
| Control plane helper | [[automation/pantheonctl/README|pantheonctl]] | Validates docs, generates inventory, checks links, coordinates safe workflows |
| Domain-owned automation | [[systems/prometheus/automation/README|system automation]] | Stores automation that affects a specific domain |
| Shared Ansible assets | [[automation/shared/ansible/README|Shared Ansible]] | Reusable Ansible roles and collections |
| Shared Pulumi assets | [[automation/shared/pulumi/README|Shared Pulumi]] | Reusable Pulumi C# components |
| Shared Terraform/OpenTofu assets | [[automation/shared/terraform/README|Shared Terraform/OpenTofu]] | Optional reusable Terraform/OpenTofu modules |
| Automation policies | [[automation/policies/README|Automation Policies]] | Secrets, state, classification, and safety boundaries |

## Initial Safe Target

Automation begins with low-risk, rebuildable systems.

Initial safe target:

- [[systems/prometheus|Prometheus]]

High-risk domains remain manual or guardrail-only until validated:

- [[systems/network|Network]]
- [[systems/atlas|Atlas]] storage configuration

## Rules

- Do not automate what is not documented.
- Do not automate what cannot be validated.
- Do not automate what cannot be rolled back.
- Do not store secrets in Git.
- Do not store Terraform/OpenTofu state in Git.
- Do not use automation to bypass architecture decisions.
- Do not hide infrastructure changes behind custom C# commands.
- Prefer read-only validation before mutation.

## Related Docs

- [[systems/network/architecture]]
- [[systems/atlas/architecture]]
- [[systems/prometheus/architecture]]
- [[systems/prometheus/automation/README|Prometheus Automation]]
- [[automation/policies/automation-classification]]
