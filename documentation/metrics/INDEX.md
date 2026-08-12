# Metrics Reference — Per-Metric Documentation

Each metric collected by the FreeIPA IdM Health extension is documented individually below. All metrics carry `freeipa.server` and `freeipa.domain` as base dimensions.

## Service Health

| Metric | Key | Source |
|---|---|---|
| [Service Status](service_status.md) | `custom.freeipa.idm.service.status` | systemd / IPA API |

## LDAP Monitor (cn=monitor)

| Metric | Key | Source |
|---|---|---|
| [Current Connections](ldap_current_connections.md) | `custom.freeipa.idm.ldap.current_connections` | LDAP `cn=monitor` |
| [Total Connections](ldap_total_connections.md) | `custom.freeipa.idm.ldap.total_connections` | LDAP `cn=monitor` |
| [Connections at Max Threads](ldap_connections_at_maxthreads.md) | `custom.freeipa.idm.ldap.connections_at_maxthreads` | LDAP `cn=monitor` |
| [Operations Initiated](ldap_ops_initiated.md) | `custom.freeipa.idm.ldap.ops_initiated` | LDAP `cn=monitor` |
| [Operations Completed](ldap_ops_completed.md) | `custom.freeipa.idm.ldap.ops_completed` | LDAP `cn=monitor` |
| [Entries Sent](ldap_entries_sent.md) | `custom.freeipa.idm.ldap.entries_sent` | LDAP `cn=monitor` |
| [Bytes Sent](ldap_bytes_sent.md) | `custom.freeipa.idm.ldap.bytes_sent` | LDAP `cn=monitor` |
| [Worker Threads](ldap_threads.md) | `custom.freeipa.idm.ldap.threads` | LDAP `cn=monitor` |
| [Read Waiters](ldap_read_waiters.md) | `custom.freeipa.idm.ldap.read_waiters` | LDAP `cn=monitor` |
| [File Descriptor Table Size](ldap_dtable_size.md) | `custom.freeipa.idm.ldap.dtable_size` | LDAP `cn=monitor` |

## LDAP SNMP (cn=snmp,cn=monitor)

| Metric | Key | Source |
|---|---|---|
| [Anonymous Binds](ldap_anonymous_binds.md) | `custom.freeipa.idm.ldap.anonymous_binds` | LDAP `cn=snmp,cn=monitor` |
| [Simple Auth Binds](ldap_simple_auth_binds.md) | `custom.freeipa.idm.ldap.simple_auth_binds` | LDAP `cn=snmp,cn=monitor` |
| [Strong Auth Binds](ldap_strong_auth_binds.md) | `custom.freeipa.idm.ldap.strong_auth_binds` | LDAP `cn=snmp,cn=monitor` |
| [Bind Security Errors](ldap_bind_security_errors.md) | `custom.freeipa.idm.ldap.bind_security_errors` | LDAP `cn=snmp,cn=monitor` |
| [Search Operations](ldap_search_ops.md) | `custom.freeipa.idm.ldap.search_ops` | LDAP `cn=snmp,cn=monitor` |
| [Add Entry Operations](ldap_add_entry_ops.md) | `custom.freeipa.idm.ldap.add_entry_ops` | LDAP `cn=snmp,cn=monitor` |
| [Modify Entry Operations](ldap_modify_entry_ops.md) | `custom.freeipa.idm.ldap.modify_entry_ops` | LDAP `cn=snmp,cn=monitor` |
| [Remove Entry Operations](ldap_remove_entry_ops.md) | `custom.freeipa.idm.ldap.remove_entry_ops` | LDAP `cn=snmp,cn=monitor` |
| [Errors](ldap_errors.md) | `custom.freeipa.idm.ldap.errors` | LDAP `cn=snmp,cn=monitor` |

## Backend Cache (per database backend)

