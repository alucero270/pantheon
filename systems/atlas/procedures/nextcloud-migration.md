# Procedure — Migrate Nextcloud from Atlas to Prometheus

## Purpose

Migrate the Nextcloud runtime from Atlas to Prometheus without:

- Reinstalling Nextcloud
- Re-uploading any data
- Changing users, permissions, or configuration

All authoritative data remains on Atlas.
SECTION 2 — Preconditions
markdown
Copy code
## Preconditions

Before starting, verify:

- Prometheus is fully initialized
- Docker and Docker Compose are installed on Prometheus
- Atlas exports are reachable from Prometheus
- The following directories exist on Atlas:
  - /mnt/user/nextcloud-data
  - /mnt/user/appdata/nextcloud
  - /mnt/user/appdata/mariadb-nextcloud
- Nextcloud, MariaDB, and Redis are currently running on Atlas
SECTION 3 — Stop Services on Atlas
vbnet
Copy code
## Step 1 — Stop Services on Atlas

Stop the following containers on Atlas:

- Nextcloud
- MariaDB (Nextcloud)
- Redis (Nextcloud)

Verify that all three containers are fully stopped
before proceeding.

Do NOT delete any containers or data.
SECTION 4 — Mount Atlas Data on Prometheus
perl
Copy code
## Step 2 — Mount Atlas Data on Prometheus

On Prometheus, mount the Atlas shares so that the following
paths resolve identically:

- /mnt/user/nextcloud-data
- /mnt/user/appdata/nextcloud
- /mnt/user/appdata/mariadb-nextcloud

These mounts are typically provided via NFS.

Paths must match exactly.
Do NOT remap or rename directories.
SECTION 5 — Deploy Containers on Prometheus
markdown
Copy code
## Step 3 — Deploy Containers on Prometheus

Deploy the following containers on Prometheus:

- MariaDB (Nextcloud)
- Redis (Nextcloud)
- Nextcloud

Requirements:

- Container names must match the original names
- Environment variables must match exactly
- Volume mounts must point to the same Atlas-backed paths
- No new data directories may be created

This ensures Nextcloud recognizes the existing installation.
SECTION 6 — Start Order
vbnet
Copy code
## Step 4 — Start Containers in Correct Order

Start containers in the following order:

1. MariaDB
2. Redis
3. Nextcloud

Wait for each container to report healthy before starting
the next one.
SECTION 7 — Validation
markdown
Copy code
## Step 5 — Validation

Verify the following:

- Nextcloud web UI loads normally
- Existing users are present
- Files and folders appear intact
- No maintenance mode warnings appear
- Upload and sync operations succeed

No data migration should have occurred.
SECTION 8 — Failure Handling
markdown
Copy code
## Failure Handling

If Nextcloud does not start correctly:

- Stop all containers on Prometheus
- Verify all volume paths are correct
- Confirm permissions on Atlas directories
- Restart containers in correct order

If unresolved, stop and investigate before proceeding.
SECTION 9 — Stopping Point
pgsql
Copy code
🛑 Stopping Point

Nextcloud is now running on Prometheus.

- Atlas remains the authoritative data store
- Compute responsibilities have moved cleanly
- No data movement or reconfiguration occurred
