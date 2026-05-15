# Network

## System Purpose

Network is the Pantheon system domain for routing, switching, VLAN segmentation, DNS, DHCP, ingress paths, and remote access boundaries.

## Role

Network contains the firewall/router, core switch, access points, and network architecture that make Pantheon reachable while preserving explicit security boundaries.

## Responsibilities

- Enforce VLAN segmentation and routing boundaries.
- Provide DNS and DHCP authority where documented.
- Carry VLAN traffic across switching and wireless infrastructure.
- Define ingress and remote-access behavior.
- Preserve MGMT isolation and no-default-lateral-access rules.

## Explicit Non-Responsibilities

- Do not store authoritative user or application data.
- Do not host compute workloads except network control-plane services where documented.
- Do not bypass architecture decisions for convenience.

## Network Placement

Network spans all documented VLANs. Management access belongs on MGMT and must remain explicitly controlled.

## Data Ownership

Network owns configuration state for Cerberus, Axon, access points, DNS, DHCP, firewall rules, and remote access policy. It owns no user data.

## Device Index

- [[systems/network/devices/cerberus]]
- [[systems/network/devices/axon]]
- [[systems/network/devices/access-points]]

## Architecture Index

- [[systems/network/architecture/network-architecture]]
- [[systems/network/architecture/vlan-design]]
- [[systems/network/architecture/dns-plan]]
- [[systems/network/architecture/ingress-flow]]
- [[systems/network/architecture/tailscale-remote-access]]

## Procedure Index

- [[systems/network/procedures/network-rebuild]]
- [[systems/network/procedures/rebuild-network]]
- [[systems/network/procedures/tailscale-remote-access]]

## Automation Classification

Do not automate yet

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Network |
| Host/system/device owner | Cerberus, Axon, access points, and network control-plane services |
| Runtime type | Firewall/router, switching, wireless, DNS/DHCP, routing, ingress paths, remote access |
| Source of truth | Network documentation and device configuration; live device exports need validation |
| Config path | Needs validation |
| Data path | No user data; device configuration only |
| Secret requirements | Do not commit secrets; final model is [[automation/policies/secrets-policy|Needs decision]] |
| Network ports | Needs validation |
| Dependencies | Management access, device backups, rollback path, out-of-band access |
| Backup requirement | Current config backup required before any automation |
| Validation command | Needs validation |
| Recovery procedure | [[systems/network/procedures/README]] |
| Automation classification | Do not automate yet |
| Preferred automation tool | Manual only; Pulumi candidate for future API-backed resources after validation |

## Automation Index

- [[systems/network/automation/README]]
- [[systems/network/automation/guardrails]]

## What Good Looks Like

Network documentation makes routing, VLANs, DNS, DHCP, firewall behavior, ingress, remote access, and management boundaries explicit without increasing lockout or exposure risk.

## What To Avoid

- Do not automate firewall or switch changes before backup, rollback, and management recovery are proven.
- Do not weaken MGMT isolation.
- Do not introduce broad inter-VLAN allow rules.
- Do not document planned remote access as currently deployed.
