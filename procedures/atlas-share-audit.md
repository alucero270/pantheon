# procedures/atlas-share-audit.md

__Purpose:__
Validate and enforce **ADR-004 (Atlas Share Storage Model: Array-only authoritative data)** on Atlas.

Authoritative datasets covered by this procedure:

- `documents`
- `shared-media`
- `managed-media`
- `photos`
- `scans`
- `backups`
- `nextcloud-data`

**Desired state (ADR-004):**
- Primary storage: **Array**
- Secondary storage: **None**
- Mover: **Not used / irrelevant** (there should be no cache participation for these shares)

This procedure provides:
1) A short validation checklist + CLI commands  
2) A safe remediation procedure if cache residue exists (no data loss)  
3) Notes aligned with a commercial setting: repeatability, audit trail, and least risk


---

__Scope & assumptions:__
- Platform: Unraid-style share config (`/boot/config/shares/*.cfg`) and mount layout (`/mnt/user`, `/mnt/diskX`, `/mnt/cache`).
- This is an **audit + remediation** for storage placement only.
- This procedure does **not** modify network exports (SMB/NFS) or app configs beyond pausing writers when needed.

> If Atlas runs apps that write into any of these shares (Nextcloud, photo ingest, backup jobs, etc.), you must pause them during remediation.


---

__Security & change control (commercial baseline):__
- Run all commands as `root` in a local console/SSH session restricted to the MGMT VLAN.
- Capture evidence for ticket/audit: command outputs + timestamps.
- Use a maintenance window if any share is actively written to.

Recommended: start a session log.

```bash
# Optional: log everything to a file for audit evidence
mkdir -p /root/audit-logs
script -q /root/audit-logs/atlas-share-audit-$(date +%F_%H%M%S).log
```

---

__Quick validation checklist:__

You are “green” when all are true:

*[ ] Each authoritative share’s config matches Array-only (no cache/secondary).

*[ ] /mnt/cache/<share> does not exist, or is empty for authoritative shares.

*[ ] There is no unexpected authoritative data on cache (verified by size + file listing).

*[ ] If any remediation occurred: a verification pass confirms files are present on array-backed paths and cache residue removed.

---

#### Variables

Edit the list only if ADR-004 changes.
```bash
AUTHORITATIVE_SHARES=(
  "documents"
  "shared-media"
  "managed-media"
  "photos"
  "scans"
  "backups"
  "nextcloud-data"
)
```

### 1) Validate share configuration matches ADR-004

#### 1.1 Inspect share config files

Unraid stores share settings in /boot/config/shares/<share>.cfg.
```bash
ls -lah /boot/config/shares
```

Dump configs for authoritative shares:
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  echo "===== ${s} ====="
  cfg="/boot/config/shares/${s}.cfg"
  if [[ -f "$cfg" ]]; then
    sed -n '1,200p' "$cfg"
  else
    echo "MISSING CONFIG: $cfg"
  fi
  echo
done
```

### 1.2 Extract and normalize the cache-related fields

Different Unraid versions/plugins may represent “cache/secondary” slightly differently.
This grep focuses on common fields that indicate cache usage.
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  cfg="/boot/config/shares/${s}.cfg"
  echo "===== ${s} (cache-related fields) ====="
  if [[ -f "$cfg" ]]; then
    egrep -i '^(share(Cache|cache)|cache|secondary|pool|mover|shareUseCache|shareUseCachePool|shareCache|shareCachePool)=' "$cfg" || echo "(no matching fields found)"
  else
    echo "MISSING CONFIG: $cfg"
  fi
  echo
done
```

Interpretation guidance

You are looking for any value that implies:

a cache pool is enabled for the share, or

a secondary storage/pool is set, or

“Use cache: Yes/Prefer/Only” semantics apply.

Pass condition: No authoritative share should be configured to use cache/pools for data placement.

If you maintain an internal “expected config snippet” for ADR-004, add it here as a reference block and compare diffs (recommended for reproducibility).

# 2) Validate no authoritative data exists on cache
### 2.1 Check for presence of cache directories
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  p="/mnt/cache/${s}"
  if [[ -d "$p" ]]; then
    echo "[FOUND] $p"
  else
    echo "[OK]    $p (missing)"
  fi
