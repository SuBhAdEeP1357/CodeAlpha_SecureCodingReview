# Secure Coding Review

## Review Overview

**Project:** CodeAlpha Secure Coding Review  
**Application:** Controlled Python demonstration application  
**Target:** `target_app/vulnerable_app.py`  
**Remediated reference:** `secure_version/secure_app.py`  
**Language:** Python 3.13.15  
**Static-analysis tool:** Bandit 1.9.4  
**Testing framework:** pytest 9.1.1  
**Review methods:** Manual source inspection + Bandit static analysis

This project demonstrates a complete secure-coding review lifecycle using a deliberately vulnerable local application. The vulnerable target is retained as an audit artifact, while security fixes are implemented separately in the secure reference implementation.

> **Safety note:** The target application is intentionally insecure for educational review purposes. It must not be deployed or exposed to untrusted users.

---

## CodeAlpha Task 3 Alignment

The project addresses the core Task 3 activities:

| Task activity | Project implementation |
|---|---|
| Select a programming language | Python |
| Select an application to audit | `target_app/vulnerable_app.py` |
| Perform a security review | Manual source inspection |
| Use static analysis | Bandit 1.9.4 |
| Identify vulnerabilities | Security finding register in `reports/FINDINGS.md` |
| Provide secure-coding recommendations | Findings and remediation documentation |
| Implement remediation | `secure_version/secure_app.py` |
| Verify remediation | Bandit re-scan + pytest regression tests |
| Document the review | `reports/SECURITY_REVIEW.md`, `FINDINGS.md`, and `REMEDIATION.md` |

---

## Scope

The review focuses on these security-sensitive implementation areas:

- secrets management
- password storage
- database queries
- operating-system command execution
- file and path handling
- deserialization
- sensitive-data logging

The review is limited to source-code security properties. It is not a production penetration test, infrastructure assessment, or deployment security assessment.

---

## Methodology

The review followed these steps:

1. Inspect the target source for security-sensitive coding patterns.
2. Run Bandit against `target_app/`.
3. Review every Bandit result and distinguish module-level advisories from actionable vulnerabilities.
4. Perform manual analysis for security weaknesses that static analysis does not fully establish.
5. Assign a review risk level based on practical impact and exploitability.
6. Implement corrective controls in `secure_version/secure_app.py`.
7. Re-run Bandit against the remediated implementation.
8. Run the security regression test suite.
9. Preserve the reports and machine-readable scan output for reproducibility.

---

## Baseline Static Analysis

### Command

```powershell
python -m bandit -r target_app
```

### Baseline Environment

```text
Python: 3.13.15
Bandit: 1.9.4
```

### Recorded Baseline

```text
Lines of code scanned: 187
High:   1
Medium: 3
Low:    3
Total:  7
Errors: 0
Files skipped: 0
```

The machine-readable baseline report was generated with:

```powershell
python -m bandit -r target_app -f json -o reports\bandit_report.json
```

and is stored at:

```text
reports/bandit_report.json
```

### Bandit Baseline Findings

| Bandit ID | Description | Severity | Confidence | CWE |
|---|---|---|---|---|
| B403 | `pickle` module import advisory | Low | High | CWE-502 |
| B404 | `subprocess` module import advisory | Low | High | CWE-78 |
| B105 | Possible hard-coded password/secret | Low | Medium | CWE-259 |
| B608 | Possible SQL injection in `create_user()` | Medium | Low | CWE-89 |
| B608 | Possible SQL injection in `find_user()` | Medium | Low | CWE-89 |
| B602 | `subprocess` call with `shell=True` | High | High | CWE-78 |
| B301 | Unsafe `pickle.load()` deserialization | Medium | High | CWE-502 |

### Interpretation of B403 and B404

B403 and B404 are module-level advisories. Importing `pickle` or `subprocess` is not, by itself, proof of an exploitable vulnerability.

The actionable risks are:

- `pickle.load()` for untrusted data, documented as **SC-007**
- `subprocess` with `shell=True`, documented as **SC-005**

These advisories are therefore retained as supporting scanner evidence rather than counted as separate standalone vulnerabilities in the final manual review.

---

## Final Security Finding Register

The combined manual review and static analysis produced **eight actionable findings**:

| ID | Finding | Primary evidence | Review risk |
|---|---|---|---|
| SC-001 | Hard-coded application secret | B105 + manual review | Medium |
| SC-002 | Weak password hashing | Manual review | High |
| SC-003 | SQL injection in `create_user()` | B608 + manual review | High |
| SC-004 | SQL injection in `find_user()` | B608 + manual review | High |
| SC-005 | OS command injection | B602 + manual review | High |
| SC-006 | Path traversal | Manual review | Medium |
| SC-007 | Unsafe deserialization with `pickle` | B301 + B403 + manual review | High |
| SC-008 | Plaintext password logging | Manual review | High |

Detailed descriptions, evidence, recommendations, and remediation references are documented in:

```text
reports/FINDINGS.md
```

---

## Risk Assessment Approach

Two classifications are used in this project:

