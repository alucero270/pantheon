# ADR-001: Zero-Trust Lite Network Model

## Status
Accepted

## Context
The homelab contains multiple classes of devices with different trust levels,
including user devices, servers, IoT devices, and management infrastructure.

Allowing implicit trust or unrestricted lateral movement between these devices
would increase blast radius in the event of compromise.

Constraints:
- Single firewall (Cerberus) responsible for enforcement
- VLAN-based segmentation
- Home environment (not enterprise-scale zero trust)

## Decision
Adopt a **Zero-Trust Lite** network model where:

- No VLAN is trusted by default
- Inter-VLAN communication is explicitly allowed only when required
- Firewall policy enforcement occurs centrally on Cerberus
- Management access is restricted to a dedicated MGMT VLAN

## Rationale
This approach balances security and operational complexity.

It provides:
- Strong segmentation
- Reduced lateral movement
- Clear trust boundaries

Without requiring:
- Per-device identity enforcement
- Complex service meshes
- Enterprise identity infrastructure

## Consequences
- Firewall rules must be explicitly defined and maintained
- Misconfiguration can cause service outages
- Security posture is significantly improved
- Troubleshooting requires awareness of VLAN boundaries

## Alternatives Considered
- Flat network (rejected due to excessive trust and blast radius)
- Full zero-trust with identity enforcement (rejected due to complexity and scope)

## Related Documents
- architecture/network-overview.md
- systems/cerberus.md
- systems/axon.md

---

**Date:** 2026-01-XX  
**Author:** Alex
