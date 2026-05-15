# pantheonctl

## Purpose

`pantheonctl` is the C# control-plane helper for Pantheon.

It validates documentation, generates inventories, checks wiki links, classifies automation readiness, and prepares safe automation inputs for Ansible and Pulumi.

It does not replace Ansible, Pulumi, or Terraform/OpenTofu.

## Initial Scope

Allowed:

- read Pantheon Markdown files
- validate required documentation fields
- check wiki links
- list domains, systems, devices, and services
- generate Ansible inventory scaffolds
- generate Pulumi config scaffolds
- report automation readiness

Forbidden initially:

- modifying live infrastructure
- running Ansible against hosts
- running Pulumi updates
- running Terraform/OpenTofu apply
- changing firewall rules
- changing switch config
- changing Atlas storage
- handling secrets directly

## Planned Commands

| Command | Purpose | Status |
|---|---|---|
| `pantheonctl docs validate` | Validate required docs and metadata | Scaffold |
| `pantheonctl links check` | Check internal wiki links | Scaffold |
| `pantheonctl systems list` | List documented systems/domains | Scaffold |
| `pantheonctl devices list` | List network devices | Scaffold |
| `pantheonctl services list` | List documented services | Scaffold |
| `pantheonctl inventory generate` | Generate inventory from docs | Scaffold |
| `pantheonctl automation classify` | Report automation readiness | Scaffold |
| `pantheonctl ansible render-inventory` | Render Ansible inventory | Scaffold |
| `pantheonctl pulumi render-config` | Render Pulumi config inputs | Scaffold |
| `pantheonctl report readiness` | Generate automation readiness report | Scaffold |

## Related Docs

- [[automation/README|Automation]]
- [[systems/prometheus/automation/ansible/README|Prometheus Ansible]]
- [[automation/shared/pulumi/README|Shared Pulumi]]
- [[automation/shared/terraform/README|Shared Terraform/OpenTofu]]
- [[systems/prometheus|Prometheus]]
- [[systems/network|Network]]
- [[systems/atlas|Atlas]]
- [[systems/network/architecture/security-model|Security Model]]
