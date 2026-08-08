import json
import shutil
import subprocess


class HealthcheckRunner:

    def __init__(self, hostname, domain, logger):
        self._hostname = hostname
        self._domain = domain
        self._logger = logger

    def is_available(self):
        return shutil.which("ipa-healthcheck") is not None

    def run(self):
        if not self.is_available():
            self._logger.debug("ipa-healthcheck not found, skipping")
            return None

        try:
            result = subprocess.run(
                ["ipa-healthcheck", "--output-type", "json"],
                capture_output=True, text=True, timeout=120
            )
            return self._parse_output(result.stdout)
        except subprocess.TimeoutExpired:
            self._logger.error("ipa-healthcheck timed out after 120s")
            return None
        except Exception as e:
            self._logger.error(f"ipa-healthcheck execution failed: {e}")
            return None

    def _parse_output(self, output):
        try:
            checks = json.loads(output)
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse ipa-healthcheck JSON output: {e}")
            return None

        if not isinstance(checks, list):
            self._logger.error("Unexpected ipa-healthcheck output format")
            return None

        severity_map = {0: "SUCCESS", 1: "CRITICAL", 2: "ERROR", 3: "WARNING"}

        counts = {
            "total": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "critical": 0,
        }
        failures = []

        for check in checks:
            counts["total"] += 1
            severity = check.get("severity", 0)

            if severity == 0:
                counts["success"] += 1
            elif severity == 1:
                counts["critical"] += 1
                failures.append(self._format_failure(check, "CRITICAL"))
            elif severity == 2:
                counts["error"] += 1
                failures.append(self._format_failure(check, "ERROR"))
            elif severity == 3:
                counts["warning"] += 1
                failures.append(self._format_failure(check, "WARNING"))

        return {
            "counts": counts,
            "failures": failures,
        }

    def _format_failure(self, check, severity):
        source = check.get("source", "unknown")
        check_name = check.get("check", "unknown")
        kw = check.get("kw", {})
        msg = kw.get("msg", "No message provided")

        return {
            "severity": severity,
            "source": source,
            "check": check_name,
            "message": msg,
            "title": f"[{severity}] {source}.{check_name}",
            "description": msg,
        }
