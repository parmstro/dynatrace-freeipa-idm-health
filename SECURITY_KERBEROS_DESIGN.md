# Kerberos Authentication Design — Security Addendum

This document records the design decision for how the extension handles Kerberos authentication when running on a Dynatrace ActiveGate, and the security trade-offs considered.

## Problem

The Dynatrace Extension Execution Controller (EEC) ships its own bundled Python runtime (currently 3.14). The standard Python libraries for Kerberos/GSSAPI authentication (`gssapi`, `krb5`) are C extensions that require compilation against system `libkrb5`/`libgssapi_krb5`. These packages do not publish pre-built binary wheels on PyPI, and the EEC build toolchain (`dt-sdk build`) enforces `--only-binary=:all:`, meaning only packages with pre-built wheels can be bundled into the extension package.

This creates a gap: the extension cannot include `gssapi` or `krb5` Python packages in its built artifact, which breaks two code paths:

1. **LDAP GSSAPI bind** — `ldap3` requires the `gssapi` Python package for SASL/GSSAPI authentication
2. **IPA API Kerberos auth** — `requests-kerberos` depends on `pyspnego`, which delegates to `gssapi` and `krb5` for the SPNEGO token exchange

## Options Evaluated

### Option 1: Build gssapi/krb5 wheels locally

Compile the `gssapi` and `krb5` Python packages against the EEC's Python 3.14 runtime and ship the resulting `.so` files inside the extension package.

**Security assessment:**

- The compiled C extensions are not from a trusted binary source (PyPI, OS vendor RPM). The extension maintainer becomes the packager, and every consumer must trust that build.
- On RHEL, the system Kerberos libraries (`krb5-libs`, `krb5-workstation`) are FIPS 140-2/140-3 validated. Self-compiled Python bindings wrapping those libraries fall outside the FIPS cryptographic boundary. For customers in regulated environments (FedRAMP, HIPAA, PCI-DSS), this creates a compliance gap.
- Maintenance burden: CVEs in `gssapi` or `krb5` require the extension maintainer to rebuild and redistribute. EEC Python version bumps require recompilation.
- The build machine becomes part of the supply chain trust boundary.

### Option 2: Subprocess-based Kerberos (selected)

Use the system-installed `kinit` (from `krb5-workstation` RPM) and `curl --negotiate` (from `curl` RPM with GSSAPI support) via `subprocess.run()` calls. No Python Kerberos C extensions are required.

**Security assessment:**

- Uses OS-vendor-managed, RPM-installed binaries. On RHEL, `kinit` and `curl` are patched by Red Hat via security errata and are within the FIPS-validated cryptographic boundary.
- Zero custom C code in the extension package. No compilation, no supply chain extension.
- Customers already trust these tools — they are part of the base RHEL installation.
- Process listing exposure: `kinit -kt /path/to/keytab principal@REALM` is briefly visible via `ps`. This reveals the keytab file path and principal name, but not key material. The window is sub-second.
- Credential cache: after `kinit`, the Kerberos ticket resides in a file-based credential cache (`/tmp/krb5cc_<uid>` or the path set by `KRB5CCNAME`). Any process running as the same OS user can read this cache. This exposure is identical in both options — Option 1 also calls `kinit` via subprocess.
- Command injection: mitigated by using list-form `subprocess.run(["kinit", "-kt", path, principal])` rather than shell strings. All arguments come from the Dynatrace configuration form (activationSchema.json), not from untrusted external input.

## Decision

**Option 2 (subprocess-based Kerberos) was selected.** The rationale:

1. **FIPS compliance**: system `kinit` and `curl` on RHEL are within the validated FIPS boundary. Self-compiled Python C extensions are not.
2. **Supply chain**: no custom-compiled binary artifacts to build, audit, maintain, or redistribute.
3. **Vendor trust**: Red Hat patches and certifies these tools. The extension maintainer does not need to take on C extension maintenance.
4. **Equivalent credential exposure**: both options call `kinit` via subprocess and use the same file-based credential cache. The process-listing exposure of the keytab path is brief and does not reveal key material.
5. **Customer acceptance**: Red Hat customers already trust and run these system binaries. No additional risk introduction.

## Implementation

### LDAP GSSAPI bind

1. Call `kinit -kt <keytab_path> <principal>` via `subprocess.run()` to populate the credential cache
2. Use `ldap3` SASL/GSSAPI bind — `ldap3` will use the credential cache via the system GSSAPI library

**Note:** `ldap3`'s GSSAPI bind still requires the `gssapi` Python package at import time. Since this package cannot be bundled, the LDAP path falls back to simple bind when Kerberos is configured. The credential cache populated by `kinit` is used by the IPA API path instead.

### IPA API Kerberos auth

1. Call `kinit -kt <keytab_path> <principal>` via `subprocess.run()` to populate the credential cache
2. Call `curl --negotiate -u : <url>` via `subprocess.run()` to perform SPNEGO authentication against the IPA API login endpoint
3. Extract the session cookie from the curl response
4. Use the session cookie with `requests.Session()` for subsequent IPA JSON-RPC calls

This eliminates the dependency on `requests-kerberos`, `pyspnego`, `gssapi`, and `krb5` Python packages entirely.

### LDAP authentication when Kerberos is enabled

Since `ldap3` SASL/GSSAPI requires the `gssapi` Python package (which cannot be bundled), LDAP queries use simple bind even when Kerberos mode is enabled. The monitoring account's password is still required for LDAP access. Kerberos authentication is used exclusively for the IPA API, which provides service role status and certificate data that LDAP simple bind cannot access.

A future alternative would be to use `ldapsearch` via subprocess for LDAP queries when Kerberos is enabled, but this adds significant complexity for minimal security benefit — the LDAP bind password and Kerberos keytab provide equivalent access to the same data.

## Mitigations

| Risk | Mitigation |
|---|---|
| Keytab path visible in `ps` output | Sub-second window; path only, not key material; ActiveGate host should have restricted user access |
| Credential cache readable by same-uid processes | Set `KRB5CCNAME` to a per-process path with restrictive permissions; ActiveGate runs as dedicated `dtuserag` user |
| `curl` output contains session cookie | Captured via `subprocess.run(capture_output=True)` — never written to disk or logged |
| Stale credential cache | Extension calls `kinit` before each authentication attempt; `kdestroy` on shutdown |

## Prerequisites

The following system packages must be installed on the ActiveGate host when Kerberos mode is enabled:

| Package | RPM | Purpose |
|---|---|---|
| `kinit` | `krb5-workstation` | Kerberos ticket acquisition from keytab |
| `curl` with GSSAPI | `curl` + `libcurl` (built with GSS-Negotiate) | SPNEGO authentication to IPA API |

Verify curl has GSSAPI support:

```bash
curl --version | grep -i gss
```

Expected output should include `GSS-Negotiate` or `SPNEGO` in the features list.
