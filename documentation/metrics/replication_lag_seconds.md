[< Back to Metrics Index](INDEX.md)

# replication.lag_seconds

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.replication.lag_seconds` |
| **Data Type** | Gauge (float) |
| **Dynatrace Unit** | Second |
| **Dimensions** | `replication.agreement`, `replication.replica_host`, `replication.suffix`, `freeipa.server`, `freeipa.domain` |

## Meaning

The time in seconds between the start and end of the last replication update for a specific agreement. A large value indicates slow replication — possibly due to a large change set, network latency, or a busy replica.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0.0 |
| **Maximum** | Unbounded |
| **Healthy value** | < 60 seconds for most environments |
| **Not present** | Single-server deployments have no replication agreements |

## Collection Method

Calculated from two attributes on the replication agreement entry:

```
nsds5replicaLastUpdateStart — format: YYYYMMDDHHMMSSz
nsds5replicaLastUpdateEnd   — format: YYYYMMDDHHMMSSz
```

The lag is computed as: `max(0, (end - start).total_seconds())`

The replication agreement entries are found via:

```
Search Base: cn=mapping tree,cn=config
Scope:       SUBTREE
Filter:      (objectclass=nsds5replicationagreement)
```

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_replication_agreements()`, `_calculate_lag()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `Read Replication Agreements` permission

---
[< Back to Metrics Index](INDEX.md)
