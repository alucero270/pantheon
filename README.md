# Homelab Infrastructure & Services

This repository documents the design, configuration, and operational procedures for a self-hosted homelab environment built around strong network segmentation, centralized storage, and dedicated compute.

The goal of this project is **reproducibility**, **security**, and **clarity** — not experimentation for its own sake.

---

## 🎯 Design Principles

- **Separation of concerns**
  - Network security, storage, and compute are isolated
- **Zero-trust inspired**
  - Explicit access only, no implicit trust between VLANs
- **Reproducible builds**
  - Every system can be rebuilt from documentation alone
- **Centralized data, distributed compute**
  - Storage is authoritative; compute is disposable

---

## 🧠 Core Systems

| Name | Role | OS |
|-----|-----|----|
| Cerberus | Firewall / Router | OPNsense |
| Axon | Core Switch | Cisco SG350 |
| Atlas | NAS / Storage | Unraid |
| Prometheus | Compute / AI / VMs | Ubuntu Server |
| Ares | Daily Workstation | Windows |
| Nomad | Mobile Client | Windows |

---

## 🌐 Network Overview

- VLAN-segmented network
- Dedicated MGMT, USER, SERVERS, IOT, GUEST, UNTRUSTED networks
- No lateral movement by default
- Management access restricted to MGMT VLAN

See: `architecture/vlan-design.md`

---

## 📂 Repository Structure
homelab-infrastructure/
  ├── architecture/ # High-level design decisions
  ├── systems/ # Per-host build guides
  ├── services/ # Application/service documentation
  ├── procedures/ # Rebuild, restore, DR steps
  ├── decisions/ # Architecture Decision Records (ADRs)
  ├── CHANGELOG.md
  └── README.md

---

## 🧱 Documentation Rules

- All documentation is written in **Markdown**
- Changes must be:
  - Intentional
  - Documented
  - Committable
- If a change alters architecture, an **ADR is required**

---

## 🧭 Current Status

- Network v1.0: **Stable**
- Atlas (NAS): **Operational**
- Nextcloud: **Operational**
- Prometheus: **Initialization in progress**
- VPN / External access: **Deferred**

---

## 📌 Non-Goals

- No automatic configuration management (yet)
- No “magic” undocumented tweaks
- No production exposure to the internet

---

## 📜 License

Internal / personal use. Documentation may be reused with attribution.
