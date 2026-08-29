"""
Secure reference implementation package for the CodeAlpha Secure Coding Review.

This package contains the remediated version of the intentionally vulnerable
target application used for the educational security assessment.

The secure implementation demonstrates:
- Environment-based secret management
- Salted PBKDF2-HMAC password hashing
- Parameterized SQL queries
- Allowlisted subprocess execution with shell=False
- Path traversal protection
- JSON-based data serialization
- Credential-safe logging
"""