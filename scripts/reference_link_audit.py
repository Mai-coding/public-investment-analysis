#!/usr/bin/env python3
"""Check active skill markdown/JSON references for missing local files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TOKEN_RE = re.compile(r"`([^`]+\.(?:md|json|py))`")
IGNORE_PREFIXES = ("[Target]", "handoff_task", "manifest", "charts_manifest", "source_ledger", "product_images_manifest")


def candidates(root: Path, source: Path, token: str) -> list[Path]:
    if token.startswith(("http://", "https://")):
        return []
    if token.startswith(("references/", "scripts/", "assets/", "examples/", "cold_storage/")):
        return [root / token]
    if token.endswith(".py"):
        return [root / "scripts" / token, source.parent / token]
    return [source.parent / token, root / "references" / token, root / token]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    failures: list[str] = []

    active_files = [
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".md", ".json"}
        and "cold_storage" not in p.parts
    ]
    for source in active_files:
        text = source.read_text(encoding="utf-8", errors="replace")
        for token in TOKEN_RE.findall(text):
            token = token.strip()
            if token.startswith(IGNORE_PREFIXES) or any(x in token for x in ("<", ">", "*", "–", "—")):
                continue
            paths = candidates(root, source, token)
            if not paths:  # external URL
                continue
            if not any(path.exists() for path in paths):
                failures.append(f"{source.relative_to(root)} -> {token}")

    # machine-readable load map gets a strict path check
    load_map = json.loads((root / "references" / "task_load_map.json").read_text(encoding="utf-8"))
    for task, config in load_map["tasks"].items():
        groups = {k: v for k, v in config.items() if isinstance(v, list)}
        for condition, refs in config.get("conditional", {}).items():
            groups[f"conditional.{condition}"] = refs
        for group, refs in groups.items():
            for ref in refs:
                path = (root / "references" / ref).resolve()
                if not path.exists():
                    failures.append(f"task_load_map {task}.{group} -> {ref}")

    for failure in sorted(set(failures)):
        print(f"[FAIL] {failure}")
    if failures:
        print(f"SUMMARY: {len(set(failures))} missing reference(s)")
        return 1
    print(f"PASS: checked {len(active_files)} active markdown/JSON files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
