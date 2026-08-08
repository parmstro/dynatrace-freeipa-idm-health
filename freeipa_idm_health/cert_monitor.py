import re
import subprocess
from datetime import datetime

from . import constants as C


class CertMonitor:

    def __init__(self, hostname, domain, logger, is_local=False, ipa_api_client=None):
        self._hostname = hostname
        self._domain = domain
        self._logger = logger
        self._is_local = is_local
        self._ipa_api_client = ipa_api_client

    def collect_all(self):
        if self._is_local:
            return self._collect_local()
        elif self._ipa_api_client:
            return self._collect_remote()
        return {"certs": [], "total_tracked": 0}

    def _collect_local(self):
        try:
            result = subprocess.run(
                ["getcert", "list"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self._logger.error(f"getcert list failed: {result.stderr}")
                return {"certs": [], "total_tracked": 0}
            return self._parse_getcert_output(result.stdout)
        except subprocess.TimeoutExpired:
            self._logger.error("Timeout running getcert list")
            return {"certs": [], "total_tracked": 0}
        except FileNotFoundError:
            self._logger.debug("getcert command not found")
            return {"certs": [], "total_tracked": 0}

    def _parse_getcert_output(self, output):
        certs = []
        current = {}

        for line in output.splitlines():
            line = line.strip()

            if line.startswith("Request ID"):
                if current:
                    certs.append(current)
                current = {"request_id": line.split("'")[1] if "'" in line else ""}

            elif line.startswith("status:"):
                current["status"] = line.split(":", 1)[1].strip()

            elif line.startswith("subject:"):
                current["subject"] = line.split(":", 1)[1].strip()

            elif line.startswith("expires:"):
                expiry_str = line.split(":", 1)[1].strip()
                current["expiry_str"] = expiry_str
                current["days_until_expiry"] = self._parse_expiry(expiry_str)

            elif line.startswith("serial number:"):
                current["serial"] = line.split(":", 1)[1].strip()

        if current:
            certs.append(current)

        parsed = []
        for cert in certs:
            status = cert.get("status", "")
            is_monitoring = 1 if status == "MONITORING" else 0
            days = cert.get("days_until_expiry", -1)
            subject = cert.get("subject", "unknown")
            serial = cert.get("serial", "unknown")

            parsed.append({
                "subject": subject,
                "serial": serial,
                "status_value": is_monitoring,
                "days_until_expiry": days,
                "status_text": status,
            })

        return {"certs": parsed, "total_tracked": len(parsed)}

    def _parse_expiry(self, expiry_str):
        formats = [
            "%Y-%m-%d %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S",
            "%a %b %d %H:%M:%S %Y %Z",
            "%a %b %d %H:%M:%S %Y",
        ]
        for fmt in formats:
            try:
                expiry = datetime.strptime(expiry_str, fmt)
                delta = expiry - datetime.utcnow()
                return max(0, delta.days)
            except ValueError:
                continue

        match = re.search(r"(\d{4}-\d{2}-\d{2})", expiry_str)
        if match:
            try:
                expiry = datetime.strptime(match.group(1), "%Y-%m-%d")
                delta = expiry - datetime.utcnow()
                return max(0, delta.days)
            except ValueError:
                pass

        self._logger.warning(f"Could not parse certificate expiry date: {expiry_str}")
        return -1

    def _collect_remote(self):
        try:
            certs = self._ipa_api_client.cert_find()
            parsed = []
            for cert in certs:
                not_after = cert.get("valid_not_after", "")
                subject = cert.get("subject", "unknown")
                serial = str(cert.get("serial_number", "unknown"))
                status = cert.get("status", "")

                days = -1
                if not_after:
                    days = self._parse_api_expiry(not_after)

                is_valid = 1 if status in ("VALID", "") else 0

                parsed.append({
                    "subject": subject,
                    "serial": serial,
                    "status_value": is_valid,
                    "days_until_expiry": days,
                    "status_text": status,
                })

            return {"certs": parsed, "total_tracked": len(parsed)}
        except Exception as e:
            self._logger.error(f"Remote certificate collection failed: {e}")
            return {"certs": [], "total_tracked": 0}

    def _parse_api_expiry(self, not_after):
        if isinstance(not_after, str):
            formats = [
                "%a %b %d %H:%M:%S %Y %Z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y%m%d%H%M%SZ",
            ]
            for fmt in formats:
                try:
                    expiry = datetime.strptime(not_after, fmt)
                    delta = expiry - datetime.utcnow()
                    return max(0, delta.days)
                except ValueError:
                    continue
        return -1

    def get_expiry_alerts(self, certs, warning_days=30, critical_days=7):
        alerts = []
        for cert in certs:
            days = cert.get("days_until_expiry", -1)
            if days < 0:
                continue

            subject = cert.get("subject", "unknown")
            if days <= critical_days:
                alerts.append({
                    "severity": "CRITICAL",
                    "title": f"Certificate expiring in {days} days",
                    "description": f"Certificate {subject} expires in {days} days",
                    "subject": subject,
                })
            elif days <= warning_days:
                alerts.append({
                    "severity": "WARNING",
                    "title": f"Certificate expiring in {days} days",
                    "description": f"Certificate {subject} expires in {days} days",
                    "subject": subject,
                })

        return alerts
