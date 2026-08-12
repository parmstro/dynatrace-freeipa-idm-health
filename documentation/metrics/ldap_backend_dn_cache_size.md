[< Back to Metrics Index](INDEX.md)

# ldap.backend.dn_cache_size

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.dn_cache_size` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Byte |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The current size in bytes of the in-memory DN cache for a given database backend. The DN cache is typically much smaller than the entry cache since it only stores DN strings and entry IDs, not full entry data.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | `nsslapd-dncachememsize` (default: 10485760 / 10 MB) |
| **Configurable via** | `dsconf {instance} backend suffix set --dncache-memsize` |

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

The value is read from the `currententrydncachesize` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
