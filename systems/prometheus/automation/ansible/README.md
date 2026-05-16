# Prometheus Ansible Automation

## Purpose

This folder contains Ansible scaffolding for Prometheus host configuration.

Prometheus is the first safe automation target because it is disposable compute and can be rebuilt without authoritative data loss.

## Initial Scope

Allowed future automation:

- packages
- SSH configuration
- Docker installation
- Docker networks
- NFS client mounts
- local directory layout
- systemd services
- Docker Compose scaffolding
- validation commands

## Out of Scope

Do not automate from here:

- network firewall rules
- switch configuration
- Atlas storage shares
- Atlas array configuration
- secrets rotation

## Rules

- Do not store secrets in inventory.
- Do not run playbooks against live hosts without explicit approval.
- Do not automate undocumented state.
- Do not automate anything that cannot be validated.
- Prefer check mode and validation playbooks before configuration playbooks.

## Related Docs

- [[automation/README|Automation]]
- [[automation/pantheonctl/README|pantheonctl]]
- [[systems/prometheus|Prometheus]]
- [[systems/prometheus/services|Prometheus Services]]
