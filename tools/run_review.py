"""
CodeAlpha Secure Coding Review - Automated Security Review Helper.

This script runs Bandit against the intentionally vulnerable target
application and saves the machine-readable baseline report under
reports/bandit_report.json.

Usage:
    python tools/run_review.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "target_app"
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "bandit_report.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_bandit_report(path: Path) -> dict[str, Any]:
    """Load and validate the generated Bandit JSON report."""
    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Unable to read Bandit report: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            "Bandit report has an unexpected JSON structure."
        )

    return data


def print_summary(data: dict[str, Any]) -> None:
    """Print a concise summary of the Bandit baseline results."""
    metrics = data.get("metrics", {})
    totals = metrics.get("_totals", {})

    print()
    print("=" * 64)
    print("CODEALPHA SECURE CODING REVIEW")
    print("=" * 64)
    print("Bandit baseline security scan")
    print()

    print(f"Target: {TARGET}")
    print(f"Report: {OUTPUT}")
    print()

    print("Scan summary")
    print("-" * 64)
    print(
        f"Lines scanned: "
        f"{totals.get('loc', 'unknown')}"
    )
    print(
        f"High:          "
        f"{totals.get('SEVERITY.HIGH', 0)}"
    )
    print(
        f"Medium:        "
        f"{totals.get('SEVERITY.MEDIUM', 0)}"
    )
    print(
        f"Low:           "
        f"{totals.get('SEVERITY.LOW', 0)}"
    )
    print(
        f"Total findings: "
        f"{sum(
            int(totals.get(key, 0))
            for key in (
                'SEVERITY.HIGH',
                'SEVERITY.MEDIUM',
                'SEVERITY.LOW',
            )
        )}"
    )
    print(
        f"Errors:         "
        f"{data.get('errors', []) and len(data.get('errors', [])) or 0}"
    )
    print(
        f"Files skipped:  "
        f"{totals.get('skipped_tests', 0)}"
    )

    print("=" * 64)
    print()


def run_bandit() -> int:
    """Run Bandit against the intentionally vulnerable target."""
    REPORTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        str(TARGET),
        "-f",
        "json",
        "-o",
        str(OUTPUT),
    ]

    print("Running Bandit baseline scan...")
    print()

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
        )
    except OSError as exc:
        print(
            f"Error: unable to start Bandit: {exc}",
            file=sys.stderr,
        )
        return 1

    if not OUTPUT.exists():
        print(
            "Error: Bandit did not create the expected report:",
            file=sys.stderr,
        )
        print(
            OUTPUT,
            file=sys.stderr,
        )
        return result.returncode or 1

    try:
        report = load_bandit_report(OUTPUT)
    except RuntimeError as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )
        return result.returncode or 1

    print_summary(report)

    # Bandit normally returns a non-zero exit status when findings are
    # present. That is expected here because target_app is intentionally
    # vulnerable and is being scanned as the baseline.
    if result.returncode != 0:
        print(
            "Bandit reported findings in the intentionally vulnerable "
            "target. This is expected for the baseline audit."
        )
        print()

    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the automated security review helper."""
    if not TARGET.exists():
        print(
            f"Error: target directory not found: {TARGET}",
            file=sys.stderr,
        )
        return 1

    if not TARGET.is_dir():
        print(
            f"Error: target path is not a directory: {TARGET}",
            file=sys.stderr,
        )
        return 1

    return run_bandit()


if __name__ == "__main__":
    raise SystemExit(main())