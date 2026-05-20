# AI Services - Compute & Inference

Last validated: 2026-05-20

This document defines the role of AI workloads within the homelab, their relationship to compute and storage systems, and the constraints under which they operate.

This is a service-level document. It describes what runs, where it runs, and what it depends on.

## Service Role

AI workloads provide:

- local inference
- model experimentation
- data processing assistance
- compute acceleration for other services

AI workloads are compute-intensive and ephemeral by design. They do not own authoritative data.

## System Responsibilities

AI services are split across systems as follows:

- Prometheus - AI compute and execution
- Atlas - authoritative storage for inputs and retained outputs

This separation is intentional and enforced.

## Prometheus - AI Compute Node

Prometheus is responsible for:

- running AI inference workloads
- hosting AI runtimes and containers
- utilizing GPU acceleration where available
- processing data sourced from Atlas

Prometheus may be rebuilt without loss of authoritative AI data.

## Data Interaction Model

AI workloads interact with data as follows:

- Input data is read from Atlas when it is authoritative.
- Processing occurs on Prometheus.
- Outputs are written back to Atlas if retained.
- Temporary artifacts remain local to Prometheus.

AI workloads must never be the sole holder of important data.

## Persistent vs Disposable AI Data

### Persistent Data

Stored on Atlas:

- training datasets
- reference datasets
- final inference outputs
- results used by other services

### Disposable Data

Stored on Prometheus:

- model caches
- temporary embeddings
- intermediate tensors
- scratch data
- generated outputs that have not been promoted to Atlas

Disposable AI data is not backed up by current docs.

## GPU Usage Model

GPU acceleration is optional but expected for AI workloads.

Constraints:

- GPU resources belong to Prometheus.
- GPU workloads must not introduce data coupling.
- Loss of GPU availability must not cause authoritative data loss.

GPU enablement and passthrough are documented separately.

## Network & Access Constraints

- AI services run within the SERVERS VLAN.
- Administrative access occurs only via MGMT VLAN.
- User-facing AI surfaces should be exposed through [[systems/prometheus/services/traefik]] where approved.
- Direct host port exposure should be avoided unless explicitly documented.
- Public WAN exposure is explicitly disallowed at this stage.

## Explicit Non-Goals

AI services must not:

- act as authoritative storage
- replace cloud-scale AI platforms
- be exposed publicly
- require authoritative state on compute nodes
- bypass network segmentation

## Deployed AI Services

The following AI services are currently deployed on Prometheus:

- [[systems/prometheus/services/comfyui]] - node-based image and media generation
- [[systems/prometheus/services/llamacpp]] - local GGUF runtime and active llama.cpp router
- [[systems/prometheus/services/llama-swap]] - OpenAI-compatible model switching proxy for llama.cpp-compatible backends
- [[systems/prometheus/services/ollama]] - local LLM runtime and inference API
- [[systems/prometheus/services/openwebui]] - human-facing UI for LLM interaction
- [[systems/prometheus/services/searxng]] - local metasearch service intended for OpenWebUI web-search tooling

## Current Compose and Ingress State

Live state observed on 2026-05-17:

| Service | Container | Image | Compose Path | Access |
|---|---|---|---|---|
| ComfyUI | `comfy` | `mmartial/comfyui-nvidia-docker:latest` | `/home/alex/stacks/ai/docker-compose.yml` | Traefik route `comfy.home.arpa`; no host port |
| llama.cpp router | `llamacpp-router.service` | Native `llama-server` from `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant` | `/mnt/local/nvme/ai/profiles/start-scripts/llama-router.sh`; `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | `172.17.0.1:8084`; local API key |
| llama-swap | `llama-swap.service` | Native `llama-swap` v214; MTP/NextN models use `/mnt/local/nvme/ai/runtimes/atomic-llama-cpp-turboquant/build/bin/llama-server` | `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` | `172.17.0.1:8085`; local API key |
| Ollama | `ollama` | `ollama/ollama:latest` | `/home/alex/stacks/ai/docker-compose.yml` | Host port `127.0.0.1:11434`; live Traefik route `ollama.home.arpa` needs decision |
| OpenWebUI | `openwebui` | `ghcr.io/open-webui/open-webui:latest` | `/home/alex/stacks/ai/docker-compose.yml` | Traefik route `openwebui.home.arpa`; no host port |
| SearXNG | `searxng`, `searxng-redis` | `searxng/searxng:latest`, `redis:7-alpine` | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | Traefik route `searxng.home.arpa`; no host port |

Ollama's live Traefik route is drift from [[decisions/ADR-007-centralized-ingress-on-prometheus]], which says Ollama remains internal-only and is not routed.

## Relationship to Other Services

AI services may support:

- media processing workflows
- 3D scanning post-processing
- data analysis tasks
- automation and assistance tools

These integrations must respect data authority rules.

## Planned AI Service Candidates

- [[systems/prometheus/services/voice-agent]] - planned Pipecat-based realtime voice interface beside [[systems/prometheus/services/openwebui]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | AI runtime service group |
| Source of truth | [[systems/prometheus/procedures/ai-stack-initialization]], service docs, and validated compose paths |
| Config path | `/home/alex/stacks/ai/docker-compose.yml`; `/mnt/local/ssd/ai/services/searxng/docker-compose.yml`; service-specific config paths |
| Data path | Prometheus local disposable/persistent-runtime storage by service |
| Secret requirements | Do not commit secrets or model-provider tokens |
| Network ports | See individual service docs; current user-facing access is primarily through Traefik |
| Dependencies | GPU/runtime details, Docker, local storage, service dependencies |
| Backup requirement | No authoritative data; preserve sanitized config and document recovery for persistent runtime paths |
| Validation command | `docker compose ls`; service-specific validation commands |
| Recovery procedure | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Automation classification | Ansible candidate after access-model drift and secrets handling are resolved |
| Preferred automation tool | Ansible |
