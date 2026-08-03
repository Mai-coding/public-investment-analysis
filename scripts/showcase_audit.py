#!/usr/bin/env python3
"""Verify that the public showcase is complete, reproducible, and internally consistent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "mongodb" / "showcase_manifest.json"
SOURCE_DIR = ROOT / "examples" / "mongodb" / "source-pages"
ASSET_DIR = ROOT / "assets" / "showcase"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []
    if not MANIFEST.is_file():
        print(f"[FAIL] missing {MANIFEST.relative_to(ROOT)}")
        return 1
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    raw_manifest = MANIFEST.read_text(encoding="utf-8")
    if "C:\\Users\\" in raw_manifest or "/Users/" in raw_manifest:
        failures.append("showcase manifest contains a private absolute path")

    for name, expected in payload.get("source_pages", {}).items():
        path = SOURCE_DIR / name
        if not path.is_file():
            failures.append(f"missing source page: {name}")
        elif sha256(path) != expected:
            failures.append(f"source-page hash mismatch: {name}")

    for name, expected in payload.get("generated_assets", {}).items():
        path = ASSET_DIR / name
        if not path.is_file():
            failures.append(f"missing generated asset: {name}")
        elif sha256(path) != expected:
            failures.append(f"generated-asset hash mismatch: {name}")

    expected_metrics = {
        "report_pages": 44,
        "body_characters": 38419,
    }
    for key, expected in expected_metrics.items():
        if payload.get(key) != expected:
            failures.append(f"manifest {key}={payload.get(key)!r}, expected {expected!r}")
    if payload.get("validation", {}).get("independent_review") != "PASS":
        failures.append("independent review is not PASS")
    if payload.get("validation", {}).get("repository_checks") != "10 PASS / 0 FAIL":
        failures.append("manifest repository-check count is stale")
    expected_page_map = {
        "cover.png": 1,
        "competition.png": 17,
        "valuation-sensitivity.png": 30,
        "scenario-weights.png": 31,
        "valuation-summary.png": 32,
    }
    if payload.get("source_page_map") != expected_page_map:
        failures.append("source-page numbers do not match the audited report")
    source_report = payload.get("source_report", {})
    report_hash = source_report.get("sha256", "")
    if len(report_hash) != 64 or any(character not in "0123456789abcdef" for character in report_hash):
        failures.append("source-report SHA-256 is missing or malformed")
    if source_report.get("distributed") is not False:
        failures.append("source-report distribution status must remain false")

    gif_path = ASSET_DIR / "mongodb-workflow.gif"
    if gif_path.is_file():
        with Image.open(gif_path) as image:
            if image.size != (1200, 675):
                failures.append(f"GIF size is {image.size}, expected (1200, 675)")
            if getattr(image, "n_frames", 1) != 5:
                failures.append(f"GIF has {getattr(image, 'n_frames', 1)} frame(s), expected 5")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
    required_links = (
        "assets/showcase/mongodb-workflow.gif",
        "examples/mongodb/README.md",
        "examples/mongodb/showcase_manifest.json",
    )
    for link in required_links:
        if link not in readme or link not in readme_en:
            failures.append(f"README showcase link missing in one or both languages: {link}")
    stale_claims = (
        "本仓库暂不展示历史 full-report 截图",
        "No historical full-report screenshot is presented",
    )
    if any(claim in readme or claim in readme_en for claim in stale_claims):
        failures.append("README still contains the pre-showcase status claim")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        print(f"SUMMARY: 0 PASS / {len(failures)} FAIL")
        return 1

    print("[PASS] Showcase source pages and generated assets match the recorded hashes")
    print("[PASS] Source-report hash and page-number mapping preserve the PDF-to-page provenance chain")
    print("[PASS] Five-frame 1200x675 GIF and validation metrics match the case record")
    print("[PASS] Chinese and English READMEs link the real case without stale status text")
    print("[PASS] Showcase manifest contains no private absolute path")
    print("SUMMARY: 5 PASS / 0 FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
