# Service Health Monitoring Design

This document records how the extension determines whether each FreeIPA service is running when monitored remotely from a Dynatrace ActiveGate.

## Problem

The extension runs on a remote ActiveGate, not on the IdM server itself. Unlike `ipactl status`, which calls `systemctl is-active` locally, the extension cannot query systemd directly.

The initial implementation used the IPA API `server_role_find` RPC call, which returns whether a service role is **configured** ("enabled" / "absent"), not whether the underlying process is **currently running**. This produced two failure modes:

1. **False positives** — a service could be stopped (`systemctl stop named`) but the role would still report "enabled", so the dashboard showed UP.
2. **Blind spots** — if `httpd` was stopped, the IPA API itself became unreachable, so no service health was reported at all. The dashboard went silent rather than showing DOWN.

## Design: Protocol-Level Probes

Each service is checked using the most meaningful probe that is remotely accessible. The probe strategy is selected per-service based on which ports are reachable from outside the IdM server and what protocol proves the service is genuinely functional.

### Probe Matrix

| Service | Probe Method | Port | Rationale |
|---|---|---|---|
| **dirsrv** | TLS handshake | 636 | LDAPS port is open to ActiveGate by design. A successful TLS handshake proves 389 DS is accepting encrypted connections, not just that a port is open. |
| **krb5kdc** | TCP connect | 88 | KDC port must be open for domain operations. No standard unauthenticated Kerberos probe exists, so TCP connect is the best available check. |
| **kadmin** | TCP connect | 464 | kadmind serves kpasswd on port 464, which must be open for IdM to function (users need it for password changes). Port 749 (kadmin admin) is typically firewalled from non-IdM hosts. If kadmind is stopped, both ports go down. |
| **httpd** | HTTPS GET `/ipa/config/ca.crt` | 443 | A public, unauthenticated endpoint. Any HTTP response (including 4xx/5xx) proves Apache is serving. Connection refused or timeout means httpd is down. |
| **pki-tomcatd** | HTTPS GET `/ca/ocsp` | 443 (via httpd) | Dogtag PKI binds to localhost:8443 — not reachable remotely. httpd proxies `/ca/` to pki-tomcatd, so an HTTP response to `/ca/ocsp` proves the PKI backend is alive. |
| **named** | DNS query via `dig @hostname` | 53 | A real DNS resolution proves named is functional, not just listening. Falls back to TCP port 53 check if `dig` is not installed on the ActiveGate. |
| **certmonger** | Role check only | — | certmonger is a local daemon with no network port. If the CA server role is "enabled", certmonger is assumed running. This is the one service that cannot be verified remotely. |

### Why Not Just Port Checks?

Plain TCP port probes (connect to port, close) tell you something is listening but not whether the service is healthy. Protocol-level probes verify actual functionality:

- A TLS handshake proves the server can negotiate encryption and present a certificate
- An HTTPS GET proves the web stack is serving content, not just accepting connections
- A DNS query proves name resolution works end-to-end

### Port Accessibility Constraints

Not all service ports are reachable from a remote ActiveGate:

| Port | Service | Remotely Accessible | Notes |
|---|---|---|---|
| 88 | krb5kdc | Yes | Required for Kerberos authentication |
| 443 | httpd | Yes | Required for IPA web UI and API |
| 464 | kadmin (kpasswd) | Yes | Required for password changes — IdM cannot function without it |
| 636 | dirsrv (LDAPS) | Yes | Required for LDAP queries |
| 53 | named | Yes | Required for DNS resolution |
| 749 | kadmin (admin) | No | Typically firewalled; only IdM replicas need access |
| 8443 | pki-tomcatd | No | Bound to localhost; httpd proxies to it |
| — | certmonger | No | Local daemon, no network port |

These constraints drove the probe strategy. Services with inaccessible ports use indirect verification through ports that are guaranteed to be open.

### Fallback Behavior

When a protocol-level probe cannot be performed (e.g., `dig` not installed for DNS), the check falls back to a TCP port probe. If the IPA API is unreachable (httpd is down), core services are still probed directly via their ports — the extension does not depend on the IPA API being available to report service health.

Role-based services (pki-tomcatd, certmonger, named) require role information from `server_role_find` to determine whether they should exist on the server. If the API is unreachable and roles cannot be fetched, these services are skipped (not reported) rather than reported as DOWN — avoiding false negatives for services that may not be configured.

### Local Mode

When the extension runs directly on the IdM server (`is_local=True`), all services are checked via `systemctl is-active` against their systemd unit names. This is the most authoritative check and matches `ipactl status` behavior. The probe strategy described above applies only to remote ActiveGate deployments.

## Validation

Each probe was tested by stopping the corresponding service on the IdM server and verifying the dashboard reflected the change:

| Test | Expected | Result |
|---|---|---|
| `systemctl stop named-pkcs11` | named shows DOWN | Confirmed |
| `systemctl start named-pkcs11` | named shows UP | Confirmed |
| `systemctl stop httpd` | httpd shows DOWN | Confirmed |
| `systemctl start httpd` | httpd shows UP | Confirmed |
| `systemctl stop kadmin` | kadmin shows DOWN | Confirmed |
| `systemctl start kadmin` | kadmin shows UP | Confirmed |
| `systemctl stop krb5kdc` (kadmin still running) | Only krb5kdc shows DOWN | Confirmed |
| `systemctl stop dirsrv@REALM` | dirsrv shows DOWN | Confirmed |
| `systemctl start dirsrv@REALM` | dirsrv shows UP | Confirmed |
| `systemctl stop pki-tomcatd@pki-tomcat` | pki-tomcatd shows DOWN | Confirmed (via 502 from httpd proxy) |
| `systemctl start pki-tomcatd@pki-tomcat` | pki-tomcatd shows UP | Confirmed |
| Stop krb5kdc + kadmin | Both show DOWN | Confirmed |
