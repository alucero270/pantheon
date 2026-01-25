---
type: service
service_name: ollama
status: active
last_updated: 2026-01-25
---

# Ollama

## Purpose
Ollama provides a local **LLM runtime and model serving API** for AI workloads on [[systems/prometheus]].

It is consumed primarily by [[services/openwebui]] and may also be used directly by CLI or API clients.

---

## Hosting
- **System:** [[systems/prometheus]]
- **Container / VM:** Docker container (`ollama`)
- **Runtime:** Docker Engine + NVIDIA Container Toolkit

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

---

## Configuration

### Environment variables
- `OLLAMA_HOST=0.0.0.0:11434` (container listens on 11434)

### Volumes
- `/mnt/local/nvme/ai/services/ollama:/root/.ollama`

### Ports
- `127.0.0.1:11434 -> 11434/tcp`

---

## Access

### Local API (on Prometheus)
- `http://127.0.0.1:11434`

### UI Access
- Primary UI is [[services/openwebui]] (which calls Ollama over the Docker network).

Remote access to the API is performed via SSH tunnel when needed (see [[procedures/prometheus-ai-stack-bringup]]).

---

## Security Notes
- Bound to **localhost** by default to avoid LAN exposure.
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

---

## Upgrade Strategy
- Upgrades occur by updating the container image and redeploying the compose stack.
- Any model re-download is acceptable under the disposable compute model.

---

## Known Issues
- None recorded.

---

## Related Docs
- **Procedures:** [[prometheus-ai-stack-initialization]]
- **Services:** [[services/openwebui]], [[services/comfyui]]
- **Architecture:** [[architecture/data-strategy]]

