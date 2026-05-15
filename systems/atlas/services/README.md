# Atlas Services

## Folder Purpose

This folder contains services owned by Atlas.

## Service Documentation Requirements

Each service document should include:

- purpose
- hosting system
- runtime type
- dependencies
- storage paths
- config paths
- ports / exposure
- data classification
- backup posture
- validation commands
- related docs
- automation classification

## Service Index

- [[systems/atlas/services/nextcloud]]
- [[systems/atlas/services/mariadb]]
- [[systems/atlas/services/redis]]

## What To Avoid

- Do not hide persistent data paths.
- Do not omit exposed ports.
- Do not treat container-layer state as authoritative.
- Do not document future services as deployed.
