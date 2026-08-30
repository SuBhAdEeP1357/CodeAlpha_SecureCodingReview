# CodeAlpha Secure Coding Review

<p align="center">
  <img src="screenshots/00_project_banner.png" alt="CodeAlpha Secure Coding Review - Task 3" width="100%">
</p>

<p align="center">
  <strong>CodeAlpha Cyber Security Internship · Task 3</strong><br>
  Secure coding review, vulnerability identification, remediation, static analysis, and regression testing.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/Bandit-1.9.4-111827?style=for-the-badge" alt="Bandit 1.9.4">
  <img src="https://img.shields.io/badge/Tests-8%20passed-16a34a?style=for-the-badge" alt="8 tests passed">
  <img src="https://img.shields.io/badge/Secure%20re--scan-High%200-16a34a?style=for-the-badge" alt="No high severity secure-version findings">
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#security-review-workflow">Workflow</a> •
  <a href="#key-findings">Findings</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#secure-version">Remediation</a> •
  <a href="#evidence">Evidence</a> •
  <a href="#security--privacy">Security & Privacy</a>
</p>

> **Authorized-use notice:** The vulnerable application in this repository is intentionally insecure and must remain in a controlled local environment. Do not expose it to untrusted users or deploy it as a production application.

---

## Overview

The **CodeAlpha Secure Coding Review** project demonstrates a practical secure-coding workflow using a deliberately vulnerable Python application and a separately implemented secure reference version.

The review combines:

- manual source inspection
- **Bandit 1.9.4** static security analysis
- security finding classification
- risk assessment
- secure remediation
- regression/security testing
- reproducible evidence and documentation

The project preserves the vulnerable application as an **audit artifact** so the
before-and-after security differences remain visible and reviewable.

---

## Security Review Workflow

```text
┌───────────────────────────────────┐
│ Controlled Vulnerable Application │
│ target_app/vulnerable_app.py      │
└──────────────────┬────────────────┘
                   │
                   ▼
        Manual Source Inspection
                   +
          Bandit Static Analysis
                   │
                   ▼
          Security Findings
                   │
                   ▼
             Risk Assessment
                   │
                   ▼
           Secure Remediation
                   │
                   ▼
┌───────────────────────────────────┐
│ Secure Reference Implementation   │
│ secure_version/secure_app.py      │
└──────────────────┬────────────────┘
                   │
                   ▼
       Automated Regression Tests
```

### Operational Workflow

```text
1. Review controlled vulnerable source
             ↓
2. Run Bandit baseline
             ↓
3. Classify and document findings
             ↓
4. Implement secure coding controls
             ↓
5. Re-scan the secure reference
             ↓
6. Run regression/security tests
             ↓
7. Preserve reports and screenshots
```

---

## Objectives

The project was designed to demonstrate that a secure-coding review can:

1. Identify weaknesses in intentionally vulnerable application code.
2. Combine automated static analysis with manual inspection.
3. Document security impact and review risk.
4. Map weaknesses to concrete remediation controls.
5. Implement a separate secure reference version.
6. Re-run static analysis after remediation.
7. Verify the secure implementation with automated tests.
8. Preserve clear evidence of the before-and-after security state.

---

## Key Findings

The review identified **eight actionable security findings** through a combination
of Bandit evidence and manual source inspection.

| ID | Finding | Evidence | Review Risk |
|---|---|---|---|
| SC-001 | Hard-coded application secret | Bandit B105 | Medium |
| SC-002 | Weak password hashing | Manual review | High |
| SC-003 | SQL injection in `create_user()` | Bandit B608 | High |
| SC-004 | SQL injection in `find_user()` | Bandit B608 | High |
| SC-005 | OS command injection | Bandit B602 | High |
| SC-006 | Path traversal | Manual review | Medium |
| SC-007 | Unsafe deserialization with `pickle` | Bandit B301/B403 | High |
| SC-008 | Plaintext password logging | Manual review | High |

Bandit also reports module-level advisories for:

```text
B403 → pickle import
B404 → subprocess import
```

These advisories support the relevant actionable findings and are not counted as
additional standalone vulnerabilities in the eight-finding review register.

Detailed analysis is available in
[`reports/FINDINGS.md`](reports/FINDINGS.md).

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3 |
| Static Security Analysis | Bandit 1.9.4 |
| Automated Testing | pytest 9.1.1 |
| Database | SQLite |
| Secure Password KDF | PBKDF2-HMAC-SHA256 |
| Serialization | JSON |
| Version Control | Git / GitHub |
| Documentation | Markdown |

### Verified Environment

```text
Python:   3.13.15
Bandit:   1.9.4
pytest:   9.1.1
```

---

## Project Structure

