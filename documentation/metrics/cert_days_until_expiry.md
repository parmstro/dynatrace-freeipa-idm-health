[< Back to Metrics Index](INDEX.md)

# cert.days_until_expiry

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.cert.days_until_expiry` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `cert.subject`, `cert.serial_number`, `freeipa.server`, `freeipa.domain` |

## Meaning

The number of days remaining before a tracked certificate expires. The extension generates Dynatrace events when certificates approach expiry:

| Threshold | Event Severity |
|---|---|
| <= 30 days | WARNING |
| <= 7 days | CRITICAL |

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 (expired certificates are clamped to 0) |
| **Maximum** | Typically 730 (2 years) for FreeIPA service certificates |
| **IPA CA certificate** | Valid for 20 years from installation |
| **Service certificates** | Default validity: 2 years, auto-renewed by certmonger |
| **Special value** | -1 indicates the expiry date could not be parsed |

## Collection Method

**Local mode:** Runs `getcert list` via subprocess and parses the `expires:` field from each certificate block. Attempts multiple date formats:
- `%Y-%m-%d %H:%M:%S %Z`
- `%Y-%m-%d %H:%M:%S`
- `%a %b %d %H:%M:%S %Y %Z`
- `%a %b %d %H:%M:%S %Y`
- Falls back to extracting `YYYY-MM-DD` via regex

The days value is computed as: `max(0, (expiry - utcnow).days)`

**Remote mode:** Calls the IPA JSON-RPC API:

```
IPA JSON-RPC: cert_find
  options: { sizelimit: 0 }
```

For each certificate, reads the `valid_not_after` field and parses it using formats:
- `%a %b %d %H:%M:%S %Y %Z`
- `%Y-%m-%dT%H:%M:%SZ`
- `%Y%m%d%H%M%SZ`

**Source file:** `freeipa_idm_health/cert_monitor.py` — `_parse_expiry()`, `_parse_api_expiry()`
**Authentication:** IPA API password or Kerberos keytab (remote); none (local)

---
[< Back to Metrics Index](INDEX.md)
