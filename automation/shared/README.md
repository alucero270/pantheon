# Shared Automation Assets

## Purpose

This folder contains reusable automation assets shared across Pantheon domains.

Domain-specific automation belongs under `systems/<domain>/automation/`.

## Shared Areas

- [[automation/shared/ansible/README|Shared Ansible]]
- [[automation/shared/pulumi/README|Shared Pulumi]]
- [[automation/shared/terraform/README|Shared Terraform/OpenTofu]]

## Rules

- Do not place Prometheus-specific playbooks here.
- Do not place Atlas storage actions here.
- Do not place network firewall or switch changes here.
- Keep shared assets reusable and explicitly documented.