done
```
### 2.2 Check size (fast signal)
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  p="/mnt/cache/${s}"
  if [[ -d "$p" ]]; then
    echo "===== Size: $p ====="
    du -sh "$p"
  fi
done
```

### 2.3 Identify unexpected files (evidence-grade listing)

This prints a shallow listing first, then a full count.
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  p="/mnt/cache/${s}"
  if [[ -d "$p" ]]; then
    echo "===== Listing (top level): $p ====="
    ls -lah "$p" | sed -n '1,200p'
    echo "===== File count (recursive): $p ====="
    find "$p" -type f 2>/dev/null | wc -l
    echo
  fi
done
```
### 2.4 Confirm “array-backed” data exists where expected

This is not perfect (because /mnt/user/<share> is the FUSE union),
but it confirms the share is present and accessible.

```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  echo "===== /mnt/user/${s} ====="
  ls -lah "/mnt/user/${s}" | sed -n '1,80p'
  echo
done
```

If you want stronger evidence of “on array”, spot-check disks:

#### List disks present
ls -lah /mnt | egrep '^d.*disk[0-9]+' || true

#### Spot-check each share across disks
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  echo "===== Disk locations for ${s} ====="
  for d in /mnt/disk*; do
    [[ -d "${d}/${s}" ]] && echo "FOUND: ${d}/${s}"
  done
  echo
done
```

Pass condition: /mnt/cache/<share> is missing or empty for every authoritative share.

## 3) Safe remediation if cache residue exists (no data loss)
#### Safety model

We treat cache residue as “at risk of being missed/backed up inconsistently” and relocate it to the array.
We will:

1. stop writers

2. copy cache → array-backed disk path

3. verify

4. remove cache residue

5. re-check config

This avoids data loss and leaves a clear audit trail.

### 3.1 Preparation: stop writers to authoritative shares

Do one of these approaches, depending on your stack:

- Stop/disable containers and VMs that write into these shares (Nextcloud, backup jobs, ingest tools, etc.)

- Temporarily stop SMB clients or scheduled jobs if they write into them

- If this is a maintenance window, stop the entire application layer for Atlas

#### CLI hints (optional, environment dependent):

If docker exists on this host:
```bash
docker ps
```

If libvirt/VMs exist (Unraid typically)
```bash
virsh list --all 2>/dev/null || true
```


Validate no open file handles on cache paths (good commercial hygiene):
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  p="/mnt/cache/${s}"
  [[ -d "$p" ]] && echo "===== lsof $p =====" && lsof +D "$p" 2>/dev/null | sed -n '1,50p'
done
```

If you see active writers, stop them before proceeding.

### 3.2 Choose a target disk path (avoid /mnt/user for the copy)

For remediation copies, prefer writing to a specific array disk path to avoid FUSE edge cases.

Pick a disk (example: disk1), or the disk where most of the share already lives.
```bash
TARGET_DISK="/mnt/disk1"
```

#### Create target directories if missing:
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  mkdir -p "${TARGET_DISK}/${s}"
done
```

### 3.3 Copy cache residue to the array (non-destructive)

Use rsync with archive flags and verbose output.

```bash 
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  SRC="/mnt/cache/${s}/"
  DST="${TARGET_DISK}/${s}/"
  if [[ -d "/mnt/cache/${s}" ]]; then
    echo "===== RSYNC ${s}: cache -> array (${TARGET_DISK}) ====="
    rsync -avh --progress --stats "$SRC" "$DST"
    echo
  fi
done
```


This copies data without deleting anything yet.

### 3.4 Verify integrity (practical verification)

At minimum, compare counts and sizes. For high assurance, add checksums (slower).

Fast checks:
```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  C="/mnt/cache/${s}"
  A="${TARGET_DISK}/${s}"
  if [[ -d "$C" ]]; then
    echo "===== VERIFY ${s} ====="
    echo "[cache] du -sh:"
    du -sh "$C"
    echo "[array] du -sh:"
    du -sh "$A"
    echo "[cache] file count:"
    find "$C" -type f 2>/dev/null | wc -l
    echo "[array] file count:"
    find "$A" -type f 2>/dev/null | wc -l
    echo
  fi
done
```

Optional stronger check (sampled checksums):

#### Example: checksum first N files as a spot-check
N=200

