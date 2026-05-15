# Procedure — Deploy Nextcloud (Migration-Safe)

## Purpose

Deploy Nextcloud in a way that:

- Stores all authoritative data on Atlas
- Allows lift-and-shift migration to Prometheus
- Avoids reinstall, reupload, or permission surgery later

This procedure is copy-safe and reproducible.
SECTION 2 — Preconditions
markdown
Copy code
## Preconditions

Verify the following on Atlas before proceeding:

- Unraid is operational
- Docker service is enabled
- Internet and DNS resolution work
- The following shares exist:
  - appdata
  - nextcloud-data
SECTION 3 — Create Directory Structure
bash
Copy code
## Step 1 — Create Directory Structure

Ensure the required directories exist on Atlas:

mkdir -p /mnt/user/appdata/nextcloud
mkdir -p /mnt/user/appdata/mariadb-nextcloud
mkdir -p /mnt/user/nextcloud-data
SECTION 4 — Deploy MariaDB Container
diff
Copy code
## Step 2 — Deploy MariaDB Container

Install MariaDB (linuxserver.io) using Unraid Apps.

### Configuration

Paths:
- /config → /mnt/user/appdata/mariadb-nextcloud

Environment Variables:
- MYSQL_ROOT_PASSWORD=<strong password>
- MYSQL_DATABASE=nextcloud
- MYSQL_USER=nextcloud
- MYSQL_PASSWORD=<strong password>
- TZ=<your timezone>

Network:
- Bridge

Start the container and wait until it reports running.
SECTION 5 — Deploy Nextcloud Container
markdown
Copy code
## Step 3 — Deploy Nextcloud Container

Install Nextcloud (linuxserver.io) using Unraid Apps.

### Configuration

Paths:
- /config → /mnt/user/appdata/nextcloud
- /data → /mnt/user/nextcloud-data

Environment Variables:
- PUID=99
- PGID=100
- TZ=<your timezone>

Network:
- Bridge

Start the container.
SECTION 6 — Initial Web Setup
yaml
Copy code
## Step 4 — Initial Web Setup

Access the Nextcloud installer:

http://<atlas-ip>:<mapped-port>

### Installer Settings

Admin Account:
- Username: admin (or preferred)
- Password: strong password

Database Configuration:
- Database user: nextcloud
- Database password: <MYSQL_PASSWORD>
- Database name: nextcloud
- Database host: mariadb-nextcloud

WARNING:
Do NOT change the data directory.
It must remain /data.

Click Install.
SECTION 7 — Validate Data Placement
bash
Copy code
## Step 5 — Validate Data Placement

Verify the data directory contents:

ls /mnt/user/nextcloud-data

Expected structure:
- files/
- uploads/
- appdata_*
- .ncdata

If data appears under:
/mnt/user/appdata/nextcloud

STOP — the deployment is invalid.
SECTION 8 — Fix Permissions (If Required)
bash
Copy code
## Step 6 — Fix Permissions (If Required)

If uploads or sync fail, correct ownership:

chown -R 99:100 /mnt/user/nextcloud-data
chown -R 99:100 /mnt/user/appdata/nextcloud

Restart both the Nextcloud and MariaDB containers.
SECTION 9 — Post-Install Health Checks
markdown
Copy code
## Step 7 — Post-Install Health Checks

Run inside the Nextcloud container:

php occ db:add-missing-indices
php occ maintenance:repair --include-expensive

Verify:
- No admin warnings
- Uploads work
- Sync works
SECTION 10 — Validation Checklist & Stop Point
pgsql
Copy code
## Validation Checklist

- Web UI accessible internally
- Data stored under /mnt/user/nextcloud-data
- No files written inside container layers
- Users can upload and sync files

🛑 Stopping Point

Nextcloud is deployed, operational, and migration-safe.
Do NOT expose externally or add a reverse proxy yet.
