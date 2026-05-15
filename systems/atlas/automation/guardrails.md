# Atlas Automation Guardrails

## Purpose

Atlas automation is intentionally restricted because Atlas is the authoritative storage system.

Mistakes in this domain can cause data loss.

## Initial Classification

`Do not automate storage yet`

## Do Not Automate Yet

- disk assignment
- array configuration
- parity configuration
- share deletion
- share migration
- authoritative data paths
- destructive storage operations

## Possible Future Candidates

Possible future automation candidates after validation:

- read-only inventory
- backup validation
- NFS/SMB export documentation checks
- Docker service documentation validation
- non-destructive health checks

## Required Before Automation

- verified backup strategy
- restore procedure
- export of current configuration
- dry-run workflow
- rollback procedure
- validation checklist

## Related Docs

- [[systems/atlas/architecture]]
- [[systems/atlas/services]]
- [[systems/atlas/procedures]]
- [[automation/policies/automation-classification]]
