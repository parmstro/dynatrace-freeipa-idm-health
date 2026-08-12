[< Back to Metrics Index](INDEX.md)

# replication.conflict_entries

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.replication.conflict_entries` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The count of replication conflict entries across the entire directory. Conflict entries are created when two replicas modify the same entry simultaneously and the changes cannot be automatically merged. A non-zero value indicates a split-brain condition that requires manual resolution.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Healthy value** | 0 |

Any non-zero value should be investigated. Conflict entries have `nsds5ReplConflict` as an operational attribute and can be found with:
```
ldapsearch -b "dc=example,dc=com" "(nsds5ReplConflict=*)"
```

## Collection Method

LDAP subtree search across the entire base DN for entries with the `nsds5ReplConflict` attribute:

```
Search Base: {base_dn}  (e.g. dc=example,dc=com)
Scope:       SUBTREE
Filter:      (nsds5ReplConflict=*)
Attributes:  dn
```

The metric value is the count of returned entries.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `count_replication_conflicts()`
**Orchestration:** `freeipa_idm_health/replication_monitor.py` — `collect_all()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
