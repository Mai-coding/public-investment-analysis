#!/usr/bin/env python3
"""Audit just-in-time reference load size and missing paths.

Approximation: CJK chars ~= 1.3 tokens; non-CJK chars ~= 0.25 token.
This is a routing regression guard, not an exact tokenizer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
DEFAULT_LIMIT = 18000


def estimate_tokens(text: str) -> int:
    cjk = len(CJK_RE.findall(text))
    other = max(0, len(text) - cjk)
    return round(cjk * 1.3 + other * 0.25)


def resolve(root: Path, ref: str) -> Path:
    # map entries are relative to references/ unless they explicitly leave it
    return (root / "references" / ref).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    load_map = json.loads((root / "references" / "task_load_map.json").read_text(encoding="utf-8"))
    missing: list[str] = []
    failures: list[str] = []

    print("Context budget audit (approximate tokens)")
    for task, config in load_map["tasks"].items():
        phase_totals: list[tuple[str, int, list[str]]] = []
        for phase, refs in config.items():
            if phase == "conditional" or not isinstance(refs, list):
                continue
            total = 0
            names = []
            for ref in refs:
                path = resolve(root, ref)
                if not path.exists():
                    missing.append(f"{task}/{phase}: {ref}")
                    continue
                total += estimate_tokens(path.read_text(encoding="utf-8", errors="replace"))
                names.append(ref)
            phase_totals.append((phase, total, names))

        for phase, total, names in phase_totals:
            status = "PASS" if total <= args.limit else "FAIL"
            print(f"[{status}] {task}.{phase}: ~{total:,} tokens across {len(names)} files")
            if status == "FAIL":
                failures.append(f"{task}.{phase} exceeds {args.limit}: {total}")

        conditional = config.get("conditional", {})
        for condition, refs in conditional.items():
            total = 0
            count = 0
            for ref in refs:
                path = resolve(root, ref)
                if not path.exists():
                    missing.append(f"{task}/conditional/{condition}: {ref}")
                    continue
                total += estimate_tokens(path.read_text(encoding="utf-8", errors="replace"))
                count += 1
            print(f"[INFO] {task}.conditional.{condition}: ~{total:,} tokens across {count} files (opt-in)")

    if missing:
        for item in missing:
            print(f"[FAIL] missing reference: {item}")
        failures.extend(missing)

    print(f"SUMMARY: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
