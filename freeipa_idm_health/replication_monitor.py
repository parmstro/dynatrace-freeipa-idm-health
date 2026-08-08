from . import constants as C


class ReplicationMonitor:

    def __init__(self, ldap_collector, hostname, domain, logger):
        self._ldap = ldap_collector
        self._hostname = hostname
        self._domain = domain
        self._logger = logger

    def collect_all(self):
        agreements = self._ldap.collect_replication_agreements()
        conflict_count = self._ldap.count_replication_conflicts()

        results = []
        for agr in agreements:
            results.append({
                "agreement_name": agr["cn"],
                "replica_host": agr["replica_host"],
                "suffix": agr["suffix"],
                "metrics": {
                    C.REPL_STATUS: agr["status_code"],
                    C.REPL_LAG_SECONDS: agr["lag_seconds"],
                    C.REPL_UPDATE_IN_PROGRESS: agr["update_in_progress"],
                    C.REPL_CHANGES_SENT: agr["changes_sent"],
                },
            })

            if agr["status_code"] != 0:
                self._logger.warning(
                    f"Replication agreement {agr['cn']} to {agr['replica_host']} "
                    f"has non-zero status: {agr['status_text']}"
                )

        return {
            "agreements": results,
            "conflict_count": conflict_count,
        }
