# Security Model — Zero-Trust Lite

This homelab uses a Zero-Trust-inspired model adapted for a small environment.

---

## Core Principles

- No implicit trust between systems
- All access is explicitly defined
- Network segmentation is the primary control plane

---

## Enforcement Layers

### Network Layer

- VLAN isolation
- Firewall rules enforced by Cerberus
- No lateral routing without explicit rules

### Access Layer

- Administrative access restricted to MGMT VLAN
- No admin access from USER or GUEST Wi-Fi
- Future VPN will terminate into MGMT

### Service Layer

- Services expose only required ports
- No service is both user-facing and authoritative for data
- Compromise of a service must not compromise storage

---

## Explicit Constraints

- USER VLAN must never gain blanket access to SERVERS
- Wi-Fi must never be a trusted admin path
- Infrastructure admin panels are not user conveniences

---

🛑 Stopping Point

Security posture is defined here.
Implementation details live in system and firewall documentation.
