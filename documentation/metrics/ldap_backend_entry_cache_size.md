[< Back to Metrics Index](INDEX.md)

# ldap.backend.entry_cache_size

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.entry_cache_size` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Byte |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The current size in bytes of the in-memory entry cache for a given database backend. When this approaches `entry_cache_max_size`, the cache will begin evicting entries and the hit ratio may drop.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | `entry_cache_max_size` |

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

The value is read from the `currententrycachesize` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
