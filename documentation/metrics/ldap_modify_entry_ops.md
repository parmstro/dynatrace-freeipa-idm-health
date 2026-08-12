[< Back to Metrics Index](INDEX.md)

# ldap.modify_entry_ops

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.modify_entry_ops` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of LDAP modify operations since the 389 Directory Server process started. Includes attribute changes on existing entries — password changes, group membership updates, policy modifications, and Kerberos key updates.

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

The value is read from the `modifyEntryOps` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
