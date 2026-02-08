# TODO — Homelab Documentation Backlog

This file tracks **future documentation work** that was **not fully present**
in the original source notes and build logs.

Everything listed here is **new work**, not retroactive documentation.

---

## ✅ Completed (From Original Source Material)

The following are complete, authoritative, and sourced directly from the
original documentation:

- architecture/
- systems/
- services/
  - Nextcloud (full detail, migration-safe)
  - Media architecture
  - Redis (Nextcloud usage)
  - MariaDB (Nextcloud usage)
- procedures/
  - Nextcloud deploy
  - Nextcloud migration
  - Network rebuild
  - Atlas recovery

No further work is required here unless behavior changes.

---

## 📂 procedures/ (HIGH PRIORITY)

Operationally critical procedures that should be completed first.

### 🔴 Required

- [ ] procedures/prometheus-rebuild.md  
  - Ubuntu reinstall  
  - Network configuration (MGMT + SERVERS)  
  - Docker + libvirt setup  
  - NFS / SMB mounts from Atlas  
  - Validation checklist  

- [ ] procedures/backup-restore.md  
  - What is backed up  
  - What is NOT backed up  
  - Restore order  
  - Verification steps  

- [ ] procedures/disaster-recovery.md  
  - Total loss scenarios  
  - Order of rebuild:
    - Network  
    - Atlas  
    - Prometheus  
    - Services  
  - Decision points  

---

### 🟡 Strongly Recommended

- [ ] procedures/service-redeploy.md  
  - Generic container redeploy pattern  
  - Used for Jellyfin and future services  

- [ ] procedures/credential-rotation.md  
  - Admin passwords  
  - Database credentials  
  - API tokens  
  - SSH keys  

---

## 📂 services/ (MEDIUM–HIGH PRIORITY)

### 🔴 Required

- [ ] services/jellyfin.md (or Plex if chosen)  
  - Data paths  
  - Transcoding behavior  
  - Atlas vs Prometheus roles  
  - Network exposure rules  

- [ ] services/redis.md  
  - Finalize as a generic Redis service document  
  - Not Nextcloud-specific only  

- [ ] services/reverse-proxy.md  
  - Nginx / Traefik decision  
  - Internal-only initially  
  - TLS termination plan  

---

### 🟡 Optional / Future

- [ ] services/monitoring.md  
  - Prometheus / Grafana (if planned)  
  - Or explicit decision to defer  

---

## 📂 decisions/ (ADR — HIGH VALUE, LOW EFFORT)

These decisions are already implied by existing documentation but have not yet
been formally recorded as Architecture Decision Records.

### 🔴 Required ADRs (extract from existing content)

- [ ] ADR — Zero-Trust Lite Network Model  
- [ ] ADR — Atlas as Authoritative Storage  
- [ ] ADR — Disposable Compute (Prometheus)  
- [ ] ADR — Nextcloud Migration-Safe Deployment Model  

These can be written quickly because:
- The decisions are already made
- The rationale is already documented

---

### 🟡 Recommended ADRs

- [ ] ADR — Backup Scope & Retention  
- [ ] ADR — Reverse Proxy & TLS Strategy  
- [ ] ADR — VPN / Remote Access Strategy  
- [ ] ADR — Monitoring Strategy (or explicit deferral)  

---

## 📂 architecture/ (LOW PRIORITY — OPTIONAL POLISH)

Architecture is solid; these add clarity for future reference.

- [ ] architecture/external-access.md  
  - Explicitly document what is NOT exposed  

- [ ] architecture/failure-domains.md  
  - What breaks when X fails  
  - Reinforces design intent  

---

## 📂 Repository-Level Cleanup

- [ ] CHANGELOG.md  
  - Date  
  - Summary  
  - Sections touched  

- [ ] README cross-links  
  - Link architecture → systems → procedures  
  - Prevents readers from guessing order  

---

## 🧭 Recommended Execution Order (Optimal)

For highest safety per hour spent:

