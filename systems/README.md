# Systems

## Purpose

This folder contains documentation for Pantheon infrastructure systems: hosts, firewall/router, switch, NAS, compute node, access points, and related devices.

System docs should keep ownership, responsibilities, non-responsibilities, network placement, data ownership, service ownership, and automation classification explicit.

## Current Systems

- [[systems/cerberus-opensense]] - Cerberus, OPNsense firewall and router.
- [[systems/axon-cisco-sg350]] - Axon, Cisco SG350 core switch.
- [[systems/atlas-unraid]] - Atlas, Unraid NAS and authoritative storage.
- [[systems/prometheus-ubuntu]] - Prometheus, Ubuntu compute and virtualization node.
- [[systems/access-points]] - Access point documentation.
- [[systems/prometheus-services-inventory]] - Prometheus service inventory.

## Target System Folders

Pass 2 should create or validate:

- `systems/cerberus/`
- `systems/axon/`
- `systems/atlas/`
- `systems/prometheus/`

Each system folder should include `README.md`, `REFERENCES.md`, `services/`, and `procedures/` indexes before service documents are moved.

## Templates

- Folder-local template: [[systems/sytems-template]]
- Shared fallback templates: [[templates/README]]

## Needs Validation

- Current template filename is `sytems-template.md`; target spelling is `systems-template.md`.
- `axon` is the correct spelling; do not use `axion`.
- Current system docs are flat files and should not be moved until Pass 2.
