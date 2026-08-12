[< Back to Metrics Index](INDEX.md)

# replication.update_in_progress

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.replication.update_in_progress` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `replication.agreement`, `replication.replica_host`, `replication.suffix`, `freeipa.server`, `freeipa.domain` |

## Values

| Value | Meaning |
|---|---|
| `1` | Replication sync is currently in progress |
| `0` | Idle — no active replication for this agreement |

## FreeIPA Defaults

| | Value |
|---|---|
| **Healthy value** | 0 most of the time; `1` transiently during sync |
| **Not present** | Single-server deployments have no replication agreements |

A persistently stuck `1` indicates a stalled replication session.

## Collection Method

Read from the `nsds5replicaUpdateInProgress` attribute on the replication agreement entry. The string value `TRUE` maps to `1`, anything else to `0`.

```
Search Base: cn=mapping tree,cn=config
Scope:       SUBTREE
Filter:      (objectclass=nsds5replicationagreement)
```

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_replication_agreements()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `Read Replication Agreements` permission

---
[< Back to Metrics Index](INDEX.md)