```text
CodeAlpha_SecureCodingReview/
│
├── reports/
│   ├── bandit_report.json
│   ├── FINDINGS.md
│   ├── REMEDIATION.md
│   └── SECURITY_REVIEW.md
│
├── screenshots/
│   ├── 00_project_banner.png
│   ├── 01_project_structure.png
│   ├── 02_bandit_baseline.png
│   ├── 03_security_findings.png
│   ├── 04_secure_remediation.png
│   ├── 05_tests_passed.png
│   └── README.md
│
├── secure_version/
│   ├── __init__.py
│   └── secure_app.py
│
├── target_app/
│   ├── __init__.py
│   └── vulnerable_app.py
│
├── tests/
│   └── test_security.py
│
├── tools/
│   └── run_review.py
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### Directory Responsibilities

| Directory | Responsibility |
|---|---|
| `target_app/` | Deliberately vulnerable audit target |
| `secure_version/` | Remediated reference implementation |
| `tests/` | Automated security/regression tests |
| `tools/` | Review and Bandit helper |
| `reports/` | Findings, remediation, review, and machine-readable analysis |
| `screenshots/` | Visual evidence from the review workflow |

---

## Requirements

Install:

- Python 3.10+
- pytest 9.1.1
- Bandit 1.9.4

The recorded verification environment used **Python 3.13.15**.

---

## Quick Start

### 1. Open the project

```powershell
cd CodeAlpha_SecureCodingReview
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Verify pytest

```powershell
python -m pytest --version
```

### 4. Verify Bandit

```powershell
python -m bandit --version
```

---

## Running the Vulnerable Target

The vulnerable application exists only for **controlled security-review practice**.

Run locally:

```powershell
python target_app\vulnerable_app.py
```

Do not:

- deploy it as a production application
- expose it to the network
- provide it with untrusted users or data
- use it against systems you do not own or have authorization to assess

The vulnerable source is intentionally retained so the security weaknesses can
be reviewed and compared with the remediation.

---

## Running the Bandit Baseline

### Console Scan

```powershell
python -m bandit -r target_app
```

### Machine-Readable Report

```powershell
python -m bandit -r target_app -f json -o reports\bandit_report.json
```

### Project Helper

```powershell
python tools\run_review.py
```

### Recorded Baseline

The recorded Bandit baseline scanned **187 lines of code** and reported:

```text
High:    1
Medium:  3
Low:     3
Total:   7
```

The baseline is intentionally non-clean because `target_app/` is deliberately
vulnerable.

---

## Secure Version

The secure reference implementation is:

```text
secure_version/secure_app.py
```

It demonstrates the corresponding defensive controls.

### 1. Secret Management

The application secret is loaded from:

```text
CODEALPHA_APP_SECRET
```

rather than being hard-coded in the source.

### 2. Password Protection

Passwords are protected with:

```text
PBKDF2-HMAC-SHA256
```

using a random salt and a configured work factor.

### 3. Parameterized SQL

User-controlled values are passed to SQLite through parameterized placeholders
instead of SQL string interpolation.

### 4. Safe Command Execution

Command execution is restricted to an explicit allowlist and uses:

```text
shell=False
```

with a timeout.

### 5. Path Traversal Protection

User-supplied filenames are resolved and checked so the final path remains
inside the approved data directory.

### 6. Safe Serialization

The vulnerable `pickle` path is replaced with JSON serialization/deserialization.

### 7. Secure Logging

Passwords and authentication secrets are not written to application logs.

---

## Secure-Version Bandit Verification

Run:

```powershell
python -m bandit -r secure_version
```

Recorded result:

```text
Total lines of code: 257

Undefined: 0
Low:       2
Medium:    0
High:      0
```

The remaining low-severity findings are:

```text
B404 → subprocess module-level advisory
B603 → subprocess call without shell interpretation
```

These do **not** indicate that the original `shell=True` command-injection
vulnerability remains.

The secure implementation uses:

```text
explicit command allowlist
shell=False
timeout
```

---

## Regression Testing

Run:

```powershell
python -m pytest -q
```

### Verified Result

```text
8 passed
```

The regression/security suite verifies:

| Test Area | Verification |
|---|---|
| Password hashing | Salted PBKDF2 behavior |
| Password verification | Correct and incorrect credential handling |
| Salt uniqueness | Different salts for repeated hashing |
| Database access | Parameterized SQL operations |
| Serialization | JSON serialization/deserialization |
| Path security | Traversal rejection |
| Command execution | Allowlisting |
| Approved command | Expected command execution |
| JSON export | Valid JSON output |

A successful test run confirms that the secure reference implementation satisfies
the project's regression checks.

---

## Before-and-After Security State

```text
Vulnerable Target
      │
      ├── Hard-coded secret
      ├── Weak password hashing
      ├── SQL injection
      ├── Command injection
      ├── Path traversal
      ├── Unsafe pickle deserialization
      └── Plaintext password logging
      │
      ▼
Security Review + Bandit
      │
      ▼
Remediation
      │
      ▼
Secure Reference
      │
      ├── Environment-based secret
      ├── PBKDF2-HMAC-SHA256
      ├── Parameterized SQL
      ├── Allowlisted shell=False execution
      ├── Path containment checks
      ├── JSON serialization
      └── Secret-free logging
      │
      ▼
Bandit Re-scan + pytest
```

