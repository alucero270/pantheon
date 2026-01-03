# Architecture Overview

This repository documents the design, configuration, and operational procedures
for a self-hosted homelab environment built around strong network segmentation,
centralized storage, and dedicated compute.

The goal of this project is:

- Reproducibility
- Security
- Clarity

This is not an experimentation lab. All changes are intentional, documented,
and recoverable.

---

## Design Principles

### Separation of Concerns

- Network security, storage, and compute are isolated
- No system owns responsibilities outside its role

### Zero-Trust Lite

- No implicit trust between VLANs
- All access is explicitly permitted
- Lateral movement is blocked by default

### Reproducible Builds

- Every system can be rebuilt from documentation alone
- No undocumented tweaks or tribal knowledge

### Centralized Data, Disposable Compute

- Storage is authoritative
- Compute nodes are rebuildable
- Data must survive compute failure

---

## Core Systems

| Name | Role | OS |
|-----|-----|----|
| Cerberus | Firewall / Router | OPNsense |
| Axon | Core Switch | Cisco SG350 |
| Atlas | NAS / Storage | Unraid |
| Prometheus | Compute / AI / VMs | Ubuntu Server |
| Ares | Daily Workstation | Windows |
| Nomad | Mobile Client | Windows |

---

## Non-Goals

- No automatic configuration management (yet)
- No undocumented “magic” changes
- No production internet exposure

---

🛑 Stopping Point

This document defines intent only.  
Implementation details live in `systems/`, `services/`, and `procedures/`.
