# Shared Pulumi Components

## Purpose

This folder contains shared Pulumi C# components for Pantheon API-backed infrastructure.

Pulumi is the preferred C# IaC option for resources with reliable providers, meaningful previews, and safe rollback paths.

## Initial Scope

Candidate future resources:

- Tailscale configuration
- external DNS
- Cloudflare DNS / tunnels, if adopted
- cloud resources, if Pantheon expands into cloud infrastructure

## Out of Scope

Do not automate yet:

- firewall rules
- switch configuration
- Atlas storage
- any resource without a proven backup and rollback path

## Rules

- Do not run `pulumi up` without explicit approval.
- Do not create production stacks during scaffolding.
- Do not commit secrets.
- Do not automate undocumented resources.
- Do not use Pulumi to bypass Pantheon architecture decisions.

## Relationship To pantheonctl

[[automation/pantheonctl/README|pantheonctl]] may later generate Pulumi configuration inputs or coordinate Pulumi preview workflows.

It must not hide Pulumi changes from the operator.
