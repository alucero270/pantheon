# 3D Scanning — Capture, Processing, and Data Ownership

This document defines how 3D scanning workloads are handled
within the homelab, including capture, processing, storage,
and system responsibilities.

This is a service-level document.
SECTION 2 — Service Role
markdown
Copy code
## Service Role

3D scanning services provide:

- Processing of raw scan data
- Alignment and fusion of scans
- Mesh generation and cleanup
- Preparation of scan outputs for downstream use

3D scanning services do not perform scan capture.
They operate exclusively on existing scan data.
SECTION 3 — Capture vs Processing Model
csharp
Copy code
## Capture vs Processing Model

3D scanning is intentionally split into two phases:

- Capture
- Processing

This separation exists due to hardware, thermal,
and memory constraints on capture devices.
SECTION 4 — Capture Phase (External)
vbnet
Copy code
## Capture Phase (External)

Scan capture occurs outside the homelab environment.

Characteristics:

- Performed on dedicated scanning hardware or workstation
- Produces raw scan data
- Raw data is transferred to Atlas after capture

Capture devices do not perform heavy processing.
SECTION 5 — Processing Phase (Homelab)
markdown
Copy code
## Processing Phase (Homelab)

Processing occurs on Prometheus.

Responsibilities include:

- Aligning scan passes
- Fusing point clouds
- Generating meshes
- Running texturing workflows
- Handling memory-intensive operations

Prometheus is selected due to:
- High CPU availability
- High memory capacity
- Optional GPU acceleration
SECTION 6 — System Responsibilities
markdown
Copy code
## System Responsibilities

Responsibilities are divided as follows:

- Prometheus:
  - Executes 3D scan processing workloads
  - Hosts processing software and VMs
  - Uses local scratch space for intermediate data

- Atlas:
  - Stores raw scan inputs
  - Stores finalized scan outputs
  - Acts as the authoritative data store
SECTION 7 — Data Classification
markdown
Copy code
## Data Classification

### Authoritative Data (Atlas)

- Raw scan files
- Final meshes
- Cleaned and exported models
- Outputs required for reuse or archiving

### Disposable Data (Prometheus)

- Intermediate processing artifacts
- Temporary alignment data
- Scratch working directories

Disposable data is not backed up.
SECTION 8 — Data Flow
kotlin
Copy code
## Data Flow

1. Raw scan data is captured externally
2. Raw data is transferred to Atlas
3. Prometheus mounts scan data from Atlas
4. Processing occurs on Prometheus
5. Final outputs are written back to Atlas
6. Intermediate data is discarded
SECTION 9 — Network & Access Constraints
pgsql
Copy code
## Network & Access Constraints

- 3D scanning services run within the SERVERS VLAN
- No user devices directly access Prometheus processing storage
- Administrative access is restricted to MGMT VLAN
- No external exposure is permitted
SECTION 10 — Relationship to AI Services
markdown
Copy code
## Relationship to AI Services

3D scanning workflows may leverage AI services for:

- Mesh cleanup assistance
- Feature recognition
- Post-processing automation

AI services follow the same data authority rules:
- Compute on Prometheus
- Persistence on Atlas
SECTION 11 — Explicit Non-Goals
markdown
Copy code
## Explicit Non-Goals

3D scanning services must not:

- Perform scan capture
- Act as authoritative storage
- Persist intermediate data long-term
- Bypass the data strategy
- Introduce cloud dependencies
SECTION 12 — Stopping Point
pgsql
Copy code
🛑 Stopping Point

3D scanning services are defined as
compute-heavy, data-consumptive workloads.

All authoritative scan data resides on Atlas.
All processing occurs on Prometheus.
