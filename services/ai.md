# AI Services — Compute & Inference

This document defines the role of AI workloads within the homelab,
their relationship to compute and storage systems, and the constraints
under which they operate.

This is a service-level document.
It describes what runs, where it runs, and what it depends on.

## Service Role

AI workloads provide:

- Local inference
- Model experimentation
- Data processing assistance
- Compute acceleration for other services

AI workloads are compute-intensive and ephemeral by design.
They do not own data.

## System Responsibilities

AI services are split across systems as follows:

- Prometheus — AI compute and execution
- Atlas — Authoritative storage for inputs and outputs

This separation is intentional and enforced.

## Prometheus — AI Compute Node

Prometheus is responsible for:

- Running AI inference workloads
- Hosting AI runtimes and containers
- Utilizing GPU acceleration (where available)
- Processing data sourced from Atlas

Prometheus may be rebuilt at any time without loss of AI state.

## Data Interaction Model

AI workloads interact with data as follows:

- Input data is read from Atlas
- Processing occurs on Prometheus
- Outputs are written back to Atlas (if retained)
- Temporary artifacts remain local to Prometheus

AI workloads must never be the sole holder of important data.

## Persistent vs Disposable AI Data

### Persistent Data

Stored on Atlas:
- Training datasets
- Reference datasets
- Final inference outputs
- Results used by other services

### Disposable Data

Stored on Prometheus:
- Model caches
- Temporary embeddings
- Intermediate tensors
- Scratch data

Disposable AI data is not backed up.

## GPU Usage Model

GPU acceleration is optional but expected for AI workloads.

Constraints:

- GPU resources belong to Prometheus
- GPU workloads must not introduce data coupling
- Loss of GPU availability must not cause data loss

GPU enablement and passthrough are documented separately.

## Network & Access Constraints

- AI services run within the SERVERS VLAN
- No AI service is exposed directly to USER or GUEST VLANs
- Administrative access occurs only via MGMT VLAN
- External exposure is explicitly disallowed at this stage

## Explicit Non-Goals

AI services must not:

- Act as authoritative storage
- Replace cloud-scale AI platforms
- Be exposed publicly
- Require persistent state on compute nodes
- Bypass network segmentation

## Relationship to Other Services

AI services may support:

- Media processing workflows
- 3D scanning post-processing
- Data analysis tasks
- Automation and assistance tools

These integrations must respect data authority rules.

### Deployed AI Services

The following AI services are currently deployed on Prometheus:

- [[services/comfyui]] — node-based image and media generation
- [[services/ollama]] — local LLM runtime and inference API
- [[services/openwebui]] — human-facing UI for LLM interaction