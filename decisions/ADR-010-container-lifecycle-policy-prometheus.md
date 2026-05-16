# ADR-010: Prometheus Container Lifecycle Policy

## Status
Proposed (Needs validation)

## Context
Pantheon runs multiple services on [[systems/prometheus]].

Not all containers, volumes, and compose stacks have the same importance or recovery cost. Treating every container as equally important causes:

- unsafe cleanup decisions
- unclear backup obligations
- untracked drift in compose sources and data paths
- accidental elevation of Prometheus into an authoritative storage role

Pantheon must preserve the existing architecture:

- Atlas is the authoritative storage system: [[decisions/ADR-002-atlas-as-storage]]
- Atlas authoritative shares are array-only: [[decisions/ADR-005-atlas-share-storage-model]]
- Prometheus is disposable compute: [[decisions/ADR-003-disposable-compute-prometheus]]

## Decision
Adopt an explicit container lifecycle classification policy for Prometheus.

The lifecycle class of a container/stack determines:

- backup requirements
- cleanup and pruning decisions
- rebuild and rollback procedures
- what is tracked in Git
- how the service may depend on Atlas

Unknown containers/volumes must be investigated before deletion.

## Lifecycle Classes

| Class | Definition | Prometheus Rule |
|---|---|---|
| Authoritative | Sole source of truth for important data | Prometheus containers must not be authoritative without a separate ADR |
| Persistent runtime | Operational state needed to restore a service, but not the human/source data authority | Allowed if documented and recoverable |
| Disposable runtime | Cache, downloaded models, generated state, or rebuildable local runtime data | Allowed; cleanup only after impact validation |
| Experimental | Trial, temporary, or exploratory container/stack | Must be isolated and easy to remove |
| Unknown | Container/volume/path with unclear owner or data role | Must be investigated before deletion |

## Class Effects

| Class | Backup Requirement | Cleanup Decision | Rebuild Procedure | Git Tracking | Atlas Dependency |
|---|---|---|---|---|---|
| Authoritative | Required before any change | Do not clean up from Prometheus without ADR and migration plan | Restore from Atlas-backed source of truth | Must be documented and linked to ADR | Must live on or be promoted to Atlas |
| Persistent runtime | Required if needed for service continuity | Clean only after export/backup and rollback plan | Rebuild from Git plus backed-up runtime data | Compose/config Git-tracked; local secrets excluded | May depend on Atlas for authoritative data |
| Disposable runtime | Not required unless explicitly promoted | Clean after validation and service stop plan | Rebuild from Git, package/image pulls, or documented procedure | Compose/config tracked; cache/state usually not tracked | Should not depend on Atlas except for inputs/outputs |
| Experimental | Optional; usually none | Remove after owner confirms no retained data | Recreate from notes or branch if still needed | Track only if becoming repeatable | Must not write authoritative data |
| Unknown | Required to investigate before action | Do not delete | Determine owner, compose source, volumes, ports, and data role first | Add inventory entry before action | Needs validation |

## Examples (Current Repo Evidence)

| Container / Stack | Current Class | Evidence | Notes |
|---|---|---|---|
| `comfy` / ComfyUI | Disposable runtime | [[systems/prometheus/services/comfyui]], [[decisions/ADR-006-comfyui-storage-constraints]] | Local state and outputs are rebuildable unless promoted to Atlas |
| `ollama` | Disposable runtime | [[systems/prometheus/services/ollama]] | Model cache is rebuildable by current docs |
| `openwebui` | Disposable runtime (may become persistent runtime later) | [[systems/prometheus/services/openwebui]] | Current docs treat state as disposable; revisit if it becomes production-facing |
| Reverse proxy (Traefik) | Persistent runtime | [[systems/prometheus/services/traefik]], [[systems/prometheus/procedures/reverse-proxy]] | Config and cert handling are service-critical; Git/source of truth needs validation |
| Media/VPN stack (`/opt/vpn`) | Unknown / Needs validation | [[systems/prometheus/inventory]], [[systems/prometheus/architecture/compose-registry]] | Do not delete or migrate until compose, volumes, secrets, and Atlas media paths are mapped |
| `anemoi` | Unknown / Experimental candidate | [[systems/prometheus/inventory]] | Investigate before deletion |
| `gemma-192k` | Unknown / Experimental candidate | [[systems/prometheus/inventory]] | Investigate whether it is model/runtime residue before deletion |
| Anonymous Docker volumes | Unknown / Cleanup candidate | [[systems/prometheus/inventory]] | Inspect volume ownership before pruning |

## Consequences

- Cleanup work must be driven by [[systems/prometheus/inventory]] and the compose registry.
- Unknown containers and volumes create a hard stop until investigated.
- Git must track sanitized compose and docs, not secrets.
- Prometheus remains disposable compute; important outputs must be promoted to Atlas to become authoritative.

## Related Documents

- [[systems/prometheus/inventory]]
- [[systems/prometheus/architecture/compose-registry]]
- [[systems/atlas/architecture/data-strategy]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[systems/atlas/architecture/storage-authority-map]]

---

**Date:** 2026-05-16  
**Author:** Needs validation
