[< Back to Metrics Index](INDEX.md)

# ldap.simple_auth_binds

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.simple_auth_binds` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of simple (password-based) LDAP bind operations since the 389 Directory Server process started. Simple binds transmit the DN and password in cleartext over the connection, which is why LDAPS (port 636) or STARTTLS is required.

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

The value is read from the `simpleAuthBinds` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
