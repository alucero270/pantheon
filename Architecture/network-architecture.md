# Network Architecture — High Level

This document describes how network components interact at a systems level.
Procedural configuration lives elsewhere.

---

## Components

- Cerberus — Firewall / Router
- Axon — Core Switch
- Access Points — USER / GUEST Wi-Fi
- Atlas — SERVERS VLAN
- Prometheus — SERVERS VLAN

---

## High-Level Flow

USER Devices
  ↓
Firewall (Cerberus)
  ↓
Internet

Administrative Access
  ↓
MGMT VLAN
  ↓
Infrastructure Systems

---

## Design Intent

- Firewall is the enforcement point
- Switch is not a policy engine
- Access points bridge VLANs only as defined
- No routing occurs outside Cerberus

---

## Explicit Non-Goals

- No east-west trust
- No smart switching rules
- No “temporary” firewall exceptions

---

### IP Addressing

Network devices use DHCP reservations managed by Cerberus (OPNsense).

- VLAN: SERVERS (60)
-- Atlas: 192.168.60.102
- Assignment: DHCP reservation (MAC-bound)
- Rationale:
  - Centralized control
  - Prevents conflicts
  - Survives OS reinstall
  - Enterprise-aligned

Static IPs are not configured at the OS level.

🛑 Stopping Point

This document defines topology, not configuration.
