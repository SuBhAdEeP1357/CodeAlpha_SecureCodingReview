# Security Findings

## Executive Summary

A controlled Python application was reviewed using manual source inspection and Bandit static analysis.

The final Bandit 1.9.4 baseline scan covered **187 lines of code** and produced **7 security-related findings**:

| Bandit severity | Count |
|---|---:|
| High | 1 |
| Medium | 3 |
| Low | 3 |
| **Total** | **7** |

The baseline scan completed with no scanner errors and no skipped files.

Two Bandit results, **B403** and **B404**, are module-level advisories. They are retained as supporting static-analysis evidence rather than treated as standalone exploitable vulnerabilities. The actionable issues are the unsafe `pickle.load()` operation and the `subprocess` call using `shell=True`.

Manual review additionally identified security weaknesses that static analysis does not fully establish by itself, including weak password hashing, path traversal, and plaintext credential logging.

The secure reference implementation is maintained separately in `secure_version/secure_app.py`. It addresses the identified weaknesses without altering the intentionally vulnerable audit target.

---

## Finding Register

The combined static-analysis and manual review produced the following **8 actionable security findings**:

| ID | Finding | Evidence | Bandit Severity | Review Risk |
|---|---|---|---|---|
| SC-001 | Hard-coded application secret | B105 | Low | Medium |
| SC-002 | Weak password hashing | Manual review | Not reported by Bandit | High |
| SC-003 | SQL injection in `create_user()` | B608 | Medium | High |
| SC-004 | SQL injection in `find_user()` | B608 | Medium | High |
| SC-005 | OS command injection | B602 | High | High |
| SC-006 | Path traversal | Manual review | Not reported by Bandit | Medium |
| SC-007 | Unsafe deserialization with `pickle` | B301 + B403 | Medium + Low advisory | High |
| SC-008 | Plaintext password logging | Manual review | Not reported by Bandit | High |

### Baseline Static-Analysis Evidence

The Bandit 1.9.4 baseline reported:

- **B403**: importing `pickle` - Low severity, High confidence
- **B404**: importing `subprocess` - Low severity, High confidence
- **B105**: possible hard-coded password/secret string - Low severity, Medium confidence
- **B608**: possible SQL injection vector in `create_user()` - Medium severity, Low confidence
- **B608**: possible SQL injection vector in `find_user()` - Medium severity, Low confidence
- **B602**: `subprocess` call with `shell=True` - High severity, High confidence
- **B301**: unsafe `pickle.load()` deserialization - Medium severity, High confidence

The exact machine-readable baseline is stored in:

```text
reports/bandit_report.json
```

---

## SC-001: Hard-Coded Application Secret

**Location:** `target_app/vulnerable_app.py` - `APP_SECRET` definition  
**Bandit:** B105  
**CWE:** CWE-259  
**Bandit severity:** Low  
**Bandit confidence:** Medium  
**Review risk:** Medium

### Description

The target application stores an application secret directly in its source code.

Hard-coded secrets may be exposed through source-control history, backups, copied source distributions, or unauthorized access to the repository.

### Evidence

```python
APP_SECRET = "CodeAlpha-Demo-Secret-2026"
```

### Impact

Anyone who obtains the source code can recover the embedded secret. In a real application, exposing an application secret could weaken authentication, signing, encryption, or other security controls depending on how the value is used.

### Recommendation

Do not store secrets directly in application source code. Load them from environment variables or a dedicated secret-management system with appropriate access controls.

### Remediation

The secure implementation retrieves the application secret from the `CODEALPHA_APP_SECRET` environment variable instead of embedding the secret in source code.

---

## SC-002: Weak Password Hashing

**Location:** `target_app/vulnerable_app.py` - `create_user()`  
**CWE:** CWE-916 / CWE-327  
**Evidence source:** Manual security review  
**Review risk:** High

### Description

The target application hashes passwords with fast, unsalted SHA-256.

```python
password_hash = hashlib.sha256(
    password.encode("utf-8")
).hexdigest()
```

A general-purpose fast hash is not designed for password storage. The lack of a unique salt also means identical passwords can produce identical stored hashes.

### Impact

If password hashes are disclosed, offline password guessing is easier than it would be with a dedicated password KDF using a unique salt and suitable work factor.

### Recommendation

Use a password-specific key-derivation function such as Argon2id, scrypt, or PBKDF2 with a unique per-password salt and an appropriate work factor.

