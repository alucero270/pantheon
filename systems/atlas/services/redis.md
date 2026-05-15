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
