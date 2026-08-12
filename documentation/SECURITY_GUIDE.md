# FreeIPA IdM Health Extension - Security Guide

This guide covers the identity, access control, and credential management required to run the Dynatrace FreeIPA IdM Health extension securely.

The extension supports two authentication modes that can be used independently:

| Mode | Runtime Credentials | Use When |
|---|---|---|
| **LDAP simple bind** | Bind DN + password | Kerberos infrastructure not available, or LDAP-only monitoring |
| **Kerberos keytab** | Keytab file + principal | Password-free runtime preferred, or IPA API features needed |

When Kerberos is enabled (`use_kerberos: true`), the extension uses SASL/GSSAPI for LDAP and Kerberos for the IPA API. **No password needs to be stored on the ActiveGate host.**

---

## 1. Monitoring Service Account

### Create the User

Create a dedicated IdM user for the extension. Do not reuse an existing user or admin account.

```bash
ipa user-add ldap-lookup \
  --first="LDAP" \
  --last="Lookup" \
  --shell=/sbin/nologin \
  --password
```

Set a strong, randomly generated password (minimum 20 characters, mixed case, digits, symbols). This password is used for the LDAP simple bind. If using Kerberos keytab authentication, the password is only needed during initial account creation and keytab retrieval -- it is not stored or used at runtime.

> **Do not** use a system account (`cn=sysaccounts,cn=etc`). The extension requires a regular IdM user so it can be assigned to IPA roles and use Kerberos authentication.

### Disable Interactive Login

The monitoring account should never be used for interactive login. Setting the shell to `/sbin/nologin` prevents SSH access. Additionally, consider setting the account to not require password expiry rotation:

```bash
ipa user-mod ldap-lookup --password-expiration=99990101000000Z
```

---

## 2. IPA Roles and Permissions (PBAC)

The extension requires read-only access to specific IdM data. All permissions are granted through IPA's Permission-Based Access Control (PBAC) model: **Permissions -> Privileges -> Roles -> Users**.

### Create the Privilege and Role

```bash
# Create privilege
ipa privilege-add "IdM Monitoring" \
  --desc="Read-only access for Dynatrace IdM health monitoring"

# Add permissions to the privilege
ipa privilege-add-permission "IdM Monitoring" \
  --permissions="Read Replication Agreements" \
  --permissions="System: Read DNS Entries"

# Create role
ipa role-add "IdM Monitor" \
  --desc="Role for Dynatrace IdM health monitoring extension"

# Attach privilege to role
ipa role-add-privilege "IdM Monitor" \
  --privileges="IdM Monitoring"

# Assign the monitoring user to the role
ipa role-add-member "IdM Monitor" \
  --users=ldap-lookup
```

### Permissions Granted

| Permission | Purpose | Scope |
|---|---|---|
| Read Replication Agreements | Read replication agreement status and lag | `cn=mapping tree,cn=config` |
| System: Read DNS Entries | Read DNS zones and records from LDAP | `cn=dns,{base_dn}` |

These are **IPA-managed permissions** and grant read-only access only.

### What Does NOT Require Explicit Permissions

| Data Source | Why No Permission Needed |
|---|---|
| `cn=monitor` (LDAP stats) | Readable by any authenticated LDAP user |
| `cn=snmp,cn=monitor` (SNMP counters) | Readable by any authenticated LDAP user |
| IPA API (`server_role_find`, `cert_find`) | Available to any Kerberos-authenticated IPA user |

---

## 3. Backend Cache ACI (Directory Manager)

The backend cache metrics live under `cn=ldbm database,cn=plugins,cn=config`, which is outside the IPA-managed permission scope. Access requires a direct LDAP ACI applied by the Directory Manager.

### Apply the ACI

```bash
ldapmodify -x -D "cn=Directory Manager" -W -H ldaps://idm1.example.com:636 <<EOF
dn: cn=ldbm database,cn=plugins,cn=config
changetype: modify
add: aci
aci: (targetattr = "*")(version 3.0; acl "IdM Monitoring read backend cache"; allow (read, search, compare) userdn = "ldap:///uid=ldap-lookup,cn=users,cn=accounts,dc=example,dc=com";)
EOF
```

> **Why `targetattr = "*"`?** Backend cache attributes (`entrycachehitratio`, `currententrycachecount`, etc.) are virtual/operational attributes not defined in the LDAP schema. Specifying them individually causes an `INVALID_SYNTAX` error. The wildcard is scoped to a single subtree and a single user, limiting exposure.

