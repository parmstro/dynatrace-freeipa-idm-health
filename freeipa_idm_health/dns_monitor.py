from . import constants as C


class DnsMonitor:

    def __init__(self, ldap_collector, hostname, domain, logger):
        self._ldap = ldap_collector
        self._hostname = hostname
        self._domain = domain
        self._logger = logger

    def collect_all(self):
        zones = self._ldap.collect_dns_zones()
        zone_count = len(zones)

        zone_records = []
        for zone in zones:
            record_count = self._ldap.count_dns_records(zone["dn"])
            zone_records.append({
                "zone_name": zone["name"],
                "record_count": record_count,
            })

        srv_results = self._check_srv_records(zones)

        return {
            "zone_count": zone_count,
            "zones": zone_records,
            "srv_records": srv_results,
        }

    def _check_srv_records(self, zones):
        domain_zone = None
        for zone in zones:
            if zone["name"].rstrip(".") == self._domain.rstrip("."):
                domain_zone = zone
                break

        if not domain_zone:
            self._logger.debug(f"Domain zone {self._domain} not found in DNS zones")
            return []

        results = []
        for srv_name in C.SRV_RECORDS:
            valid = self._ldap.check_srv_record(domain_zone["dn"], srv_name)
            results.append({
                "srv_type": srv_name,
                "valid": 1 if valid else 0,
            })
            if not valid:
                self._logger.warning(f"SRV record {srv_name}.{self._domain} is missing or invalid")

        return results
