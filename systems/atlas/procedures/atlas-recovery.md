# Procedure — Atlas Recovery (Unraid NAS)

## Purpose

Recover Atlas after:

- Disk replacement
- OS reinstall
- Controller reset
- Hardware migration

This procedure restores Atlas as the authoritative storage system
without data loss.
SECTION 2 — Preconditions
markdown
Copy code
## Preconditions

Before starting, ensure:

- Physical access to Atlas
- Unraid installation media available (if reinstall required)
- All storage drives are connected
- RAID controller is configured for HBA / passthrough mode
- Network connectivity to Cerberus exists

This procedure assumes data disks are intact unless otherwise noted.
SECTION 3 — Boot & Initial Access
markdown
Copy code
## Step 1 — Boot & Initial Access

1. Power on Atlas
2. Boot into Unraid
3. Access the Unraid web UI from a management workstation

If Unraid is not installed:
- Install Unraid
- Assign USB boot device
- Complete basic setup
SECTION 4 — Verify Disk Detection
markdown
Copy code
## Step 2 — Verify Disk Detection

Navigate to:
Main → Array Devices

Verify:

- All data disks are detected individually
- No disks are presented as RAID volumes
- Cache device (NVMe) is visible

If disks are missing:
- Power down
- Check cabling
- Verify controller mode (HBA)
SECTION 5 — Assign Disks
vbnet
Copy code
## Step 3 — Assign Disks

Assign disks as follows:

- Assign all data disks to data slots
- Assign cache disk to cache pool
- Do NOT assign parity disks unless explicitly planned

IMPORTANT:
- Disk order does not matter for data disks
- Parity assignment is optional during recovery
SECTION 6 — Start the Array
markdown
Copy code
## Step 4 — Start the Array

1. Start the array
2. Confirm disk assignments
3. Allow Unraid to mount filesystems

If prompted to format:
- STOP
- Recheck assignments
- Do NOT format unless disks are confirmed empty
SECTION 7 — Cache Pool Validation
vbnet
Copy code
## Step 5 — Validate Cache Pool

Navigate to:
Main → Cache Devices

Verify:

- Cache pool is mounted
- Filesystem is BTRFS
- No errors are reported
SECTION 8 — Share Validation
markdown
Copy code
## Step 6 — Validate Shares

Navigate to:
Shares

Verify the following shares exist:

- media
- documents
- backups
- appdata
- nextcloud-data
- scans

If shares are missing:
- Recreate the share
- Do NOT move or delete existing data
SECTION 9 — Restore Docker & Services
markdown
Copy code
## Step 7 — Restore Docker & Services

Navigate to:
Settings → Docker

1. Enable Docker
2. Point Docker image and appdata paths to:
   - /mnt/user/appdata

Reinstall containers via Unraid Apps:

- MariaDB (Nextcloud)
- Redis (Nextcloud)
- Nextcloud (if still hosted on Atlas)
- Any additional services as required

Ensure all containers use existing appdata paths.
SECTION 10 — Permission Validation
bash
Copy code
## Step 8 — Validate Permissions

If services fail to start or access data:

chown -R 99:100 /mnt/user/appdata
chown -R 99:100 /mnt/user/nextcloud-data

Restart affected containers after correction.
SECTION 11 — Network Validation
vbnet
Copy code
## Step 9 — Network Validation

Verify:

- Atlas has an IP address
- DNS resolution works
- Atlas is reachable from MGMT and SERVERS VLANs
- SMB access works from USER VLAN (as designed)
SECTION 12 — Final Validation
markdown
Copy code
## Step 10 — Final Validation

Confirm:

- Array is started
- Shares are accessible
- No disks show errors
- Services start cleanly
- No unintended formatting occurred
SECTION 13 — Stopping Point
pgsql
Copy code
🛑 Stopping Point

Atlas is recovered and operational.

- Data integrity preserved
- Storage authority restored
- Ready to serve compute and services
