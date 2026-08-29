"""
CodeAlpha Secure Coding Review - Controlled Vulnerable Target.

This module is intentionally vulnerable and exists only as a local
educational target for the CodeAlpha Secure Coding Review.

The application demonstrates insecure coding patterns involving:
- hard-coded secrets
- weak password hashing
- SQL injection
- operating-system command execution
- path traversal
- unsafe deserialization
- plaintext credential logging

IMPORTANT:
This application must not be deployed to production or exposed to
untrusted users. It is intended only for authorized local security
testing, static analysis, and remediation practice.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import sqlite3
import subprocess
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

DATABASE_FILE = "users.db"

# SC-001: Intentionally hard-coded application secret.
# This exists so the security review can identify the secret-management issue.
APP_SECRET = "CodeAlpha-Demo-Secret-2026"


# ============================================================================
# Database
# ============================================================================

def get_connection() -> sqlite3.Connection:
    """Return a connection to the local demonstration database."""
    return sqlite3.connect(DATABASE_FILE)


def initialize_database() -> None:
    """Create the demonstration users table if it does not exist."""
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


# ============================================================================
# User creation
# ============================================================================

def create_user(
    username: str,
    password: str,
) -> None:
    """
    Create a demonstration user.

    WARNING:
    This function intentionally uses a fast, unsalted SHA-256 hash and
    constructs SQL with string interpolation so that the security review
    can identify these weaknesses.
    """

    # SC-002: Intentionally weak password storage.
    # SHA-256 is a fast general-purpose hash and no unique salt is used.
    password_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    try:
        # SC-003: Intentionally vulnerable SQL construction.
        # User-controlled input is interpolated into the SQL statement.
        query = (
            "INSERT INTO users (username, password_hash) "
            f"VALUES ('{username}', '{password_hash}')"
        )

        connection.execute(query)
        connection.commit()
    finally:
        connection.close()


# ============================================================================
# User lookup
# ============================================================================

def find_user(
    username: str,
) -> list[tuple]:
    """
    Find a demonstration user.

    WARNING:
    The SQL statement intentionally interpolates the supplied username
    directly into the query so that SQL injection can be identified
    during the security review.
    """

    connection = get_connection()

    try:
        # SC-004: Intentionally vulnerable SQL construction.
        query = (
            "SELECT id, username, password_hash "
            f"FROM users WHERE username = '{username}'"
        )

        return connection.execute(query).fetchall()
    finally:
        connection.close()


# ============================================================================
# Operating-system command execution
# ============================================================================

def run_system_command(
    command: str,
) -> str:
    """
    Execute a demonstration operating-system command.

    WARNING:
    This function is intentionally unsafe. It accepts arbitrary command
    text and passes it to a shell so that command-injection risk can be
    identified by the security review and Bandit.
    """

    # SC-005: Intentionally vulnerable command execution.
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout


# ============================================================================
# File access
# ============================================================================

def read_user_file(
    filename: str,
) -> str:
    """
    Read a file from the demonstration data directory.

    WARNING:
    The target intentionally fails to validate the final resolved path,
    allowing the security review to identify path-traversal risk.
    """

    # SC-006: Intentionally vulnerable path handling.
    base_directory = Path("data")
    file_path = base_directory / filename

    return file_path.read_text(
        encoding="utf-8"
    )


# ============================================================================
# Serialized object loading
# ============================================================================

def load_saved_object(
    filename: str,
):
    """
    Load a serialized demonstration object.

    WARNING:
    pickle is intentionally used here to demonstrate unsafe deserialization
    of potentially untrusted data.
    """

    # SC-007: Intentionally unsafe deserialization.
    with open(
        filename,
        "rb",
    ) as file:
        return pickle.load(file)


# ============================================================================
# Authentication logging
# ============================================================================

def log_login(
    username: str,
    password: str,
) -> None:
    """
    Record a demonstration login event.

    WARNING:
    The password is intentionally written to the log so that the review
    can identify plaintext credential exposure.
    """

    # SC-008: Intentionally logs plaintext credentials.
    with open(
        "login.log",
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"username={username}, password={password}\n"
        )


# ============================================================================
# Environment helper
# ============================================================================

def get_environment_value(
    name: str,
) -> str:
    """Return an environment variable value for demonstration purposes."""
    return os.getenv(
        name,
        "",
    )


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    """Initialize the controlled vulnerable demonstration application."""
    initialize_database()

    print(
        "CodeAlpha Secure Coding Review target application"
    )
    print(
        "This application is intentionally vulnerable "
        "for local security-review practice."
    )
    print(
        "Do not deploy or expose this application "
        "to untrusted users."
    )


if __name__ == "__main__":
    main()