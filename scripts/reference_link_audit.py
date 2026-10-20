#!/usr/bin/env python3
"""Check local file references and Markdown section anchors in the active package."""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

TOKEN_RE = re.compile(r'`([^`]+\.(?:md|json|py))`')
LINK_RE = re.compile(r'\[[^\]\n]*\]\(([^)\n]+)\)')
IGNORE_PREFIXES = ('[Target]', 'handoff_task', 'manifest', 'charts_manifest', 'source_ledger', 'product_images_manifest')

def candidates(root: Path, source: Path, token: str) -> list[Path]:
    if token.startswith(('http://', 'https://', 'mailto:', 'app://', 'codex://')):
        return []
    if token.startswith(('references/', 'scripts/', 'assets/', 'examples/', 'cold_storage/')):
        return [root / token]
    if token.endswith('.py'):
        return [root / 'scripts' / token, source.parent / token]
    return [source.parent / token, root / 'references' / token, root / token]

def slug(heading: str) -> str:
    heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading).strip().lower()
    return ''.join(c for c in heading if c in '-_ ' or unicodedata.category(c)[0] in 'LN').replace(' ', '-')

def anchors(text: str) -> set[str]:
    result = set(re.findall(r'<(?:a|h[1-6])\s+[^>]*id=[\"\x27]([^\"\x27]+)', text))
    counts, in_fence = {}, False
    for line in text.splitlines():
        if re.match(r'^\s*(?:```|~~~)', line):
            in_fence = not in_fence
            continue
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?$', line)
        if match and not in_fence:
            base = slug(match[1])
            count = counts.get(base, 0)
            result.add(base if count == 0 else f'{base}-{count}')
            counts[base] = count + 1
    return result

def audit(root: Path) -> tuple[list[str], int]:
    failures = []
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.md', '.json'}
             and 'cold_storage' not in p.parts]
    for source in files:
        text = source.read_text(encoding='utf-8', errors='replace')
        for token in TOKEN_RE.findall(text):
            token = token.strip()
            if token.startswith(IGNORE_PREFIXES) or any(x in token for x in ('<', '>', '*', '–', '—')):
                continue
            paths = candidates(root, source, token)
            if paths and not any(path.exists() for path in paths):
                failures.append(f'{source.relative_to(root)} -> {token}')
        for raw in LINK_RE.findall(text):
            token = unquote(raw.strip().strip('<>'))
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', token):
                continue
            local, _, anchor = token.partition('#')
            paths = candidates(root, source, local) if local else [source]
            target = next((p for p in paths if p.exists()), None)
            if target is None:
                failures.append(f'{source.relative_to(root)} -> {token}')
            elif anchor and target.suffix.lower() == '.md' and anchor not in anchors(target.read_text(encoding='utf-8')):
                failures.append(f'{source.relative_to(root)} -> missing anchor {token}')
    load_map = json.loads((root / 'references/task_load_map.json').read_text(encoding='utf-8'))
    refs = [load_map.get('entrypoint', '../SKILL.md'), *load_map.get('shared', [])]
    for config in load_map['tasks'].values():
        refs.extend(ref for value in config.values() if isinstance(value, list) for ref in value)
        refs.extend(ref for value in config.get('conditional', {}).values() for ref in value)
    for ref in refs:
        path = (root / 'references' / ref).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            failures.append(f'task_load_map -> {ref}')
    return sorted(set(failures)), len(files)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    failures, count = audit(Path(args.root).resolve())
    for failure in failures:
        print(f'[FAIL] {failure}')
    print(f'SUMMARY: {len(failures)} missing file/anchor reference(s)' if failures
          else f'PASS: checked {count} active markdown/JSON files and section anchors')
    return int(bool(failures))

if __name__ == '__main__':
    raise SystemExit(main())
