# ADR-002: Atlas as Authoritative Storage

## Status
Accepted

## Context
Multiple systems in the homelab consume and process data, including media,
documents, AI workloads, and 3D scanning.

Without a single authoritative storage system, data duplication,
inconsistency, and loss risk increase significantly.

Constraints:
- Limited number of systems
- Need for migration-safe services
- Desire for simple backup scope

## Decision
Designate **Atlas** as the **single authoritative storage system**.

All persistent data must reside on Atlas, including:
- User data
- Media libraries
- Application data
- Databases
- Scan outputs

Other systems may consume data but must not be authoritative.

## Rationale
Centralizing data authority simplifies:
- Backup strategy
- Recovery planning
- Migration
- Operational reasoning

It also allows compute systems to remain disposable.

## Consequences
- Atlas is a critical system requiring protection and backups
- Network mounts become foundational infrastructure
- Storage performance impacts multiple services
- Compute failures do not result in data loss

## Alternatives Considered
- Distributed storage across compute nodes (rejected due to complexity)
- Per-service storage ownership (rejected due to migration difficulty)

## Related Documents
- architecture/data-strategy.md
- architecture/media-architecture.md
- systems/atlas.md

---

**Date:** 2026-01-XX  
**Author:** Alex
