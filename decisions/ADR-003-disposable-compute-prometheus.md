# ADR-003: Disposable Compute Node (Prometheus)

## Status
Accepted

## Context
Prometheus is intended to run compute-heavy workloads including:
- AI inference
- Media services
- 3D scanning processing
- Containers and VMs

These workloads should not introduce data coupling or recovery complexity.

Constraints:
- Single primary compute node
- GPU acceleration
- Network-attached storage available

## Decision
Treat **Prometheus** as a **disposable compute node**.

Prometheus:
- Performs computation only
- Does not store authoritative data
- May be rebuilt or replaced without data migration

All persistent data must reside on Atlas.

## Rationale
This model:
- Simplifies recovery
- Encourages clean separation of concerns
- Allows aggressive experimentation on compute
- Reduces fear of failure

## Consequences
- Prometheus rebuild procedures must be documented
- Local data loss is expected and acceptable
- Performance depends on network storage availability
- Clear distinction between compute and storage roles

## Alternatives Considered
- Persistent compute node (rejected due to recovery complexity)
- Hyperconverged model (rejected due to tight coupling)

## Related Documents
- architecture/data-strategy.md
- services/ai.md
- services/3d-scanning.md
- systems/prometheus.md

---

**Date:** 2026-01-XX  
**Author:**
