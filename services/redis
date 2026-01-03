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
