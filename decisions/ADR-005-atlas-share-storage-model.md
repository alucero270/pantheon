# ADR-004 — Atlas Share Storage Model (Array-Only Authoritative Data)

## Status
**Accepted** — Locked

## Context

Atlas is the authoritative storage system for the homelab.
Its primary responsibility is durability, integrity, and recoverability of data.

During initial configuration, several shares were temporarily configured with
cache involvement, leading to confusion around mover behavior, share mutability,
and data placement.

This ADR formalizes the final storage model for all authoritative data hosted on Atlas.

---

## Decision

All **authoritative data shares** on Atlas are configured as **Array-only**.

### Final Share Model

For authoritative shares:

Primary storage:   Array
Secondary storage: None
Mover action:      Not used (implicit)

This applies to, but is not limited to:

- documents
- shared-media
- managed-media
- photos
- scans
- backups
- nextcloud-data

## Rationale
### Why Array-only?
- Ensures parity protection at write time
- Eliminates cache ambiguity
- Prevents split data paths
- Removes reliance on mover timing
- Aligns with enterprise NAS best practices
- Matches the declared Data Strategy — Authoritative Design
- Why not Cache + Array?
- Cache introduces operational complexity
- Cache failure becomes a data-loss risk
- Mover timing is non-deterministic
- No strong performance requirement for these datasets

### Consequences
__Positive__

Predictable data placement
- Maximum durability
- Simplified mental model
- Clean separation between:
- Authoritative data (Atlas)
- Runtime / compute data (Prometheus)

__Tradeoffs__

- Initial writes are slower than cache-assisted writes
- Acceptable given Atlas’ role as storage-first
- Explicit Non-Goals

#### This ADR does not apply to:

- Appdata
- Container runtime state
- Transcoding buffers
- AI model caches
- Temporary compute artifacts

Those remain cache-backed or compute-local by design.

## Enforcement

- Any share storing authoritative data must be Array-only
- Any deviation requires a new ADR
- Cache usage for authoritative data is prohibited

### Related Documents

- architecture/data-strategy.md
- architecture/atlas.md
- procedures/nextcloud-external-storage.md