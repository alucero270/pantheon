# Security Model

## Zero-Trust Lite# Cerberus — OPNsense Firewall

## Role

- Firewall
- Router
- DNS / DHCP authority

## Configuration Scope

- VLAN creation
- Firewall rules
- DNS resolver
- DHCP

See also:
- architecture/vlan-design.md
- procedures/network-rebuild.md


- Explicit access only
- No implicit trust between VLANs
- Admin access restricted to MGMT

## Enforcement Points

- Firewall rules (Cerberus)
- VLAN segmentation (Axon)
- Service exposure rules
