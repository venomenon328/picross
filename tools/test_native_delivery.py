"""Small synthetic failure deliveries; no engine, render or historical replay."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from native_contract import GROUPS
from native_delivery import stage
from native_results import bind_files, digest, read, validate_all, validate_payload


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n', encoding='utf-8')


class Delivery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'output'
        self.technical = self.output / 'technical'
        self.destination = self.root / 'delivery'
        self.identity = dict(source_commit='a'*40, tested_checkout_commit='b'*40,
                             base_commit='c'*40, github_run_id='123', github_run_attempt='1')
        self.result = dict(format='picross-native-result-v1', identity=self.identity,
                           status='failure', groups=list(GROUPS), results=[])
        for group in GROUPS:
            self.result['results'].append(dict(group=group, status='success', exit_code=0))
            write(self.technical / group / 'product-report.json', dict(
                status='success', checks=[], selected_evidence=dict(files=[])))
            log = self.technical / (group + '-process.log')
            log.write_text(group + ' process output\n', encoding='utf-8')

    def deliver(self, outcome='failure'):
        self.result['files'] = bind_files(self.technical, exclude={'native-result.json'})
        write(self.technical / 'native-result.json', self.result)
        return stage(self.output, self.destination, outcome, self.identity)

    def mark_failed(self, group='graphics', phase='current-drawing-pixel-oracles'):
        row = next(r for r in self.result['results'] if r['group'] == group)
        row.update(status='failure', exit_code=1)
        directory = self.technical / group
        # Nomination follows the oracle's actual input; no screenshot name list.
        write(directory / 'product-report.json', dict(status='failure', checks=[
            dict(name=phase, status='failure', timed_out=True)], selected_evidence=dict(files=[
                dict(file='case/actual.png', failure_priority=True),
                dict(file='case/earlier.png', failure_priority=False)])))
        for name in ('actual.png', 'earlier.png'):
            path = directory / 'selected/case' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic original ' + name.encode())
        path = directory / 'logs' / (phase + '.log')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('original timeout / oracle error\n', encoding='utf-8')

    def test_failed_oracle_keeps_actual_inputs_logs_and_six_success_statuses_only(self):
        self.mark_failed()
        self.result['files'] = bind_files(self.technical, exclude={'native-result.json'})
        write(self.technical / 'native-result.json', self.result)
        before = bind_files(self.technical)
        result = self.deliver()
        self.assertFalse(result['accepted'])
        self.assertEqual(len(result['groups']), 7)
        self.assertEqual([r['group'] for r in result['groups'] if r['diagnostics']], ['graphics'])
        names = {r['file'] for r in bind_files(self.destination)}
        self.assertIn('graphics/selected/case/actual.png', names)
        self.assertNotIn('graphics/selected/case/earlier.png', names)
        self.assertIn('graphics/logs/current-drawing-pixel-oracles.log', names)
        self.assertFalse(any(n.startswith('catalog/') or n == 'catalog-process.log' for n in names))
        self.assertEqual(bind_files(self.technical), before)  # No source cleanup/mutation.
        self.assertEqual((self.destination/'native-result.json').read_bytes(),
                         (self.technical/'native-result.json').read_bytes())
        with self.assertRaises(ValueError):
            validate_payload(read(self.destination/'native-result.json'), self.destination)

    def test_two_independent_failures_are_both_delivered(self):
        self.mark_failed('graphics'); self.mark_failed('catalog', 'kat2-at')
        result = self.deliver()
        self.assertEqual([r['group'] for r in result['groups'] if r['diagnostics']], ['catalog','graphics'])
        for group in ('catalog', 'graphics'):
            self.assertTrue((self.destination/group/'selected/case/actual.png').is_file())

    def test_success_stages_exact_original_payload_without_diagnostic_wrapper(self):
        self.result['status'] = 'success'
        self.deliver('success')
        self.assertEqual(bind_files(self.technical), bind_files(self.destination))
        self.assertFalse((self.destination/'diagnostics.json').exists())

    def test_staged_success_passes_existing_independent_gate_and_mutation_fails(self):
        from test_ci_c import NativeGate
        fixture = NativeGate()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.check()
        output = self.root/'valid-output'
        shutil.copytree(fixture.root, output/'technical')
        stage(output, self.destination, 'success', fixture.result['identity'])
        summary = validate_all(fixture.plan, self.destination, None, dict(product_attempt='2'), '3')
        self.assertEqual(summary['groups'], ['core'])
        original = self.destination/'core/product-report.json'
        original.write_bytes(b'forged')
        with self.assertRaises(ValueError):
            validate_all(fixture.plan, self.destination, None, dict(product_attempt='2'), '3')

    def test_early_missing_report_import_or_kill_is_diagnostic_only(self):
        for label in ('import', 'kill', 'no-report'):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp:
                output = Path(temp)/'output'; tech = output/'technical'
                (tech/'core/logs').mkdir(parents=True)
                (tech/'core-process.log').write_text('killed', encoding='utf-8')
                (tech/'core/logs/import.log').write_text('partial import', encoding='utf-8')
                result = stage(output, Path(temp)/'delivery', 'failure', self.identity)
                self.assertFalse(result['accepted'])
                self.assertTrue((Path(temp)/'delivery/core/logs/import.log').is_file())
                self.assertFalse((Path(temp)/'delivery/native-result.json').exists())

    def test_interrupted_before_retention_recovers_report_bound_phase_original(self):
        self.mark_failed(phase='current-drawing-capture')
        raw = self.output/'groups/graphics/drawing-renders'
        write(raw/'zs2-after.json', dict(images=['unusual.png']))
        (raw/'unusual.png').write_bytes(b'original frame')
        self.deliver()
        self.assertEqual((self.destination/'graphics/selected/drawing-renders/unusual.png').read_bytes(),
                         b'original frame')

    def test_live_raw_tree_does_not_expand_existing_oracle_nomination(self):
        self.mark_failed()
        report_path = self.technical/'graphics/product-report.json'
        report = read(report_path)
        report['selected_evidence']['files'] = [dict(file='drawing-renders/actual.png', failure_priority=True)]
        write(report_path, report)
        write(self.output/'groups/graphics/drawing-renders/zs2-after.json',
              dict(captures=['actual.png', 'unrelated.png']))
        for name in ('actual.png', 'unrelated.png'):
            path = self.output/'groups/graphics/drawing-renders'/name
            path.write_bytes(name.encode())
        # The actual oracle input survives even if its retained copy was lost.
        self.deliver()
        self.assertTrue((self.destination/'graphics/selected/drawing-renders/actual.png').is_file())
        self.assertFalse((self.destination/'graphics/selected/drawing-renders/unrelated.png').exists())

    def test_missing_partial_report_still_retains_actual_failure_capture(self):
        self.mark_failed()
        (self.technical/'graphics/product-report.json').unlink()
        raw = self.output/'groups/graphics/renders'
        raw.mkdir(parents=True)
        (raw/'failure-actual.png').write_bytes(b'last native error frame')
        result = self.deliver()
        self.assertFalse(result['accepted'])
        self.assertTrue((self.destination/'graphics/selected/renders/failure-actual.png').is_file())

    def test_validation_failure_retains_affected_originals_even_after_aliasing(self):
        self.mark_failed('graphics')
        self.result['results'][-2].update(status='success', exit_code=0)
        self.result.update(validation_group='graphics', validation_error='original pixel mismatch',
                           image_aliases=[dict(file='graphics/selected/case/aliased.png',
                                               source='catalog/selected/shared.png')])
        write(self.technical/'catalog/selected/shared.png', {'original': True})
        original = self.technical/'catalog/selected/shared.png'
        self.result['image_aliases'][0].update(bytes=original.stat().st_size, sha256=digest(original))
        self.deliver()
        self.assertTrue((self.destination/'graphics/selected/case/earlier.png').is_file())
        self.assertTrue((self.destination/'graphics/selected/case/aliased.png').is_file())
        self.assertFalse((self.destination/'catalog/product-report.json').exists())

    def test_wrong_identity_is_not_reused_and_cannot_be_staged_as_success(self):
        for field in ('source_commit','base_commit','tested_checkout_commit','github_run_id','github_run_attempt'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                changed = deepcopy(self.result); changed['identity'] = dict(self.identity, **{field:'wrong'})
                write(Path(temp)/'technical/native-result.json', changed)
                result = stage(Path(temp), Path(temp)/'delivery', 'failure', self.identity)
                self.assertTrue(result['issues'])
                self.assertFalse((Path(temp)/'delivery/native-result.json').exists())
        with self.assertRaises(ValueError): self.deliver('success')

    def test_missing_and_traversing_oracle_originals_are_reported_not_substituted(self):
        self.mark_failed()
        path = self.technical/'graphics/product-report.json'
        report = read(path)
        report['selected_evidence']['files'] += [dict(file='../escape.png', failure_priority=True),
                                                dict(file='missing.png', failure_priority=True)]
        write(path, report)
        result = self.deliver()
        self.assertTrue(any('Unsafe' in s for s in result['issues']))
        self.assertTrue(any('Missing' in s for s in result['issues']))
        self.assertFalse(result['accepted'])

    def test_linked_oracle_file_is_not_followed(self):
        self.mark_failed()
        path = self.technical/'graphics/selected/case/actual.png'
        path.unlink()
        outside = self.root/'foreign.png'
        outside.write_bytes(b'foreign original')
        try:
            os.symlink(outside, path)
        except OSError:
            self.skipTest('Host does not permit creating symlinks')
        result = self.deliver()
        self.assertTrue(result['issues'])
        self.assertFalse((self.destination/'graphics/selected/case/actual.png').exists())

    def test_workflow_stages_only_upload_source_and_retains_real_retention(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root/'.github/workflows/p1-product.yml').read_text(encoding='utf-8')
        self.assertIn('--outcome "$NATIVE_OUTCOME"', workflow)
        self.assertIn('path: ${{ runner.temp }}/p1-product-delivery/', workflow)
        self.assertNotIn('path: ${{ runner.temp }}/p1-product-output/technical/', workflow)
        self.assertNotIn('continue-on-error', workflow)
        for filename in ('p1-product.yml','delivery.yml','web-chromium.yml','puzzle-production.yml','ci-chromium.yml'):
            source = (root/'.github/workflows'/filename).read_text(encoding='utf-8')
            for block in source.split('uses: actions/upload-artifact@')[1:]:
                block = block.split('      - name:')[0]
                player = any('name: '+name in block for name in
                             ('picross-p1-player-', 'picross-delivery-player-', 'picross-web-player-'))
                self.assertIn('retention-days: '+('14' if player else '7'), block)


if __name__ == '__main__':
    unittest.main()
