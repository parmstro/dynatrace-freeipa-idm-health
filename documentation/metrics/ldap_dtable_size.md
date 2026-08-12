[< Back to Metrics Index](INDEX.md)

# ldap.dtable_size

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.ldap.dtable_size` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The file descriptor table size — the maximum number of file descriptors the 389 Directory Server process can open. Each LDAP connection consumes one file descriptor, so this represents the upper bound on concurrent connections plus internal file handles.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 1 |
| **Default** | 65536 (set by `nsslapd-maxdescriptors`) |
| **Maximum** | Limited by OS `ulimit -n` for the `dirsrv` process |

If `current_connections` approaches this value, new connections will be refused.

## Collection Method

LDAP base-scope search against the `cn=monitor` suffix:

```
Search Base: cn=monitor
Scope:       BASE
Filter:      (objectclass=*)
Attributes:  * +
```

The value is read from the `dtableSize` operational attribute of the `cn=monitor` entry.

**Source file:** `freeipa_idm_health/ldap_collector.py` — `collect_monitor_metrics()`
**Authentication:** LDAP simple bind (DN + password) or GSSAPI

---
[< Back to Metrics Index](INDEX.md)
