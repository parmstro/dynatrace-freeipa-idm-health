[< Back to Metrics Index](INDEX.md)

# ldap.anonymous_binds

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.anonymous_binds` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of anonymous (unauthenticated) LDAP bind operations since the 389 Directory Server process started. FreeIPA permits limited anonymous access by default for service discovery. A high rate may indicate misconfigured clients or scanning activity.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |
| **Anonymous access** | Enabled by default (`nsslapd-allow-anonymous-access: rootdse`) for root DSE and schema |

## Collection Method

LDAP base-scope search against the `cn=snmp,cn=monitor` suffix:

```
Search Base: cn=snmp,cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `anonymousBinds` operational attribute. These attributes follow the LDAP MIB (RFC 2605) naming conventions exposed by 389 DS for SNMP integration.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
