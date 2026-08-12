[< Back to Metrics Index](INDEX.md)

# ldap.backend.entry_cache_count

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.entry_cache_count` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The number of directory entries currently held in the in-memory entry cache for a given database backend. Compare with the total number of entries in the backend to gauge cache coverage.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Bounded by `entry_cache_max_size` (memory) and entry count in the database |

## Collection Method

**Step 1 — Discover backends:**
```
Search Base: cn=ldbm database,cn=plugins,cn=config
Scope:       ONE
Filter:      (objectclass=nsBackendInstance)
Attributes:  cn
```

**Step 2 — Read cache stats per backend:**
```
Search Base: cn=monitor,cn={backend},cn=ldbm database,cn=plugins,cn=config
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `currententrycachecount` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
