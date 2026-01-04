# ADR 0002: Atlas as Authoritative Storage

### Status: Accepted

## Context

The homelab requires a single, authoritative storage location to ensure that critical data (media, user files, backups, etc.) remains consistent and safe. Multiple systems in the environment may generate or process data, but only Atlas should be responsible for the authoritative storage.

## Decision

All persistent and authoritative data will reside on Atlas, the Unraid-based NAS. Atlas will handle:

Storage of media, backups, application data, and user files

Mounting data to Prometheus and other compute nodes for processing

Prometheus will never be responsible for storing authoritative data. Its role is solely compute-focused.

## Consequences

Atlas must remain stable and protected, as data loss would have significant impact on the entire system

Compute nodes (e.g., Prometheus) must always access data on Atlas via network mounts (e.g., NFS, SMB)

Data integrity and recovery procedures must focus on Atlas
