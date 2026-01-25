---
type: service
service_name: openwebui
status: active
last_updated: 2026-01-25
---

# OpenWebUI

## Purpose
OpenWebUI provides a **web-based user interface for interacting with large language models** hosted by [[services/ollama]].

It serves as the primary human-facing UI for LLM experimentation on [[systems/prometheus]].

---

## Hosting
- **System:** [[systems/prometheus]]
- **Runtime:** Docker container (`openwebui`)
- **Dependencies:** [[services/ollama]]

---

## Data Classification
- **Authoritative:** no
- **Runtime:** yes
- **Disposable:** yes

All OpenWebUI state is treated as disposable compute data.

---

## Storage Paths

| Path | Read/Write | Description |
|-----|-----------|-------------|
| `/mnt/local/ssd/ai/projects/openwebui` | RW | Application state, users, settings |

Mounted into the container at:
- `/app/backend/data`

---

## Configuration

### Environment Variables
- `OLLAMA_BASE_URL=http://ollama:11434`

### Ports
- `127.0.0.1:3000 -> 8080/tcp`

### Volumes
- `/mnt/local/ssd/ai/projects/openwebui:/app/backend/data`

---

## Access

### Local Access (on Prometheus)
- `http://127.0.0.1:3000`

### Remote Access
Remote access is performed via SSH tunneling when required (see [[procedures/prometheus-ai-stack-bringup]]).

OpenWebUI communicates with Ollama over the Docker network and does not require direct LAN access to Ollama.

---

## Security Notes
- Service is bound to **localhost** only
- No direct LAN exposure
- Authentication is handled internally by OpenWebUI

---

## Backup Strategy
- **Backed up:** no
- **Rationale:** user data and settings are disposable and can be recreated

If OpenWebUI becomes multi-user or production-facing, revisit this decision.

---

## Monitoring & Health

### Basic health
```bash
curl -I http://127.0.0.1:3000
```

### Container state
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^openwebui\b"
```

---

## Upgrade Strategy
- Upgrades performed by updating the container image
- Database migrations handled automatically by the application

---

## Known Issues
- None recorded.

---

## Related Docs
- **Services:** [[services/ollama]], [[services/comfyui]]
- **Procedures:** [[procedures/prometheus-ai-stack-bringup]]
- **Architecture:** [[architecture/data-strategy]]

