# Remediation Report

## Objective

The vulnerable target application is retained strictly as a security-audit artifact. All corrective changes are implemented separately in `secure_version/secure_app.py`.

This separation provides a clear before-and-after comparison:

```text
target_app/vulnerable_app.py
          |
          | Security review
          v
    Security findings
          |
          | Remediation
          v
secure_version/secure_app.py
          |
          | Verification
          v
 Bandit re-scan + pytest
```

The remediation work addresses the weaknesses identified through Bandit static analysis and manual source inspection.

---

## Baseline Review Results

The verified Bandit 1.9.4 baseline scan of `target_app/` covered **187 lines of code** and reported **7 findings**:

| Bandit severity | Count |
|---|---:|
| High | 1 |
| Medium | 3 |
| Low | 3 |
| **Total** | **7** |

The baseline scan completed with:

```text
Errors: 0
Files skipped: 0
```

The seven Bandit findings were:

| Bandit ID | Issue | Severity |
|---|---|---|
| B403 | `pickle` module import advisory | Low |
| B404 | `subprocess` module import advisory | Low |
| B105 | Possible hard-coded password/secret | Low |
| B608 | Possible SQL injection vector in `create_user()` | Medium |
| B608 | Possible SQL injection vector in `find_user()` | Medium |
| B602 | `subprocess` call with `shell=True` | High |
| B301 | Unsafe `pickle.load()` deserialization | Medium |

Manual inspection additionally identified:

- weak unsalted SHA-256 password hashing
- path traversal risk
- plaintext password logging

The machine-readable baseline evidence is stored in:

```text
reports/bandit_report.json
```

---

## Remediation Matrix

| Finding | Security weakness | Secure change | Verification |
|---|---|---|---|
| SC-001 | Hard-coded secret | Environment-based secret loading | Secure-source review |
| SC-002 | Weak password hashing | Salted PBKDF2-HMAC with stored work factor | Password hashing tests |
| SC-003 | SQL injection in `create_user()` | Parameterized `INSERT` query | Database regression test |
| SC-004 | SQL injection in `find_user()` | Parameterized `SELECT` query | Database regression test |
| SC-005 | OS command injection | Explicit command allowlist + `shell=False` + timeout | Allowlist tests + Bandit re-scan |
| SC-006 | Path traversal | Resolved-path containment validation | Traversal rejection test |
| SC-007 | Unsafe deserialization | JSON instead of `pickle` | JSON round-trip test + Bandit re-scan |
| SC-008 | Plaintext password logging | Password removed from logs | Secure logging-path review |

---

## Detailed Remediation

### SC-001: Hard-Coded Application Secret

**Original weakness**

The vulnerable target stores an application secret directly in source code.

```python
APP_SECRET = "CodeAlpha-Demo-Secret-2026"
```

**Secure change**

The secure version removes the embedded secret and reads it from the environment:

```python
secret = os.getenv("CODEALPHA_APP_SECRET")
```

The application raises an error when the required environment variable is not configured.

**Security benefit**

The secret is separated from application source code and can be managed through deployment configuration or an appropriate secret-management system.

---

### SC-002: Weak Password Hashing

**Original weakness**

The target application uses a fast, unsalted SHA-256 hash:

```python
password_hash = hashlib.sha256(
    password.encode("utf-8")
).hexdigest()
```

**Secure change**

The secure implementation uses PBKDF2-HMAC-SHA256 with:

- a randomly generated 16-byte salt
- a stored iteration count
- constant-time verification with `hmac.compare_digest()`

**Security benefit**

A password-specific KDF with a unique salt is substantially better suited to password storage than a fast unsalted general-purpose hash.

---

### SC-003: SQL Injection in `create_user()`

**Original weakness**

The vulnerable implementation interpolates the username into the SQL statement.

```python
query = (
    "INSERT INTO users (username, password_hash) "
    f"VALUES ('{username}', '{password_hash}')"
)
```

**Secure change**

The secure version uses parameter binding:

```python
connection.execute(
    """
    INSERT INTO users (username, password_hash)
    VALUES (?, ?)
    """,
    (username, password_hash),
)
```

**Security benefit**

User-controlled data remains separate from the SQL command structure.

---

### SC-004: SQL Injection in `find_user()`

**Original weakness**

The vulnerable implementation interpolates the username directly into the query.

```python
query = (
    "SELECT id, username, password_hash "
    f"FROM users WHERE username = '{username}'"
)
```

**Secure change**

The secure version uses a parameterized query:

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

**Security benefit**

The SQL structure remains fixed while the username is supplied as data.

---

### SC-005: OS Command Injection

**Original weakness**

The target application accepts arbitrary command text and passes it to a shell:

```python
subprocess.run(
    command,
    shell=True,
    ...
)
```

**Secure change**

The secure implementation:

1. accepts only predefined command names
2. maps those names to fixed argument lists
3. executes with `shell=False`
4. applies a timeout