### Security Considerations for This ACI

- The ACI grants **read-only** access (read, search, compare) -- no write operations
- It is scoped to a **single user DN** -- only the monitoring account can use it
- It is applied to `cn=ldbm database,cn=plugins,cn=config` only -- it does not grant access to other `cn=config` subtrees
- This matches the pattern used by the built-in `pkidbuser` ACI in 389 Directory Server

---

## 4. Kerberos Keytab

The extension uses a Kerberos keytab for both **LDAP GSSAPI authentication** and **IPA API authentication**. When `use_kerberos` is enabled, the keytab replaces the LDAP bind password entirely -- no password needs to be stored on the ActiveGate host at runtime.

The keytab authenticates:
- **LDAP queries** via SASL/GSSAPI bind (monitor stats, replication, DNS, backend cache)
- **IPA API calls** via Kerberos/SPNEGO (service roles, certificates)

### Retrieve the Keytab

> **WARNING: Always use the `-r` flag with `ipa-getkeytab`.**
>
> Without `-r`, the command **resets the principal's keys**, immediately invalidating all previously issued keytabs for that user. This will break any running extension instances that hold the old keytab.
>
> The `-r` flag retrieves the existing keys without resetting them. It requires Directory Manager credentials because it reads keys directly from LDAP.

```bash
ipa-getkeytab -r \
  -s idm1.example.com \
  -p ldap-lookup@EXAMPLE.COM \
  -k /path/to/ldap-lookup.keytab \
  -D "cn=Directory Manager" -w <dm_password>
```

### Keytab File Permissions

```bash
chown root:dynatrace /path/to/ldap-lookup.keytab
chmod 640 /path/to/ldap-lookup.keytab
```

Replace `dynatrace` with the user/group under which the ActiveGate process runs.

**A keytab is equivalent to a password.** Anyone who can read the keytab file can authenticate as that principal. Protect it accordingly:

- Store it outside of web-accessible directories
- Do not commit it to version control
- Do not include it in the extension package
- Restrict file permissions to the ActiveGate service account only
- Rotate if the file is ever exposed (use `ipa-getkeytab` without `-r` to reset keys, then redistribute)

---

## 5. LDAP Bind Password

> **Note:** When Kerberos authentication is enabled (`use_kerberos: true`), the LDAP bind password is **not required**. The extension authenticates to LDAP using SASL/GSSAPI with the Kerberos keytab instead. Skip this section if using Kerberos.

The LDAP bind password is used for direct LDAP queries (monitor stats, replication, DNS, backend cache) when operating in simple bind mode.

### Storage in Dynatrace

In production, the password is stored in the Dynatrace credential vault and referenced by ID in the extension configuration. The activation schema should use a `"credential"` type field, and the password is resolved at runtime by the Extension Execution Controller (EEC).

### Development / Testing

During development, credentials can be stored in a local `secrets.json` file:

```json
{
  "ldap_password": "<password>",
  "dm_password": "<password>"
}
```

**This file must never be committed to version control.** Ensure it is listed in `.gitignore`:

```
secrets.json
*.keytab
```

### Password Requirements

- Minimum 20 characters, randomly generated
- Use a password manager or `openssl rand -base64 24` to generate
- Rotate on a schedule consistent with your organization's policy
- The monitoring account password should be distinct from all other service account passwords

---

## 6. Directory Manager Password

The Directory Manager password is only required during initial setup (applying the backend cache ACI and retrieving the keytab). It is **not** used at runtime by the extension.

- Do not store the DM password in the extension configuration
- Do not store it on the ActiveGate host
- Use it only interactively or via the Ansible playbook (`setup_idm_monitoring_role.yml`), which prompts for it at runtime
- If stored temporarily for automation, remove it immediately after use

---

## 7. CA Certificate

The extension validates the IdM server's TLS certificate using the IPA CA certificate.

### Deploy the CA Certificate

```bash
scp root@idm1.example.com:/etc/ipa/ca.crt /etc/ipa/ca.crt
```

Or fetch it via HTTP (the CA cert itself is public):

```bash
curl -o /etc/ipa/ca.crt https://idm1.example.com/ipa/config/ca.crt
```

### Verify the Certificate

```bash
openssl x509 -in /etc/ipa/ca.crt -noout -subject -issuer -dates
```

