import subprocess

import requests
from requests.exceptions import ConnectionError, Timeout


class IpaApiClient:

    def __init__(self, hostname, ca_cert_path, logger,
                 use_kerberos=False, keytab_path=None, principal=None,
                 api_password=None, api_username=None):
        self._hostname = hostname
        self._ca_cert_path = ca_cert_path
        self._logger = logger
        self._use_kerberos = use_kerberos
        self._keytab_path = keytab_path
        self._principal = principal
        self._api_password = api_password
        self._api_username = api_username
        self._session = requests.Session()
        self._session.verify = ca_cert_path if ca_cert_path else True
        self._authenticated = False
        self._api_version = "2.251"

    @property
    def _base_url(self):
        return f"https://{self._hostname}/ipa"

    @property
    def _json_url(self):
        return f"{self._base_url}/session/json"

    def authenticate(self):
        if self._use_kerberos and self._keytab_path:
            return self._authenticate_kerberos()
        elif self._api_password:
            return self._authenticate_password()
        else:
            self._logger.error("No authentication method configured for IPA API")
            return False

    def _authenticate_password(self):
        login_url = f"{self._base_url}/session/login_password"
        username = self._api_username or "admin"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"https://{self._hostname}/ipa/ui/",
        }

        try:
            response = self._session.post(
                login_url,
                data=f"user={username}&password={self._api_password}",
                headers=headers,
                timeout=(5, 30),
            )
            if response.status_code == 200:
                self._authenticated = True
                self._logger.info("IPA API password authentication successful")
                return True
            else:
                self._logger.error(
                    f"IPA API password auth failed: HTTP {response.status_code}"
                )
                return False
        except (ConnectionError, Timeout) as e:
            self._logger.error(f"IPA API connection failed: {e}")
            return False

    def _authenticate_kerberos(self):
        try:
            subprocess.run(
                ["kinit", "-kt", self._keytab_path, self._principal],
                capture_output=True, text=True, timeout=10, check=True,
            )
            self._logger.info(f"kinit successful for {self._principal}")
        except subprocess.CalledProcessError as e:
            self._logger.error(f"kinit failed: {e.stderr}")
            return False
        except FileNotFoundError:
            self._logger.error(
                "kinit not found — is krb5-workstation installed?"
            )
            return False

        login_url = f"{self._base_url}/session/login_kerberos"

        try:
            curl_cmd = [
                "curl", "--negotiate", "-u", ":",
                "-s", "-o", "/dev/null",
                "-w", "%{http_code}",
                "-D", "-",
                "-H", f"Referer: https://{self._hostname}/ipa/ui/",
                login_url,
            ]
            if self._ca_cert_path:
                curl_cmd.extend(["--cacert", self._ca_cert_path])

            result = subprocess.run(
                curl_cmd,
                capture_output=True, text=True, timeout=30,
            )

            http_code = result.stdout.strip().split("\n")[-1].strip()
            if http_code != "200":
                self._logger.error(
                    f"IPA API Kerberos auth failed: HTTP {http_code}"
                )
                return False

            for line in result.stderr.split("\n") + result.stdout.split("\n"):
                if line.lower().startswith("set-cookie:"):
                    cookie_str = line.split(":", 1)[1].strip()
                    cookie_name = cookie_str.split("=")[0].strip()
                    cookie_val = cookie_str.split("=", 1)[1].split(";")[0].strip()
                    self._session.cookies.set(
                        cookie_name, cookie_val,
                        domain=self._hostname, path="/ipa",
                    )

            self._authenticated = True
            self._logger.info("IPA API Kerberos authentication successful")
            return True

        except subprocess.CalledProcessError as e:
            self._logger.error(f"curl negotiate failed: {e.stderr}")
            return False
        except FileNotFoundError:
            self._logger.error(
                "curl not found — is curl installed with GSSAPI support?"
            )
            return False
        except Exception as e:
            self._logger.error(f"IPA API Kerberos auth error: {e}")
            return False

    def _ensure_authenticated(self):
        if not self._authenticated:
            self.authenticate()

    def _rpc_call(self, method, args=None, options=None):
        self._ensure_authenticated()

        if args is None:
            args = []
        if options is None:
            options = {}
        options["version"] = self._api_version

        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://{self._hostname}/ipa/ui/",
            "Accept": "application/json",
        }

        payload = {
            "method": method,
            "params": [args, options],
            "id": 0,
        }

        try:
            response = self._session.post(
                self._json_url,
                json=payload,
                headers=headers,
                timeout=(5, 30),
            )

            if response.status_code == 401:
                self._authenticated = False
                self.authenticate()
                response = self._session.post(
                    self._json_url,
                    json=payload,
                    headers=headers,
                    timeout=(5, 30),
                )

            response.raise_for_status()
            data = response.json()

            if data.get("error"):
                error = data["error"]
                self._logger.error(
                    f"IPA API error: {error.get('name', 'unknown')}: "
                    f"{error.get('message', 'no message')}"
                )
                return None

            return data.get("result", {})

        except (ConnectionError, Timeout) as e:
            self._logger.error(f"IPA API request failed: {e}")
            return None
        except Exception as e:
            self._logger.error(f"IPA API unexpected error: {e}")
            return None

    def ping(self):
        result = self._rpc_call("ping")
        return result is not None

    def server_find(self):
        result = self._rpc_call("server_find", options={"sizelimit": 0})
        if result:
            return result.get("result", [])
        return []

    def cert_find(self, **kwargs):
        options = {"sizelimit": 0}
        options.update(kwargs)
        result = self._rpc_call("cert_find", options=options)
        if result:
            return result.get("result", [])
        return []

    def dnszone_find(self):
        result = self._rpc_call("dnszone_find", options={"sizelimit": 0, "pkey_only": True})
        if result:
            return result.get("result", [])
        return []

    def topologysegment_find(self, suffix="domain"):
        result = self._rpc_call("topologysegment_find", args=[suffix], options={"sizelimit": 0})
        if result:
            return result.get("result", [])
        return []

    def close(self):
        self._session.close()
        if self._use_kerberos:
            try:
                subprocess.run(
                    ["kdestroy"], capture_output=True, timeout=5,
                )
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
