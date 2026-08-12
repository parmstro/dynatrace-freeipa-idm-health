[< Back to Metrics Index](INDEX.md)

# replication.changes_sent

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.replication.changes_sent` |
| **Data Type** | Counter (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `replication.agreement`, `replication.replica_host`, `replication.suffix`, `freeipa.server`, `freeipa.domain` |

## Meaning

Cumulative count of changes sent to the replica partner for a specific replication agreement since the 389 Directory Server process started. Useful for measuring replication throughput and verifying that changes are flowing.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Maximum** | Unbounded (counter) |
| **Resets** | On `dirsrv` service restart |
| **Not present** | Single-server deployments have no replication agreements |

## Collection Method

Read from the `nsds5replicaChangesSentSinceStartup` attribute on the replication agreement entry:

```
Search Base: cn=mapping tree,cn=config
Scope:       SUBTREE
Filter:      (objectclass=nsds5replicationagreement)
```

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_replication_agreements()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `Read Replication Agreements` permission

---
[< Back to Metrics Index](INDEX.md)
