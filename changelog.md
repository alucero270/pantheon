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

## [2026-01] Documentation Normalization & Structuring

### Summary

Initial normalization of existing homelab documentation into
a structured, reproducible repository layout.

No new architecture was introduced.
All content was sourced from existing notes and build records.

### Architecture

- Created architecture/data-strategy.md
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
