[< Back to Metrics Index](INDEX.md)

# ldap.threads

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.threads` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The current number of active worker threads in the 389 Directory Server thread pool. Each thread handles one LDAP operation at a time.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | `nsslapd-threadnumber` (default: auto-tuned based on CPU count) |
| **Default thread count** | 389 DS auto-calculates: typically 2x CPU cores, minimum 16 |

When threads consistently equal the max, the server is saturated. Check `connections_at_maxthreads` and `read_waiters` for confirmation.

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `threads` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