---

## Evidence

The repository contains five visual evidence screenshots documenting the major
stages of the security review.

### 01 · Project Structure

![Project Structure](screenshots/01_project_structure.png)

Shows the organized repository structure, including the vulnerable target, secure
version, tests, reports, tools, and evidence directories.

### 02 · Bandit Baseline

![Bandit Baseline](screenshots/02_bandit_baseline.png)

Shows the Bandit baseline scan against the intentionally vulnerable target.

Recorded baseline:

```text
High:    1
Medium:  3
Low:     3
Total:   7
```

### 03 · Security Findings

![Security Findings](screenshots/03_security_findings.png)

Shows the documented security finding register containing the eight actionable
review findings.

### 04 · Secure Remediation

![Secure Remediation](screenshots/04_secure_remediation.png)

Shows the secure reference implementation and key defensive controls including
environment-based secrets, PBKDF2 password hashing, parameterized SQL, safe
command execution, path validation, and secure logging.

### 05 · Tests Passed

![Tests Passed](screenshots/05_tests_passed.png)

Shows the completed automated verification:

```text
8 passed
```

The screenshot index is also available in
[`screenshots/README.md`](screenshots/README.md).

---

## Reports

### Findings

[`reports/FINDINGS.md`](reports/FINDINGS.md)

Contains:

- finding register
- Bandit evidence
- CWE references
- security impact
- review risk
- recommendations
- remediation references

### Remediation

[`reports/REMEDIATION.md`](reports/REMEDIATION.md)

Contains:

- remediation matrix
- secure coding practices
- verification approach
- regression-test information

### Security Review

[`reports/SECURITY_REVIEW.md`](reports/SECURITY_REVIEW.md)

Contains:

- review scope
- methodology
- baseline analysis
- security findings
- verification
- final conclusion

### Bandit Evidence

[`reports/bandit_report.json`](reports/bandit_report.json)

Contains the machine-readable Bandit baseline generated from the vulnerable
target.

---

## CodeAlpha Task 3 Mapping

| Task 3 Activity | Project Implementation |
|---|---|
| Select a language and application to audit | Controlled vulnerable Python application |
| Perform a security review | Manual source inspection |
| Use static analysis | Bandit 1.9.4 |
| Identify vulnerabilities | Eight actionable findings |
| Assess security risk | Finding-level review risk |
| Recommend secure practices | Documented recommendations |
| Implement remediation | Separate secure reference implementation |
| Verify remediation | pytest regression/security suite |
| Re-scan secure implementation | Bandit secure-version scan |
| Document the review | Findings, remediation, and review reports |
| Preserve evidence | Bandit JSON and screenshot evidence |

---

## Security & Privacy

This repository is an educational secure-coding exercise.

### Authorized Use

Only assess:

```text
Owned applications
Controlled laboratory environments
Explicitly authorized systems and data
```

### Never Publish

Do not commit:

- production credentials
- API keys
- authentication tokens
- private secrets
- confidential application data
- sensitive logs
- private test data
- unauthorized security evidence

The vulnerable target should remain local and controlled.

### Repository Hygiene

Before committing:

```powershell
git status --short
```

Also verify that generated Python caches are excluded:

```powershell
git check-ignore -v `
".pytest_cache" `
"__pycache__"
```

Only source code, documentation, deliberate evidence, and reviewed machine-readable
reports should be included in the public repository.

---

## Limitations

This project is an educational secure-coding review and remediation exercise.

It does not claim to be:

- a complete application security assessment
- a production penetration test
- a formal secure-development lifecycle
- a replacement for peer review
- a replacement for dependency, infrastructure, or deployment security testing

Bandit findings depend on the analyzer version and configured rules, while
manual review depends on application context.

Passing the regression suite demonstrates expected behavior for the included
tests. It does not prove the secure implementation is free of all possible
security defects.

---

## Project Status

```text
Controlled vulnerable target       ✅
Manual security review             ✅
Bandit baseline analysis           ✅
Security findings documented       ✅
Secure reference implementation    ✅
Regression/security tests          ✅ 8 passed
Secure-version Bandit re-scan      ✅
Review documentation               ✅
Evidence screenshots               ✅
GitHub repository                  ✅ Published
```

### Validated Results

```text
Python version:                3.13.15
Bandit version:                1.9.4
pytest version:                9.1.1
Vulnerable baseline:           1 High / 3 Medium / 3 Low
Actionable findings:           8
Secure-version High findings:  0
Secure-version Medium:         0
Secure-version Low:            2
Regression tests:              8 passed
Evidence screenshots:          5
```

---

## Author

**Subhadeep Adhikary**

CodeAlpha Cyber Security Intern

---

## License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.
