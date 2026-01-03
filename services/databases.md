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
