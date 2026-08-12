[< Back to Metrics Index](INDEX.md)

# ldap.entries_sent

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.entries_sent` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of directory entries returned to clients since the 389 Directory Server process started. A rapid increase indicates heavy search activity or searches returning large result sets.

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

The value is read from the `entriesSent` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