**Bandit severity** is the severity assigned by the static-analysis rule.

**Review risk** is the project's contextual assessment based on likely security impact and exploitability.

These values are intentionally not treated as interchangeable.

For example, Bandit rates the hard-coded secret as Low, while the review assigns Medium risk because exposure of a real application secret could compromise dependent security controls.

Similarly, the manually identified plaintext password logging issue receives High review risk because disclosure of authentication credentials can directly affect account security.

---

## Remediation Overview

The secure reference implementation is:

```text
secure_version/secure_app.py
```

The primary controls introduced are:

| Finding | Remediation |
|---|---|
| SC-001 | Read the application secret from an environment variable |
| SC-002 | Use salted PBKDF2-HMAC password hashing with a stored work factor |
| SC-003 | Use parameterized `INSERT` queries |
| SC-004 | Use parameterized `SELECT` queries |
| SC-005 | Use a fixed command allowlist, `shell=False`, and a timeout |
| SC-006 | Resolve paths and enforce directory containment |
| SC-007 | Replace `pickle` with JSON for structured data |
| SC-008 | Remove passwords from application logs |

Complete remediation details are documented in:

```text
reports/REMEDIATION.md
```

---

## Secure-Version Static Analysis

### Command

```powershell
python -m bandit -r secure_version
```

### Verified Result

```text
Lines of code scanned: 257
High:   0
Medium: 0
Low:    2
Files skipped: 0
```

The two remaining Low findings are:

```text
B404  subprocess import advisory
B603  subprocess call with shell=False
```

The original High-severity `B602` finding caused by `shell=True` is no longer present.

The secure implementation additionally restricts execution to a fixed command allowlist and applies a timeout. The remaining Low advisories are documented rather than hidden or suppressed.

---

## Automated Verification

The remediated implementation was tested using:

```powershell
python -m pytest -q
```

Verified result:

```text
8 passed
```

The regression suite verifies:

- salted password hashing and password verification
- different salts for repeated password hashing
- JSON serialization and deserialization
- path traversal rejection
- rejection of unapproved commands
- execution of an allowlisted command
- valid JSON output
- secure database behavior with parameterized queries

---

## Before-and-After Comparison

| Measure | Vulnerable target | Secure version |
|---|---:|---:|
| Lines scanned | 187 | 257 |
| High Bandit findings | 1 | 0 |
| Medium Bandit findings | 3 | 0 |
| Low Bandit findings | 3 | 2 |
| Automated regression tests | N/A | 8 passed |

The comparison demonstrates that the original High- and Medium-severity Bandit findings were remediated in the secure reference implementation.

The remaining two Low findings are documented Bandit advisories associated with controlled subprocess usage rather than the original `shell=True` vulnerability.

---

## Security Review Evidence

The review package contains:

```text
reports/
├── bandit_report.json
├── FINDINGS.md
├── REMEDIATION.md
└── SECURITY_REVIEW.md
```

Supporting visual evidence is stored in:

```text
screenshots/
├── 01_project_structure.png
├── 02_bandit_baseline.png
├── 03_security_findings.png
├── 04_secure_remediation.png
├── 05_tests_passed.png
└── README.md
```

The evidence chain is:

```text
Vulnerable source code
        ↓
Manual source review
        ↓
Bandit baseline
        ↓
Finding register
        ↓
Remediation
        ↓
Secure-version Bandit re-scan
        ↓
Regression tests
```

This provides a clear before-and-after comparison and allows the review process to be reproduced.

---

## Reproduction Commands

From the project root:

### 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Run the vulnerable target locally

```powershell
python target_app\vulnerable_app.py
```

This target is intentionally insecure and should be used only for the controlled review.

### 3. Run the baseline Bandit scan

```powershell
python -m bandit -r target_app
```

### 4. Generate the JSON evidence

```powershell
python -m bandit -r target_app -f json -o reports\bandit_report.json
```

### 5. Scan the secure implementation

```powershell
python -m bandit -r secure_version
```

### 6. Run the regression tests

```powershell
python -m pytest -q
```

Expected regression result:

```text
8 passed
```

---

## Review Limitations

This project is an educational secure-coding exercise using a deliberately small local application.

The review does not claim to provide:

- a full penetration test
- infrastructure or network security testing
- production configuration assessment
- dependency vulnerability management
- cloud-security assessment
- complete application threat modeling

The conclusions apply to the reviewed source code and the demonstrated remediation controls.

---

## Conclusion

The project demonstrates a complete secure-coding review lifecycle:

```text
Identify
   ↓
Assess
   ↓
Document
   ↓
Remediate
   ↓
Re-scan
   ↓
Retest
```

The vulnerable target produced a real Bandit baseline of **7 findings** across **187 lines of code**. The secure implementation reduced the Bandit result to **0 High, 0 Medium, and 2 Low findings**, while the security regression suite completed with **8 passed tests**.

The vulnerable application remains available for controlled audit comparison, while `secure_version/secure_app.py` provides the remediated reference implementation.

The project should be treated as an educational and authorized security-review artifact.
