# Anemoi Integration for OpenCode

## Overview

OpenCode can now use **Anemoi Governed Coding** alongside direct llama-swap models. This provides intelligent model selection and resource management.

## How It Works

### When you select "Anemoi Governed Coding"

1. **Your request** is sent to `https://anemoi.home.arpa/v1/chat/completions`
   - The `model` field is `"coding"` (governance domain)
   - Your code/messages are passed through

2. **Anemoi's decision engine** evaluates:
   - Available resources on each runtime
   - Load and queue depth
   - Your latency requirements
   - Model capabilities needed for the task

3. **Anemoi selects and forwards** to the best-fit runtime
   - Rewrites the request with the actual model ID
   - Injects authentication
   - Streams the response back

4. **Response includes metadata**:
   - `X-Anemoi-Decision-Id`: Unique identifier for this decision
   - `X-Anemoi-Selected-Model`: The actual model used
   - `X-Anemoi-Action`: What anemoi did (mock vs. live)

## Available Models

### Anemoi Governed (Recommended for intelligent selection)

- **Model Name**: Anemoi Governed Coding (dynamic model selection)
- **Use Case**: When you want the best model chosen automatically
- **Performance**: Adapts to load, memory, and context requirements

### Direct llama-swap Models (For specific choices)

- Gemma 4 26B (various quantizations)
- Qwen 3.6 35B (with MTP optimization)
- Qwen 3.5 122B (if you need large context)

These bypass anemoi and go directly to llama-swap.

## Configuration

### models.json Structure

```json
{
  "providers": {
    "prometheus-anemoi": {
      "baseUrl": "https://anemoi.home.arpa/v1",
      "api": "openai-completions",
      "models": [
        {
          "id": "coding",
          "name": "Anemoi Governed Coding (dynamic model selection)"
        }
      ]
    },
    "prometheus-llama-swap": {
      "baseUrl": "https://llama-swap.home.arpa/v1",
      "api": "openai-completions",
      "models": [...]
    }
  }
}
```

## Decision Flow

```
Your Request (with model="coding")
         ↓
Anemoi Endpoint (anemoi.home.arpa)
         ↓
Decision Engine (What's the best model right now?)
         ↓
Forward to Runtime (llama-swap with selected model)
         ↓
Stream Response (with telemetry headers)
         ↓
Your Code (with insights in response headers)
```

## Why Use Anemoi?

✓ **No manual tuning** — Anemoi picks the best model for your context size, load, latency needs
✓ **Automatic fallback** — If preferred model is busy, fall back to faster option
✓ **Transparent decisions** — Every choice is logged with explanation
✓ **Resource aware** — Considers VRAM, RAM, KV cache, active requests

## When to Use Direct Models

- Benchmarking a specific model
- Testing performance baselines
- Requiring deterministic model choice (for reproducibility)
- Troubleshooting model-specific issues

## Troubleshooting

### "Anemoi Governed Coding" not visible

- Verify `models.json` contains the `prometheus-anemoi` provider
- Check that `anemoi.home.arpa` is reachable (`curl http://anemoi.home.arpa/v1/models`)
- Restart OpenCode if needed

### Request fails: "Unknown domain: coding"

- Anemoi daemon is not running or not accessible
- Check Traefik routing on prometheus
- Verify the reverse proxy is forwarding to localhost:7070

### What model was actually selected?

Look at response headers:
- `X-Anemoi-Selected-Model`: The runtime model ID anemoi chose
- `X-Anemoi-Decision-Id`: ID for debugging/logging

## Next Steps

1. Try "Anemoi Governed Coding" for code generation tasks
2. Observe which model is selected for different request types
3. Compare with direct llama-swap models for performance
4. Use decision IDs to correlate requests with anemoi logs
