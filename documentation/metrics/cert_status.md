[< Back to Metrics Index](INDEX.md)

# cert.status

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.cert.status` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `cert.subject`, `cert.serial_number`, `freeipa.server`, `freeipa.domain` |

## Values

**Local mode (certmonger):**

| Value | Meaning |
|---|---|
| `1` | Certificate status is `MONITORING` (healthy) |
| `0` | Any other certmonger status (`SUBMITTING`, `CA_UNREACHABLE`, `NEED_GUIDANCE`, etc.) |

**Remote mode (IPA API):**

| Value | Meaning |
|---|---|
| `1` | Certificate status is `VALID` or empty (healthy) |
| `0` | Certificate is revoked, expired, or has another non-valid status |

## FreeIPA Defaults

| | Value |
|---|---|
| **Healthy value** | 1 for all tracked certificates |

## Collection Method

**Local mode:** Runs `getcert list` via subprocess and parses the output line by line. Extracts `status:`, `subject:`, `serial number:`, and `expires:` fields from each certificate block.

**Remote mode:** Calls the IPA JSON-RPC API:

```
IPA JSON-RPC: cert_find
  options: { sizelimit: 0 }
```

For each certificate in the result, reads the `status`, `subject`, and `serial_number` fields.

**Source file:** `freeipa_idm_health/cert_monitor.py` — `_collect_local()`, `_collect_remote()`
**Authentication:** IPA API password or Kerberos keytab (remote); none (local)

---
[< Back to Metrics Index](INDEX.md)
