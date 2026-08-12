[< Back to Metrics Index](INDEX.md)

# dns.zone_count

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.dns.zone_count` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The total number of DNS zones managed by the FreeIPA integrated DNS server. Includes forward zones, reverse zones, and the domain's primary zone.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 (if DNS role is not installed) |
| **Typical minimum** | 2 (forward zone + reverse zone on a standard deployment with DNS) |

## Collection Method

LDAP one-level search under the DNS container for zone objects:

```
Search Base: cn=dns,{base_dn}  (e.g. cn=dns,dc=example,dc=com)
Scope:       ONE
Filter:      (objectclass=idnszone)
Attributes:  idnsName
```

The metric value is the count of returned entries.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_dns_zones()`
**Orchestration:** `freeipa_idm_health/dns_monitor.py` — `collect_all()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `System: Read DNS Entries` permission

---
[< Back to Metrics Index](INDEX.md)
