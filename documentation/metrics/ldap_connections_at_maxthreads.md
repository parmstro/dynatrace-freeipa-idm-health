[< Back to Metrics Index](INDEX.md)

# ldap.connections_at_maxthreads

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.connections_at_maxthreads` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The number of client connections currently queued because all worker threads are busy. This is a saturation indicator — a sustained non-zero value means the server cannot keep up with incoming requests.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Bounded by `nsslapd-maxdescriptors` |
| **Healthy value** | 0 |

A non-zero value indicates thread pool exhaustion. Consider increasing `nsslapd-threadnumber` or investigating slow operations.

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `currentConnectionsAtMaxThreads` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
