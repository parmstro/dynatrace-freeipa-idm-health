[< Back to Metrics Index](INDEX.md)

# dns.srv_record_valid

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.dns.srv_record_valid` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `dns.srv_type`, `freeipa.server`, `freeipa.domain` |

## Values

| Value | Meaning |
|---|---|
| `1` | SRV record exists and contains data |
| `0` | SRV record is missing or empty |

## SRV Records Checked

| dns.srv_type | Purpose |
|---|---|
| `_ldap._tcp` | LDAP service discovery |
| `_kerberos._tcp` | Kerberos KDC (TCP) |
| `_kerberos._udp` | Kerberos KDC (UDP) |
| `_kpasswd._tcp` | Kerberos password change (TCP) |
| `_kpasswd._udp` | Kerberos password change (UDP) |

## FreeIPA Defaults

All five SRV records are created automatically during FreeIPA server installation with DNS. All should report `1` on a healthy deployment. A missing SRV record will prevent enrolled clients from discovering the IdM services.

## Collection Method

For each SRV record type, a base-scope search is performed against the domain's DNS zone:

```
Search Base: idnsName={srv_type},{zone_dn}
             (e.g. idnsName=_ldap._tcp,idnsName=example.com.,cn=dns,dc=example,dc=com)
Scope:       BASE
Filter:      (objectclass=idnsrecord)
Attributes:  sRVRecord
```

The record is valid if the entry exists and the `sRVRecord` attribute is non-empty.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `check_srv_record()`
**Orchestration:** `freeipa_idm_health/dns_monitor.py` — `_check_srv_records()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `System: Read DNS Entries` permission

---
[< Back to Metrics Index](INDEX.md)
