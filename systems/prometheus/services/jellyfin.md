---
type: service
service_name: jellyfin
status: Needs validation
last_updated: 2026-05-16
---

# Jellyfin

## Purpose

Jellyfin is the media streaming service for Pantheon.

This document is a scaffold. It does not claim Jellyfin is deployed on Prometheus until validated by repository evidence or an approved live inventory run.

## Hosting

- **System:** [[systems/prometheus]]
- **Runtime:** Docker (Needs validation)
- **Compose path:** Needs validation

## Storage Authority

Jellyfin must not become authoritative storage.

Media libraries are authoritative on [[systems/atlas]] per:

- [[decisions/ADR-002-atlas-as-storage]]
- [[decisions/ADR-005-atlas-share-storage-model]]
- [[systems/atlas/architecture/storage-authority-map]]

## Data Paths

Host paths and container paths are `Needs validation`.

Expected model (must be validated before change):

- Prometheus consumes media read-only from Atlas (NFS preferred)
- Jellyfin config/runtime data is persistent runtime (service-critical), but not authoritative user data
- Target media mount: `/mnt/atlas/managed-media:/media:ro`
- Do not mark Jellyfin as deployed on Prometheus until live state is validated.

## Ports / Exposure

Needs validation.

Requirements:

- No WAN exposure
- Do not expose admin surfaces to USER or GUEST VLANs without explicit approval and firewall policy

## Dependencies

- Atlas media shares (authoritative)
- Prometheus Docker/runtime
- Network ingress policy (if exposed via Traefik): [[systems/prometheus/services/traefik]]

## Lifecycle Classification

See [[decisions/ADR-010-container-lifecycle-policy-prometheus]].

Initial classification (scaffold):

- Media library data: Authoritative on Atlas
- Jellyfin config/runtime: Persistent runtime (Needs validation)
- Transcode/cache: Disposable runtime (Needs validation)

## Recommended Action

- Treat Jellyfin-on-Prometheus as a migration candidate.
- Do not remove any Jellyfin instance from Atlas until:
  - compose source is documented
  - host paths and volumes are mapped
  - rollback is documented
  - library paths are validated
  - network exposure rules are validated

## Validation Commands

Run only when explicitly approved on Prometheus.

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | rg -i 'jellyfin'
docker inspect jellyfin
```

## Related Docs

- [[systems/prometheus/inventory]]
- [[systems/prometheus/architecture/compose-registry]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
