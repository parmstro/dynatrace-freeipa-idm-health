[< Back to Metrics Index](INDEX.md)

# healthcheck.total_checks

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.healthcheck.total_checks` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `freeipa.server`, `freeipa.domain` |

## Meaning

The total number of checks executed by `ipa-healthcheck` in the latest run. This is the sum of all results across all check sources (SUCCESS + WARNING + ERROR + CRITICAL).

## FreeIPA Defaults

| | Value |
|---|---|
| **Minimum** | 0 |
| **Typical range** | 100-200+ depending on installed roles and plugins |
| **Availability** | Local mode only; requires `ipa-healthcheck` package installed and root access |

## Collection Method

Runs `ipa-healthcheck` via subprocess:

```
Command: ipa-healthcheck --output-type json
Timeout: 120 seconds
```

The JSON output is an array of check results. Each result has a `severity` field (0 = SUCCESS, 1 = CRITICAL, 2 = ERROR, 3 = WARNING). The total is the length of the array.

**Source file:** `freeipa_idm_health/healthcheck_runner.py` — `run()`, `_parse_output()`
**Authentication:** None (requires local root access)
**Availability:** Only when `ipa-healthcheck` is in `$PATH` (checked via `shutil.which`)

---
[< Back to Metrics Index](INDEX.md)
