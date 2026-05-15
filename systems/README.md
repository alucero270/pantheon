# Systems

## Purpose

This folder contains Pantheon system-domain documentation.

System domains own their local architecture, devices, services, and procedures. Pantheon-wide constraints remain in [[systems/README]] and locked decisions remain in [[decisions/README]].

## Current Systems

- [[systems/network]] - Network domain: firewall, switch, access points, VLANs, DNS, DHCP, ingress, and remote access.
- [[systems/atlas]] - Storage/data domain: Unraid NAS, authoritative storage, and data-adjacent services.
- [[systems/prometheus]] - Compute/runtime domain: Ubuntu compute, containers, AI workloads, ingress runtime, and disposable service execution.

## System Components

- [[systems/network/devices/cerberus]]
- [[systems/network/devices/axon]]
- [[systems/network/devices/access-points]]

## Templates

- Shared system template: [[templates/sytems]]
- Shared fallback templates: [[templates/README]]

## Needs Validation

- Current shared template filename is `sytems.md`; target spelling should be reviewed before any rename.
- Prometheus service inventory candidate exists on `codex/deferred-local-changes`.