```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  C="/mnt/cache/${s}"
  A="${TARGET_DISK}/${s}"
  if [[ -d "$C" ]]; then
    echo "===== CHECKSUM SPOT-CHECK ${s} (first ${N} files) ====="
    (cd "$C" && find . -type f | head -n "$N" | xargs -r sha256sum) > "/root/audit-logs/${s}-cache-sha256.txt"
    (cd "$A" && find . -type f | head -n "$N" | xargs -r sha256sum) > "/root/audit-logs/${s}-array-sha256.txt"
    diff -u "/root/audit-logs/${s}-cache-sha256.txt" "/root/audit-logs/${s}-array-sha256.txt" || true
    echo
  fi
done
```

### 3.5 Remove cache residue ONLY after verification

Once you are satisfied the array copy is good, remove cache contents.

Safer step: rename first (quick rollback)

```bash
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  C="/mnt/cache/${s}"
  if [[ -d "$C" ]]; then
    TS="$(date +%F_%H%M%S)"
    echo "===== RENAMING cache dir for ${s} ====="
    mv "$C" "/mnt/cache/${s}.MIGRATED_${TS}"
  fi
done
```


Confirm the renamed directories exist and are not being recreated:

```bash
ls -lah /mnt/cache | egrep 'MIGRATED_' || true
```


If everything remains stable (no writers recreating the original paths), you can delete the migrated residue:

## DANGER: destructive. Only run after you confirm success.
```bash
for d in /mnt/cache/*.MIGRATED_*; do
  [[ -d "$d" ]] && echo "Removing $d" && rm -rf --one-file-system "$d"
done
```

### 3.6 Enforce config: set authoritative shares to Array-only

This step is usually done in the Unraid GUI to ensure correctness, but you can still validate by re-reading cfg files.

After setting:
```text
Primary: Array

Secondary: None

Mover: not used
```
Re-run the config extraction in 1.2 and confirm the values align with ADR-004.

### 3.7 Post-remediation validation

Re-run:

- Section 2.1–2.3: confirm /mnt/cache/<share> is missing/empty

- Section 1.2: confirm cfg shows no cache/pool usage

- Spot-check key folders in /mnt/user/<share> for availability

- Finally, re-enable services/writers and monitor for reappearance of cache directories.

## Watch cache for unexpected share recreation (short observation window)
```bash 
watch -n 2 "ls -lah /mnt/cache | egrep -i 'documents|shared-media|managed-media|photos|scans|backups|nextcloud-data' || true"
```

## Operational notes & common failure modes

__Writers still running:__ if apps are still writing to cache paths, you’ll see directories reappear. Stop writers, clean again.

__Copying via /mnt/user:__ avoid during remediation copies; prefer /mnt/diskX targets.

__Permissions/ownership:__ rsync preserves by default with -a. If you see permission issues, fix after copy (owner/group/mode) using your standard ACL procedure.

__Nextcloud:__ ensure Nextcloud’s config and data directory policies don’t point at cache/pool paths. This procedure only moves files; it doesn’t rewrite application configs.

## Evidence to attach to ticket/change record

- Output of section 1.2 (share cfg cache-related fields)
- Output of section 2.2 (du sizes for cache dirs)
- rsync logs (section 3.3)
- verification output (section 3.4)
- final post-check outputs (section 3.7)

## Done criteria
- All authoritative shares configured Array-only per ADR-004
- No authoritative residue exists under /mnt/cache/<share>
- Services restored and no recurrence observed during the post-check window
- Appendix: one-shot audit command bundle (read-only)

This is safe to run anytime and produces a compact report:
```bash
echo "=== SHARE CFG (cache-related) ==="
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  cfg="/boot/config/shares/${s}.cfg"
  echo "----- $s -----"
  [[ -f "$cfg" ]] && egrep -i '^(share(Cache|cache)|cache|secondary|pool|mover|shareUseCache|shareUseCachePool|shareCache|shareCachePool)=' "$cfg" || echo "missing cfg"
done

echo
echo "=== CACHE RESIDUE CHECK ==="
for s in "${AUTHORITATIVE_SHARES[@]}"; do
  p="/mnt/cache/${s}"
  if [[ -d "$p" ]]; then
    echo "[FOUND] $p : $(du -sh "$p" | awk '{print $1}')"
  else
    echo "[OK]    $p"
  fi
done
```

End the logging session (if you used script) with exit.