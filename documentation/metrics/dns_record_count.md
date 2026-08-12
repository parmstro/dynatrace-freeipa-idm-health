[< Back to Metrics Index](INDEX.md)

# dns.record_count

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.dns.record_count` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `dns.zone`, `freeipa.server`, `freeipa.domain` |

## Meaning

The number of DNS records in each zone managed by FreeIPA. One metric is emitted per zone with the zone name as the `dns.zone` dimension. A sudden drop in record count may indicate accidental zone deletion or replication issues.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Typical range** | Varies by deployment size; a basic deployment has ~20-50 records in the forward zone |

## Collection Method

For each zone discovered by `collect_dns_zones()`, a one-level search counts the DNS record entries:

```
Search Base: {zone_dn}  (e.g. idnsName=example.com.,cn=dns,dc=example,dc=com)
Scope:       ONE
Filter:      (objectclass=idnsrecord)
Attributes:  dn
```

The metric value is the count of returned entries per zone.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `count_dns_records()`
**Orchestration:** `freeipa_idm_health/dns_monitor.py` — `collect_all()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `System: Read DNS Entries` permission

---
[< Back to Metrics Index](INDEX.md)
