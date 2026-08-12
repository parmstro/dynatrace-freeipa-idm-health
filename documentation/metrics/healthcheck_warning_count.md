[< Back to Metrics Index](INDEX.md)

# healthcheck.warning_count

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.healthcheck.warning_count` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The number of `ipa-healthcheck` checks that returned WARNING severity in the latest run. Warnings indicate non-critical issues that should be investigated but do not impact service availability.

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Healthy value** | 0 |
| **Availability** | Local mode only |

## Collection Method

Runs `ipa-healthcheck` via subprocess:

```
Command: ipa-healthcheck --output-type json
Timeout: 120 seconds
```

The JSON output is an array of check results. Each result has a `severity` field where `3` = WARNING. The count is the number of entries with `severity == 3`.

**Source file:** `freeipa_idm_health/healthcheck_runner.py` — `run()`, `_parse_output()`
**Authentication:** None (requires local root access)
**Availability:** Only when `ipa-healthcheck` is in `$PATH`

---
[< Back to Metrics Index](INDEX.md)
