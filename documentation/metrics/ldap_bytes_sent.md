[< Back to Metrics Index](INDEX.md)

# ldap.bytes_sent

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.bytes_sent` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Byte |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of bytes sent to LDAP clients since the 389 Directory Server process started. Useful for tracking network throughput and detecting unusually large queries.

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

The value is read from the `bytesSent` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
