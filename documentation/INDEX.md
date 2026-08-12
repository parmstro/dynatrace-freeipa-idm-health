# FreeIPA IdM Health Extension - Documentation Index

## Guides

| Document | Description |
|---|---|
| [README](../README.md) | Project overview, deployment guide, troubleshooting, and configuration reference |
| [Security Guide](SECURITY_GUIDE.md) | Identity, access control, and credential management for the extension |
| [Metrics Reference](METRICS_REFERENCE.md) | Summary of all metric keys with dimensions, meanings, and data sources |
| [Per-Metric Documentation](metrics/INDEX.md) | Individual metric files with collection details, LDAP queries, API calls, and FreeIPA defaults |

## Design Documents

| Document | Description |
|---|---|
| [Kerberos Authentication Design](SECURITY_KERBEROS_DESIGN.md) | Design rationale for Kerberos authentication via `kinit` + `curl --negotiate` on ActiveGate |
| [Service Health Monitoring Design](SERVICE_HEALTH_DESIGN.md) | How the extension determines FreeIPA service status via remote protocol-level probes |

## Dashboard Screenshots

| Screenshot | Description |
|---|---|
| ![thumb](images/Dynatrace_RHIdM_Default_Dashboard1.png) | Service Health honeycomb, Bind Security Errors, and LDAP Performance |
| ![thumb](images/Dynatrace_RHIdM_Default_Dashboard2.png) | DNS gauges, SRV validation, certificate expiry tracking |
