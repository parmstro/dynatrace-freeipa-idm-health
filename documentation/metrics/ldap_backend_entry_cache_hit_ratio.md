[< Back to Metrics Index](INDEX.md)

# ldap.backend.entry_cache_hit_ratio

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.backend.entry_cache_hit_ratio` |
| **Data Type** | Gauge (float) |
| **Dynatrace Unit** | Percent |
| **Dimensions** | `ldap.backend`, `freeipa.server`, `freeipa.domain` |

## Meaning

The percentage of entry lookups served from the in-memory entry cache for a given database backend, rather than reading from disk. A high hit ratio (>95%) indicates the working set fits in memory and the cache is effective.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | 100 |
| **Healthy value** | > 95% |

## Backends

389 DS creates one backend per suffix. Typical FreeIPA backends:

| Backend | Suffix | Content |
|---|---|---|
| `userroot` | `dc=example,dc=com` | Users, groups, hosts, services, policies |
| `ipaca` | `o=ipaca` | CA certificate store (if CA role enabled) |

## Collection Method

The extension first discovers all backends, then queries each backend's monitor entry:

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

The value is read from the `entrycachehitratio` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_backend_cache_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires ACI granting read access to `cn=config`

---
[< Back to Metrics Index](INDEX.md)
