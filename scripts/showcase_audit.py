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


def audit_intel() -> list[str]:
    from build_intel_showcase import APPROVED_PAGE_HASHES, SLIDES

    failures = []
    base = ROOT / 'examples/intel'
    manifest = base / 'showcase_manifest.json'
    if not manifest.is_file():
        return ['Intel showcase manifest is missing']
    payload = json.loads(manifest.read_text(encoding='utf-8'))
    expected_paths = {'README.md', 'showcase_manifest.json',
                      *('source-pages/' + name for name in APPROVED_PAGE_HASHES)}
    actual_paths = {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    if actual_paths != expected_paths:
        failures.append('Intel case must contain exactly its README, manifest and five approved PNG pages')
    if payload.get('source_page_map') != {s[0]: s[1] for s in SLIDES}:
        failures.append('Intel source-page mapping differs from approved PDF pages 1, 3, 23, 40, 41')
    if payload.get('source_pages') != APPROVED_PAGE_HASHES:
        failures.append('Intel page allowlist differs from the approved source hashes')
    for name, expected in APPROVED_PAGE_HASHES.items():
        page = base / 'source-pages' / name
        if not page.is_file() or sha256(page) != expected:
            failures.append('Intel source-page hash mismatch: ' + name)
    expected_assets = {'intel-workflow.gif', 'intel-showcase.png', 'intel-result-card.png'}
    actual_assets = {p.name for p in ASSET_DIR.glob('intel*') if p.is_file()}
    if actual_assets != expected_assets:
        failures.append('Unexpected Intel preview file outside the approved asset list')
    assets = payload.get('generated_assets', {})
    if set(assets) != expected_assets:
        failures.append('Intel must expose only the three derived preview assets')
    for name in expected_assets:
        p = ASSET_DIR / name
        if not p.is_file() or sha256(p) != assets.get(name):
            failures.append('Intel generated-asset hash mismatch: ' + name)
    for key, expected in {'report_pages': 58, 'published_pages': 5,
                          'report_date': '2026-10-19', 'market_snapshot': '2026-10-16'}.items():
        if payload.get(key) != expected:
            failures.append('Intel manifest has incorrect ' + key)
    source = payload.get('source_report', {})
    if source.get('distributed') is not False or source.get('sha256') != '073b7af82a740da3aa9a718942d135ec29ae8ceb14ec8929a5ffbc9639e0749c':
        failures.append('Intel source PDF provenance/distribution boundary changed')
    forbidden = {'.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.7z'}
    for p in ROOT.rglob('*'):
        if '.git' not in p.relative_to(ROOT).parts and p.is_file() and p.suffix.lower() in forbidden:
            failures.append('Complete report/model/archive is not allowed in the public package: ' + p.relative_to(ROOT).as_posix())
    raw = manifest.read_text(encoding='utf-8')
    if 'C:\\Users\\' in raw or '/Users/' in raw:
        failures.append('Intel manifest contains a private absolute path')
    gif = ASSET_DIR / 'intel-workflow.gif'
    if gif.is_file():
        with Image.open(gif) as im:
            if im.size != (1600, 1000) or getattr(im, 'n_frames', 1) != 5:
                failures.append('Intel GIF must be 1600x1000 with exactly five frames')
    for name in ['README.md', 'README_EN.md']:
        text = (ROOT / name).read_text(encoding='utf-8')
        for link in ['assets/showcase/intel-workflow.gif', 'assets/showcase/intel-showcase.png',
                     'examples/intel/README.md', 'examples/intel/showcase_manifest.json']:
            if link not in text:
                failures.append(f'{name} missing Intel showcase link: {link}')
    return failures


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = audit_intel()
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
    print("[PASS] Historical MongoDB five-frame 1200x675 GIF and metrics match its case record")
    print("[PASS] Chinese and English READMEs link the real case without stale status text")
    print("[PASS] Showcase manifest contains no private absolute path")
    print("[PASS] Intel exposes only five approved pages; source hashes and derived previews agree")
    print("[PASS] No full report, model or archive is present in the public package")
    print("SUMMARY: 7 PASS / 0 FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
