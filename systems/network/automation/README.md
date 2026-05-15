# Network Automation

## Purpose

This folder contains automation documentation and guardrails for the Network domain.

Network automation is guardrail-only until configuration backup, rollback, and validation workflows are proven.

## Initial Classification

`Do not automate yet`

## Preferred Automation Tool

- Read-only validation: `pantheonctl`
- Future API-backed resources: `Pulumi candidate`
- Firewall and switch configuration: `Manual only` until validated

## Folder Index

- [[systems/network/automation/guardrails]]
- [[systems/network/automation/ansible/README|Network Ansible]]
- [[systems/network/automation/pulumi/README|Network Pulumi]]
- [[systems/network/automation/terraform/README|Network Terraform/OpenTofu]]

## Related Docs

- [[systems/network]]
- [[systems/network/architecture]]
- [[systems/network/devices]]
- [[automation/policies/automation-classification]]
