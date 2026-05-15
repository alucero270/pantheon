# Prometheus Automation

## Purpose

This folder contains automation scaffolding for the Prometheus domain.

Prometheus is the first safe automation target because it is disposable compute and can be rebuilt without authoritative data loss.

## Initial Classification

`Automation ready / Ansible candidate`

## Preferred Automation Tool

- Host configuration: Ansible
- API-backed future resources: Pulumi candidate after validation
- Terraform/OpenTofu: Deferred unless explicitly justified

## Folder Index

- [[systems/prometheus/automation/ansible/README|Prometheus Ansible]]
- [[systems/prometheus/automation/pulumi/README|Prometheus Pulumi]]

## Rules

- Do not store secrets in automation files.
- Do not run playbooks against live hosts without explicit approval.
- Do not automate undocumented state.
- Do not treat Prometheus local data as authoritative.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/services]]
- [[systems/prometheus/procedures]]
- [[automation/policies/automation-classification]]
