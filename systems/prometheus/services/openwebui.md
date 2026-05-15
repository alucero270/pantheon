---
type: service
service_name: openwebui
status: active
last_updated: 2026-01-25
---
---

## type: service
service_name: openwebui
status: active
host: prometheus
exposure: localhost-only
last_updated: 2026-02-02

# OpenWebUI

## Purpose

OpenWebUI provides the primary **human-facing UI** for interacting with local LLMs hosted by [[systems/prometheus/services/ollama]] on [[systems/prometheus]].

It is used for:

- Interactive chat and prompt experimentation

- UX evaluation of model behavior

- Validating constraints and tuning decisions (latency, context, VRAM)

- Early validation of future routing strategies


OpenWebUI is **not** authoritative storage.

---

## Hosting

- **System:** [[systems/prometheus]]

- **Runtime:** Docker container (`openwebui`)

- **Dependency:** [[systems/prometheus/services/ollama]]


---

## Network & Access

- Bound to **localhost only**

- Exposed port:

    - `127.0.0.1:3000 -> 8080/tcp`


### Local Access (on Prometheus)

- `http://127.0.0.1:3000`


### Remote Access

Remote access is via SSH tunneling only.

See:

- [[systems/prometheus/procedures/ai-stack-initialization]]


---

## Data Classification

- **Authoritative:** no

- **Runtime:** yes

- **Disposable:** yes


All OpenWebUI state is treated as disposable compute data.

---

## Storage Paths

|Path|Read/Write|Description|
|---|---|---|
|`/mnt/local/ssd/ai/projects/openwebui`|RW|App state (users, chats, settings)|

Mounted into the container:

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

## Operational Notes

- OpenWebUI may surface `500` errors that originate from Ollama (e.g., model load failures, VRAM allocation failures).

- CLI success does **not** guarantee UI success due to:

    - Different request patterns

    - Model switching

    - Keepalive behavior

    - Potential concurrency


---

## Security Notes

- Service is bound to **localhost** only

- No direct LAN exposure

- Authentication is handled internally by OpenWebUI


---

## Backup Strategy

- **Backed up:** no

- **Rationale:** OpenWebUI is disposable and can be recreated


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

- Update container image

- App handles internal migrations automatically


---

## Known Issues

- None recorded.

---

## Related Docs

- **Services:** [[systems/prometheus/services/ollama]], [[systems/prometheus/services/comfyui]]
- **Procedures:** [[systems/prometheus/procedures/ai-stack-initialization]]
- **Architecture:** [[systems/atlas/architecture/data-strategy]]
## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker web UI; Needs validation |
| Source of truth | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Config path | Needs validation |
| Data path | Needs validation |
| Secret requirements | Do not commit secrets |
| Network ports | Needs validation |
| Dependencies | [[systems/prometheus/services/ollama]], Docker, ingress path if exposed |
| Backup requirement | Needs validation |
| Validation command | Needs validation |
| Recovery procedure | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Automation classification | Needs validation |
| Preferred automation tool | Ansible candidate after compose inventory |
