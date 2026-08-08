# FreeIPA IdM Health Extension - Metrics Reference

## 1. Services (`enable_services`)

| Metric Key | Dimensions | Meaning |
|---|---|---|
| `custom.freeipa.idm.service.status` | `service.name` | 1 = active, 0 = inactive. Local: checks systemd unit. Remote: inferred from `server_role_find` via IPA API |

**Services monitored:** `dirsrv`, `krb5kdc`, `kadmin`, `httpd`, `pki-tomcatd`, `named`, `certmonger`

---

## 2. LDAP Monitor (`enable_ldap_metrics`) — from `cn=monitor`

| Metric Key | Meaning |
|---|---|
| `custom.freeipa.idm.ldap.current_connections` | Number of currently open LDAP connections |
| `custom.freeipa.idm.ldap.total_connections` | Total LDAP connections since server start |
| `custom.freeipa.idm.ldap.connections_at_maxthreads` | Connections queued because all worker threads are busy |
| `custom.freeipa.idm.ldap.ops_initiated` | Total LDAP operations initiated since start |
| `custom.freeipa.idm.ldap.ops_completed` | Total LDAP operations completed since start |
| `custom.freeipa.idm.ldap.entries_sent` | Total directory entries returned to clients |
| `custom.freeipa.idm.ldap.bytes_sent` | Total bytes sent to clients |
| `custom.freeipa.idm.ldap.threads` | Current number of active worker threads |
| `custom.freeipa.idm.ldap.read_waiters` | Threads waiting to read from a client connection |
| `custom.freeipa.idm.ldap.dtable_size` | File descriptor table size (max open files) |

---

## 3. LDAP SNMP (`enable_ldap_metrics`) — from `cn=snmp,cn=monitor`

| Metric Key | Meaning |
|---|---|
| `custom.freeipa.idm.ldap.anonymous_binds` | Total anonymous (unauthenticated) bind operations |
| `custom.freeipa.idm.ldap.simple_auth_binds` | Total simple (password) bind operations |
| `custom.freeipa.idm.ldap.strong_auth_binds` | Total SASL/Kerberos (strong auth) bind operations |
| `custom.freeipa.idm.ldap.bind_security_errors` | Failed bind attempts (wrong password, denied) |
| `custom.freeipa.idm.ldap.search_ops` | Total search operations |
| `custom.freeipa.idm.ldap.add_entry_ops` | Total add (create) operations |
| `custom.freeipa.idm.ldap.modify_entry_ops` | Total modify operations |
| `custom.freeipa.idm.ldap.remove_entry_ops` | Total delete operations |
| `custom.freeipa.idm.ldap.errors` | Total LDAP errors returned to clients |

---

## 4. Backend Cache (`enable_ldap_metrics`) — per backend (e.g. `userroot`, `ipaca`, `changelog`)

| Metric Key | Dimensions | Meaning |
|---|---|---|
| `custom.freeipa.idm.ldap.backend.entry_cache_hit_ratio` | `ldap.backend` | % of entry lookups served from cache (0-100) |
| `custom.freeipa.idm.ldap.backend.entry_cache_count` | `ldap.backend` | Number of entries currently in the entry cache |
| `custom.freeipa.idm.ldap.backend.entry_cache_size` | `ldap.backend` | Current entry cache size in bytes |
| `custom.freeipa.idm.ldap.backend.entry_cache_max_size` | `ldap.backend` | Configured maximum entry cache size in bytes |
| `custom.freeipa.idm.ldap.backend.dn_cache_hit_ratio` | `ldap.backend` | % of DN lookups served from cache (0-100) |
| `custom.freeipa.idm.ldap.backend.dn_cache_count` | `ldap.backend` | Number of DNs currently in the DN cache |
| `custom.freeipa.idm.ldap.backend.dn_cache_size` | `ldap.backend` | Current DN cache size in bytes |

---

## 5. Replication (`enable_replication`) — per agreement

| Metric Key | Dimensions | Meaning |
|---|---|---|
| `custom.freeipa.idm.replication.status` | `replication.agreement`, `replication.replica_host`, `replication.suffix` | Status code from 389 DS. 0 = OK, non-zero = error |
| `custom.freeipa.idm.replication.lag_seconds` | (same) | Seconds between last update start and end (replication delay) |
| `custom.freeipa.idm.replication.update_in_progress` | (same) | 1 = replication sync currently running, 0 = idle |
| `custom.freeipa.idm.replication.changes_sent` | (same) | Number of changes sent to replica since server start |
| `custom.freeipa.idm.replication.conflict_entries` | (none) | Count of replication conflict entries (`nsds5ReplConflict`) across the directory. Non-zero indicates split-brain |

---

## 6. DNS (`enable_dns`)

| Metric Key | Dimensions | Meaning |
|---|---|---|
| `custom.freeipa.idm.dns.zone_count` | (none) | Total number of DNS zones managed by IdM |
| `custom.freeipa.idm.dns.record_count` | `dns.zone` | Number of DNS records in each zone |
| `custom.freeipa.idm.dns.srv_record_valid` | `dns.srv_type` | 1 = SRV record exists and has data, 0 = missing. Checks: `_ldap._tcp`, `_kerberos._tcp`, `_kerberos._udp`, `_kpasswd._tcp`, `_kpasswd._udp` |

---

## 7. Certificates (`enable_certificates`)

| Metric Key | Dimensions | Meaning |
|---|---|---|
| `custom.freeipa.idm.cert.total_tracked` | (none) | Total number of certificates tracked |
| `custom.freeipa.idm.cert.status` | `cert.subject`, `cert.serial_number` | Local: 1 = certmonger MONITORING, 0 = not. Remote: 1 = VALID, 0 = revoked/expired |
| `custom.freeipa.idm.cert.days_until_expiry` | `cert.subject`, `cert.serial_number` | Days remaining before certificate expires. Generates WARNING event at <=30 days, CRITICAL at <=7 |

---

## 8. Healthcheck (`enable_healthcheck`, local only)

| Metric Key | Meaning |
|---|---|
| `custom.freeipa.idm.healthcheck.total_checks` | Total checks run by `ipa-healthcheck` |
| `custom.freeipa.idm.healthcheck.warning_count` | Number of checks returning WARNING |
| `custom.freeipa.idm.healthcheck.error_count` | Number of checks returning ERROR |
| `custom.freeipa.idm.healthcheck.critical_count` | Number of checks returning CRITICAL |

---

## Summary

| Collector | Source | Metric Count | Auth Required |
|---|---|---|---|
| Services | systemd (local) / IPA API (remote) | 1 x 7 services | Kerberos for remote |
| LDAP Monitor | `cn=monitor` | 10 | LDAP bind |
| LDAP SNMP | `cn=snmp,cn=monitor` | 9 | LDAP bind |
| Backend Cache | `cn=monitor,cn={backend},...` | 7 x N backends | LDAP bind + ACI on `cn=config` |
| Replication | `cn=mapping tree,cn=config` | 4 per agreement + 1 global | LDAP bind + Read Replication Agreements perm |
| DNS | `cn=dns,{base_dn}` | 2 + 1 per SRV type | LDAP bind + System: Read DNS Entries perm |
| Certificates | `getcert list` (local) / IPA API (remote) | 3 | Kerberos for remote |
| Healthcheck | `ipa-healthcheck` CLI | 4 | Local only, requires root |

**Total: 39 unique metric keys** across 8 collectors. All metrics carry `freeipa.server` and `freeipa.domain` as base dimensions.
