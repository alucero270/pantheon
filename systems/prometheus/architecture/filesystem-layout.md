# Prometheus Filesystem Layout

## Purpose

This document defines the filesystem-mirrored documentation model for [[systems/prometheus]].

Prometheus documentation is organized to match the live host layout. The mirrored documentation tree is canonical for Prometheus service, config, and procedure documentation.

## Layout Model

| Documentation path | Represents | Role |
|---|---|---|
| `systems/prometheus/opt` | `/opt` on Prometheus | Stack definitions, app-owned source trees, operator paths, and local service roots |
| `systems/prometheus/mnt/atlas` | `/mnt/atlas` on Prometheus | Atlas-backed authoritative NFS mounts visible from Prometheus |
| `systems/prometheus/mnt/local/nvme` | `/mnt/local/nvme` on Prometheus | Fast local AI models, runtimes, caches, service mounts, and Docker artifacts needing validation |
| `systems/prometheus/mnt/local/ssd` | `/mnt/local/ssd` on Prometheus | Local service state, project state, outputs, and container runtime storage |

## Current vs Desired Paths

Path pages must distinguish current live state from target normalization work.

Use these labels consistently:

| Label | Meaning |
|---|---|
| Current live path | Path observed on Prometheus or documented from validated live state |
| Desired normalized path | Target path that should exist only after approved migration |
| Status | Active, planned, historical, cleanup candidate, or unknown |
| Authority | Authoritative, persistent runtime, disposable, or unknown |

## Rules

- Do not treat desired normalized paths as implemented facts.
- Do not treat Prometheus-local paths as authoritative without an ADR.
- Keep Git-backed config sanitized and separate from live-only secrets, snapshots, transcripts, voice samples, and generated user data.
- Keep service config notes under the service folder that owns them.
- Keep service procedures under the service folder that owns them.
- Keep old service and procedure folders as indexes only.
- Use `No service-specific procedure documented yet` when a procedure folder exists only as a completeness marker.
- Use `No Git-backed sanitized config documented yet` when a config folder exists only as a completeness marker.

## Service Folder Contract

Each service folder should contain:

| Path | Purpose |
|---|---|
| `README.md` | Service folder index and live/desired path context |
| `<service>.md` | Canonical service document |
| `config/README.md` | Git-backed sanitized config inventory and live config boundaries |
| `procedures/README.md` | Service-specific runbooks and validation procedures |

The `config/` folder is for sanitized desired-state config examples, restore notes, and validation guidance. It must not contain live secrets, API keys, private voice samples, transcripts, generated user data, or host-only sensitive values.

## Related Docs

- [[systems/prometheus/architecture/compose-registry]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/opt/stacks/procedures/config-versioning-and-restore]]
