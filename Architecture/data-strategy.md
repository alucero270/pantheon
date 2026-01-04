# Data Strategy — Authoritative Design

This document defines where data lives, how it is classified,
what is authoritative, and what is disposable.

This is an architectural document.
It defines truth, not procedure.
SECTION 2 — Core Principles
markdown
Copy code
## Core Principles

- Data must have a single authoritative home
- Compute must be disposable
- Loss of compute must not imply loss of data
- Data location determines backup and recovery strategy
- No service may be the sole holder of important data
SECTION 3 — Data Classification Model
markdown
Copy code
## Data Classification Model

All data in the homelab is classified into one of three categories:

1. Authoritative (Persistent)
2. Runtime / Configuration State
3. Disposable / Ephemeral

Each category has different durability and recovery requirements.
SECTION 4 — Authoritative (Persistent) Data
markdown
Copy code
## 1. Authoritative (Persistent) Data

Authoritative data must survive:

- Service restarts
- Compute node rebuilds
- Container redeployments
- Planned migrations

Examples include:

- Family documents
- Media libraries
- Photos
- Backups
- Nextcloud user data
- Application databases
- 3D scan source data and finalized outputs

Authoritative data is never stored exclusively on compute nodes.
SECTION 5 — Runtime / Configuration State
markdown
Copy code
## 2. Runtime / Configuration State

Runtime and configuration data is important, but rebuildable
if preserved correctly.

Examples include:

- Container configuration
- Application appdata
- Databases backing services
- Service metadata

This data:

- Is stored on Atlas
- Is mounted into containers or VMs
- May be regenerated, but should not be casually discarded
SECTION 6 — Disposable / Ephemeral Data
markdown
Copy code
## 3. Disposable / Ephemeral Data

Disposable data may be lost without consequence.

Examples include:

- AI model caches
- Temporary inference artifacts
- Transcoding buffers
- Scratch space
- Temporary VM disks
- Intermediate 3D scan processing files

This data:

- Is never backed up
- Is expected to be regenerated
- Typically lives on Prometheus local storage
SECTION 7 — Storage Authority Declaration
markdown
Copy code
## Storage Authority Declaration

Atlas is the single authoritative storage system.

Atlas is responsible for:

- All persistent data
- All service data directories
- All backups
- All shared datasets

Atlas is not responsible for:

- VM operating system disks
- AI caches
- Compute scratch space
- Temporary processing outputs
SECTION 8 — Compute Relationship (Prometheus)
kotlin
Copy code
## Relationship to Compute (Prometheus)

Prometheus is a compute-only system.

Prometheus:

- Consumes data from Atlas
- Processes data
- Generates outputs

Prometheus must never be the only location of important data.

If Prometheus is lost or rebuilt:
- No authoritative data is lost
- Services can be redeployed
- Data remains intact on Atlas
SECTION 9 — Data Access Protocol Strategy
markdown
Copy code
## Data Access Protocol Strategy

Different consumers require different access models.

### SMB — Human Access

Used by:
- User workstations
- Laptops
- Family devices

Characteristics:
- User authentication
- Familiar workflows
- Interactive file access
SECTION 10 — NFS — Compute Access
markdown
Copy code
### NFS — Compute Access

Used by:
- Prometheus
- Linux VMs
- Containers

Characteristics:
- High throughput
- Stable mounts
- POSIX permissions
- Low overhead

NFS is the preferred protocol for service and compute workloads.
SECTION 11 — Explicit Constraints
pgsql
Copy code
## Explicit Constraints

- No service may store its only copy of data on Prometheus
- No container may rely on container-layer storage for persistence
- Backup scope is determined by data classification
- Data placement must be documented before service deployment
SECTION 12 — Stopping Point
pgsql
Copy code
🛑 Stopping Point

This data strategy is authoritative.

All systems, services, and procedures must conform
to this model unless an explicit architectural change is made.
