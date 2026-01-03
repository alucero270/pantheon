# Axon — Cisco SG350 Core Switch

## Role

Axon is the Layer-2 enforcement point for VLAN segmentation.

Responsibilities:
- VLAN tagging
- Port-to-VLAN assignment
- Trunking to Cerberus
- No routing or policy logic

---

## Design Constraints

- Axon does not route traffic
- All routing decisions occur on Cerberus
- VLAN assignments must match documented intent
- Trunk configuration must remain stable

---

## VLAN Presence

Axon carries the following VLANs:

- 10 — EXPOSED
- 20 — USER
- 30 — IOT
- 40 — GUEST
- 50 — UNTRUSTED
- 60 — SERVERS
- 99 — MGMT

---

## Port Grouping Strategy

### USER VLAN (20)

- GE1 → Atlas (temporary)
- GE2 → Atlas (temporary)
- GE6 → AP uplink (temporary)
- GE12
- GE13
- GE14

---

### IOT VLAN (30)

- GE3
- GE4
- GE15
- GE16

---

### GUEST VLAN (40)

- GE5
- GE17

---

### UNTRUSTED VLAN (50)

- GE6 (future reassignment planned)
- GE18

---

### SERVERS VLAN (60)

- GE7 → Atlas (final)
- GE19 → Prometheus

---

### MGMT VLAN (99)

- GE2 → Switch management / admin access

---

### Trunk Ports

- GE24 → Cerberus (`em0`)

Tagged VLANs:
- 10, 20, 30, 40, 50, 60, 99

Native VLAN:
- VLAN 1 (unused)

---

## Access Point Considerations

- APs may trunk USER and GUEST VLANs
- AP management must not leak into USER traffic
- Temporary AP recovery placed APs on USER VLAN only

---

## Known Issues & Recovery Notes

- Misassigned AP ports can break Wi-Fi
- VLAN 20 reassignment restored AP connectivity
- This was intentional and temporary

---

🛑 Stopping Point

Axon configuration is stable.
Port changes must be documented to avoid drift.