Example:

```python
ALLOWED_COMMANDS = {
    "whoami": ["whoami"],
    "ipconfig": ["ipconfig"],
}
```

**Security benefit**

Untrusted input is no longer interpreted by a shell, and only explicitly permitted operations can be executed.

**Verification**

The original High-severity `B602` finding is absent from the secure-version scan.

A Low-severity `B603` advisory remains because Bandit recommends review of subprocess execution even when `shell=False` is used.

---

### SC-006: Path Traversal

**Original weakness**

The target combines an untrusted filename with a base directory without validating the final resolved path.

**Secure change**

The secure implementation:

1. resolves the approved data directory
2. resolves the candidate path
3. checks that the candidate is inside the approved directory
4. rejects paths that escape the approved directory

Conceptually:

```text
requested filename
       |
       v
resolved candidate
       |
       v
inside approved directory?
       |              |
      Yes             No
       |              |
     allow           reject
```

**Security benefit**

Relative traversal components such as `..` cannot be used to escape the intended data directory.

---

### SC-007: Unsafe Deserialization

**Original weakness**

The vulnerable target loads serialized Python objects with:

```python
pickle.load(file)
```

**Secure change**

The secure implementation replaces pickle with JSON:

```python
json.loads(...)
```

and stores structured application data as JSON.

**Security benefit**

The secure implementation avoids the executable object-reconstruction behavior associated with loading untrusted pickle data.

**Verification**

The original `B301` unsafe-deserialization finding is absent from the secure-version scan, and the JSON round-trip tests pass.

---

### SC-008: Plaintext Password Logging

**Original weakness**

The vulnerable target writes the user's plaintext password to a log file:

```python
file.write(
    f"username={username}, password={password}
"
)
```

**Secure change**

The secure logger records the event without the password:

```python
file.write(
    f"successful login for username={username}
"
)
```

**Security benefit**

Authentication credentials are not exposed through application logs.

---

## Secure Coding Practices Applied

### Secrets Management

Application secrets are loaded from environment-based configuration rather than embedded in source code.

### Secure Password Storage

Passwords are protected with a salted, deliberately expensive password KDF instead of a fast unsalted general-purpose hash.

### Parameterized Database Access

SQL statements use parameter binding for user-controlled values.

### Safe Command Execution

Commands are selected from an explicit allowlist, represented as fixed argument arrays, executed with `shell=False`, and constrained by a timeout.

### Secure File Handling

File paths are resolved and checked against the approved directory before access.

### Safe Deserialization

JSON is used instead of executable Python serialization for structured application data.

### Sensitive Data Minimization

Passwords and authentication secrets are excluded from application logs.

---

## Verification

### Automated Security Regression Tests

Run:

```powershell
python -m pytest -q
```

Verified result:

```text
8 passed
```

The regression suite verifies:

- password hashing and verification
- random salting
- parameterized database operations
- JSON serialization and deserialization
- path traversal rejection
- command allowlisting
- allowlisted command execution
- valid JSON output

### Secure-Version Static Analysis

Run:

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

These do not reproduce the original High-severity `B602` `shell=True` pattern.

The secure implementation additionally uses an explicit command allowlist and a timeout. The Low advisories are retained and documented rather than suppressed.

---

## Remediation Outcome

The verified before-and-after results are:

| Measure | Vulnerable Target | Secure Version |
|---|---:|---:|
| Lines scanned | 187 | 257 |
| High Bandit findings | 1 | 0 |
| Medium Bandit findings | 3 | 0 |
| Low Bandit findings | 3 | 2 |
| Regression tests | N/A | 8 passed |

The original High- and Medium-severity Bandit findings are no longer present in the secure implementation.

The remaining two Low findings are documented subprocess advisories associated with the secure use of `subprocess` with `shell=False`.

---

## Reproducibility

From the project root, a reviewer can reproduce the review with:

```powershell
python -m pip install -r requirements.txt
python -m bandit -r target_app
python -m bandit -r target_app -f json -o reportsandit_report.json
python -m bandit -r secure_version
python -m pytest -q
```

Expected results:

```text
Baseline target:
187 lines scanned
High:   1
Medium: 3
Low:    3
Total:  7

Secure version:
257 lines scanned
High:   0
Medium: 0
Low:    2

Regression tests:
8 passed
```

---

## Conclusion

The remediation process demonstrates a complete secure-coding lifecycle:

```text
Identify
   |
   v
Assess
   |
   v
Document
   |
   v
Remediate
   |
   v
Re-scan
   |
   v
Retest
```

The intentionally vulnerable target remains available as a controlled educational audit artifact, while `secure_version/secure_app.py` demonstrates the corresponding defensive coding practices.

The final verified evidence shows **7 Bandit baseline findings**, **0 High and 0 Medium findings after remediation**, **2 documented Low subprocess advisories**, and **8 passing security regression tests**.
