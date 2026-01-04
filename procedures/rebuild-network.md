# Procedure — Network Rebuild (Cerberus + Axon)

## Purpose

Rebuild the entire network stack after a firewall reset,
hardware replacement, or full configuration loss.

This procedure restores:
- VLAN segmentation
- Firewall enforcement
- DNS and DHCP services
- Administrative access boundaries
SECTION 2 — Preconditions
markdown
Copy code
## Preconditions

Before starting, ensure:

- Physical access to Cerberus (firewall)
- Console or local access available
- Axon (Cisco SG350) is reachable
- Internet connection available on WAN
- Architecture documentation is accessible

This procedure assumes a clean or factory-reset state.
SECTION 3 — Install OPNsense on Cerberus
vbnet
Copy code
## Step 1 — Install OPNsense

1. Install OPNsense on Cerberus
2. Assign interfaces:
   - WAN → em6 (or correct WAN interface)
   - LAN → em0

Important:
- Do NOT assign an IP address to LAN
- LAN will function as a VLAN trunk only
SECTION 4 — Initial System Setup
markdown
Copy code
## Step 2 — Initial System Setup

Complete the OPNsense setup wizard with the following constraints:

- WAN:
  - IPv4: DHCP
  - IPv6: As required (optional)
- LAN:
  - IPv4: None
  - IPv6: None

Set:
- Admin password
- Hostname
- DNS servers (temporary if needed)

Finish the wizard.
SECTION 5 — Create VLANs
vbnet
Copy code
## Step 3 — Create VLANs

Navigate to:
Interfaces → Other Types → VLAN

Create the following VLANs on parent interface em0:

10  EXPOSED
20  USER
30  IOT
40  GUEST
50  UNTRUSTED
60  SERVERS
99  MGMT

Save after each VLAN is created.
SECTION 6 — Assign VLAN Interfaces
vbnet
Copy code
## Step 4 — Assign VLAN Interfaces

Navigate to:
Interfaces → Assignments

For each VLAN interface:

- Enable interface
- IPv4 Configuration: Static IPv4
- IPv6 Configuration: None
- Apply changes one interface at a time

Do NOT configure WAN VLANs.
SECTION 7 — Configure Interface IPs
yaml
Copy code
## Step 5 — Configure Interface IP Addresses

Assign the following subnets:

- EXPOSED (10):   192.168.10.1/24
- USER (20):      192.168.20.1/24
- IOT (30):       192.168.30.1/24
- GUEST (40):     192.168.40.1/24
- UNTRUSTED (50): 192.168.50.1/24
- SERVERS (60):   192.168.60.1/24
- MGMT (99):      192.168.99.1/24

Apply changes after each interface.
SECTION 8 — Configure DHCP
vbnet
Copy code
## Step 6 — Configure DHCP

Navigate to:
Services → DHCPv4

For each VLAN interface:

- Enable DHCP
- Set range: .100 – .200
- Gateway: Interface IP

Save after each configuration.
SECTION 9 — Configure DNS Resolver
markdown
Copy code
## Step 7 — Configure DNS Resolver (Unbound)

Navigate to:
Services → Unbound DNS → General

Enable:
- Enable Unbound DNS
- Listen Interfaces: All
- Register DHCP leases
- Register static mappings

Temporary (diagnostics only):
- Enable query logging
- Log verbosity: 2

These settings should be disabled after validation.
SECTION 10 — Configure System DNS
vbnet
Copy code
## Step 8 — Configure System DNS

Navigate to:
System → Settings → General

Set DNS servers:
- 1.1.1.1
- 8.8.8.8

Disable:
- Allow DNS server list to be overridden by DHCP/PPP on WAN

Save changes.
SECTION 11 — Create Firewall Aliases
vbnet
Copy code
## Step 9 — Create Firewall Aliases

Navigate to:
Firewall → Aliases

Create alias: PrivateNetworks

Type: Network(s)

Values:
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16

Save alias.
SECTION 12 — Apply Firewall Rules
markdown
Copy code
## Step 10 — Apply Firewall Rules

For EACH VLAN interface:

Universal DNS Rule:
- Action: Pass
- Protocol: TCP/UDP
- Source: <VLAN> net
- Destination: This Firewall
- Port: 53

USER VLAN rules (order matters):
1. Allow DNS → Firewall
2. Allow USER → specific internal services (if any)
3. Allow USER → !PrivateNetworks

EXPOSED / IOT / GUEST:
1. Allow DNS → Firewall
2. Allow → !PrivateNetworks

MGMT VLAN:
- Allow MGMT → This Firewall (443)
- Allow MGMT → Axon (443)

Implicit deny applies to all other traffic.
SECTION 13 — Switch (Axon) Validation
csharp
Copy code
## Step 11 — Validate Switch Configuration (Axon)

Verify on Axon:

- Trunk port to Cerberus is tagged with:
  10, 20, 30, 40, 50, 60, 99
- Access ports match intended VLAN assignments
- No routing enabled on switch

Correct any mismatches before proceeding.
SECTION 14 — Validation & Testing
markdown
Copy code
## Step 12 — Validation & Testing

Verify the following:

- Internet access works from USER VLAN
- USER cannot access MGMT resources
- Wi-Fi clients cannot reach admin panels
- SERVERS VLAN is isolated
- MGMT VLAN can administer infrastructure
- DNS resolution works on all VLANs
SECTION 15 — Stopping Point
vbnet
Copy code
🛑 Stopping Point

The network baseline is restored and stable.

Do NOT:
- Add VPN
- Add port forwards
- Add multi-WAN logic

Until a configuration backup is taken.
