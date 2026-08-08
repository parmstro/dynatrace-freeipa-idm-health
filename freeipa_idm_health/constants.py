METRIC_PREFIX = "custom.freeipa.idm"

# Service Health
SERVICE_STATUS = f"{METRIC_PREFIX}.service.status"

# LDAP Performance
LDAP_CURRENT_CONNECTIONS = f"{METRIC_PREFIX}.ldap.current_connections"
LDAP_TOTAL_CONNECTIONS = f"{METRIC_PREFIX}.ldap.total_connections"
LDAP_CONNECTIONS_AT_MAXTHREADS = f"{METRIC_PREFIX}.ldap.connections_at_maxthreads"
LDAP_OPS_INITIATED = f"{METRIC_PREFIX}.ldap.ops_initiated"
LDAP_OPS_COMPLETED = f"{METRIC_PREFIX}.ldap.ops_completed"
LDAP_ENTRIES_SENT = f"{METRIC_PREFIX}.ldap.entries_sent"
LDAP_BYTES_SENT = f"{METRIC_PREFIX}.ldap.bytes_sent"
LDAP_THREADS = f"{METRIC_PREFIX}.ldap.threads"
LDAP_READ_WAITERS = f"{METRIC_PREFIX}.ldap.read_waiters"
LDAP_DTABLE_SIZE = f"{METRIC_PREFIX}.ldap.dtable_size"
LDAP_ANONYMOUS_BINDS = f"{METRIC_PREFIX}.ldap.anonymous_binds"
LDAP_SIMPLE_AUTH_BINDS = f"{METRIC_PREFIX}.ldap.simple_auth_binds"
LDAP_STRONG_AUTH_BINDS = f"{METRIC_PREFIX}.ldap.strong_auth_binds"
LDAP_BIND_SECURITY_ERRORS = f"{METRIC_PREFIX}.ldap.bind_security_errors"
LDAP_SEARCH_OPS = f"{METRIC_PREFIX}.ldap.search_ops"
LDAP_ADD_ENTRY_OPS = f"{METRIC_PREFIX}.ldap.add_entry_ops"
LDAP_MODIFY_ENTRY_OPS = f"{METRIC_PREFIX}.ldap.modify_entry_ops"
LDAP_REMOVE_ENTRY_OPS = f"{METRIC_PREFIX}.ldap.remove_entry_ops"
LDAP_ERRORS = f"{METRIC_PREFIX}.ldap.errors"
LDAP_BACKEND_ENTRY_CACHE_HIT_RATIO = f"{METRIC_PREFIX}.ldap.backend.entry_cache_hit_ratio"
LDAP_BACKEND_ENTRY_CACHE_COUNT = f"{METRIC_PREFIX}.ldap.backend.entry_cache_count"
LDAP_BACKEND_ENTRY_CACHE_SIZE = f"{METRIC_PREFIX}.ldap.backend.entry_cache_size"
LDAP_BACKEND_ENTRY_CACHE_MAX_SIZE = f"{METRIC_PREFIX}.ldap.backend.entry_cache_max_size"
LDAP_BACKEND_DN_CACHE_HIT_RATIO = f"{METRIC_PREFIX}.ldap.backend.dn_cache_hit_ratio"
LDAP_BACKEND_DN_CACHE_COUNT = f"{METRIC_PREFIX}.ldap.backend.dn_cache_count"
LDAP_BACKEND_DN_CACHE_SIZE = f"{METRIC_PREFIX}.ldap.backend.dn_cache_size"

# Replication
REPL_STATUS = f"{METRIC_PREFIX}.replication.status"
REPL_LAG_SECONDS = f"{METRIC_PREFIX}.replication.lag_seconds"
REPL_UPDATE_IN_PROGRESS = f"{METRIC_PREFIX}.replication.update_in_progress"
REPL_CHANGES_SENT = f"{METRIC_PREFIX}.replication.changes_sent"
REPL_CONFLICT_ENTRIES = f"{METRIC_PREFIX}.replication.conflict_entries"

# DNS
DNS_ZONE_COUNT = f"{METRIC_PREFIX}.dns.zone_count"
DNS_RECORD_COUNT = f"{METRIC_PREFIX}.dns.record_count"
DNS_SRV_RECORD_VALID = f"{METRIC_PREFIX}.dns.srv_record_valid"

# Certificates
CERT_DAYS_UNTIL_EXPIRY = f"{METRIC_PREFIX}.cert.days_until_expiry"
CERT_STATUS = f"{METRIC_PREFIX}.cert.status"
CERT_TOTAL_TRACKED = f"{METRIC_PREFIX}.cert.total_tracked"

# Healthcheck
HC_WARNING_COUNT = f"{METRIC_PREFIX}.healthcheck.warning_count"
HC_ERROR_COUNT = f"{METRIC_PREFIX}.healthcheck.error_count"
HC_CRITICAL_COUNT = f"{METRIC_PREFIX}.healthcheck.critical_count"
HC_TOTAL_CHECKS = f"{METRIC_PREFIX}.healthcheck.total_checks"

# LDAP Base DNs and search filters
MONITOR_DN = "cn=monitor"
SNMP_MONITOR_DN = "cn=snmp,cn=monitor"
LDBM_PLUGIN_DN = "cn=ldbm database,cn=plugins,cn=config"
MAPPING_TREE_DN = "cn=mapping tree,cn=config"

REPL_AGREEMENT_FILTER = "(objectclass=nsds5replicationagreement)"
REPL_CONFLICT_FILTER = "(nsds5ReplConflict=*)"
DNS_ZONE_FILTER = "(objectclass=idnszone)"
DNS_RECORD_FILTER = "(objectclass=idnsrecord)"
BACKEND_FILTER = "(objectclass=nsBackendInstance)"

# Request all attributes including operational ones — 389 DS cn=monitor
# attributes are non-standard and ldap3 rejects them by name
ALL_ATTRS = ["*", "+"]

MONITOR_ATTRS = ALL_ATTRS
SNMP_ATTRS = ALL_ATTRS
BACKEND_CACHE_ATTRS = ALL_ATTRS

REPL_ATTRS = [
    "nsDS5ReplicaHost",
    "nsds5replicaLastUpdateStatus",
    "nsds5replicaLastUpdateStart",
    "nsds5replicaLastUpdateEnd",
    "nsds5replicaUpdateInProgress",
    "nsds5replicaChangesSentSinceStartup",
    "cn",
    "nsDS5ReplicaRoot",
]

# FreeIPA services to monitor (systemd unit names)
IPA_SERVICES = [
    ("dirsrv", "dirsrv@{realm}"),
    ("krb5kdc", "krb5kdc"),
    ("kadmin", "kadmin"),
    ("httpd", "httpd"),
    ("pki-tomcatd", "pki-tomcatd@pki-tomcat"),
    ("named", "named-pkcs11"),
    ("certmonger", "certmonger"),
]

# SRV records to validate
SRV_RECORDS = [
    "_ldap._tcp",
    "_kerberos._tcp",
    "_kerberos._udp",
    "_kpasswd._tcp",
    "_kpasswd._udp",
]

DEFAULT_LDAP_PORT = 636
DEFAULT_LDAP_TIMEOUT = 10
DEFAULT_POLLING_INTERVAL = 300
