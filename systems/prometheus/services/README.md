# Prometheus Services

## Folder Purpose

This folder contains services owned by Prometheus.

## Service Documentation Requirements

Each service document should include:

- purpose
- hosting system
- runtime type
- dependencies
- storage paths
- config paths
- ports / exposure
- data classification
- backup posture
- validation commands
- related docs
- automation classification

## Service Index

- [[systems/prometheus/services/ai-runtime]]
- [[systems/prometheus/services/jellyfin]]
- [[systems/prometheus/services/ollama]]
- [[systems/prometheus/services/openwebui]]
- [[systems/prometheus/services/comfyui]]
- [[systems/prometheus/services/traefik]]
- [[systems/prometheus/services/3d-scanning]]

## What To Avoid

- Do not hide persistent data paths.
- Do not omit exposed ports.
- Do not treat container-layer state as authoritative.
- Do not document future services as deployed.
