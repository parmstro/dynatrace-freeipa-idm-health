[< Back to Metrics Index](INDEX.md)

# ldap.backend.entry_cache_max_size

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.entry_cache_max_size` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Byte |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The maximum configured size in bytes for the in-memory entry cache of a given database backend. This is the configured upper bound set by `nsslapd-cachememsize` on the backend entry. The actual cache size (`entry_cache_size`) will not exceed this value.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 500000 (389 DS minimum) |
| **FreeIPA default** | 209715200 (200 MB) for `userroot`; auto-sized for other backends |
| **Configurable via** | `dsconf {instance} backend suffix set --cache-memsize` |

If the hit ratio is low and `entry_cache_size` equals `entry_cache_max_size`, increasing this value will improve cache coverage.

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

The value is read from the `maxentrycachesize` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
