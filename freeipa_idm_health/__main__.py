from dynatrace_extension import Extension, Status, StatusValue

from . import constants as C
from .cert_monitor import CertMonitor
from .dns_monitor import DnsMonitor
from .healthcheck_runner import HealthcheckRunner
from .ipa_api_client import IpaApiClient
from .ldap_collector import LdapCollector
from .replication_monitor import ReplicationMonitor
from .service_checker import ServiceChecker


class FreeIpaExtension(Extension):

    def initialize(self):
        self._ldap = None
        self._ipa_api = None
        self._config = {}
        self._is_local = False

    def query(self):
        config = self._load_config()
        if config is None:
            return

        self._setup_collectors(config)

        base_dims = {
            "freeipa.server": config["hostname"],
            "freeipa.domain": self._extract_domain(config["ldap_base_dn"]),
        }

        collectors = [
            ("services", config.get("enable_services", True), self._collect_services),
            ("ldap", config.get("enable_ldap_metrics", True), self._collect_ldap_metrics),
            ("replication", config.get("enable_replication", True), self._collect_replication),
            ("dns", config.get("enable_dns", True), self._collect_dns),
            ("certificates", config.get("enable_certificates", True), self._collect_certificates),
            ("healthcheck", config.get("enable_healthcheck", False) and self._is_local, self._collect_healthcheck),
        ]

        for name, enabled, collector_fn in collectors:
            if not enabled:
                continue
            try:
                collector_fn(config, base_dims)
            except Exception as e:
                self.logger.error(f"Collection failed for {name}: {e}")

    def fastcheck(self):
        config = self._load_config()
        if config is None:
            return Status(StatusValue.INVALID_CONFIG_ERROR, "No configuration found")

        has_ldap_creds = config.get("ldap_bind_dn") and config.get("ldap_bind_password")

        if has_ldap_creds:
            try:
                ldap_conn = LdapCollector(
                    hostname=config["hostname"],
                    port=config.get("ldap_port", C.DEFAULT_LDAP_PORT),
                    use_ssl=config.get("ldap_use_ssl", True),
                    bind_dn=config.get("ldap_bind_dn", ""),
                    bind_password=config.get("ldap_bind_password", ""),
                    base_dn=config["ldap_base_dn"],
                    timeout=config.get("ldap_timeout", C.DEFAULT_LDAP_TIMEOUT),
                    ca_cert_path=config.get("ldap_ca_cert_path", ""),
                    logger=self.logger,
                )
                ldap_conn.connect()
                ldap_conn.disconnect()
                return Status(StatusValue.OK, f"Connected to {config['hostname']}")
            except Exception as e:
                return Status(StatusValue.DEVICE_CONNECTION_ERROR, f"LDAP connection failed: {e}")

        if config.get("use_kerberos"):
            try:
                api = IpaApiClient(
                    hostname=config["hostname"],
                    ca_cert_path=config.get("ldap_ca_cert_path", ""),
                    logger=self.logger,
                    use_kerberos=True,
                    keytab_path=config.get("kerberos_keytab_path", ""),
                    principal=config.get("kerberos_principal", ""),
                )
                if api.authenticate():
                    api.close()
                    return Status(StatusValue.OK, f"Kerberos auth to {config['hostname']}")
                api.close()
                return Status(StatusValue.DEVICE_CONNECTION_ERROR, "IPA API Kerberos auth failed")
            except Exception as e:
                return Status(StatusValue.DEVICE_CONNECTION_ERROR, f"Kerberos auth failed: {e}")

        return Status(StatusValue.INVALID_CONFIG_ERROR, "No LDAP or Kerberos credentials configured")

    def on_shutdown(self):
        if self._ldap:
            self._ldap.disconnect()
        if self._ipa_api:
            self._ipa_api.close()

    def _load_config(self):
        activation = self.get_activation_config()
        if not activation.get("hostname"):
            self.logger.error("No hostname configured")
            return None

        use_kerberos = activation.get("use_kerberos", False)
        has_ldap_creds = activation.get("ldap_bind_dn") and activation.get("ldap_bind_password")
        has_kerberos_creds = activation.get("kerberos_keytab_path") and activation.get("kerberos_principal")

        if use_kerberos and not has_kerberos_creds:
            self.logger.error("Kerberos keytab path and principal required when Kerberos is enabled")
            return None

        if not use_kerberos and not has_ldap_creds:
            self.logger.error("LDAP bind DN and password required when Kerberos is disabled")
            return None

        return activation

    def _setup_collectors(self, config):
        has_ldap_creds = config.get("ldap_bind_dn") and config.get("ldap_bind_password")

        if self._ldap is None and has_ldap_creds:
            self._ldap = LdapCollector(
                hostname=config["hostname"],
                port=config.get("ldap_port", C.DEFAULT_LDAP_PORT),
                use_ssl=config.get("ldap_use_ssl", True),
                bind_dn=config.get("ldap_bind_dn", ""),
                bind_password=config.get("ldap_bind_password", ""),
                base_dn=config["ldap_base_dn"],
                timeout=config.get("ldap_timeout", C.DEFAULT_LDAP_TIMEOUT),
                ca_cert_path=config.get("ldap_ca_cert_path", ""),
                logger=self.logger,
            )

        if self._ipa_api is None and (config.get("use_kerberos") or config.get("ipa_api_password")):
            bind_dn = config.get("ldap_bind_dn", "")
            api_username = None
            if "uid=" in bind_dn:
                api_username = bind_dn.split("uid=")[1].split(",")[0]

            self._ipa_api = IpaApiClient(
                hostname=config["hostname"],
                ca_cert_path=config.get("ldap_ca_cert_path", ""),
                logger=self.logger,
                use_kerberos=config.get("use_kerberos", False),
                keytab_path=config.get("kerberos_keytab_path", ""),
                principal=config.get("kerberos_principal", ""),
                api_password=config.get("ipa_api_password", ""),
                api_username=api_username,
            )

    def _extract_domain(self, base_dn):
        parts = []
        for component in base_dn.split(","):
            component = component.strip()
            if component.lower().startswith("dc="):
                parts.append(component[3:])
        return ".".join(parts) if parts else base_dn

    def _extract_realm(self, base_dn):
        return self._extract_domain(base_dn).upper().replace(".", "-")

    def _collect_services(self, config, base_dims):
        domain = self._extract_domain(config["ldap_base_dn"])
        realm = domain.upper()
        checker = ServiceChecker(
            hostname=config["hostname"],
            realm=realm,
            logger=self.logger,
            is_local=self._is_local,
            ipa_api_client=self._ipa_api,
        )

        services = checker.check_all_services()
        for service_name, status in services.items():
            if status < 0:
                continue
            dims = {**base_dims, "service.name": service_name}
            self.report_metric(key=C.SERVICE_STATUS, value=status, dimensions=dims)

    def _collect_ldap_metrics(self, config, base_dims):
        if self._ldap is None:
            return
        monitor_metrics = self._ldap.collect_monitor_metrics()
        for metric_key, value in monitor_metrics.items():
            self.report_metric(key=metric_key, value=value, dimensions=base_dims)

        snmp_metrics = self._ldap.collect_snmp_metrics()
        for metric_key, value in snmp_metrics.items():
            self.report_metric(key=metric_key, value=value, dimensions=base_dims)

        backend_metrics = self._ldap.collect_backend_cache_metrics()
        for backend_data in backend_metrics:
            backend_name = backend_data.pop("backend")
            dims = {**base_dims, "ldap.backend": backend_name}
            for metric_key, value in backend_data.items():
                self.report_metric(key=metric_key, value=value, dimensions=dims)

    def _collect_replication(self, config, base_dims):
        if self._ldap is None:
            return
        domain = self._extract_domain(config["ldap_base_dn"])
        monitor = ReplicationMonitor(self._ldap, config["hostname"], domain, self.logger)
        result = monitor.collect_all()

        for agreement in result["agreements"]:
            dims = {
                **base_dims,
                "replication.agreement": agreement["agreement_name"],
                "replication.replica_host": agreement["replica_host"],
                "replication.suffix": agreement["suffix"],
            }
            for metric_key, value in agreement["metrics"].items():
                self.report_metric(key=metric_key, value=value, dimensions=dims)

        self.report_metric(
            key=C.REPL_CONFLICT_ENTRIES,
            value=result["conflict_count"],
            dimensions=base_dims,
        )

        if result["conflict_count"] > 0:
            self.report_event(
                title=f"Replication conflicts detected: {result['conflict_count']}",
                description=f"{result['conflict_count']} replication conflict entries found on {config['hostname']}",
            )

    def _collect_certificates(self, config, base_dims):
        domain = self._extract_domain(config["ldap_base_dn"])
        monitor = CertMonitor(
            hostname=config["hostname"],
            domain=domain,
            logger=self.logger,
            is_local=self._is_local,
            ipa_api_client=self._ipa_api,
        )

        result = monitor.collect_all()
        self.report_metric(
            key=C.CERT_TOTAL_TRACKED,
            value=result["total_tracked"],
            dimensions=base_dims,
        )

        for cert in result["certs"]:
            dims = {
                **base_dims,
                "cert.subject": cert["subject"],
                "cert.serial_number": cert["serial"],
            }
            self.report_metric(key=C.CERT_STATUS, value=cert["status_value"], dimensions=dims)
            if cert["days_until_expiry"] >= 0:
                self.report_metric(key=C.CERT_DAYS_UNTIL_EXPIRY, value=cert["days_until_expiry"], dimensions=dims)

        alerts = monitor.get_expiry_alerts(result["certs"])
        for alert in alerts:
            self.report_event(title=alert["title"], description=alert["description"])

    def _collect_dns(self, config, base_dims):
        if self._ldap is None:
            return
        domain = self._extract_domain(config["ldap_base_dn"])
        monitor = DnsMonitor(self._ldap, config["hostname"], domain, self.logger)
        result = monitor.collect_all()

        self.report_metric(key=C.DNS_ZONE_COUNT, value=result["zone_count"], dimensions=base_dims)

        for zone in result["zones"]:
            dims = {**base_dims, "dns.zone": zone["zone_name"]}
            self.report_metric(key=C.DNS_RECORD_COUNT, value=zone["record_count"], dimensions=dims)

        for srv in result["srv_records"]:
            dims = {**base_dims, "dns.srv_type": srv["srv_type"]}
            self.report_metric(key=C.DNS_SRV_RECORD_VALID, value=srv["valid"], dimensions=dims)

    def _collect_healthcheck(self, config, base_dims):
        runner = HealthcheckRunner(config["hostname"], self._extract_domain(config["ldap_base_dn"]), self.logger)
        result = runner.run()
        if result is None:
            return

        counts = result["counts"]
        self.report_metric(key=C.HC_TOTAL_CHECKS, value=counts["total"], dimensions=base_dims)
        self.report_metric(key=C.HC_WARNING_COUNT, value=counts["warning"], dimensions=base_dims)
        self.report_metric(key=C.HC_ERROR_COUNT, value=counts["error"], dimensions=base_dims)
        self.report_metric(key=C.HC_CRITICAL_COUNT, value=counts["critical"], dimensions=base_dims)

        for failure in result["failures"]:
            self.report_event(title=failure["title"], description=failure["description"])


def main():
    FreeIpaExtension().run()


if __name__ == "__main__":
    main()
