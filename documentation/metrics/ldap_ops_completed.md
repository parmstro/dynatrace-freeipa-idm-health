[< Back to Metrics Index](INDEX.md)

# ldap.ops_completed

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.ops_completed` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of all LDAP operations completed since the 389 Directory Server process started. When this diverges significantly from `ops_initiated`, it indicates operations are stalling or taking a long time to complete.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `opsCompleted` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
