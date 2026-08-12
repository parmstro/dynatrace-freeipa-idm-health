[< Back to Metrics Index](INDEX.md)

# ldap.search_ops

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.search_ops` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of LDAP search operations since the 389 Directory Server process started. Searches are the dominant operation type in a FreeIPA environment, driven by SSSD lookups from enrolled clients, Kerberos principal resolution, and DNS queries.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |
| **Size limit** | Default `nsslapd-sizelimit`: 2000 entries per search |
| **Time limit** | Default `nsslapd-timelimit`: 3600 seconds |

## Collection Method

LDAP base-scope search against the `cn=snmp,cn=monitor` suffix:

```
Search Base: cn=snmp,cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `searchOps` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
