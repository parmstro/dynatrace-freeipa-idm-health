[< Back to Metrics Index](INDEX.md)

# ldap.errors

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.errors` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of all LDAP errors returned to clients since the 389 Directory Server process started. Includes all non-success result codes: `noSuchObject`, `insufficientAccessRights`, `sizeLimitExceeded`, `timeLimitExceeded`, and others. Not all errors indicate problems — `noSuchObject` during normal SSSD lookups is expected.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |

## Collection Method

LDAP base-scope search against the `cn=snmp,cn=monitor` suffix:

```
Search Base: cn=snmp,cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `errors` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
