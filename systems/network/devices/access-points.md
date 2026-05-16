# Access Points — Wireless Network Edge

Access points provide wireless connectivity for user,
guest, and IoT devices.

They act as Layer-2 extensions of the wired network
and must not bypass firewall or VLAN controls.

## Design Intent

- Extend VLANs wirelessly without changing trust boundaries
- Treat Wi-Fi as untrusted by default
- Prevent administrative access over Wi-Fi
- Preserve parity between wired and wireless security models

## VLAN Mapping Model

Wireless networks map directly to VLANs:

- USER Wi-Fi   → VLAN 20 (USER)
- GUEST Wi-Fi  → VLAN 40 (GUEST)
- IOT Wi-Fi    → VLAN 30 (IOT)

No wireless network maps to:
- MGMT VLAN
- SERVERS VLAN
- EXPOSED VLAN

## Trunk vs Access Ports

Access points may be connected using:

### Trunk Ports
- Carry USER and GUEST VLANs
- Required for multi-SSID deployments
- Tagged VLAN traffic only

### Access Ports
- Carry a single VLAN
- Used temporarily for recovery or diagnostics
- Must be documented if used

Trunking is the normal operational mode.

## Management Access Constraints

Access point management interfaces:

- Must not be reachable from USER Wi-Fi
- Must not be reachable from GUEST Wi-Fi
- Should be reachable only from MGMT VLAN

Wireless clients must never have administrative access
to infrastructure devices.

## Recovery & Exception Handling

During recovery scenarios:

- An access point may be temporarily placed on USER VLAN
- This is allowed only to restore connectivity
- The exception must be documented

Once recovery is complete:
- AP must be returned to its intended trunk configuration

## Security Implications

This design ensures:

- Wireless compromise does not grant admin access
- Guest users are isolated from trusted devices
- IoT devices cannot laterally move
- Firewall policies remain authoritative

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Network |
| Host/system/device owner | Access points |
| Runtime type | Wireless Layer-2 edge |
| Source of truth | Network docs; device model and configuration export need validation |
| Config path | Needs validation |
| Data path | No user data; wireless configuration only |
| Secret requirements | Do not commit Wi-Fi secrets or admin credentials |
| Network ports | Needs validation |
| Dependencies | VLAN trunking, management access, config backup |
| Backup requirement | Current AP configuration backup required before automation |
| Validation command | Needs validation |
| Recovery procedure | Needs validation |
| Automation classification | Manual only |
| Preferred automation tool | Manual only |

## Explicit Non-Responsibilities

Access points must never:

- Perform routing
- Enforce firewall policy
- Provide administrative access paths
- Act as trusted infrastructure endpoints

## Validation Checklist

- USER Wi-Fi maps only to VLAN 20
- GUEST Wi-Fi maps only to VLAN 40
- IoT Wi-Fi maps only to VLAN 30
- No wireless access to MGMT VLAN
- AP admin UI unreachable from Wi-Fi clients

🛑 Stopping Point

Wireless access is correctly segmented and constrained.

Any SSID or VLAN mapping changes must be documented
to preserve security boundaries.
