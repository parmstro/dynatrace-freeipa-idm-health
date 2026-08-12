[< Back to Metrics Index](INDEX.md)

# ldap.bind_security_errors

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.bind_security_errors` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of failed bind attempts since the 389 Directory Server process started. Includes wrong passwords, expired credentials, and access denied errors. A sudden spike may indicate brute-force attacks or misconfigured service accounts.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Healthy value** | Low and stable rate |
| **Resets** | On `dirsrv` service restart |
| **Lockout policy** | FreeIPA default: 6 failed attempts triggers a 600-second lockout (`ipa pwpolicy-show`) |

## Collection Method

LDAP base-scope search against the `cn=snmp,cn=monitor` suffix:

```
Search Base: cn=snmp,cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `bindSecurityErrors` operational attribute.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_snmp_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
