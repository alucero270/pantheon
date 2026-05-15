# Databases — MariaDB (Nextcloud)

## Purpose

MariaDB provides the relational database backend
for Nextcloud.

SQLite is explicitly disallowed.

---

## Deployment Model

- LinuxServer.io MariaDB container
- Dedicated database for Nextcloud
- Data stored on Atlas

---

## Configuration Constraints

- Database data directory must live on Atlas
- Credentials must not be reused elsewhere
- Database must be reachable only within SERVERS VLAN

---

## Known Version Note

MariaDB 12.x may exceed Nextcloud’s documented recommendations.

Current stance:
- Works reliably
- No action required unless issues arise

---

## Maintenance Tasks

- Missing indices check
- Expensive repair jobs (as needed)

Performed via `occ` commands.

---

🛑 Stopping Point

Database backend is stable and compliant with migration goals.

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Atlas |
| Host/system/device owner | Atlas |
| Runtime type | Database service; Needs validation |
| Source of truth | Service documentation and validated backup/restore model |
| Config path | Needs validation |
| Data path | Authoritative data on Atlas; exact paths need validation |
| Secret requirements | Do not commit database credentials |
| Network ports | Needs validation |
| Dependencies | Nextcloud and Atlas storage model |
| Backup requirement | Required before automation |
| Validation command | Needs validation |
| Recovery procedure | [[systems/atlas/procedures/README]] |
| Automation classification | Needs validation |
| Preferred automation tool | Needs validation |
