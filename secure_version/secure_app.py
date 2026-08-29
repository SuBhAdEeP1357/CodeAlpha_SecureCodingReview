"""
CodeAlpha Secure Coding Review - Remediated Reference Implementation.

This module contains the secure reference implementation used to demonstrate
remediation of the weaknesses identified in the intentionally vulnerable
target application.

Security controls demonstrated:
- Environment-based secret management
- Salted PBKDF2-HMAC password hashing
- Parameterized SQLite queries
- Allowlisted subprocess execution with shell=False
- Path traversal protection
- JSON-based serialization
- Credential-safe logging

This module is intended for educational and authorized security-review use.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_FILE = Path("secure_users.db").resolve()
DATA_DIRECTORY = Path("data").resolve()

# Only fixed, predefined commands may be executed.
# No caller-provided command string is ever passed to a shell.
ALLOWED_COMMANDS: dict[str, list[str]] = {
    "whoami": ["whoami"],
    "ipconfig": ["ipconfig"],
}

PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 310_000
SALT_LENGTH = 16


# ---------------------------------------------------------------------------
# Secrets management
# ---------------------------------------------------------------------------

def get_app_secret() -> str:
    """Return the application secret from the environment.

    Raises:
        RuntimeError: If CODEALPHA_APP_SECRET is not configured.
    """
    secret = os.getenv("CODEALPHA_APP_SECRET")

    if not secret:
        raise RuntimeError(
            "CODEALPHA_APP_SECRET is not configured"
        )

    return secret


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with foreign-key enforcement enabled."""
    connection = sqlite3.connect(DATABASE_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    """Create the demo users table when it does not already exist."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(
    password: str,
    salt: bytes | None = None,
) -> str:
    """Hash a password with a unique salt using PBKDF2-HMAC-SHA256.

    The iteration count is stored with the resulting representation so that
    the value can be verified consistently later.
    """
    if not isinstance(password, str):
        raise TypeError("password must be a string")

    if salt is None:
        salt = os.urandom(SALT_LENGTH)

    if len(salt) != SALT_LENGTH:
        raise ValueError(
            f"salt must be exactly {SALT_LENGTH} bytes"
        )

    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        f"pbkdf2_{PBKDF2_ALGORITHM}"
        f"${PBKDF2_ITERATIONS}"
        f"${salt.hex()}"
        f"${digest.hex()}"
    )


def verify_password(
    password: str,
    stored_value: str,
) -> bool:
    """Verify a plaintext password against a stored PBKDF2 representation."""
    if not isinstance(password, str):
        return False

    if not isinstance(stored_value, str):
        return False

    try:
        (
            algorithm_name,
            iterations_text,
            salt_hex,
            digest_hex,
        ) = stored_value.split("$")

        expected_algorithm = f"pbkdf2_{PBKDF2_ALGORITHM}"

        if algorithm_name != expected_algorithm:
            return False

        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)

        if iterations <= 0 or len(salt) != SALT_LENGTH:
            return False

    except (TypeError, ValueError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return hmac.compare_digest(
        actual_digest,
        expected_digest,
    )


# ---------------------------------------------------------------------------
# Secure database operations
# ---------------------------------------------------------------------------

def create_user(
    username: str,
    password: str,
) -> None:
    """Create a user using a salted password hash and parameterized SQL."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("username must be a non-empty string")

    password_hash = hash_password(password)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash),
        )
        connection.commit()
    finally:
        connection.close()


def find_user(username: str) -> list[tuple]:
    """Find users using a parameterized SQL statement."""
    if not isinstance(username, str):
        raise TypeError("username must be a string")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        return cursor.fetchall()
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Safe command execution
# ---------------------------------------------------------------------------

def run_allowed_command(command_name: str) -> str:
    """Execute one predefined command without shell interpretation.

    Raises:
        ValueError: If the command is not in the explicit allowlist.
    """
    if command_name not in ALLOWED_COMMANDS:
        raise ValueError("Command is not permitted")

    result = subprocess.run(
        ALLOWED_COMMANDS[command_name],
        shell=False,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    return result.stdout


# ---------------------------------------------------------------------------
# Safe file handling
# ---------------------------------------------------------------------------

def safe_data_file(filename: str) -> Path:
    """Resolve a data path and ensure it remains inside DATA_DIRECTORY."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename must be a non-empty string")

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidate = (DATA_DIRECTORY / filename).resolve()

    try:
        candidate.relative_to(DATA_DIRECTORY)
    except ValueError as exc:
        raise ValueError(
            "Path escapes the application data directory"
        ) from exc

    return candidate


def read_user_file(filename: str) -> str:
    """Read a text file only when it is inside the approved data directory."""
    path = safe_data_file(filename)
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------

def save_json_object(
    filename: str,
    value: Any,
) -> None:
    """Serialize application data as JSON."""
    path = safe_data_file(filename)

    path.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_saved_object(filename: str) -> Any:
    """Load JSON data from the approved application data directory."""
    path = safe_data_file(filename)

    return json.loads(
        path.read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Credential-safe logging
# ---------------------------------------------------------------------------

def log_login(username: str) -> None:
    """Log a login event without storing the user's password."""
    if not isinstance(username, str):
        raise TypeError("username must be a string")

    with Path("secure_login.log").open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"successful login for username={username}\n"
        )


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Initialize the secure demonstration application."""
    initialize_database()

    print(
        "CodeAlpha Secure Coding Review secure reference application"
    )
    print(
        "This implementation demonstrates remediated security controls."
    )


if __name__ == "__main__":
    main()
