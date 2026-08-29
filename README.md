# CodeAlpha Secure Coding Review

A Python-based **secure coding review and remediation project** developed for the **CodeAlpha Cyber Security Internship, Task 3**.

The project demonstrates an end-to-end security review workflow using a deliberately vulnerable local Python application, manual source inspection, Bandit static analysis, documented findings, secure remediation, and automated regression testing.

> **Educational use only:** The vulnerable application is intentionally insecure and is provided solely as a controlled local audit target. Do not deploy it to production or expose it to untrusted users.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Objective](#objective)
- [Workflow](#workflow)
- [Key Security Areas](#key-security-areas)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Baseline Security Scan](#baseline-security-scan)
- [Security Findings](#security-findings)
- [Secure Version](#secure-version)
- [Verification and Testing](#verification-and-testing)
- [Reports](#reports)
- [CodeAlpha Task 3 Mapping](#codealpha-task-3-mapping)
- [Security and Ethical Use](#security-and-ethical-use)
- [Project Status](#project-status)
- [Author](#author)
- [License](#license)

---

## Project Overview

The purpose of this project is to demonstrate a practical **secure-coding review lifecycle**.

A deliberately vulnerable Python application is reviewed to identify insecure implementation patterns. The identified issues are then documented, assigned a review risk level, remediated in a separate secure reference implementation, and verified with static analysis and regression tests.

The project intentionally maintains two implementations:

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

This separation provides a clear before-and-after comparison without modifying the original audit target.

---

## Objective

The project objectives are to:

1. Review a controlled Python application for common secure-coding weaknesses.
2. Use both **manual source inspection** and **Bandit static analysis**.
3. Document findings with evidence, impact, risk, and recommendations.
4. Implement secure alternatives in a separate reference implementation.
5. Re-scan the secure implementation.
6. Verify important security controls through automated regression tests.
7. Preserve the review evidence in a form that can be reproduced by another reviewer.

---

## Workflow

```text
Controlled Vulnerable Application
                |
                v
        Manual Code Review
                +
        Bandit Static Analysis
                |
                v
         Security Findings
                |
                v
          Risk Assessment
                |
                v
         Secure Remediation
                |
                v
        Bandit Re-scan
                |
                v
       Security Regression Tests
```

---

## Key Security Areas

The review covers the following security-sensitive areas:

- Application secrets and configuration
- Password hashing and storage
- SQL query construction
- Operating-system command execution
- File and path handling
- Serialized data handling
- Authentication logging
- Security regression testing

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

Generated local files such as Python cache directories, pytest cache, SQLite databases, log files, and virtual environments are excluded through `.gitignore`.

---

## Requirements

- Python 3.10 or newer
- `pytest`
- `bandit`

The verified development environment used for the current review was:

```text
Python:  3.13.15
pytest:  9.1.1
Bandit:  1.9.4
```

---

## Installation

From the project root:

```powershell
python -m pip install -r requirements.txt
```

Verify the installed tools:

```powershell
python -m pytest --version
python -m bandit --version
```

---

## Running the Project

### 1. Run the vulnerable target

The vulnerable application is intended only for controlled local review:

```powershell
python target_app\vulnerable_app.py
```

It initializes the demonstration database and identifies itself as the intentionally vulnerable target.

Do not expose this application to untrusted users.

### 2. Run the security regression tests

```powershell
python -m pytest -q
```

The current verified regression-test result is:

```text
8 passed
```

---

## Baseline Security Scan

The baseline scan is performed against the intentionally vulnerable target.

### Run Bandit

```powershell
python -m bandit -r target_app
```

### Generate the JSON report

```powershell
python -m bandit -r target_app -f json -o reports\bandit_report.json
```

The generated report is stored at:

```text
reports/bandit_report.json
```

### Run the review helper

The project also includes an automated helper:

```powershell
python tools\run_review.py
```

It executes Bandit against `target_app/`, writes the JSON report, and prints a concise summary.

### Recorded baseline

The verified Bandit 1.9.4 scan covered **187 lines of code** and reported **7 findings**:

| Bandit severity | Count |
|---|---:|
| High | 1 |
| Medium | 3 |
| Low | 3 |
| **Total** | **7** |

The baseline scan completed without scanner errors or skipped files.

### Important interpretation

Two of the seven Bandit results are module-level advisories:

- **B403** for importing `pickle`
- **B404** for importing `subprocess`

These are retained as scanner evidence but are not treated as standalone exploitable vulnerabilities. The actionable weaknesses are the unsafe `pickle.load()` usage and the `subprocess` call using `shell=True`.

---

## Security Findings

The combined manual review and static analysis produced **eight actionable findings**:

| ID | Finding | Evidence | Review Risk |
|---|---|---|---|
| SC-001 | Hard-coded application secret | B105 + manual review | Medium |
| SC-002 | Weak password hashing | Manual review | High |
| SC-003 | SQL injection in `create_user()` | B608 + manual review | High |
| SC-004 | SQL injection in `find_user()` | B608 + manual review | High |
| SC-005 | OS command injection | B602 + manual review | High |
| SC-006 | Path traversal | Manual review | Medium |
| SC-007 | Unsafe deserialization with `pickle` | B301 + B403 + manual review | High |
| SC-008 | Plaintext password logging | Manual review | High |

Detailed descriptions, evidence, impacts, recommendations, and remediation references are available in:

[`reports/FINDINGS.md`](reports/FINDINGS.md)

---

## Secure Version

The remediated reference implementation is:

```text
secure_version/secure_app.py
```

The secure version demonstrates the following controls:

- Environment-based application secret loading
- Salted PBKDF2-HMAC password hashing
- Constant-time password verification
- Parameterized SQLite queries
- Explicit command allowlisting
- `shell=False` for subprocess execution
- Command execution timeout
- Resolved-path containment validation
- JSON instead of `pickle`
- Credential-safe authentication logging
- Input validation for security-sensitive operations

The secure version is intentionally kept separate from the vulnerable target so that the review remains easy to reproduce.

---

## Verification and Testing

### Secure-version static analysis

Run:

```powershell
python -m bandit -r secure_version
```

Verified result:

```text
High:   0
Medium: 0
Low:    2
```

The original High- and Medium-severity Bandit findings are no longer present in the secure implementation.

The remaining Low findings are related to controlled `subprocess` usage. The secure implementation uses a fixed command allowlist and `shell=False`, so the original `B602` `shell=True` pattern is not present.

The remaining advisory is documented rather than hidden or suppressed.

### Security regression tests

Run:

```powershell
python -m pytest -q
```

Verified result:

```text
8 passed
```

The regression suite covers:

- Salted password hashing
- Password verification
- Different salts for repeated password hashing
- Parameterized database operations
- JSON serialization and deserialization
- Path traversal rejection
- Command allowlisting
- Safe execution of an allowlisted command
- JSON output validity

---

## Before-and-After Results

| Measure | Vulnerable Target | Secure Version |
|---|---:|---:|
| Lines scanned | 187 | 257 |
| High Bandit findings | 1 | 0 |
| Medium Bandit findings | 3 | 0 |
| Low Bandit findings | 3 | 2 |
| Regression tests | N/A | 8 passed |

The results demonstrate a reduction in the most significant static-analysis findings after remediation.

---

## Reports

The project includes three human-readable reports:

- [`reports/SECURITY_REVIEW.md`](reports/SECURITY_REVIEW.md)  
  Review scope, methodology, baseline, risk interpretation, remediation overview, and verification.

- [`reports/FINDINGS.md`](reports/FINDINGS.md)  
  Detailed finding register, evidence, impact, recommendations, and remediation references.

- [`reports/REMEDIATION.md`](reports/REMEDIATION.md)  
  Remediation matrix, secure-coding practices, implementation changes, and verification results.

The machine-readable Bandit evidence is stored in:

```text
reports/bandit_report.json
```

---

## CodeAlpha Task 3 Mapping

CodeAlpha Task 3 requires a security review of a selected application, use of static analysis or manual inspection, secure-coding recommendations, and documented remediation.

| CodeAlpha Task 3 requirement | Project implementation |
|---|---|
| Select a language and application | Python controlled target application |
| Perform a security review | Manual source inspection |
| Use static analysis or manual inspection | Bandit 1.9.4 + manual review |
| Identify security vulnerabilities | Eight-item security finding register |
| Provide secure-coding recommendations | Finding-level recommendations |
| Implement remediation | `secure_version/secure_app.py` |
| Verify remediation | Bandit re-scan + pytest |
| Document findings and remediation | `reports/` documentation |

---

## Security and Ethical Use

This project is an educational secure-coding exercise.

The intentionally vulnerable application exists only to demonstrate security review and remediation techniques. It must not be used as a production application.

Only assess systems, applications, networks, or data that you own or have explicit authorization to test.

Do not use the vulnerable target to access, alter, or interfere with systems belonging to other users.

---

## Project Status

```text
Vulnerable target application       ✅
Manual security review              ✅
Bandit baseline scan                ✅
Baseline JSON evidence              ✅
Security findings documented        ✅
Secure remediation                  ✅
Secure-version Bandit re-scan       ✅
Security regression tests           ✅ 8 passed
Project documentation               ✅
Final evidence screenshots          ✅
GitHub submission                   ✅
CodeAlpha submission form           ✅
LinkedIn project video              ✅
```

The **technical Task 3 implementation and verification are complete**. The remaining items are submission and presentation evidence.

---

## Author

**Subhadeep Adhikary**

Cyber Security Intern - CodeAlpha

---

## License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for the complete license text.
