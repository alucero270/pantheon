# VLAN Design (Authoritative)

This document defines the authoritative VLAN structure and intent.
VLAN definitions are architectural constraints and must not be altered
without an ADR.

---

## VLAN Inventory

| VLAN ID | Name | Purpose |
|-------:|------|--------|
| 10 | EXPOSED | Public-facing / DMZ-style services |
| 20 | USER | Trusted user devices |
| 30 | IOT | IoT devices |
| 40 | GUEST | Guest Wi-Fi |
| 50 | UNTRUSTED | Quarantine / testing |
| 60 | SERVERS | Internal servers |
| 99 | MGMT | Infrastructure management |

---

## Architectural Rules

### Isolation

- No VLAN may access another VLAN unless explicitly permitted
- SERVERS VLAN is not reachable from USER or Wi-Fi by default
- MGMT VLAN is hard-isolated

### Wi-Fi Constraints

- USER Wi-Fi devices are treated as USER VLAN devices
- USER Wi-Fi cannot access:
  - Firewall admin UI
  - Switch admin UI
  - NAS admin UI
- Administrative access requires MGMT VLAN or future VPN

### Management Access

- All infrastructure management occurs on MGMT VLAN
- MGMT VLAN is reachable only from:
  - Wired admin ports
  - Dedicated MGMT SSID (planned)
  - VPN (future)

---

## Design Notes

- SERVERS VLAN exists to protect infrastructure and data
- USER VLAN is intentionally restricted despite being “trusted”
- UNTRUSTED VLAN exists for containment, not convenience

---

🔒 Decision (Locked)

This VLAN model defines the security boundary of the homelab.
Changes require an Architecture Decision Record (ADR).
