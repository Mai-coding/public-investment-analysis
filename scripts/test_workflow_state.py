#!/usr/bin/env python3
"""Behavior regressions for routing, anchors and recorded task-state eligibility."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import context_budget_audit as context
import handoff_audit as state
import reference_link_audit as links


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'references').mkdir()
        (self.root / 'SKILL.md').write_text('entry', encoding='utf-8')
        for name in ('shared.md', 'a.md', 'b.md', 'c.md'):
            (self.root / 'references' / name).write_text('中' * 10, encoding='utf-8')
        self.load_map = {
            'entrypoint': '../SKILL.md', 'shared': ['shared.md'],
            'budgets': {'phase_tokens': 100, 'task_tokens': 100, 'route_tokens': 100},
            'tasks': {'task1': {'bootstrap': ['a.md', 'a.md'], 'write': ['a.md'],
                                 'conditional': {'more': ['b.md'], 'also': ['c.md']}}},
            'routes': {'full_report': {'tasks': ['task1']}},
        }

    def test_overhead_alias_dedup_and_increment(self):
        self.load_map['tasks']['task1']['write'].append('./a.md')
        result = context.audit(self.root, self.load_map)
        rows = {r['path']: r for r in result['rows']}
        self.assertFalse(result['errors'])
        self.assertEqual(rows['task1.bootstrap']['tokens'], 27)
        self.assertEqual(rows['task1.bootstrap']['files'], 3)
        self.assertEqual(rows['task1.write']['new_tokens'], 0)
        self.assertEqual(rows['route.full_report']['tokens'], 27)

    def test_condition_combinations_fail_even_if_each_alone_fits(self):
        self.load_map['budgets']['task_tokens'] = 45
        result = context.audit(self.root, self.load_map)
        rows = {r['path']: r for r in result['rows']}
        self.assertEqual(rows['task1.conditional.more']['status'], 'PASS')
        self.assertEqual(rows['task1.all_conditions']['status'], 'FAIL')

    def test_route_overhead_and_missing_shared_reference(self):
        self.load_map['budgets']['route_tokens'] = 20
        self.load_map['shared'].append('missing.md')
        result = context.audit(self.root, self.load_map)
        self.assertTrue(any('Missing reference' in e for e in result['errors']))
        self.assertTrue(any('route.full_report' in e for e in result['errors']))
        with self.assertRaises(ValueError):
            context.resolve(self.root, '../../escape.md')

    def test_selected_route_rejects_unknown_or_unrelated_conditions(self):
        result = context.audit(self.root, self.load_map, conditions=['task1.more'])
        row = next(r for r in result['rows'] if r['path'] == 'selected_route')
        self.assertEqual(row['tokens'], 40)
        with self.assertRaises(KeyError):
            context.audit(self.root, self.load_map, conditions=['task1.unknown'])
        with self.assertRaises(ValueError):
            context.audit(self.root, self.load_map, selected_route='unknown')


class AnchorTests(unittest.TestCase):
    def test_duplicate_headings_chinese_and_code_fences(self):
        text = '# 五、全局影响矩阵\n## Repeat\n## Repeat\n```\n# Hidden\n```\n'
        self.assertEqual(links.anchors(text), {'五全局影响矩阵', 'repeat', 'repeat-1'})

    def test_existing_file_with_removed_heading_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'references').mkdir()
            (root / 'SKILL.md').write_text('[valid](references/owner.md#current)\n[old](references/owner.md#removed)', encoding='utf-8')
            (root / 'references/owner.md').write_text('# Current\n', encoding='utf-8')
            (root / 'references/task_load_map.json').write_text('{"tasks": {}}', encoding='utf-8')
            errors, _ = links.audit(root)
            self.assertEqual(len(errors), 1)
            self.assertIn('removed', errors[0])


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.schema = json.loads(state.SCHEMA_PATH.read_text(encoding='utf-8'))
        for name in ('research.md', 'model.xlsx', 'source.md', 'audit.log'):
            (self.root / name).write_text(name, encoding='utf-8')

    def record(self, name):
        return {'path': name, 'sha256': state.fingerprint(self.root / name)}

    def handoff(self, task=1, outputs=None, scope='staged'):
        outputs = outputs or ['research.md']
        data = {'schema_version': '2.0', 'analysis_id': 'analysis-A', 'target': 'Target',
                'task': task, 'mode': 'full_report', 'revision': 1, 'state': 'current',
                'execution_scope': scope, 'status': 'PASS', 'snapshot_date': '2026-10-19',
                'completed_at': '2026-10-19T09:00:00+08:00', 'outputs': outputs,
                'artifacts': [self.record(name) for name in outputs], 'inputs': [],
                'upstream_handoffs': [], 'key_decisions': [], 'open_gaps': [],
                'gate_results': [{'name': name, 'status': 'PASS', 'evidence_path': 'audit.log',
                                 'evidence_sha256': state.fingerprint(self.root / 'audit.log')}
                                for name in self.schema['x-required-gates'][str(task)]]}
        if scope == 'standalone':
            data['scope_reason'] = 'User requested this task using complete supplied inputs.'
        if task == 3:
            data['valuation_assessment'] = {
                'metric': 'P/E', 'base_year': 2027, 'terminal_year': 2032,
                'market_priced_band': 'Base+', 'evidence_supported_band': 'Base',
                'confidence': 'Medium', 'rationale': 'Evidence supports the base case.',
                'decisive_gaps': [], 'family_weights': {'forward_comps': 1.0, 'terminal': 0.0}}
        return data

    def save(self, data, filename=None, seal=True):
        if seal:
            for gate in data['gate_results']:
                if gate['status'] == 'PASS':
                    gate['checked_state_sha256'] = state.checked_state_digest(data)
        path = self.root / (filename or f'handoff_task{data["task"]}.json')
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def dependency(self, path, task, revision=1):
        return {'task': task, 'revision': revision, 'path': path.name, 'sha256': state.fingerprint(path)}

    def test_current_handoff_and_changed_input(self):
        data = self.handoff()
        data['inputs'] = [self.record('source.md')]
        path = self.save(data)
        self.assertEqual(state.audit(path), [])
        (self.root / 'source.md').write_text('updated source', encoding='utf-8')
        self.assertTrue(any('input changed' in e for e in state.audit(path)))

    def test_changed_output_or_audit_evidence(self):
        path = self.save(self.handoff())
        (self.root / 'research.md').write_text('new version', encoding='utf-8')
        self.assertTrue(any('output changed' in e for e in state.audit(path)))
        (self.root / 'audit.log').write_text('different run', encoding='utf-8')
        self.assertTrue(any('evidence changed' in e for e in state.audit(path)))

    def test_refreshing_file_hashes_does_not_refresh_old_gate_results(self):
        data = self.handoff()
        self.save(data)
        (self.root / 'research.md').write_text('edited report', encoding='utf-8')
        data['artifacts'] = [self.record('research.md')]
        errors = state.audit(self.save(data, seal=False))
        self.assertTrue(any('gate is stale' in e for e in errors))
        self.assertFalse(any('output changed' in e for e in errors))

    def test_upstream_revision_change_invalidates_previously_checked_state(self):
        first = self.save(self.handoff())
        data = self.handoff(2, ['model.xlsx'])
        data['upstream_handoffs'] = [self.dependency(first, 1)]
        self.save(data)
        revised = self.handoff()
        revised['revision'] = 2
        self.save(revised)
        data['upstream_handoffs'] = [self.dependency(first, 1, revision=2)]
        self.assertTrue(any('gate is stale' in e for e in state.audit(self.save(data, seal=False))))

    def test_stale_partial_missing_gate_and_legacy(self):
        for mutation in ('stale', 'partial', 'missing_gate', 'legacy', 'no_evidence'):
            data = self.handoff()
            if mutation == 'stale':
                data.update(state='stale', change_reason='new inputs', affected_artifacts=['research.md'])
            elif mutation == 'partial':
                data['status'] = 'PARTIAL'
            elif mutation == 'missing_gate':
                data['gate_results'].pop()
            elif mutation == 'legacy':
                del data['schema_version']
            else:
                del data['gate_results'][0]['evidence_sha256']
            with self.subTest(mutation=mutation):
                self.assertTrue(state.audit(self.save(data)))

    def test_upstream_identity_revision_and_hash(self):
        first = self.save(self.handoff())
        data = self.handoff(2, ['model.xlsx'])
        data['upstream_handoffs'] = [self.dependency(first, 1)]
        path = self.save(data)
        self.assertEqual(state.audit(path), [])
        data['upstream_handoffs'][0]['revision'] = 2
        self.assertTrue(any('revision mismatch' in e for e in state.audit(self.save(data))))
        data['upstream_handoffs'][0]['revision'] = 1
        data['mode'] = 'quick_memo'
        self.assertTrue(any('mode mismatch' in e for e in state.audit(self.save(data))))
        data['mode'] = 'full_report'
        self.save(data)
        first.write_text(first.read_text() + '\n', encoding='utf-8')
        self.assertTrue(any('upstream handoff changed' in e for e in state.audit(path)))

    def test_shared_workbook_is_superseded_only_by_a_valid_descendant(self):
        task1 = self.save(self.handoff())
        model = self.handoff(2, ['model.xlsx'])
        model['upstream_handoffs'] = [self.dependency(task1, 1)]
        task2 = self.save(model)
        self.assertEqual(state.audit(task2), [])
        (self.root / 'model.xlsx').write_text('operating model plus valuation', encoding='utf-8')
        valuation = self.handoff(3, ['model.xlsx'])
        valuation['upstream_handoffs'] = [self.dependency(task2, 2)]
        task3 = self.save(valuation)
        self.assertEqual(state.audit(task3), [])
        self.assertEqual(state.audit([task1, task2, task3]), [])
        self.assertTrue(state.audit(task2))
        (self.root / 'model.xlsx').write_text('unrecorded mutation', encoding='utf-8')
        self.assertTrue(any('output changed' in e for e in state.audit(task3)))

    def test_full_dependencies_and_standalone_scope(self):
        self.assertTrue(state.audit(self.save(self.handoff(2, ['model.xlsx']))))
        self.assertEqual(state.audit(self.save(self.handoff(2, ['model.xlsx'], 'standalone'))), [])
        data = self.handoff(2, ['model.xlsx'], 'standalone')
        del data['scope_reason']
        self.assertTrue(state.audit(self.save(data)))

    def test_cycles_fail_without_recursing_forever(self):
        data = self.handoff()
        path = self.save(data)
        data['upstream_handoffs'] = [self.dependency(path, 1)]
        self.assertTrue(any('cycle' in e for e in state.audit(self.save(data))))

    def test_cli_reports_current_and_changed_artifacts(self):
        path = self.save(self.handoff())
        command = [sys.executable, '-B', str(Path(state.__file__)), '--handoff', str(path)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.root / 'research.md').write_text('changed after checks', encoding='utf-8')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_unrelated_producers_cannot_supersede_each_other(self):
        first = self.save(self.handoff(), 'first.json')
        other = self.handoff(2, ['research.md'], 'standalone')
        second = self.save(other, 'second.json')
        self.assertTrue(any('unrelated producers' in e for e in state.audit([first, second])))

    def test_directory_digest_tracks_contents_and_names(self):
        folder = self.root / 'filings'
        folder.mkdir()
        (folder / 'one.txt').write_text('first', encoding='utf-8')
        initial = state.fingerprint(folder)
        self.assertEqual(initial, state.fingerprint(folder))
        (folder / 'one.txt').rename(folder / 'two.txt')
        self.assertNotEqual(initial, state.fingerprint(folder))
        renamed = state.fingerprint(folder)
        (folder / 'two.txt').write_text('changed', encoding='utf-8')
        self.assertNotEqual(renamed, state.fingerprint(folder))

    def test_schema_does_not_ignore_new_constraints(self):
        schema = copy.deepcopy(self.schema)
        schema['properties']['revision']['multipleOf'] = 2
        with self.assertRaises(ValueError):
            state.check_schema(schema)
        data = self.handoff()
        data['task'] = True
        self.assertTrue(state.schema_errors(data, self.schema, self.schema))


if __name__ == '__main__':
    unittest.main()
