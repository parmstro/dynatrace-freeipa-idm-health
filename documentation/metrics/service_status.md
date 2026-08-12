[< Back to Metrics Index](INDEX.md)

# service.status

| Field | Value |
|---|---|
| **Metric Key** | `custom.freeipa.idm.service.status` |
| **Data Type** | Gauge (integer) |
| **Dynatrace Unit** | Count |
| **Dimensions** | `service.name`, `freeipa.server`, `freeipa.domain` |

## Values

| Value | Meaning |
|---|---|
| `1` | Service is running |
| `0` | Service is stopped or unreachable |
| `-1` | Status unknown (role not enabled or no IPA API access) |

## Services Monitored

| service.name | systemd Unit (local) | Remote Probe Method |
|---|---|---|
| `dirsrv` | `dirsrv@{realm}` | TLS handshake on port 636 |
| `krb5kdc` | `krb5kdc` | TCP connect on port 88 |
| `kadmin` | `kadmin` | TCP connect on kpasswd port 464 |
| `httpd` | `httpd` | HTTPS GET `https://{host}/ipa/config/ca.crt` |
| `pki-tomcatd` | `pki-tomcatd@pki-tomcat` | HTTPS GET `https://{host}/ca/ocsp` (502/503 = down) |
| `named` | `named-pkcs11` | `dig @{host} {host} +short +time=3 +tries=1` |
| `certmonger` | `certmonger` | IPA API role check only (no network port) |

## FreeIPA Defaults

All seven services are installed and enabled by default on a FreeIPA server. On a healthy server, all services report `1`. The `pki-tomcatd` and `named` services may legitimately be absent if the server was installed without the CA or DNS roles.

## Collection Method

**Local mode:** Runs `systemctl is-active {unit}` for each service. Returns `1` if stdout is `active`, `0` otherwise.

**Remote mode:** Core services (`dirsrv`, `krb5kdc`, `kadmin`, `httpd`) are probed directly via protocol-level network checks. Role-dependent services (`pki-tomcatd`, `named`, `certmonger`) first query the IPA API to confirm the role is enabled on the target server:

```
IPA JSON-RPC: server_role_find
  options: { server_server: "{hostname}", sizelimit: 0 }
```

The API returns role names (`CA server`, `DNS server`) and their status (`enabled`/`absent`). If a role is `absent`, the service reports `-1` rather than `0`.

**Source file:** `freeipa_idm_health/service_checker.py`
**Authentication:** IPA API password or Kerberos keytab (remote); none (local)

---
[< Back to Metrics Index](INDEX.md)
