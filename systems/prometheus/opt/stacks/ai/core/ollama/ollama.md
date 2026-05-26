---
type: service
service_name: ollama
status: active
last_updated: 2026-01-25
last_validated: 2026-05-17
---

# Ollama

## Purpose
Ollama provides a local **LLM runtime and model serving API** for AI workloads on [[systems/prometheus]].

It is consumed primarily by [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]] and may also be used directly by CLI or API clients.

---

## Hosting
- **System:** [[systems/prometheus]]
- **Container / VM:** Docker container (`ollama`)
- **Runtime:** Docker Engine + NVIDIA Container Toolkit
- **Image:** `ollama/ollama:latest`
- **Compose path:** `/opt/stacks/ai/core/compose.yml`
- **Legacy compose path:** `/home/alex/stacks/ai/docker-compose.yml` symlink

---

## Data Classification
- **Authoritative:** no
- **Runtime:** yes (service state)
- **Disposable:** yes (models/cache can be regenerated)

Ollama data is stored on Prometheus local disks and may be rebuilt.

---

## Storage Paths

| Path | Read/Write | Description |
|-----|-----------|-------------|
| `/mnt/local/nvme/ai/services/ollama` | RW | Ollama state + downloaded models (`/root/.ollama`) |
| `/mnt/local/ssd/ai/modelfiles` | RO in container | Modelfile workspace mounted at `/modelfiles` |

---

## Configuration

### Environment variables
- `OLLAMA_HOST=0.0.0.0:11434` (container listens on 11434)

### Volumes
- `/mnt/local/nvme/ai/services/ollama:/root/.ollama`

### Ports
- `127.0.0.1:11434 -> 11434/tcp`

### Traefik labels

Live state observed on 2026-05-17 includes Traefik labels for `ollama.home.arpa`.

This is drift from [[decisions/ADR-007-centralized-ingress-on-prometheus]], which says Ollama remains internal-only and is not routed. Treat the live route as `Needs decision`: either remove the route from the live compose file or update the accepted ingress decision with explicit approval.

---

## Access

### Local API (on Prometheus)
- `http://127.0.0.1:11434`

### UI Access
- Primary UI is [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]] (which calls Ollama over the Docker network).

Remote access to the API should follow the approved access model. Current live state also exposes an `ollama.home.arpa` Traefik route, but that route conflicts with the accepted ADR and needs a decision.

---

## Security Notes
- Host port is bound to `127.0.0.1` to avoid direct LAN exposure.
- Live Traefik labels route `ollama.home.arpa`; validate and resolve this drift before treating the route as approved.
- No Docker remote API exposure.
- Model directories are treated as disposable; do not store authoritative datasets here.

---

## Backup Strategy
- **Backed up:** no
- **Rationale:** models and cache are disposable and can be re-pulled.

If a model becomes expensive to reproduce (time/bandwidth), revisit this stance and document explicitly.

---

## Monitoring & Health

### Basic health
```bash
curl -I http://127.0.0.1:11434
```

### Container state
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^ollama\b"
```

### Model inventory

```bash
docker exec ollama ollama list
```

---

## Upgrade Strategy
- Upgrades occur by updating the container image and redeploying the compose stack.
- Any model re-download is acceptable under the disposable compute model.

---

## Known Issues
- None recorded.

---

## Related Docs
- **Procedures:** [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]]
- **Services:** [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]]
- **Architecture:** [[systems/atlas/architecture/data-strategy]]


## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker/API runtime |
| Source of truth | `/opt/stacks/ai/core/compose.yml`; [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]] |
| Config path | `/mnt/local/ssd/ai/modelfiles` for Modelfiles |
| Data path | `/mnt/local/nvme/ai/services/ollama` |
| Secret requirements | Do not commit secrets |
| Network ports | `127.0.0.1:11434 -> 11434/tcp`; live Traefik route `ollama.home.arpa` needs decision |
| Dependencies | Docker, model storage, [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]] |
| Backup requirement | Rebuildable; model cache is disposable unless a model becomes expensive enough to document separately |
| Validation command | `docker exec ollama ollama list`; `curl -I http://127.0.0.1:11434` |
| Recovery procedure | [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]] |
| Automation classification | Ansible candidate after access-model drift is resolved |
| Preferred automation tool | Ansible candidate after compose inventory |
