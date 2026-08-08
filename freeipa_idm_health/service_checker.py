import socket
import ssl
import subprocess
import urllib.error
import urllib.request

from . import constants as C


class ServiceChecker:

    _SERVICE_PORTS = {
        "dirsrv": 636,
        "krb5kdc": 88,
        "kadmin": 749,
        "httpd": 443,
        "pki-tomcatd": 8443,
        "named": 53,
    }

    _CORE_SERVICES = ("dirsrv", "krb5kdc", "kadmin", "httpd")

    _ROLE_TO_SERVICES = {
        "CA server": ("pki-tomcatd", "certmonger"),
        "DNS server": ("named",),
    }

    def __init__(self, hostname, realm, logger, is_local=False, ipa_api_client=None):
        self._hostname = hostname
        self._realm = realm
        self._logger = logger
        self._is_local = is_local
        self._ipa_api_client = ipa_api_client

    def check_all_services(self):
        results = {}
        roles = self._get_server_roles() if not self._is_local else None

        for service_name, unit_template in C.IPA_SERVICES:
            unit = unit_template.format(realm=self._realm)
            if self._is_local:
                results[service_name] = self._check_systemd_unit(unit)
            else:
                results[service_name] = self._check_remote_service(service_name, roles)
        return results

    def _check_systemd_unit(self, unit):
        try:
            result = subprocess.run(
                ["systemctl", "is-active", unit],
                capture_output=True, text=True, timeout=10
            )
            is_active = result.stdout.strip() == "active"
            if not is_active:
                self._logger.warning(f"Service {unit} is not active: {result.stdout.strip()}")
            return 1 if is_active else 0
        except subprocess.TimeoutExpired:
            self._logger.error(f"Timeout checking service {unit}")
            return 0
        except FileNotFoundError:
            self._logger.error("systemctl not found")
            return 0

    def _check_remote_service(self, service_name, roles):
        if service_name in self._CORE_SERVICES:
            return self._probe_service(service_name)

        if roles is None:
            return -1

        role_status = self._get_role_for_service(service_name, roles)
        if role_status != "enabled":
            return -1

        if service_name not in self._SERVICE_PORTS:
            return 1

        return self._probe_service(service_name)

    def _probe_service(self, service_name):
        probes = {
            "dirsrv": self._probe_tls,
            "httpd": self._probe_https,
            "kadmin": self._probe_kadmin,
            "pki-tomcatd": self._probe_pki,
            "named": self._probe_dns,
        }
        probe = probes.get(service_name)
        if probe:
            result = probe(service_name)
            if result is not None:
                return result
        return self._probe_port(service_name)

    def _probe_tls(self, service_name):
        port = self._SERVICE_PORTS[service_name]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            sock = socket.create_connection((self._hostname, port), timeout=5)
            ssl_sock = ctx.wrap_socket(sock, server_hostname=self._hostname)
            ssl_sock.close()
            return 1
        except (OSError, socket.timeout, ssl.SSLError):
            self._logger.warning(
                f"TLS probe failed for {service_name}:{port} on {self._hostname}"
            )
            return 0

    def _probe_https(self, _service_name):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            urllib.request.urlopen(
                f"https://{self._hostname}/ipa/config/ca.crt",
                timeout=5, context=ctx,
            )
            return 1
        except urllib.error.HTTPError:
            return 1
        except (urllib.error.URLError, socket.timeout, OSError):
            self._logger.warning(f"HTTPS probe failed for httpd on {self._hostname}")
            return 0

    def _probe_kadmin(self, _service_name):
        """kadmind serves kpasswd on port 464, which is open to remote
        clients. If kadmind is stopped, both 749 and 464 go down."""
        try:
            sock = socket.create_connection((self._hostname, 464), timeout=5)
            sock.close()
            return 1
        except (OSError, socket.timeout):
            self._logger.warning(
                f"kadmin (kpasswd) port 464 not responding on {self._hostname}"
            )
            return 0

    def _probe_pki(self, _service_name):
        """pki-tomcatd binds to localhost:8443; httpd proxies to it.
        Check the CA OCSP responder through httpd on port 443.
        502/503 from httpd means the PKI backend is down."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            urllib.request.urlopen(
                f"https://{self._hostname}/ca/ocsp",
                timeout=5, context=ctx,
            )
            return 1
        except urllib.error.HTTPError as e:
            if e.code in (502, 503):
                self._logger.warning(
                    f"pki-tomcatd backend unreachable (HTTP {e.code}) on {self._hostname}"
                )
                return 0
            return 1
        except (urllib.error.URLError, socket.timeout, OSError):
            self._logger.warning(
                f"PKI probe failed for pki-tomcatd on {self._hostname}"
            )
            return 0

    def _probe_dns(self, _service_name):
        try:
            result = subprocess.run(
                ["dig", f"@{self._hostname}", self._hostname,
                 "+short", "+time=3", "+tries=1"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return 1
            self._logger.warning(
                f"DNS probe failed for named on {self._hostname}: "
                f"dig returned {result.returncode}"
            )
            return 0
        except FileNotFoundError:
            return None
        except (subprocess.TimeoutExpired, OSError):
            self._logger.warning(f"DNS probe failed for named on {self._hostname}")
            return 0

    def _probe_port(self, service_name):
        port = self._SERVICE_PORTS[service_name]
        try:
            sock = socket.create_connection((self._hostname, port), timeout=5)
            sock.close()
            return 1
        except (OSError, socket.timeout):
            self._logger.warning(
                f"Service {service_name} port {port} not responding on {self._hostname}"
            )
            return 0

    def _get_role_for_service(self, service_name, roles):
        for role, services in self._ROLE_TO_SERVICES.items():
            if service_name in services:
                return roles.get(role)
        return None

    def _get_server_roles(self):
        if not self._ipa_api_client:
            return None
        if not hasattr(self, "_server_roles"):
            try:
                result = self._ipa_api_client._rpc_call(
                    "server_role_find",
                    options={"server_server": self._hostname, "sizelimit": 0},
                )
                if result:
                    self._server_roles = {
                        r["role_servrole"]: r["status"]
                        for r in result.get("result", [])
                    }
                else:
                    self._server_roles = None
            except Exception as e:
                self._logger.warning(f"Could not fetch server roles: {e}")
                self._server_roles = None
        return self._server_roles
