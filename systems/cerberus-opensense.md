# Cerberus — OPNsense Firewall & Router

## Role

Cerberus is the authoritative network enforcement point.

Responsibilities:
- Firewall policy enforcement
- Inter-VLAN routing
- DNS and DHCP services
- WAN connectivity
- Administrative access control

Cerberus is the *only* system permitted to route between VLANs.

---

## Platform

- Software: OPNsense
- Interfaces:
  - WAN: em6 (Starlink)
  - Secondary WAN: em5 (Fiber, optional)
  - LAN Trunk: em0 (VLAN trunk only)

---

## Design Constraints

- VLANs must never be parented to WAN interfaces
- em0 is trunk-only (no IP assigned)
- All inter-VLAN access must be explicitly defined
- Cerberus admin UI is reachable **only** from MGMT VLAN

---

## VLAN Interface Inventory

| VLAN | Name | Subnet | Status |
|-----:|------|--------|--------|
| 10 | EXPOSED | 192.168.10.0/24 | Active |
| 20 | USER | 192.168.20.0/24 | Active |
| 30 | IOT | 192.168.30.0/24 | Active |
| 40 | GUEST | 192.168.40.0/24 | Active |
| 50 | UNTRUSTED | 192.168.50.0/24 | Active |
| 60 | SERVERS | 192.168.60.0/24 | Created (hosts pending) |
| 99 | MGMT | 192.168.99.0/24 | Active |

---

## Core Services

### DHCP

- Enabled per VLAN
- Address pool: `.100 – .200`
- Gateway: VLAN interface IP

DHCP leases are registered in DNS.

---

### DNS Resolver (Unbound)

Enabled features:
- Register DHCP leases
- Register static mappings
- Listen on all interfaces

Diagnostic-only features (disabled after validation):
- Query logging
- Verbosity level 2

---

### System DNS

Upstream resolvers:
- `1.1.1.1`
- `8.8.8.8`

Constraint:
- DNS override from WAN is disabled

---

## Firewall Alias Model

### PrivateNetworks (Mandatory)

Defined once and reused across rules:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

Purpose:
- Prevent accidental east-west traffic
- Enforce “internet-only” rules safely

---

### Host Aliases

Defined as-needed for rule clarity.

Examples:
- WebServer → 192.168.10.10
- Printer → 192.168.30.10
- IPCameras → 192.168.50.10–12

---

## Firewall Rule Model (Authoritative)

### Universal DNS Rule

Applied to **every VLAN interface**:

- Action: Pass
- Protocol: TCP/UDP
- Source: `<VLAN> net`
- Destination: This Firewall
- Port: 53

🚫 Never use `any → 53`.

---

### USER VLAN Rules

Ordered rules:
1. Allow DNS → Firewall
2. Allow USER → WebServer (443)
3. Allow USER → Printer
4. Allow USER → `!PrivateNetworks` (internet-only)

---

### EXPOSED / IOT / GUEST

Pattern:
1. Allow DNS → Firewall
2. Allow → `!PrivateNetworks`

No internal access permitted.

---

### MGMT VLAN

Explicit allow-list only:
- MGMT → Cerberus (443)
- MGMT → Axon (443)

Implicit deny for all other traffic.

---

## Admin Access Strategy

- Cerberus admin UI:
  - MGMT VLAN only
- No access from USER or GUEST Wi-Fi
- Future VPN will terminate into MGMT VLAN

---

## Known Constraints & Lessons

- DNS must be explicitly allowed for MGMT VLAN
- Missing DNS causes license activation and admin issues
- Rule order is critical; implicit deny is relied upon

---

🛑 Stopping Point

Cerberus configuration is considered **stable**.
Changes require documentation and, if architectural, an ADR.
