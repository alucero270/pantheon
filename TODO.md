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
