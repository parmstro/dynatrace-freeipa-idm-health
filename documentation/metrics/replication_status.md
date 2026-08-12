[< Back to Metrics Index](INDEX.md)

# replication.status

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.replication.status` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `replication.agreement`, `replication.replica_host`, `replication.suffix`, `freeipa.server`, `freeipa.domain` |

## Meaning

The replication status code for a specific replication agreement as reported by 389 Directory Server. The code is extracted from the first word of the `nsds5replicaLastUpdateStatus` attribute.

## Values

| Value | Meaning |
|---|---|
| `0` | Replica is up to date (success) |
| `1` | Busy — replica is currently being updated |
| `-1` | Parse error (status string could not be interpreted) |
| Other | 389 DS error code — see 389 DS documentation for LDAP result codes |

## FreeIPA Defaults

| | Value |
|---|---|
| **Healthy value** | 0 |
| **Not present** | Single-server deployments have no replication agreements — no metrics are emitted |

## Collection Method

LDAP subtree search for replication agreement entries:

```
Search Base: cn=mapping tree,cn=config
Scope:       SUBTREE
Filter:      (objectclass=nsds5replicationagreement)
Attributes:  nsDS5ReplicaHost, nsds5replicaLastUpdateStatus,
             nsds5replicaLastUpdateStart, nsds5replicaLastUpdateEnd,
             nsds5replicaUpdateInProgress, nsds5replicaChangesSentSinceStartup,
             cn, nsDS5ReplicaRoot
```

The status code is parsed from `nsds5replicaLastUpdateStatus` by splitting on whitespace and converting the first token to an integer.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_replication_agreements()`
**Orchestration:** `freeipa_idm_health/replication_monitor.py` — `collect_all()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI; requires the `Read Replication Agreements` permission

---
[< Back to Metrics Index](INDEX.md)