- Store the CA cert at a well-known path (e.g., `/etc/ipa/ca.crt`)
- Set permissions to `644` (the CA cert is public, but the file should be owned by root)
- The extension enforces TLS certificate validation (`OPT_X_TLS_DEMAND`) -- it will refuse to connect if the certificate cannot be verified

---

## 8. System Dependencies for Kerberos Mode

When using Kerberos authentication (`use_kerberos: true`), the following system packages must be installed on the ActiveGate host:

```bash
dnf install cyrus-sasl-gssapi krb5-workstation
```

| Package | Purpose |
|---|---|
| `cyrus-sasl-gssapi` | Provides the GSSAPI SASL mechanism for LDAP GSSAPI bind |
| `krb5-workstation` | Provides the `kinit` command for Kerberos ticket acquisition |

Without `cyrus-sasl-gssapi`, the LDAP GSSAPI bind will fail with `SASL(-4): no mechanism available`. Without `krb5-workstation`, the extension will fail with `kinit command not found`.

These packages are **not required** when using LDAP simple bind mode only.

---

## 9. Network Security

### Required Network Access

| From | To | Port | Protocol | Purpose |
|---|---|---|---|---|
| ActiveGate host | IdM server | 636 | LDAPS | LDAP queries (monitor, replication, DNS, certs, cache) |
| ActiveGate host | IdM server | 443 | HTTPS | IPA API (service roles, certificates) |
| ActiveGate host | IdM server | 88 | Kerberos (TCP/UDP) | Kerberos ticket acquisition |

### Recommendations

- Use LDAPS (port 636) exclusively -- the extension defaults to SSL on
- If LDAPS is not available, the extension will use STARTTLS on port 389, but dedicated LDAPS is preferred
- Kerberos port 88 is only required when `use_kerberos` is enabled
- HTTPS port 443 is only required when IPA API features are enabled (services, certificates)
- Restrict firewall rules to allow only the ActiveGate host to reach the IdM server on these ports
- Do not expose the IdM LDAP or API endpoints to untrusted networks

---

## 10. Automated Setup with Ansible

The included playbook `setup_idm_monitoring_role.yml` automates the permission configuration. It prompts for the IPA admin password and Directory Manager password at runtime -- neither is stored in the playbook or inventory.

```bash
ansible-playbook setup_idm_monitoring_role.yml
```

The playbook performs:
1. Creates the "IdM Monitoring" privilege
2. Attaches "Read Replication Agreements" and "System: Read DNS Entries" permissions
3. Creates the "IdM Monitor" role
4. Assigns the `ldap-lookup` user to the role
5. Applies the backend cache ACI via Directory Manager

---

## 11. Credential Summary

| Credential | Used At | Used For | Storage |
|---|---|---|---|
| LDAP bind password | Runtime (simple bind only) | LDAP queries to 389 DS. **Not needed when `use_kerberos` is true.** | Dynatrace credential vault (prod) / `secrets.json` (dev) |
| Kerberos keytab | Runtime (Kerberos mode) | LDAP GSSAPI bind and IPA API authentication | File on ActiveGate host, `chmod 640` |
| IPA admin password | Setup only | Creating roles/privileges/permissions | Interactive prompt, not stored |
| Directory Manager password | Setup only | Applying backend cache ACI, retrieving keytab | Interactive prompt, not stored |
| IPA CA certificate | Runtime | TLS verification for LDAPS and HTTPS | `/etc/ipa/ca.crt`, public file |

---

## 12. Principle of Least Privilege

The monitoring account has been designed with minimal access:

- **No write access** to any IdM data
- **No admin privileges** -- cannot create, modify, or delete users, hosts, or policies
- **No SSH login** -- shell set to `/sbin/nologin`
- **Scoped ACI** -- backend cache read access is limited to one subtree and one user
- **IPA PBAC** -- permissions are granted through the standard role/privilege model, auditable via `ipa role-show` and `ipa privilege-show`
- **Kerberos over password** -- When Kerberos is enabled, both LDAP and IPA API authenticate via keytab, eliminating the need to store or transmit passwords at runtime

To audit what the monitoring account can access:

```bash
# Show role membership
ipa role-show "IdM Monitor" --all

# Show privilege details
ipa privilege-show "IdM Monitoring" --all

# Show the backend cache ACI
ldapsearch -x -D "cn=Directory Manager" -W \
  -H ldaps://idm1.example.com:636 \
  -b "cn=ldbm database,cn=plugins,cn=config" \
  -s base aci
```
