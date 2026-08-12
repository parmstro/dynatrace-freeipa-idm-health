[< Back to Metrics Index](INDEX.md)

# cert.total_tracked

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.cert.total_tracked` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The total number of certificates being tracked. In local mode, this is the count of certificates managed by `certmonger`. In remote mode, this is the count of certificates returned by the IPA `cert_find` API call.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Typical range** | 8-15 on a standard single-server deployment (HTTP, LDAP, KDC, CA subsystem certs, etc.) |

## Collection Method

**Local mode:** Runs `getcert list` via subprocess and counts the parsed certificate entries.

**Remote mode:** Calls the IPA JSON-RPC API:

```
IPA JSON-RPC: cert_find
  options: { sizelimit: 0 }
```

The metric value is the count of entries in the `result` array.

**Source file:** `freeipa_idm_health/cert_monitor.py` — `collect_all()`
**Authentication:** IPA API password or Kerberos keytab (remote); none (local, requires `getcert` access)

---
[< Back to Metrics Index](INDEX.md)
