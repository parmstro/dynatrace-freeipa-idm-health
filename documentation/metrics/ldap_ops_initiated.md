[< Back to Metrics Index](INDEX.md)

# ldap.ops_initiated

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.ops_initiated` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of all LDAP operations initiated since the 389 Directory Server process started. Includes binds, searches, adds, modifies, deletes, and extended operations. Compare with `ops_completed` to detect a backlog of in-flight operations.

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

The value is read from the `opsInitiated` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
