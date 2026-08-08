import ssl
import subprocess

import ldap3
from ldap3.core.exceptions import LDAPException, LDAPNoSuchObjectResult

from . import constants as C


class LdapCollector:

    def __init__(self, hostname, port, use_ssl, bind_dn="", bind_password="",
                 base_dn="", timeout=10, ca_cert_path="", logger=None,
                 use_kerberos=False, keytab_path=None, principal=None):
        self._hostname = hostname
        self._port = port
        self._use_ssl = use_ssl
        self._bind_dn = bind_dn
        self._bind_password = bind_password
        self._base_dn = base_dn
        self._timeout = timeout
        self._ca_cert_path = ca_cert_path
        self._logger = logger
        self._use_kerberos = use_kerberos
        self._keytab_path = keytab_path
        self._principal = principal
        self._conn: ldap3.Connection | None = None

    @property
    def uri(self):
        scheme = "ldaps" if self._use_ssl else "ldap"
        return f"{scheme}://{self._hostname}:{self._port}"

    def connect(self):
        self._logger.info(f"Connecting to LDAP: {self.uri}")

        tls = None
        if self._use_ssl or not self._use_ssl:
            tls_kwargs = {"validate": ssl.CERT_REQUIRED}
            if self._ca_cert_path:
                tls_kwargs["ca_certs_file"] = self._ca_cert_path
            tls = ldap3.Tls(**tls_kwargs)

        server = ldap3.Server(
            self._hostname,
            port=self._port,
            use_ssl=self._use_ssl,
            tls=tls,
            connect_timeout=self._timeout,
        )

        if self._use_kerberos and self._keytab_path:
            self._kinit()
            self._conn = ldap3.Connection(
                server,
                authentication=ldap3.SASL,
                sasl_mechanism=ldap3.GSSAPI,
                auto_bind=False,
                receive_timeout=self._timeout,
            )
            if not self._use_ssl:
                self._conn.open()
                self._conn.start_tls()
            self._conn.bind()
            self._logger.info("LDAP GSSAPI bind established")
        else:
            self._conn = ldap3.Connection(
                server,
                user=self._bind_dn,
                password=self._bind_password,
                auto_bind=False,
                receive_timeout=self._timeout,
            )
            if not self._use_ssl:
                self._conn.open()
                self._conn.start_tls()
                self._conn.bind()
            else:
                self._conn.bind()
            self._logger.info("LDAP simple bind established")

    def _kinit(self):
        try:
            subprocess.run(
                ["kinit", "-kt", self._keytab_path, self._principal],
                capture_output=True, text=True, timeout=10, check=True,
            )
            self._logger.info(f"kinit successful for {self._principal}")
        except subprocess.CalledProcessError as e:
            raise LDAPException(f"kinit failed: {e.stderr}") from e
        except FileNotFoundError:
            raise LDAPException("kinit command not found — is krb5-workstation installed?")

    def disconnect(self):
        if self._conn:
            try:
                self._conn.unbind()
            except LDAPException:
                pass
            self._conn = None

    def _ensure_connected(self):
        if self._conn is None:
            self.connect()
            return
        if not self._conn.bound:
            self._logger.warning("LDAP connection lost, reconnecting...")
            self.disconnect()
            self.connect()

    def _search(self, base, scope, filter_str, attrs):
        self._ensure_connected()
        try:
            self._conn.search(
                search_base=base,
                search_filter=filter_str,
                search_scope=scope,
                attributes=attrs,
            )
        except LDAPNoSuchObjectResult:
            raise
        except LDAPException:
            self._logger.warning("LDAP search failed, reconnecting...")
            self.disconnect()
            self.connect()
            self._conn.search(
                search_base=base,
                search_filter=filter_str,
                search_scope=scope,
                attributes=attrs,
            )

        results = []
        for entry in self._conn.entries:
            attr_dict = {}
            for attr_name in entry.entry_attributes:
                values = entry[attr_name].values
                if values:
                    attr_dict[attr_name.lower()] = values[0] if len(values) == 1 else values
            results.append((str(entry.entry_dn), attr_dict))
        return results

    def _get_attr(self, entry, attr, default="0"):
        attr_lower = attr.lower()
        val = entry.get(attr_lower)
        if val is None:
            for key in entry:
                if key.lower() == attr_lower:
                    val = entry[key]
                    break
        if val is None:
            return default
        if isinstance(val, list) and val:
            val = val[0]
        return str(val)

    def _safe_int(self, entry, attr, default=0):
        try:
            return int(self._get_attr(entry, attr, str(default)))
        except (ValueError, TypeError):
            return default

    def _safe_float(self, entry, attr, default=0.0):
        try:
            return float(self._get_attr(entry, attr, str(default)))
        except (ValueError, TypeError):
            return default

    def collect_monitor_metrics(self):
        results = self._search(C.MONITOR_DN, ldap3.BASE, "(objectclass=*)", C.MONITOR_ATTRS)
        if not results:
            return {}

        _, entry = results[0]
        metrics = {}

        attr_to_metric = {
            "currentconnections": C.LDAP_CURRENT_CONNECTIONS,
            "totalconnections": C.LDAP_TOTAL_CONNECTIONS,
            "currentconnectionsatmaxthreads": C.LDAP_CONNECTIONS_AT_MAXTHREADS,
            "opsinitiated": C.LDAP_OPS_INITIATED,
            "opscompleted": C.LDAP_OPS_COMPLETED,
            "entriessent": C.LDAP_ENTRIES_SENT,
            "bytessent": C.LDAP_BYTES_SENT,
            "threads": C.LDAP_THREADS,
            "readwaiters": C.LDAP_READ_WAITERS,
            "dtablesize": C.LDAP_DTABLE_SIZE,
        }

        for attr, metric_key in attr_to_metric.items():
            metrics[metric_key] = self._safe_int(entry, attr)

        return metrics

    def collect_snmp_metrics(self):
        results = self._search(C.SNMP_MONITOR_DN, ldap3.BASE, "(objectclass=*)", C.SNMP_ATTRS)
        if not results:
            return {}

        _, entry = results[0]
        metrics = {}

        attr_to_metric = {
            "anonymousbinds": C.LDAP_ANONYMOUS_BINDS,
            "simpleauthbinds": C.LDAP_SIMPLE_AUTH_BINDS,
            "strongauthbinds": C.LDAP_STRONG_AUTH_BINDS,
            "bindsecurityerrors": C.LDAP_BIND_SECURITY_ERRORS,
            "searchops": C.LDAP_SEARCH_OPS,
            "addentryops": C.LDAP_ADD_ENTRY_OPS,
            "modifyentryops": C.LDAP_MODIFY_ENTRY_OPS,
            "removeentryops": C.LDAP_REMOVE_ENTRY_OPS,
            "errors": C.LDAP_ERRORS,
        }

        for attr, metric_key in attr_to_metric.items():
            metrics[metric_key] = self._safe_int(entry, attr)

        return metrics

    def discover_backends(self):
        results = self._search(
            C.LDBM_PLUGIN_DN, ldap3.LEVEL,
            C.BACKEND_FILTER, ["cn"]
        )
        backends = []
        for dn, entry in results:
            cn = self._get_attr(entry, "cn", "")
            if cn:
                backends.append(cn)
        return backends

    def collect_backend_cache_metrics(self):
        backends = self.discover_backends()
        all_metrics = []

        for backend in backends:
            monitor_dn = f"cn=monitor,cn={backend},{C.LDBM_PLUGIN_DN}"
            try:
                results = self._search(
                    monitor_dn, ldap3.BASE,
                    "(objectclass=*)", C.BACKEND_CACHE_ATTRS
                )
            except LDAPNoSuchObjectResult:
                self._logger.debug(f"No monitor entry for backend {backend}")
                continue

            if not results:
                continue

            _, entry = results[0]
            metrics = {
                "backend": backend,
                C.LDAP_BACKEND_ENTRY_CACHE_HIT_RATIO: self._safe_float(entry, "entrycachehitratio"),
                C.LDAP_BACKEND_ENTRY_CACHE_COUNT: self._safe_int(entry, "currententrycachecount"),
                C.LDAP_BACKEND_ENTRY_CACHE_SIZE: self._safe_int(entry, "currententrycachesize"),
                C.LDAP_BACKEND_ENTRY_CACHE_MAX_SIZE: self._safe_int(entry, "maxentrycachesize"),
                C.LDAP_BACKEND_DN_CACHE_HIT_RATIO: self._safe_float(entry, "dncachehitratio"),
                C.LDAP_BACKEND_DN_CACHE_COUNT: self._safe_int(entry, "currententrydncachecount"),
                C.LDAP_BACKEND_DN_CACHE_SIZE: self._safe_int(entry, "currententrydncachesize"),
            }
            all_metrics.append(metrics)

        return all_metrics

    def collect_replication_agreements(self):
        try:
            results = self._search(
                C.MAPPING_TREE_DN, ldap3.SUBTREE,
                C.REPL_AGREEMENT_FILTER, C.REPL_ATTRS
            )
        except LDAPNoSuchObjectResult:
            return []

        agreements = []
        for dn, entry in results:
            cn = self._get_attr(entry, "cn", "")
            replica_host = self._get_attr(entry, "nsDS5ReplicaHost", "")
            suffix = self._get_attr(entry, "nsDS5ReplicaRoot", "")
            status_str = self._get_attr(entry, "nsds5replicaLastUpdateStatus", "")
            update_start = self._get_attr(entry, "nsds5replicaLastUpdateStart", "")
            update_end = self._get_attr(entry, "nsds5replicaLastUpdateEnd", "")
            in_progress = self._get_attr(entry, "nsds5replicaUpdateInProgress", "FALSE")
            changes_sent = self._get_attr(entry, "nsds5replicaChangesSentSinceStartup", "0")

            status_code = 0
            if status_str:
                try:
                    status_code = int(status_str.split()[0])
                except (ValueError, IndexError):
                    status_code = -1

            lag_seconds = 0.0
            if update_start and update_end:
                lag_seconds = self._calculate_lag(update_start, update_end)

            changes_int = 0
            try:
                changes_int = int(changes_sent)
            except (ValueError, TypeError):
                pass

            agreements.append({
                "cn": cn,
                "replica_host": replica_host,
                "suffix": suffix,
                "status_code": status_code,
                "status_text": status_str,
                "lag_seconds": lag_seconds,
                "update_in_progress": 1 if in_progress.upper() == "TRUE" else 0,
                "changes_sent": changes_int,
            })

        return agreements

    def _calculate_lag(self, start_str, end_str):
        from datetime import datetime
        fmt = "%Y%m%d%H%M%SZ"
        try:
            start = datetime.strptime(start_str, fmt)
            end = datetime.strptime(end_str, fmt)
            delta = (end - start).total_seconds()
            return max(0.0, delta)
        except ValueError:
            return 0.0

    def count_replication_conflicts(self):
        try:
            results = self._search(
                self._base_dn, ldap3.SUBTREE,
                C.REPL_CONFLICT_FILTER, ["dn"]
            )
            return len(results)
        except LDAPNoSuchObjectResult:
            return 0

    def collect_dns_zones(self):
        dns_dn = f"cn=dns,{self._base_dn}"
        try:
            results = self._search(
                dns_dn, ldap3.LEVEL,
                C.DNS_ZONE_FILTER, ["idnsName"]
            )
        except LDAPNoSuchObjectResult:
            return []

        zones = []
        for dn, entry in results:
            name = self._get_attr(entry, "idnsName", "")
            if name:
                zones.append({"name": name, "dn": dn})
        return zones

    def count_dns_records(self, zone_dn):
        try:
            results = self._search(
                zone_dn, ldap3.LEVEL,
                C.DNS_RECORD_FILTER, ["dn"]
            )
            return len(results)
        except LDAPNoSuchObjectResult:
            return 0

    def check_srv_record(self, zone_dn, srv_name):
        record_dn = f"idnsName={srv_name},{zone_dn}"
        try:
            results = self._search(
                record_dn, ldap3.BASE,
                "(objectclass=idnsrecord)", ["sRVRecord"]
            )
            if results:
                _, entry = results[0]
                srv_val = entry.get("srvrecord") or entry.get("sRVRecord")
                return srv_val is not None and srv_val != ""
            return False
        except LDAPNoSuchObjectResult:
            return False

    def is_connected(self):
        if self._conn is None:
            return False
        return self._conn.bound
