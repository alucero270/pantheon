# Remote Access Architecture — Tailscale

## Purpose

This document defines how remote devices securely access the homelab network using Tailscale while preserving the existing network segmentation and security model.

The goal is to make remote clients behave as if they are locally connected to the LAN without bypassing internal infrastructure such as DNS, firewall policy, or reverse proxy routing.

---

# Architecture Overview

Remote access is provided through **Tailscale**, using Prometheus as a **subnet router** to expose internal VLAN networks to remote clients.

Traffic path:

Remote Client
→ Tailscale Network
→ Prometheus (Subnet Router)
→ Internal LAN (192.168.x.x)
→ Cerberus (DNS + Firewall)
→ Traefik Reverse Proxy
→ Internal Services

This approach preserves the existing architecture:

- Cerberus remains the **DNS authority and security enforcement point**
- Axon continues to provide **VLAN segmentation**
- Prometheus hosts **services and compute workloads**
- Traefik provides **centralized ingress routing**

---

# Tailscale Components

## Subnet Router

Prometheus acts as the subnet router for the homelab.

Command used on Prometheus:

```
sudo tailscale up --advertise-routes=192.168.0.0/16
```

Approved routes in the Tailscale admin console allow remote clients to reach:

- 192.168.60.0/24 (SERVERS VLAN)
- 192.168.99.0/24 (MGMT VLAN)
- Other internal LAN segments

Once enabled, remote clients can directly access internal infrastructure.

---

# DNS Integration

Internal services use the domain:

```
home.arpa
```

Cerberus (OPNsense / Unbound) is the authoritative DNS server.

Tailscale is configured with **Split DNS**:

| Domain | Nameserver |
|------|------|
| home.arpa | 192.168.60.1 |

This ensures that remote clients resolve internal service names through Cerberus.

Example resolution path:

```
openwebui.home.arpa
   ↓
Tailscale Client
   ↓
Cerberus DNS (Unbound)
   ↓
192.168.60.103
```

---

# Firewall Considerations

Cerberus must allow DNS queries from the Tailscale address space:

```
100.64.0.0/10
```

Required firewall rule:

Allow
Source: 100.64.0.0/10
Destination: This Firewall
Ports: TCP/UDP 53
Description: Allow Tailscale DNS

Unbound DNS ACL must also permit this network.

---

# Service Access via Reverse Proxy

Internal services are accessed through Traefik using host-based routing.

Examples:

```
https://openwebui.home.arpa
https://nextcloud.home.arpa
https://proxy.home.arpa
```

Traefik routes requests based on the HTTP Host header.

Short names such as `https://openwebui` will return a 404 unless explicitly configured in Traefik router rules.

---

# Validation Checklist

Remote client connected to Tailscale should be able to:

1. Resolve internal DNS

```
nslookup openwebui.home.arpa
```

2. Reach internal DNS server

```
nslookup openwebui.home.arpa 192.168.60.1
```

3. Access services through the reverse proxy

```
https://openwebui.home.arpa
```

4. Reach internal network hosts

```
ping 192.168.60.103
```

---

# Security Model

Tailscale extends network access but does not replace firewall policy.

All traffic still passes through Cerberus where:

- Inter-VLAN restrictions remain enforced
- Administrative services remain restricted
- User VLAN access remains controlled

Remote access therefore follows the same security boundaries as local devices.

---

# Known Limitations

- Short hostnames are not supported by Traefik by default
- Split DNS requires Cerberus to be reachable
- Subnet routing requires Prometheus to remain online

---

# Operational Notes

If remote access stops working, verify the following:

1. Tailscale subnet routes are still approved
2. Prometheus is online
3. DNS queries to Cerberus succeed
4. Reverse proxy is operational

---

# Stopping Point

Remote access architecture is now stable and aligned with the homelab network design.

Future improvements may include:

- VPN-based administrative access policies
- Additional service exposure controls
- Monitoring for remote connectivity

