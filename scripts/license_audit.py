#!/usr/bin/env python3
"""Audit repository license files and vendored font provenance."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from matplotlib import font_manager as fm


ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
EXPECTED = {
    "LXGWWenKai-Regular.ttf": (
        "39ad71264b588165b469e35e6afb162a378dacd1f95348160240ba9038ac3009",
        "LXGW WenKai",
    ),
    "SourceSerif4-Regular.ttf": (
        "e5a4ee6a3d87bb9024796be390c6771e2a0eb1883dae25effaf57ca01668e24b",
        "Source Serif 4",
    ),
    "OFL-LXGW-WenKai.txt": (
        "1a25e35da1031c6c3436fde545bb9cb5aca954e9873afe510c834b8b79bd21a0",
        None,
    ),
    "OFL-Source-Serif-4.md": (
        "c21d7293d87b6d7ab1d0229a2f55b77f33a7613a6a4e66f6693d68d7d8d09464",
        None,
    ),
}
FORBIDDEN = {"simkai.ttf", "times.ttf"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    failures: list[str] = []

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    notice_text = (ROOT / "NOTICE").read_text(encoding="utf-8", errors="replace")
    third_party = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8", errors="replace")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        failures.append("LICENSE is not recognizable Apache-2.0 text")
    if "anthropics/financial-services" not in notice_text:
        failures.append("NOTICE does not identify the upstream Anthropic repository")
    if "SIL Open Font License" not in third_party:
        failures.append("THIRD_PARTY_NOTICES.md does not identify the font license")

    present_fonts = {path.name.lower() for path in FONT_DIR.glob("*.[to]tf")}
    forbidden = sorted(present_fonts & FORBIDDEN)
    if forbidden:
        failures.append("proprietary font(s) present: " + ", ".join(forbidden))

    for name, (expected_hash, expected_family) in EXPECTED.items():
        path = FONT_DIR / name
        if not path.is_file():
            failures.append(f"missing vendored asset: {name}")
            continue
        actual_hash = digest(path)
        if actual_hash != expected_hash:
            failures.append(f"hash mismatch for {name}: {actual_hash}")
        if expected_family:
            actual_family = fm.FontProperties(fname=str(path)).get_name()
            if actual_family != expected_family:
                failures.append(
                    f"font family mismatch for {name}: {actual_family!r} != {expected_family!r}"
                )

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        print(f"SUMMARY: 0 PASS / {len(failures)} FAIL")
        return 1

    print("[PASS] Apache-2.0 repository license and upstream notice are present")
    print("[PASS] Two OFL-1.1 fonts and their upstream license files match pinned hashes")
    print("[PASS] No SimKai or Times New Roman font binary is distributed")
    print("SUMMARY: 3 PASS / 0 FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
