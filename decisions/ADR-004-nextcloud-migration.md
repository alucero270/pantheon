# ADR-004: Nextcloud Migration-Safe Deployment Model

## Status
Accepted

## Context
Nextcloud is a critical user-facing service with persistent data and
stateful configuration.

The service must survive:
- Compute rebuilds
- Container redeployments
- Host migration

Without requiring data migration or reconfiguration.

Constraints:
- Containerized deployment
- Atlas as authoritative storage
- Prometheus as compute

## Decision
Deploy Nextcloud in a **migration-safe model** where:

- All data and configuration live on Atlas
- Containers are stateless
- Compute location is interchangeable
- Identical paths are preserved across hosts

## Rationale
This approach:
- Eliminates reinstallation risk
- Prevents data duplication
- Enables lift-and-shift migration
- Aligns with disposable compute principles

## Consequences
- Volume paths must never change
- Initial setup requires discipline
- Storage availability is critical
- Service migration becomes trivial

## Alternatives Considered
- Local container storage (rejected due to data loss risk)
- SQLite-based deployment (rejected due to scale and locking issues)

## Related Documents
- services/nextcloud.md
- procedures/nextcloud-migration.md
- architecture/data-strategy.md

---

**Date:** 2026-01-XX  
**Author:*Alex