1. procedures/prometheus-rebuild.md  
2. procedures/backup-restore.md  
3. ADR extraction (4 core ADRs)  
4. services/jellyfin.md  
5. procedures/disaster-recovery.md  
6. Reverse proxy decision (ADR + service)  

---

## Notes

- Items in this file are **future work only**
- Nothing listed here should be treated as already implemented
- This file exists to prevent scope creep and invented history
---

# Prometheus — Readiness Checklist

This checklist tracks the remaining non‑AI work required to bring **Prometheus** from _bring‑up state_ to a clean, policy‑aligned, and ready compute node within Pantheon.

This document is intentionally actionable and checkable.

---

## 1. Hardware Finalization

-  Power down Prometheus
    
-  Install additional **32 GB RAM**
    
-  Boot system successfully
    
-  Verify total memory:
    
    ```bash
    free -h
    ```
    
-  Verify DIMMs detected correctly:
    
    ```bash
    sudo dmidecode -t memory
    ```
    
-  Check kernel logs for memory errors:
    
    ```bash
    journalctl -k | grep -i memory
    ```
    

**Done when:**

- Total memory reflects expected capacity
    
- No ECC, timing, or kernel memory errors
    

---

## 2. Network Placement Correction

-  Move Prometheus off **USER port**
    
-  Connect Prometheus to:
    
    -  **SERVERS VLAN** (runtime traffic)
        
    -  **MGMT VLAN** (administrative access)
        
-  Confirm IP addressing (DHCP reservation or static)
    
-  Verify default gateway and DNS resolution
    

**Validation:**

```bash
ip addr
ip route
resolvectl status
```

**Done when:**

- Prometheus is no longer reachable from USER networks
    
- MGMT access is scoped and intentional
    

---

## 3. Management Surface Hardening

-  Confirm SSH access works from MGMT VLAN
    
-  Restrict Cockpit access:
    
    -  Bound to MGMT interface only **or**
        
    -  Localhost‑only until firewall rules are enforced
        
-  Verify Cockpit is **not reachable** from USER / GUEST / IOT VLANs
    

**Validation:**

```bash
ss -tulpn | grep 9090
```

**Done when:**

- All admin interfaces respect MGMT‑only policy
    

---

## 4. Atlas Integration (Foundational)

-  Confirm NFS exports on Atlas
    
-  Create local mount points on Prometheus:
    
    -  `/mnt/atlas/documents`
        
    -  `/mnt/atlas/media` (if required)
        
    -  `/mnt/atlas/appdata` (selective write)
        
-  Mount Atlas shares
    
-  Verify read/write intent matches design
    

**Validation:**

```bash
mount | grep atlas
ls -lah /mnt/atlas
```

**Done when:**

- Prometheus consumes authoritative data read‑only by default
    
- Write access is explicit and minimal
    

---

## 5. Docker Runtime Hygiene

-  Review disk usage:
    
    ```bash
    docker system df
    ```
    
-  Remove unused images and build cache (safe cleanup)
    
-  Confirm running containers are intentional
    

**Done when:**

- No orphaned or accidental containers
    
- Disk usage is understood and predictable
    

---

## 6. Documentation Alignment (Lightweight)

-  Append notes to `[[notes/prometheus-ubuntu]]` reflecting:
    
    - RAM upgrade
        
    - Network correction
        
-  Confirm procedure docs reflect **actual commands used**
    
-  Avoid refactors; append only
    

**Done when:**

- Docs match reality
    
- No known gaps between system state and documentation
    

---

## 7. Deferred / Planned (Not Blocking)

-  Portainer installation (MGMT‑only, deferred)
    
-  ComfyUI access model planning
    
-  Long‑term monitoring integration
    

These items should not proceed until **network posture is corrected**.

---

## Completion Criteria

Prometheus is considered **ready** when:

- Hardware is finalized
    
- Network posture matches architecture
    
- Atlas integration is in place
    
- Management surfaces are constrained
    
- Docker runtime is clean
    

At that point, Prometheus can safely host long‑lived workloads and support future platform systems.