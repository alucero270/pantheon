# Automation Classification

## Purpose

This policy defines the allowed automation readiness classifications for Pantheon documentation and scaffolding.

## Allowed Values

- `Automation ready`
- `Needs inventory`
- `Needs validation`
- `Manual only`
- `Do not automate yet`
- `Terraform candidate`
- `Pulumi candidate`
- `Ansible candidate`

## Initial Classification Model

| Area | Classification | Reason |
|---|---|---|
| Prometheus baseline | Automation ready / Ansible candidate | Disposable Ubuntu compute node |
| Prometheus Docker stacks | Ansible candidate after compose inventory | Rebuildable runtime services |
| Prometheus storage layout | Ansible candidate after path validation | Local paths can be declared |
| Prometheus AI stack | Needs validation | GPU/runtime details must be verified before automation |
| Atlas storage shares | Do not automate yet | Authoritative data system |
| Atlas Docker services | Needs validation | Safe only after backup/restore model is clear |
| Network firewall rules | Do not automate yet | Can lock out network access |
| Network DNS/DHCP reservations | Needs validation / Pulumi candidate later | Possible later via API/provider/export model |
| Axon switch config | Manual only | Avoid switch lockout until config backup/restore is proven |
| Tailscale routing/DNS | Pulumi candidate | API-backed and reversible |
| External DNS / Cloudflare | Pulumi candidate | Provider/API-driven if adopted |
| Generic Terraform modules | Deferred | Use only where justified |

## Rule

Use `Unknown`, `TBD`, or `Needs validation` instead of guessing.
