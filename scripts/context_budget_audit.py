#!/usr/bin/env python3
"""Measure phase overhead and deduplicated reading paths (not live context occupancy)."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

CJK_RE = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
DEFAULT_LIMIT = 18000

def estimate_tokens(text: str) -> int:
    cjk = len(CJK_RE.findall(text))
    return round(cjk * 1.3 + (len(text) - cjk) * 0.25)

def resolve(root: Path, ref: str) -> Path:
    path = (root / 'references' / ref).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Reference escapes package: {ref}')
    return path

def refs_for_tasks(load_map: dict, tasks: list[str]) -> list[str]:
    return [ref for task in tasks for value in load_map['tasks'][task].values()
            if isinstance(value, list) for ref in value]

def condition_refs(load_map: dict, selector: str) -> list[str]:
    task, condition = selector.split('.', 1)
    return load_map['tasks'][task]['conditional'][condition]

def audit(root: Path, load_map: dict, phase_limit: int | None = None,
          conditions: list[str] | None = None, selected_route: str | None = None) -> dict:
    budgets = load_map.get('budgets', {})
    phase_limit = phase_limit if phase_limit is not None else budgets.get('phase_tokens', DEFAULT_LIMIT)
    task_limit, route_limit = budgets.get('task_tokens', 42000), budgets.get('route_tokens', 90000)
    overhead = [load_map.get('entrypoint', '../SKILL.md'), *load_map.get('shared', [])]
    errors, rows, cache = [], [], {}
    def paths(refs):
        result = set()
        for ref in refs:
            try:
                path = resolve(root, ref)
                if not path.is_file():
                    raise ValueError(f'Missing reference: {ref}')
                if path not in cache:
                    cache[path] = estimate_tokens(path.read_text(encoding='utf-8'))
                result.add(path)
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(str(exc))
        return result
    def row(label, refs, limit, previous=None):
        loaded = paths(refs)
        total = sum(cache[p] for p in loaded)
        rows.append({'path': label, 'tokens': total,
                     'new_tokens': sum(cache[p] for p in loaded - (previous or set())),
                     'files': len(loaded), 'limit': limit,
                     'status': 'PASS' if total <= limit else 'FAIL'})
        if total > limit:
            errors.append(f'{label}: {total} > {limit}')
        return loaded
    for task, config in load_map['tasks'].items():
        seen = paths(overhead)
        for phase, refs in config.items():
            if isinstance(refs, list):
                seen |= row(f'{task}.{phase}', overhead + refs, phase_limit, seen)
        task_refs = overhead + refs_for_tasks(load_map, [task])
        row(f'{task}.cumulative', task_refs, task_limit)
        all_conditions = []
        for condition, refs in config.get('conditional', {}).items():
            row(f'{task}.conditional.{condition}', task_refs + refs, task_limit, paths(task_refs))
            all_conditions.extend(refs)
        if all_conditions:
            row(f'{task}.all_conditions', task_refs + all_conditions, task_limit)
    for name, route in load_map.get('routes', {}).items():
        refs = overhead + refs_for_tasks(load_map, route['tasks'])
        for condition in route.get('conditions', []):
            refs += condition_refs(load_map, condition)
        row(f'route.{name}', refs, route.get('limit', route_limit))
    if conditions or selected_route:
        route = load_map.get('routes', {}).get(selected_route or 'full_report')
        if route is None:
            raise ValueError(f'Unknown route: {selected_route}')
        refs = overhead + refs_for_tasks(load_map, route['tasks'])
        for selector in [*route.get('conditions', []), *(conditions or [])]:
            if selector.split('.', 1)[0] not in route['tasks']:
                raise ValueError(f'Condition outside selected route: {selector}')
            refs += condition_refs(load_map, selector)
        row('selected_route', refs, route.get('limit', route_limit))
    return {'approximation': 'CJK 1.3; other 0.25 tokens/char; reading-path totals',
            'rows': rows, 'errors': sorted(set(errors))}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--limit', type=int, help='Override per-phase budget only')
    parser.add_argument('--route', help='Named route from task_load_map.json')
    parser.add_argument('--conditional', action='append', default=[], help='Opt-in task.condition; repeatable')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve()
        load_map = json.loads((root / 'references/task_load_map.json').read_text(encoding='utf-8'))
        result = audit(root, load_map, args.limit, args.conditional, args.route)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'[FAIL] {exc}\n')
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('Context budgets (approximate, deduplicated reading paths)')
        for r in result['rows']:
            print(f"[{r['status']}] {r['path']}: ~{r['tokens']:,} tokens; "
                  f"new ~{r['new_tokens']:,}; {r['files']} files; limit {r['limit']:,}")
        for error in result['errors']:
            print(f'[FAIL] {error}')
        print(f"SUMMARY: {len(result['errors'])} failure(s)")
    return int(bool(result['errors']))

if __name__ == '__main__':
    raise SystemExit(main())