### Remediation

The secure implementation uses PBKDF2-HMAC-SHA256 with:

- a randomly generated 16-byte salt
- a stored iteration count
- constant-time verification using `hmac.compare_digest()`

---

## SC-003: SQL Injection in `create_user()`

**Location:** `target_app/vulnerable_app.py` - `create_user()`  
**Bandit:** B608  
**CWE:** CWE-89  
**Bandit severity:** Medium  
**Bandit confidence:** Low  
**Review risk:** High

### Description

The username is interpolated directly into an SQL statement using an f-string.

### Evidence

```python
query = (
    "INSERT INTO users (username, password_hash) "
    f"VALUES ('{username}', '{password_hash}')"
)
```

User-controlled data therefore becomes part of the SQL command itself.

### Impact

A maliciously crafted username may alter the intended SQL statement. In a larger application, this could lead to unauthorized data access, modification, or other database compromise.

### Recommendation

Use parameterized queries or prepared statements. Keep SQL structure separate from untrusted input.

### Remediation

The secure implementation uses SQLite parameter binding:

```python
connection.execute(
    """
    INSERT INTO users (username, password_hash)
    VALUES (?, ?)
    """,
    (username, password_hash),
)
```

---

## SC-004: SQL Injection in `find_user()`

**Location:** `target_app/vulnerable_app.py` - `find_user()`  
**Bandit:** B608  
**CWE:** CWE-89  
**Bandit severity:** Medium  
**Bandit confidence:** Low  
**Review risk:** High

### Description

The username supplied to `find_user()` is directly interpolated into the SQL query.

### Evidence

```python
query = (
    "SELECT id, username, password_hash "
    f"FROM users WHERE username = '{username}'"
)
```

### Impact

A specially crafted username may change the semantics of the SQL expression.

### Recommendation

Use parameterized SQL and never concatenate untrusted input into SQL statements.

### Remediation

The secure implementation uses:

```python
connection.execute(
    """
    SELECT id, username, password_hash
    FROM users
    WHERE username = ?
    """,
    (username,),
)
```

---

## SC-005: OS Command Injection

**Location:** `target_app/vulnerable_app.py` - `run_system_command()`  
**Bandit:** B602  
**CWE:** CWE-78  
**Bandit severity:** High  
**Bandit confidence:** High  
**Review risk:** High

### Description

The target application passes a command string to `subprocess.run()` with `shell=True`.

### Evidence

```python
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    check=False,
)
```

Using a shell to interpret untrusted command text can allow shell metacharacters and unintended operating-system commands to be executed.

### Impact

If an attacker can influence the command value, the application may execute arbitrary operating-system commands with the privileges of the application process.

### Recommendation

Avoid shell interpretation. Prefer a fixed allowlist of permitted operations and execute a list of fixed arguments with `shell=False`.

### Remediation

The secure implementation:

- accepts only predefined command names
- maps those names to fixed argument lists
- uses `shell=False`
- applies a timeout

This removes the original untrusted shell-command execution pattern.

---

## SC-006: Path Traversal

**Location:** `target_app/vulnerable_app.py` - `read_user_file()`  
**CWE:** CWE-22  
**Evidence source:** Manual security review  
**Review risk:** Medium

### Description

The target application combines a base directory with an attacker-influenced filename without validating the final resolved path.

### Evidence

```python
base_directory = Path("data")
file_path = base_directory / filename
```

Joining a base directory with an untrusted path does not by itself prevent traversal using components such as `..`.

### Impact

A caller could attempt to access files outside the intended application data directory.

### Recommendation

Resolve the candidate path and verify that it remains inside the approved directory before opening it.

### Remediation

The secure implementation resolves the candidate path and rejects any path that falls outside `DATA_DIRECTORY`.

---

## SC-007: Unsafe Deserialization with `pickle`

**Location:** `target_app/vulnerable_app.py` - `load_saved_object()`  
**Bandit:** B301, with B403 as supporting import advisory  
**CWE:** CWE-502  
**Bandit severity:** Medium for B301  
**Bandit confidence:** High  
**Review risk:** High

### Description

The target application deserializes data with `pickle.load()`.

### Evidence

```python
with open(filename, "rb") as file:
    return pickle.load(file)
```

Python pickle deserialization can invoke code during object reconstruction. Loading untrusted pickle content can therefore result in arbitrary code execution.

