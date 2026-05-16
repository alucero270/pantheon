# Shared Terraform / OpenTofu Modules

## Purpose

This folder contains optional Terraform/OpenTofu module scaffolding for Pantheon.

Terraform/OpenTofu is not the default automation tool. It is reserved for cases where provider coverage, module reuse, or state workflow makes it a better fit than Pulumi C#.

## Initial Scope

No production infrastructure is managed from this folder yet.

Potential future use cases:

- provider-specific resources not well covered by Pulumi
- external DNS
- cloud resources
- experimental IaC comparisons

## State Policy

Do not commit state files.

Do not create production state during scaffolding.

State backend selection is marked `Needs decision`.

## Out of Scope

Do not automate yet:

- network firewall rules
- switch configuration
- Atlas storage configuration
- production infrastructure without approved backend and rollback strategy

## Related Docs

- [[automation/README|Automation]]
- [[automation/pantheonctl/README|pantheonctl]]
- [[automation/shared/pulumi/README|Shared Pulumi]]
