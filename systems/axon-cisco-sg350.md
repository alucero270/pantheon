# Axon — Core Switch (Cisco SG350)

Axon is the Layer-2 core switch for the homelab.

It is responsible for VLAN segmentation, port assignment,
and trunking traffic to the firewall.

Axon does not perform routing or policy enforcement.

## Design Intent

- Enforce VLAN separation at Layer 2
- Centralize all switching logic
- Delegate routing and policy to Cerberus
- Avoid smart switching or implicit trust
- Keep port behavior explicit and documented

## Platform Overview

- Hardware: Cisco SG350
- Role: Core access and distribution switch
- Management: Web UI
- Management VLAN: MGMT (99)

Axon is managed only from the MGMT VLAN.

## VLAN Presence

Axon carries the following VLANs:

- VLAN 10 — EXPOSED
- VLAN 20 — USER
- VLAN 30 — IOT
- VLAN 40 — GUEST
- VLAN 50 — UNTRUSTED
- VLAN 60 — SERVERS
- VLAN 99 — MGMT

All VLAN definitions originate from Cerberus.
Axon enforces tagging only.

## Trunk Configuration

The trunk uplink to Cerberus carries all VLANs.

Trunk Port:
- GE24 → Cerberus (em0)

Tagged VLANs:
- 10, 20, 30, 40, 50, 60, 99

Native VLAN:
- VLAN 1 (unused)

No access traffic should rely on the native VLAN.

## Access Port Strategy

Ports are explicitly assigned to a single VLAN.

No port may carry multiple VLANs unless explicitly documented
as a trunk (e.g., access points).

Port assignments are intentional and documented
to prevent drift.

## Documented Port Assignments

USER VLAN (20):
- GE12
- GE13
- GE14

IOT VLAN (30):
- GE3
- GE4
- GE15
- GE16

GUEST VLAN (40):
- GE5
- GE17

UNTRUSTED VLAN (50):
- GE18

SERVERS VLAN (60):
- GE7  → Atlas (final)
- GE19 → Prometheus

MGMT VLAN (99):
- GE2  → Switch management access

Assignments may evolve but must remain documented.

## Access Point Considerations

Access points may require trunk ports.

AP ports may carry:
- USER VLAN
- GUEST VLAN

AP management traffic must not bleed into USER traffic.

Temporary recovery scenarios may place APs on USER VLAN
only; this must be documented when done.

## Explicit Non-Responsibilities

Axon must never:

- Route traffic between VLANs
- Enforce firewall policy
- Act as a security decision point
- Provide WAN connectivity

All policy enforcement occurs on Cerberus.

## Validation Checklist

- Trunk port to Cerberus is up
- All VLANs are tagged correctly
- Access ports map to intended VLANs
- Switch management reachable only from MGMT VLAN
- No unexpected inter-VLAN communication occurs

🛑 Stopping Point

Axon is configured as a stable Layer-2 switch.

Any port or VLAN changes must be documented
to avoid configuration drift.
