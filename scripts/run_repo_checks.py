#!/usr/bin/env python3
"""Run deterministic repository checks with the active Python interpreter."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(label: str, *args: str) -> bool:
    print(f"\n=== {label} ===", flush=True)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run([sys.executable, *args], cwd=ROOT, env=env)
    if result.returncode:
        print(f"FAILED: {label} (exit {result.returncode})", flush=True)
        return False
    print(f"PASSED: {label}", flush=True)
    return True


def main() -> int:
    checks = [
        ("reference links", str(SCRIPTS / "reference_link_audit.py"), "--root", str(ROOT)),
        ("license and vendored fonts", str(SCRIPTS / "license_audit.py")),
        ("context budgets", str(SCRIPTS / "context_budget_audit.py"), "--root", str(ROOT)),
        ("source coverage self-test", str(SCRIPTS / "source_coverage_audit.py"), "--self-test"),
        ("showcase integrity", str(SCRIPTS / "showcase_audit.py")),
        ("artifact audit regression", str(SCRIPTS / "test_artifact_audit.py")),
        ("chart overlap regression", str(SCRIPTS / "test_chart_text_overlap.py")),
        ("depth exclusion regression", str(SCRIPTS / "test_depth_exclusion.py")),
        ("report content regression", str(SCRIPTS / "test_report_content_audit.py")),
    ]
    passed = [run(label, *args) for label, *args in checks]

    print("\n=== Python syntax ===", flush=True)
    syntax_ok = True
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            syntax_ok = False
            print(f"FAILED: {path.relative_to(ROOT)}: {exc}", flush=True)
    print("PASSED: Python syntax" if syntax_ok else "FAILED: Python syntax", flush=True)
    passed.append(syntax_ok)

    failures = len(passed) - sum(passed)
    print(f"\nSUMMARY: {len(passed) - failures} PASS / {failures} FAIL", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
