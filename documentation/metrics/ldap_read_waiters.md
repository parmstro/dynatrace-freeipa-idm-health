[< Back to Metrics Index](INDEX.md)

# ldap.read_waiters

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.read_waiters` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The number of threads currently blocked waiting to read data from a client connection. A sustained non-zero value may indicate slow clients or network congestion.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Bounded by `nsslapd-threadnumber` |
| **Healthy value** | 0 |

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `readWaiters` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
