# Network Automation Guardrails

## Purpose

Network automation is intentionally restricted.

The network domain includes firewall, routing, DNS, DHCP, switching, VLANs, ingress, and remote access.

Mistakes in this domain can break management access or weaken segmentation.

## Initial Classification

`Do not automate yet`

## Do Not Automate Yet

- firewall rules
- inter-VLAN routing
- switch trunk ports
- VLAN assignments
- management access rules
- WAN failover
- DNS/DHCP changes that affect reachability

## Future Candidates

Possible future automation candidates after validation:

- read-only firewall rule inventory
- DNS/DHCP export validation
- Tailscale configuration
- external DNS provider resources
- config backup verification

## Required Before Automation

- current config backup
- restore procedure
- out-of-band management path
- dry-run or preview workflow
- rollback procedure
- validation checklist

## Related Docs

- [[systems/network/architecture]]
- [[systems/network/devices]]
- [[systems/network/services]]
- [[automation/policies/automation-classification]]
