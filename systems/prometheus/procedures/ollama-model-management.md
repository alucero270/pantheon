# Procedure — Prometheus Ollama Model Installation & Modelfile Management

## Status
Active

---

## Purpose

Define the standardized process for:

- Installing new Ollama base models
- Creating and modifying Modelfiles
- Building derived (tuned) models
- Validating GPU utilization
- Removing unused models safely

This ensures storage discipline, predictable VRAM usage, and reproducible model behavior.

---

## Scope

**System:** Prometheus (Ubuntu compute node)  
**Service:** Ollama (Docker container)  
**Storage Tiers:**

- NVMe (performance tier) — model blobs
- SSD (configuration tier) — Modelfiles

---

# 1. Storage Architecture (Authoritative)

### Base Model Storage (NVMe)
Host path:
```
/mnt/local/nvme/ai/services/ollama
```
Container path:
```
/root/.ollama
```

Contains:
- GGUF blobs
- Built model artifacts
- Model metadata

---

### Modelfile Storage (SSD)
Host path:
```
/mnt/local/ssd/ai/modelfiles
```
Container path (read-only):
```
/modelfiles
```

Modelfiles are configuration artifacts and should be version-controlled.

---

# 2. Installing a New Base Model

## Step 1 — Pull Model

```bash
docker exec -it ollama ollama pull <model-name>
```

Example:

```bash
docker exec -it ollama ollama pull qwen3:30b
```

---

## Step 2 — Verify Installation

```bash
docker exec -it ollama ollama list
```

Confirm:
- Model appears
- Correct size
- No duplicate tags

---

## Step 3 — Confirm Storage Location

```bash
docker inspect ollama | grep -A5 Mounts
```

Ensure `/root/.ollama` maps to NVMe storage.

---

# 3. Creating a Modelfile

## Step 1 — Create on Host (SSD Tier)

```bash
sudo nano /mnt/local/ssd/ai/modelfiles/<model-name>.Modelfile
```

---

## Standard Modelfile Template

```dockerfile
FROM <base-model>

# Context window control
PARAMETER num_ctx 8000

# Partial GPU offload (tune for 20GB GPU)
PARAMETER num_gpu 19

# Reduce memory spikes
PARAMETER num_batch 256

# Generation defaults
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

Notes:
- `num_ctx` controls KV cache growth
- `num_gpu` controls partial GPU offload
- `num_batch` controls peak allocation pressure

---

# 4. Building a Derived Model

```bash
docker exec -it ollama ollama create <new-tag> \
  -f /modelfiles/<model-name>.Modelfile
```

Example:

```bash
docker exec -it ollama ollama create qwen3-30b-stable \
  -f /modelfiles/qwen3-30b.Modelfile
```

---

## Verify Build

```bash
docker exec -it ollama ollama list
```

Ensure the new tag exists and size is correct.

---

# 5. Testing GPU Utilization

## Run Model

```bash
docker exec -it ollama ollama run <model-tag>
```

---

## Monitor GPU

In separate terminal:

```bash
watch -n 0.5 nvidia-smi
```

Expected:
- VRAM allocation increases
- GPU utilization > 0%

---

## Verify Processor Split

```bash
docker exec -it ollama ollama ps
```

Confirm GPU/CPU ratio under `PROCESSOR` column.

---

# 6. Modifying an Existing Model

1. Edit Modelfile on host.

```bash
sudo nano /mnt/local/ssd/ai/modelfiles/<model>.Modelfile
```

2. Rebuild with a new tag.

```bash
docker exec -it ollama ollama create <new-tag> \
  -f /modelfiles/<model>.Modelfile
```

Do not overwrite production tags without validation.

---

# 7. Removing Models

## Remove Derived Model

```bash
docker exec -it ollama ollama rm <model-name>
```

---

## Remove Base Model

```bash
docker exec -it ollama ollama rm <base-model>
```

---

## Verify Cleanup

```bash
docker exec -it ollama ollama list
```

Then confirm disk space:

```bash
df -h
```

---

# 8. Performance Guardrails (RTX 4000 Ada – 20GB)

Recommended ranges:

| Parameter | Suggested Range |
|------------|-----------------|
| num_ctx | 3000–8000 |
| num_gpu | 17–19 |
| num_batch | 128–256 |
| KV cache | q8_0 |

If CUDA OOM occurs:
- Reduce `num_ctx`
- Reduce `num_batch`

If CPU load too high:
- Increase `num_gpu`

---

# 9. Validation Checklist

Before promoting a model to default:

- [ ] Model loads without CUDA OOM
- [ ] GPU utilization confirmed
- [ ] Stable under 3+ prompts
- [ ] Context window validated
- [ ] Disk usage verified

---

# 10. Change Control

When adding or modifying models:

- Update AI tuning notes
- Update AI service documentation
- Record change in changelog

---

End of Procedure

