[< Back to Metrics Index](INDEX.md)

# ldap.current_connections

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.current_connections` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The number of currently open LDAP client connections to the 389 Directory Server instance. This is a point-in-time snapshot, not a cumulative counter.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Governed by `nsslapd-maxdescriptors` (default: 4096) and `nsslapd-conntablesize` |
| **Typical range** | 5-50 on a lightly loaded single-server deployment |

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `currentConnections` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
