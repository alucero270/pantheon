# Redis — Nextcloud File Locking & Performance

## Purpose

Redis is used to provide:

- Transactional file locking
- Stable performance under load
- Reduced database contention

---

## Deployment Model

- Redis runs as a dedicated container
- Memory-limited
- Internal-only access
- Used exclusively by Nextcloud

---

## Configuration (Nextcloud)

Required entries in `config.php`:

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => [
  'host' => 'Redis-Nextcloud',
  'port' => 6379,
],
```
---

## Constraints

-- Redis must not be exposed outside SERVERS VLAN

-- Redis data is disposable

-- Redis loss must not corrupt data

-- Validation

-- Nextcloud Admin → Overview shows file locking enabled

-- No Redis-related warnings present

---

## 🛑 Stopping Point

Redis integration is complete and validated.


---

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Atlas |
| Host/system/device owner | Atlas |
| Runtime type | Cache/session service; Needs validation |
| Source of truth | Service documentation |
| Config path | Needs validation |
| Data path | Needs validation |
| Secret requirements | Do not commit secrets |
| Network ports | Needs validation |
| Dependencies | Nextcloud and Atlas service runtime |
| Backup requirement | Needs validation |
| Validation command | Needs validation |
| Recovery procedure | [[systems/atlas/procedures/README]] |
| Automation classification | Needs validation |
| Preferred automation tool | Needs validation |