### Impact

An attacker who can cause a malicious pickle file to be loaded could execute code in the security context of the application.

### Recommendation

Do not deserialize untrusted data with `pickle`. Prefer a non-executable format such as JSON and validate the expected schema and data types.

### Remediation

The secure implementation replaces pickle-based loading with JSON serialization and loading.

### Supporting Bandit Advisory: B403

Bandit also reported B403 for importing the `pickle` module. This is supporting evidence rather than a separate vulnerability because the actionable security risk is the `pickle.load()` operation documented above.

---

## SC-008: Plaintext Password Logging

**Location:** `target_app/vulnerable_app.py` - `log_login()`  
**CWE:** CWE-532 / CWE-312  
**Evidence source:** Manual security review  
**Review risk:** High

### Description

The target application writes the user's plaintext password directly to a log file.

### Evidence

```python
file.write(
    f"username={username}, password={password}\n"
)
```

### Impact

Log files are commonly retained, copied, archived, forwarded, or made accessible to operators and monitoring systems. A log disclosure could therefore expose usable credentials.

### Recommendation

Never log passwords, authentication tokens, session secrets, or other sensitive authentication material. Log only the minimum operational information required.

### Remediation

The secure implementation records the username and authentication event without storing the password.

---

## Module-Level Bandit Advisories

### B403 - `pickle` Import

Bandit reports the import of `pickle` as a low-severity advisory because the module provides unsafe deserialization capabilities.

The actionable weakness is the `pickle.load()` operation documented as **SC-007**.

### B404 - `subprocess` Import

Bandit reports the import of `subprocess` as a low-severity advisory.

Use of `subprocess` is not inherently a vulnerability. The actionable weakness in the target application is the `shell=True` execution pattern documented as **SC-005**.

---

## Risk Interpretation

Bandit severity and the project's review risk are different classifications.

- **Bandit severity** reflects the static analyzer's classification of a specific code pattern.
- **Review risk** considers application context, practical exploitability, and potential security impact.

For example, Bandit rates the hard-coded secret as Low, while this review assigns Medium risk because exposure of a real application secret could compromise dependent security controls.

Similarly, the manually identified plaintext password logging issue is assessed as High risk because disclosure of authentication credentials can directly affect account security.

---

## Remediation Summary

| Finding | Remediation | Verification |
|---|---|---|
| SC-001 | Environment-based secret loading | Secure source inspection |
| SC-002 | Salted PBKDF2-HMAC password hashing | Password hashing/verification tests |
| SC-003 | Parameterized SQL in `create_user()` | Database regression test |
| SC-004 | Parameterized SQL in `find_user()` | Database regression test |
| SC-005 | Command allowlist, `shell=False`, and timeout | Allowlist tests + Bandit re-scan |
| SC-006 | Resolved-path containment validation | Traversal rejection test |
| SC-007 | JSON instead of `pickle` | JSON round-trip tests + Bandit re-scan |
| SC-008 | Remove passwords from logs | Secure logging-path review |

---

## Verification Status

The secure reference implementation was verified with:

```powershell
python -m bandit -r secure_version
```

Verified result:

```text
Lines of code scanned: 257

High:   0
Medium: 0
Low:    2
Files skipped: 0
```

The remaining Low findings are:

```text
B404  subprocess import advisory
B603  subprocess usage with shell=False
```

They do not reproduce the original High-severity `B602` finding caused by `shell=True`.

The security regression suite was verified with:

```powershell
python -m pytest -q
```

Verified result:

```text
8 passed
```

These results demonstrate the review-and-remediation cycle:

```text
Vulnerable Code
      ↓
Static Analysis + Manual Review
      ↓
Security Findings
      ↓
Secure Remediation
      ↓
Bandit Re-scan
      ↓
Regression Testing
```

---

## Conclusion

The review identified **8 actionable security findings** in the intentionally vulnerable target and documented a corresponding remediation for each issue.

The latest verified evidence shows:

```text
Baseline target:
187 lines scanned
7 Bandit findings
High:   1
Medium: 3
Low:    3

Secure version:
257 lines scanned
High:   0
Medium: 0
Low:    2

Regression tests:
8 passed
```

The vulnerable target remains preserved as a controlled educational audit artifact, while the secure reference implementation demonstrates the corresponding defensive coding practices.
