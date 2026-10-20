#!/usr/bin/env python3
"""Validate handoff shape, evidence, dependency revisions and current artifact bytes.

Uses only the standard library. The schema walker supports the handoff schema's
explicit keyword subset and rejects unknown validation keywords rather than
silently ignoring additions. It is not a general-purpose JSON Schema library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'references/handoff_schema.json'
SUPPORTED = {'$schema', '$ref', '$defs', 'title', 'description', 'type', 'required', 'properties',
             'items', 'minItems', 'minLength', 'pattern', 'minimum', 'maximum', 'enum', 'const',
             'allOf', 'if', 'then', 'x-required-gates', 'x-upstream-tasks'}


def check_schema(schema: dict) -> None:
    unknown = schema.keys() - SUPPORTED
    if unknown:
        raise ValueError(f'Unsupported handoff schema keywords: {sorted(unknown)}')
    for keyword in ('properties', '$defs'):
        for child in schema.get(keyword, {}).values():
            check_schema(child)
    for keyword in ('items', 'if', 'then'):
        if keyword in schema:
            check_schema(schema[keyword])
    for child in schema.get('allOf', []):
        check_schema(child)


def schema_errors(value, schema: dict, root: dict, at: str = '$') -> list[str]:
    errors = []
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/$defs/'):
            return [f'{at}: unsupported schema reference {ref}']
        errors += schema_errors(value, root['$defs'][ref.split('/')[-1]], root, at)
    def is_type(kind):
        return {'object': isinstance(value, dict), 'array': isinstance(value, list),
                'string': isinstance(value, str), 'integer': type(value) is int,
                'number': type(value) in (int, float), 'null': value is None,
                'boolean': type(value) is bool}[kind]
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    if types and not any(is_type(kind) for kind in types):
        return [f'{at}: expected {types}']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{at}: not in enum')
    if 'const' in schema and (value != schema['const'] or
                             isinstance(value, bool) != isinstance(schema['const'], bool)):
        errors.append(f'{at}: must equal {schema["const"]!r}')
    if isinstance(value, dict):
        errors += [f'{at}: missing {key}' for key in schema.get('required', []) if key not in value]
        for key, child in schema.get('properties', {}).items():
            if key in value:
                errors += schema_errors(value[key], child, root, f'{at}.{key}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{at}: too few items')
        for index, item in enumerate(value):
            errors += schema_errors(item, schema.get('items', {}), root, f'{at}[{index}]')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{at}: string too short')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{at}: invalid pattern')
    if type(value) in (int, float):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{at}: below minimum')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{at}: above maximum')
    for child in schema.get('allOf', []):
        errors += schema_errors(value, child, root, at)
    if 'if' in schema and not schema_errors(value, schema['if'], root, at):
        errors += schema_errors(value, schema.get('then', {}), root, at)
    return errors


def fingerprint(path: Path) -> str:
    """Hash files, or sorted relative filenames plus file hashes in a directory."""
    if path.is_symlink():
        raise ValueError(f'Symlink cannot be fingerprinted: {path}')
    if path.is_file():
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        return digest.hexdigest()
    if path.is_dir():
        entries = sorted(path.rglob('*'), key=lambda p: p.relative_to(path).as_posix())
        if any(p.is_symlink() for p in entries):
            raise ValueError(f'Directory contains a symlink: {path}')
        digest = hashlib.sha256(b'public-investment-analysis-directory-v1\0')
        for item in entries:
            if item.is_file():
                digest.update(item.relative_to(path).as_posix().encode('utf-8') + b'\0')
                digest.update(bytes.fromhex(fingerprint(item)))
        return digest.hexdigest()
    raise ValueError(f'Missing artifact: {path}')


def checked_state_digest(data: dict) -> str:
    """Bind a recorded gate to the artifacts and dependency versions it checked."""
    state = {key: data[key] for key in ('analysis_id', 'task', 'mode', 'execution_scope')}
    for key in ('artifacts', 'inputs', 'upstream_handoffs'):
        state[key] = sorted(data[key], key=lambda item: json.dumps(item, sort_keys=True))
    payload = json.dumps(state, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def audit(handoff: Path | list[Path], schema_path: Path = SCHEMA_PATH) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    check_schema(schema)
    errors, nodes, edges, active = [], {}, {}, set()

    def fail(path, message):
        errors.append(f'{path.name}: {message}')

    def local(path, value):
        return (path.parent / value).resolve()

    def verify(path, record, label):
        try:
            actual = fingerprint(local(path, record['path']))
            if actual != record['sha256']:
                fail(path, f'{label} changed: {record["path"]}')
        except (OSError, ValueError) as exc:
            fail(path, f'{label}: {exc}')

    def collect(path):
        if path in active:
            fail(path, 'dependency cycle')
            return
        if path in nodes:
            return
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            fail(path, f'cannot read handoff: {exc}')
            return
        issues = schema_errors(data, schema, schema)
        if issues:
            for issue in issues:
                fail(path, issue)
            return
        nodes[path], edges[path] = data, []
        active.add(path)
        if data['status'] != 'PASS' or data['state'] != 'current':
            fail(path, 'handoff is not PASS/current; rerun affected checks')
        try:
            datetime.fromisoformat(data['completed_at'].replace('Z', '+00:00'))
            if data['snapshot_date'] is not None:
                date.fromisoformat(data['snapshot_date'])
        except ValueError:
            fail(path, 'invalid completion or snapshot date')
        seen_tasks = set()
        for ref in data['upstream_handoffs']:
            upstream = local(path, ref['path'])
            verify(path, ref, 'upstream handoff')
            if ref['task'] in seen_tasks:
                fail(path, 'duplicate upstream task')
            seen_tasks.add(ref['task'])
            if ref['task'] >= data['task']:
                fail(path, 'upstream task must precede this task')
            edges[path].append(upstream)
            collect(upstream)
            if upstream in nodes:
                prior = nodes[upstream]
                for key in ('analysis_id', 'mode', 'target'):
                    if prior[key] != data[key]:
                        fail(path, f'upstream {key} mismatch')
                if prior['task'] != ref['task'] or prior['revision'] != ref['revision']:
                    fail(path, 'upstream task/revision mismatch')
        if data['mode'] == 'full_report' and data['execution_scope'] == 'staged':
            required = set(schema['x-upstream-tasks'].get(str(data['task']), []))
            if not required <= seen_tasks:
                fail(path, f'missing upstream tasks: {sorted(required - seen_tasks)}')
        active.remove(path)

    for root_handoff in ([handoff] if isinstance(handoff, Path) else handoff):
        collect(root_handoff.resolve())

    def reaches(child, ancestor, visited=None):
        visited = set() if visited is None else visited
        if child in visited:
            return False
        visited.add(child)
        return ancestor in edges.get(child, []) or any(reaches(p, ancestor, visited) for p in edges.get(child, []))

    producers = {}
    for path, data in nodes.items():
        artifact_paths = [local(path, r['path']) for r in data['artifacts']]
        if len(set(artifact_paths)) != len(artifact_paths):
            fail(path, 'duplicate artifact path')
        if {local(path, p) for p in data['outputs']} != set(artifact_paths):
            fail(path, 'outputs and artifact fingerprints must cover the same paths')
        for record in data['artifacts']:
            producers.setdefault(local(path, record['path']), []).append((path, record))
        for record in data['inputs']:
            verify(path, record, 'input')
        gates = {g['name']: g for g in data['gate_results']}
        if len(gates) != len(data['gate_results']):
            fail(path, 'duplicate gate name')
        required = set(schema['x-required-gates'][str(data['task'])]) if data['mode'] == 'full_report' else set()
        if not required <= gates.keys():
            fail(path, f'missing gates: {sorted(required - gates.keys())}')
        for name, gate in gates.items():
            if gate['status'] == 'PASS':
                if gate.get('checked_state_sha256') != checked_state_digest(data):
                    fail(path, f'{name}: gate is stale for this artifact/input/upstream state')
                if not gate.get('evidence_path') or not gate.get('evidence_sha256'):
                    fail(path, f'{name}: PASS needs fingerprinted evidence')
                else:
                    verify(path, {'path': gate['evidence_path'], 'sha256': gate['evidence_sha256']}, f'{name} evidence')
            elif gate['status'] != 'NOT_APPLICABLE' or name in required or not gate.get('evidence'):
                fail(path, f'{name}: required check did not pass or lacks applicability reason')

    # The existing Task 2 -> Task 3 shared workbook is a legitimate version chain.
    # Only a descendant producer can supersede a previous output at that exact path.
    for artifact, owners in producers.items():
        latest = [(owner, record) for owner, record in owners
                  if all(owner == other or reaches(owner, other) for other, _ in owners)]
        if len(latest) != 1:
            errors.append(f'{artifact}: unrelated producers; cannot determine current version')
        else:
            verify(latest[0][0], latest[0][1], 'output')
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--handoff', type=Path, action='append', help='Repeat to validate upstreams together')
    group.add_argument('--fingerprint', type=Path, help='Print a fingerprint record for actual bytes')
    group.add_argument('--state-digest', type=Path, help='Print the current checked-state digest for a draft handoff')
    args = parser.parse_args()
    try:
        if args.fingerprint:
            print(json.dumps({'path': str(args.fingerprint), 'sha256': fingerprint(args.fingerprint)}, ensure_ascii=False))
            return 0
        if args.state_digest:
            print(checked_state_digest(json.loads(args.state_digest.read_text(encoding='utf-8'))))
            return 0
        errors = audit(args.handoff)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'[FAIL] {exc}\n')
    for error in errors:
        print(f'[FAIL] {error}')
    print(f'SUMMARY: {len(errors)} failure(s)' if errors else 'PASS: handoff, upstream chain, artifacts and gate evidence are current')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
