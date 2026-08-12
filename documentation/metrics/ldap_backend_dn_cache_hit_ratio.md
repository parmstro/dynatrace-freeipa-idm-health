[< Back to Metrics Index](INDEX.md)

# ldap.backend.dn_cache_hit_ratio

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.dn_cache_hit_ratio` |
| **Data Type** | Gauge (float) |
| **Dynatrace Unit** | Percent |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The percentage of DN-to-entry-ID lookups served from the in-memory DN cache for a given database backend. The DN cache maps distinguished names to internal entry IDs, accelerating search operations that resolve DNs. A low hit ratio typically has less impact than entry cache misses, as DN lookups are faster than full entry reads.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | 100 |
| **Healthy value** | > 90% |

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

The value is read from the `dncachehitratio` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
