# State Policy

## Status

Needs decision

## Terraform/OpenTofu State

Do not commit state files.

Initial recommendation:

Local state only for experiments.

No production firewall, storage, switch, or core network state until backend and rollback strategy are approved.

## Pulumi State

Do not create production stacks during scaffolding.

Do not commit secrets.

Pulumi backend and secrets provider are `Needs decision`.

## Required Before Production State

- backend selection
- access control
- backup strategy
- lock strategy
- recovery procedure
- secret handling decision
