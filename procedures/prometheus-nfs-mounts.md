---
type: procedure
risk_level: low
last_tested: 2026-01-23
---
# Prometheus Atlas NFS Mount Configuration

## Purpose
Mount Atlas authoritative and runtime datasets on Prometheus via NFS, enforcing the Pantheon data classification model.

---

## Preconditions
- Access required:
  - SSH from MGMT VLAN
  - Sudo privileges
- Systems impacted:
  - Prometheus
  - Atlas (exports must already exist)

---

## Steps

### 1. Install NFS client
```bash
sudo apt install -y nfs-common
```
### 2. Create mount points
```bash
sudo mkdir -p /mnt/atlas
sudo mkdir -p /mnt/atlas/{appdata,datasets,managed-media,shared-media}
```
### 3. Configure **/etc/fstab
fstab
```
atlas:/exports/appdata        /mnt/atlas/appdata        nfs  rw,noatime,nofail,_netdev  0  0
atlas:/exports/datasets       /mnt/atlas/datasets       nfs  rw,noatime,nofail,_netdev  0  0
atlas:/exports/managed-media  /mnt/atlas/managed-media  nfs  ro,noatime,nofail,_netdev  0  0
atlas:/exports/shared-media   /mnt/atlas/shared-media   nfs  ro,noatime,nofail,_netdev  0  0
```

Mount all:

bash
Copy code
sudo mount -a
Validation
Command(s):

bash
Copy code
mount | grep /mnt/atlas
touch /mnt/atlas/appdata/_rw_test
touch /mnt/atlas/managed-media/_should_fail
Expected output:

RW test succeeds

RO test fails with read-only filesystem error

Rollback
bash
Copy code
sudo umount /mnt/atlas/*
sudo sed -i '\|/mnt/atlas|d' /etc/fstab
Warnings
⚠️ Incorrect mount options may allow unintended writes to authoritative datasets.

Automation Potential
Fully automatable

Suitable for rebuild scripts

Related Docs
Architecture:

[[architecture/data-strategy]]

Systems:

[[systems/prometheus]]

ADRs:

[[decisions/ADR-006]]

yaml
Copy code

---