| Metric | Key | Source |
|---|---|---|
| [Entry Cache Hit Ratio](ldap_backend_entry_cache_hit_ratio.md) | `custom.freeipa.idm.ldap.backend.entry_cache_hit_ratio` | LDAP `cn=monitor,cn={backend},...` |
| [Entry Cache Count](ldap_backend_entry_cache_count.md) | `custom.freeipa.idm.ldap.backend.entry_cache_count` | LDAP `cn=monitor,cn={backend},...` |
| [Entry Cache Size](ldap_backend_entry_cache_size.md) | `custom.freeipa.idm.ldap.backend.entry_cache_size` | LDAP `cn=monitor,cn={backend},...` |
| [Entry Cache Max Size](ldap_backend_entry_cache_max_size.md) | `custom.freeipa.idm.ldap.backend.entry_cache_max_size` | LDAP `cn=monitor,cn={backend},...` |
| [DN Cache Hit Ratio](ldap_backend_dn_cache_hit_ratio.md) | `custom.freeipa.idm.ldap.backend.dn_cache_hit_ratio` | LDAP `cn=monitor,cn={backend},...` |
| [DN Cache Count](ldap_backend_dn_cache_count.md) | `custom.freeipa.idm.ldap.backend.dn_cache_count` | LDAP `cn=monitor,cn={backend},...` |
| [DN Cache Size](ldap_backend_dn_cache_size.md) | `custom.freeipa.idm.ldap.backend.dn_cache_size` | LDAP `cn=monitor,cn={backend},...` |

## Replication (per agreement)

| Metric | Key | Source |
|---|---|---|
| [Replication Status](replication_status.md) | `custom.freeipa.idm.replication.status` | LDAP `cn=mapping tree,cn=config` |
| [Replication Lag](replication_lag_seconds.md) | `custom.freeipa.idm.replication.lag_seconds` | LDAP `cn=mapping tree,cn=config` |
| [Update In Progress](replication_update_in_progress.md) | `custom.freeipa.idm.replication.update_in_progress` | LDAP `cn=mapping tree,cn=config` |
| [Changes Sent](replication_changes_sent.md) | `custom.freeipa.idm.replication.changes_sent` | LDAP `cn=mapping tree,cn=config` |
| [Conflict Entries](replication_conflict_entries.md) | `custom.freeipa.idm.replication.conflict_entries` | LDAP `{base_dn}` subtree |

## DNS

| Metric | Key | Source |
|---|---|---|
| [Zone Count](dns_zone_count.md) | `custom.freeipa.idm.dns.zone_count` | LDAP `cn=dns,{base_dn}` |
| [Record Count](dns_record_count.md) | `custom.freeipa.idm.dns.record_count` | LDAP `cn=dns,{base_dn}` |
| [SRV Record Valid](dns_srv_record_valid.md) | `custom.freeipa.idm.dns.srv_record_valid` | LDAP `cn=dns,{base_dn}` |

## Certificates

| Metric | Key | Source |
|---|---|---|
| [Total Tracked](cert_total_tracked.md) | `custom.freeipa.idm.cert.total_tracked` | `getcert list` / IPA API |
| [Certificate Status](cert_status.md) | `custom.freeipa.idm.cert.status` | `getcert list` / IPA API |
| [Days Until Expiry](cert_days_until_expiry.md) | `custom.freeipa.idm.cert.days_until_expiry` | `getcert list` / IPA API |

## Healthcheck (local only)

| Metric | Key | Source |
|---|---|---|
| [Total Checks](healthcheck_total_checks.md) | `custom.freeipa.idm.healthcheck.total_checks` | `ipa-healthcheck` CLI |
| [Warning Count](healthcheck_warning_count.md) | `custom.freeipa.idm.healthcheck.warning_count` | `ipa-healthcheck` CLI |
| [Error Count](healthcheck_error_count.md) | `custom.freeipa.idm.healthcheck.error_count` | `ipa-healthcheck` CLI |
| [Critical Count](healthcheck_critical_count.md) | `custom.freeipa.idm.healthcheck.critical_count` | `ipa-healthcheck` CLI |

---

**Total: 42 unique metric keys** across 8 collectors.
