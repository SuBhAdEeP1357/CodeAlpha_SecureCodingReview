"""
Security regression tests for the CodeAlpha Secure Coding Review.

These tests verify that the remediated implementation addresses the
security weaknesses identified in the intentionally vulnerable target.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from secure_version.secure_app import (
    create_user,
    find_user,
    hash_password,
    initialize_database,
    load_saved_object,
    read_user_file,
    run_allowed_command,
    save_json_object,
    verify_password,
)


def test_password_hash_is_salted_and_verifiable() -> None:
    """Verify password hashing and correct/incorrect password handling."""
    stored = hash_password("CorrectHorseBatteryStaple")

    assert stored.startswith("pbkdf2_sha256$")
    assert verify_password(
        "CorrectHorseBatteryStaple",
        stored,
    )
    assert not verify_password(
        "WrongPassword",
        stored,
    )


def test_same_password_gets_different_hashes() -> None:
    """Verify that a random salt produces different hashes."""
    first = hash_password("same-password")
    second = hash_password("same-password")

    assert first != second


def test_parameterized_database_operations(
    tmp_path,
    monkeypatch,
) -> None:
    """Verify secure database creation and parameterized user queries."""
    database_path = tmp_path / "secure_users.db"

    monkeypatch.setattr(
        "secure_version.secure_app.DATABASE_FILE",
        database_path,
    )

    initialize_database()
    create_user(
        "alice",
        "safe-password",
    )

    rows = find_user("alice")

    assert len(rows) == 1
    assert rows[0][1] == "alice"
    assert rows[0][2].startswith("pbkdf2_sha256$")

    with sqlite3.connect(database_path) as connection:
        stored_hash = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            ("alice",),
        ).fetchone()

    assert stored_hash is not None
    assert verify_password(
        "safe-password",
        stored_hash[0],
    )


def test_json_round_trip(
    tmp_path,
    monkeypatch,
) -> None:
    """Verify that structured application data can be saved and loaded."""
    data_directory = tmp_path.resolve()

    monkeypatch.setattr(
        "secure_version.secure_app.DATA_DIRECTORY",
        data_directory,
    )

    payload = {
        "role": "analyst",
        "enabled": True,
        "access_level": 2,
    }

    save_json_object(
        "settings.json",
        payload,
    )

    assert load_saved_object(
        "settings.json",
    ) == payload


def test_path_traversal_is_rejected(
    tmp_path,
    monkeypatch,
) -> None:
    """Verify that paths escaping the approved directory are rejected."""
    data_directory = tmp_path.resolve()

    monkeypatch.setattr(
        "secure_version.secure_app.DATA_DIRECTORY",
        data_directory,
    )

    with pytest.raises(
        ValueError,
        match="escapes the application data directory",
    ):
        read_user_file("../outside.txt")


def test_allowed_command_rejects_unapproved_command() -> None:
    """Verify that commands outside the allowlist are rejected."""
    with pytest.raises(
        ValueError,
        match="Command is not permitted",
    ):
        run_allowed_command("format")


def test_allowed_command_runs_known_command() -> None:
    """Verify that an allowlisted command can execute safely."""
    output = run_allowed_command("whoami")

    assert isinstance(output, str)
    assert output.strip()


def test_json_output_is_valid(
    tmp_path,
    monkeypatch,
) -> None:
    """Verify that saved JSON can be parsed as valid JSON."""
    data_directory = tmp_path.resolve()

    monkeypatch.setattr(
        "secure_version.secure_app.DATA_DIRECTORY",
        data_directory,
    )

    save_json_object(
        "example.json",
        {"status": "ok"},
    )

    json_path = data_directory / "example.json"

    data = json.loads(
        json_path.read_text(
            encoding="utf-8",
        )
    )

    assert data == {
        "status": "ok",
    }