# Changelog

This changelog records significant documentation changes
to the homelab repository.

Entries reflect:
- What changed
- When it changed
- Which sections were affected

This file tracks documentation evolution, not runtime changes.

## Changelog Rules

- Only completed and committed work is recorded
- No speculative or future changes are listed
- Entries describe documentation scope, not implementation detail
- New architectural decisions are logged when documented

## [2026-05] System-Domain Documentation Restructure

### Summary

Reallocated Pantheon documentation into system-owned domains after validating `TODO.md` against current repository structure and open GitHub issues.

Future work that remains open is tracked in GitHub issues or the branch validation queue. `TODO.md` now preserves the branch validation queue instead of duplicating issue-tracked backlog items.

### Architecture

- Moved network architecture under `systems/network/architecture/`
- Moved Atlas storage and media architecture under `systems/atlas/architecture/`
- Added placeholder Prometheus architecture index under `systems/prometheus/architecture/`
- Removed redundant root architecture indexes after all architecture docs were allocated

### Systems

- Established `systems/network` as the domain for Cerberus, Axon, access points, VLANs, DNS, DHCP, ingress, and remote access
- Kept `systems/atlas` as the data and storage system
- Kept `systems/prometheus` as the compute, runtime, and AI system

### Services

- Moved Atlas services under `systems/atlas/services/`
- Moved Prometheus services under `systems/prometheus/services/`
- Removed redundant root service indexes after service docs were allocated

### Procedures

- Moved network procedures under `systems/network/procedures/`
- Moved Atlas procedures under `systems/atlas/procedures/`
- Moved Prometheus procedures under `systems/prometheus/procedures/`
- Copied the branch validation queue into `TODO.md`
- Removed redundant root procedure indexes after procedure docs were allocated

### Repository

- Updated README, REFERENCES, AGENTS, template references, and ADR references for the system-domain structure
- Preserved unresolved branch work as `Needs validation`

##[2026-01] Added remaining HDD drives
### Summary

Added missing HDD to Atlas.

### Architecture
-  1 x 4tb is used as the parity drive.
-  1x 4tb added for storage. 

### Systems
- Atlas

### Services
- <changes>

### Procedures
- <changes>

### Repository
- <changes>


## [2026-01] Documentation Normalization & Structuring

### Summary

Initial normalization of existing homelab documentation into
a structured, reproducible repository layout.

No new architecture was introduced.
All content was sourced from existing notes and build records.

### Architecture

- Created [[systems/atlas/architecture/data-strategy]]
- Created architecture/media-architecture.md
- Formalized zero-trust, data authority, and storage boundaries

### Systems

- Documented Cerberus (OPNsense firewall)
- Documented Axon (Cisco SG350 core switch)
- Documented Atlas (Unraid NAS)
- Documented Prometheus (compute node)
- Documented wireless access points

### Services

- Documented Nextcloud (migration-safe deployment model)
- Documented AI services (compute-only workloads)
- Documented 3D scanning services (capture vs processing model)
- Documented media data flow and service boundaries

### Procedures

- Added Nextcloud deployment procedure
- Added Nextcloud migration procedure
- Added network rebuild procedure
- Added Atlas recovery procedure

### Repository

- Introduced structured directory layout:
  - architecture/
  - systems/
  - services/
  - procedures/
- Added TODO.md to track future documentation work
- Established changelog framework

# TEMPLATE

## [YYYY-MM] <Title>

### Summary

Brief description of the documentation change.

### Architecture
- <changes>

### Systems
- <changes>

### Services
- <changes>

### Procedures
- <changes>

### Repository
- <changes>

## 🛑 Stopping Point

This changelog reflects the current state of documented work.

Future updates should append new entries using the template above.
