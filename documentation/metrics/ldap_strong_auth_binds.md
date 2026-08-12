[< Back to Metrics Index](INDEX.md)

# ldap.strong_auth_binds

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.strong_auth_binds` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of SASL/GSSAPI (Kerberos) bind operations since the 389 Directory Server process started. In a FreeIPA environment, this represents Kerberos-authenticated LDAP connections — the preferred authentication method for enrolled clients.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |

On a healthy FreeIPA deployment, `strong_auth_binds` should be the dominant bind type, as enrolled hosts and the SSSD daemon use GSSAPI.

## Collection Method

LDAP base-scope search against the `cn=snmp,cn=monitor` suffix:

```
Search Base: cn=snmp,cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `strongAuthBinds` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
