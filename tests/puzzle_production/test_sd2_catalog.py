"""SD2-C fixed synthetic integration cases; no real catalog reads or analyses."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production import test_catalog_integration as fixtures
from tools.puzzle_production import catalog_analysis as ca, catalog_rating as rating
from tools.puzzle_production import catalog_method as method, sd2_catalog_rating as sd2
from tools.puzzle_production import catalog_transaction as tx, catalog_publication as publication
from tools.puzzle_production import content_registry as cr, catalog_difficulty as display
from tools.puzzle_production.contract import Aborted, InvalidInput, canonical_bytes, digest, load_json, write_json
from tools.puzzle_production.sd2_contract import AnalysisBudget
from tools.puzzle_production.za1_fixtures import isolated_checkout, FIXTURES, ROOT


def stamps(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def seal(value, key):
    value.pop(key, None)
    return rating.hashed(value, key)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.CatalogTests.setUpClass.__func__(cls)
        # Most cases assert metadata/transaction behavior, not production replay.
        # Keep an immutable full source solely for the actual retirement case.
        cls.full_base = cls.home / 'full-base'
        shutil.copytree(cls.base, cls.full_base)
        from tests.puzzle_production.catalog_fixtures import compact
        compact(cls.base, [cls.identifier])
        cls.sd2_checked = ca.analyze_single(cls.base / cls.definition, cls.home / 'sd2-analysis',
            production_mode='mono', method=method.NEW)

    tearDownClass = classmethod(fixtures.CatalogTests.tearDownClass.__func__)
    setUp = fixtures.CatalogTests.setUp

    def preview(self, checked=None, run='sd2-test', selected=method.NEW):
        return ca.preview(self.checkout, self.root / run, run, 'c' * 40, ids=[self.identifier],
            checked_inputs={self.identifier: checked or self.sd2_checked}, method=selected)

    def activate(self, root=None, target=method.NEW):
        root = root or self.checkout
        old = method.current(method.load(root))['method']
        value = method.plan(root, old, target, method.method_hash(target))
        method.adopt(root, value)
        return value

    def test_checked_import_is_closed_and_keeps_frozen_result(self):
        value = self.sd2_checked
        self.assertEqual(value['format'], sd2.CHECKED)
        report = load_json(self.home / 'sd2-analysis/rating/rating.json')
        self.assertEqual(value['rating']['result'], report['result'])
        self.assertEqual(set(rating.project(value)), {'method', 'level', 'assessment_type', 'confidence', 'plausible_range', 'r4_required'})
        self.assertEqual(value['logic_binding']['matrix_hash'], self.checked['logic_binding']['matrix_hash'])
        self.assertNotEqual(value['logic_binding']['analysis_hash'], self.checked['logic_binding']['analysis_hash'])
        self.assertNotIn('trajectory', str(value))
        bundle = self.root / 'bundle'; shutil.copytree(self.home / 'sd2-analysis', bundle)
        for name in ('foreign.json', 'rating/context.json', 'rating/analysis/context.json'):
            path = bundle / name; path.write_bytes(b'{}\n')
            with self.subTest(name=name), self.assertRaises(ValueError):
                rating.import_bundle(self.checkout / self.definition, bundle)
            path.unlink()
        context = load_json(bundle / 'catalog-context.json')
        context['method'] = method.OLD
        write_json(bundle / 'catalog-context.json', seal(context, 'context_hash'))
        with self.assertRaises(ValueError): rating.import_bundle(self.checkout / self.definition, bundle)

    def test_nested_negative_data_and_old_envelopes_are_closed(self):
        for change in (
            lambda v: v.update(format=rating.CHECKED),
            lambda v: v.update(production_mode='color', unexpected=True),
            lambda v: v['compact_analysis'].update(line_analysis_complete=1),
            lambda v: v['compact_analysis'].update(new_singletons=0),
            lambda v: v['logic_binding'].update(analysis_hash='0' * 64),
            lambda v: v['rating'].update(method=method.OLD),
            lambda v: v['rating']['result']['assessment'].update(level=True),
            lambda v: v['rating']['result']['assessment'].update(score=[1, 1]),
            lambda v: v['rating']['result']['assessment']['signals'].update(raw_workload=[1, 4]),
            lambda v: v['rating']['result']['assessment']['boundaries'].update(distance_upper=[99, 1]),
            lambda v: v['rating']['source'].update(definition_id='pz-other'),
            lambda v: v['tool'].update(version=1),
        ):
            value = deepcopy(self.sd2_checked); change(value)
            value['rating'] = seal(value['rating'], 'rating_hash')
            value = seal(value, 'checked_hash')
            with self.subTest(change=change), self.assertRaises(ValueError):
                rating.validate(value, active=False, definition_bytes=(self.checkout / self.definition).read_bytes())
        old = deepcopy(self.checked); old['format'] = sd2.CHECKED; old = seal(old, 'checked_hash')
        with self.assertRaises(ValueError): rating.validate(old, active=False)

    def test_preview_adoption_mixed_history_noop_bytes_and_timestamps(self):
        before = fixtures.snapshot(self.checkout)
        report = self.preview()
        self.assertEqual(report['format'], ca.FORMAT)
        self.assertEqual(report['result']['entries'][0]['old']['method'], method.OLD)
        self.assertEqual(report['result']['entries'][0]['proposed']['method'], method.NEW)
        self.assertIn(method.PATH, report['result']['sources'])
        self.assertEqual(fixtures.snapshot(self.checkout), before)
        ca.adopt(self.checkout, self.root / 'sd2-test', apply=True)
        active = load_json(self.checkout / self.rating_path)
        self.assertEqual(active['rating_revision'], 2)
        self.assertEqual(active['rating'], self.sd2_checked['rating'])
        self.assertEqual(method.current(method.load(self.checkout))['method'], method.OLD)
        self.assertEqual(load_json(self.checkout / cr.RUNTIME)['format'], 'picross-runtime-registry-v5')
        for name, raw in before.items():
            if name not in (cr.RUNTIME, self.rating_path): self.assertEqual((self.checkout / name).read_bytes(), raw, name)
        stable = stamps(self.checkout)
        with patch.object(ca, 'analyze_single', side_effect=AssertionError('implicit analysis')), \
                patch('tools.puzzle_production.sd2_rating_io.check_rating_bundle', side_effect=AssertionError('implicit replay')):
            self.assertEqual(ca.adopt(self.checkout, self.root / 'sd2-test', apply=True)['status'], 'no-op')
            self.assertEqual(cr.registration(self.exported, self.checkout, apply=True)['status'], 'no-op')
            cr.sync_runtime(self.checkout); cr.check_checkout(self.checkout)
        self.assertEqual(stamps(self.checkout), stable)

    def test_rebind_retains_analysis_and_rejects_mode_matrix_and_identity(self):
        value = load_json(self.checkout / self.definition)
        value['revision'] += 1; value['reveal']['name'] = 'Synthetic metadata change'
        raw = canonical_bytes(value) + b'\n'
        rebound = rating.rebind_checked(self.sd2_checked, raw, production_mode='mono')
        self.assertEqual(rebound['rating'], self.sd2_checked['rating'])
        self.assertEqual(rebound['compact_analysis'], self.sd2_checked['compact_analysis'])
        self.assertEqual(rebound['current_source']['runtime_revision'], 2)
        self.assertNotEqual(rebound['checked_hash'], self.sd2_checked['checked_hash'])
        with self.assertRaisesRegex(ValueError, 'mode'): rating.rebind_checked(self.sd2_checked, raw, production_mode='color')
        with self.assertRaisesRegex(ValueError, 'Stale'): rating.validate(self.sd2_checked, active=False, definition_bytes=raw)
        value['id'] = value['reveal']['definition_id'] = 'pz-another'
        with self.assertRaises(ValueError): rating.rebind_checked(self.sd2_checked, canonical_bytes(value), production_mode='mono')
        # One foreground colour remains explicitly colour production, not inferred mono.
        color = ca.analyze_single(self.checkout / self.definition, self.root / 'color-one', production_mode='color', method=method.NEW)
        self.assertEqual(color['production_mode'], 'color')
        with self.assertRaises(ValueError): rating.validate(color, active=False, production_mode='mono')

    def test_aborted_attempt_preserves_active_rating_and_records_reason(self):
        checked = ca.analyze_single(self.checkout / self.definition, self.root / 'aborted',
            production_mode='mono', method=method.NEW, budget=AnalysisBudget(max_waves=0))
        self.assertEqual(checked['rating']['result']['status'], 'unrated')
        before = (self.checkout / self.rating_path).read_bytes()
        report = self.preview(checked)
        self.assertEqual(report['result']['entries'][0]['status'], 'unrated')
        self.assertTrue(report['result']['entries'][0]['reason'])
        ca.adopt(self.checkout, self.root / 'sd2-test', apply=True)
        self.assertEqual((self.checkout / self.rating_path).read_bytes(), before)
        with self.assertRaises(ValueError): rating.active_record(checked)

    def test_activation_is_explicit_stale_safe_and_exact_repeat(self):
        before = stamps(self.checkout)
        value = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        self.assertEqual(stamps(self.checkout), before)
        with self.assertRaises(ValueError): method.plan(self.checkout, method.NEW, method.OLD, method.method_hash(method.OLD))
        with self.assertRaises(ValueError): method.plan(self.checkout, method.OLD, method.NEW, '0' * 64)
        method.adopt(self.checkout, value)
        after = stamps(self.checkout)
        self.assertEqual({n: v for n, v in after.items() if n != method.PATH}, before)
        self.assertEqual(method.adopt(self.checkout, value)['status'], 'no-op')
        self.assertEqual(stamps(self.checkout), after)
        record = load_json(self.checkout / method.PATH)
        record['revision'] += 1
        record['previous_record_hash'] = value['expected']['record_hash'] or 'a' * 64
        write_json(self.checkout / method.PATH, seal(record, 'record_hash'))
        invalid = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): method.adopt(self.checkout, value)
        self.assertEqual(fixtures.snapshot(self.checkout), invalid)

    def test_active_method_controls_new_registration_but_not_historical_values(self):
        empty = isolated_checkout(self.root / 'new')
        before = fixtures.snapshot(empty)
        with self.assertRaisesRegex(ValueError, 'active production method'):
            cr.registration(self.exported, empty, apply=True, difficulty=self.sd2_checked)
        self.assertEqual(fixtures.snapshot(empty), before)
        self.activate(empty)
        with self.assertRaisesRegex(ValueError, 'active production method'):
            cr.registration(self.exported, empty, apply=True, difficulty=self.checked)
        plan = cr.registration(self.exported, empty, difficulty=self.sd2_checked)
        self.assertEqual(plan['status'], 'planned')
        cr.registration(self.exported, empty, apply=True, difficulty=self.sd2_checked)
        self.assertEqual(rating.project(load_json(empty / self.rating_path))['method'], method.NEW)
        stable = stamps(empty)
        self.assertEqual(cr.registration(self.exported, empty, apply=True)['status'], 'no-op')
        self.assertEqual(stamps(empty), stable)
        # Switching default alone never invalidates an existing 0.3 value.
        prior = (self.checkout / self.rating_path).read_bytes()
        self.activate(); cr.check_checkout(self.checkout)
        self.assertEqual((self.checkout / self.rating_path).read_bytes(), prior)

    def test_new_source_invalidates_preview_before_mutation_and_noop(self):
        self.preview()
        value = self.activate()
        before = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): ca.adopt(self.checkout, self.root / 'sd2-test', apply=True)
        self.assertEqual(fixtures.snapshot(self.checkout), before)
        self.preview(run='after-activation')
        ca.adopt(self.checkout, self.root / 'after-activation', apply=True)
        # An unrelated but valid category edit invalidates a repeated activation.
        catalog = load_json(self.checkout / 'content/categories.json')
        catalog['categories'][0]['name'] += ' synthetic'
        write_json(self.checkout / 'content/categories.json', catalog)
        cr.sync_runtime(self.checkout)
        before = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): method.adopt(self.checkout, value)
        with self.assertRaises(ValueError): ca.adopt(self.checkout, self.root / 'after-activation', apply=True)
        self.assertEqual(fixtures.snapshot(self.checkout), before)

    def test_adoption_and_activation_rollback_resume_and_foreign_guard(self):
        self.preview()
        before = fixtures.snapshot(self.checkout)
        with self.assertRaises(InterruptedError): ca.adopt(self.checkout, self.root / 'sd2-test', apply=True, fail_step='crash-runtime')
        journal = load_json(self.checkout / tx.LOCK)
        self.assertEqual(journal['format'], tx.FORMATS['adoption'])
        self.assertIn(method.PATH, journal['old'])
        def stop(phase, name=None):
            if phase == 'R1-runtime': raise InterruptedError('synthetic recovery interruption')
        with patch.object(publication, 'checkpoint', stop), self.assertRaises(InterruptedError): cr.recover(self.checkout)
        cr.recover(self.checkout)
        self.assertEqual(fixtures.snapshot(self.checkout), before)
        value = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        with self.assertRaises(InterruptedError): method.adopt(self.checkout, value, fail_step='crash-' + method.PATH)
        path = self.checkout / self.definition; original = path.read_bytes(); path.write_bytes(b'FOREIGN')
        foreign = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): cr.recover(self.checkout)
        self.assertEqual(fixtures.snapshot(self.checkout), foreign)
        path.write_bytes(original); cr.recover(self.checkout)
        self.assertEqual(fixtures.snapshot(self.checkout), before)

    def test_legacy_report_cannot_claim_sd2_and_old_recovery_stays_closed(self):
        report = self.preview()
        report['format'] = ca.AT_FORMAT; report['result'].pop('method')
        report['result_hash'] = digest(report['result'])
        with self.assertRaises(ValueError): ca.validate_report(report)
        snapshot = tx.capture(self.checkout)
        journal = tx.prepare(self.checkout, snapshot, {}, operation='sync')
        old = deepcopy(journal); old['format'] = tx.AT_FORMATS['sync']
        with self.assertRaises(ValueError): tx.validate_journal(self.checkout, old)
        # A genuine AT generation has no default target and v4 in both sides.
        registry = cr.check_checkout(self.checkout)
        raw = cr.projection(registry, load_json(self.checkout / 'content/categories.json'), self.checkout, version=4)
        write_json(self.checkout / cr.RUNTIME, raw)
        snapshot = tx.capture(self.checkout)
        old = tx.prepare(self.checkout, snapshot, {}, operation='sync', generation='at')
        tx.validate_journal(self.checkout, old, before_write=True)
        self.activate()
        before = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): tx.validate_journal(self.checkout, old)
        self.assertEqual(fixtures.snapshot(self.checkout), before)

    def test_cli_candidate_import_rebind_new_production_and_explicit_all_preview(self):
        import contextlib, io, json
        from tools.puzzle_production.authoring_package import open_package
        from tools.puzzle_production.target_adapter import inspect
        def cli(module, *args):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): code = module.main([str(a) for a in args])
            self.assertEqual(code, 0, output.getvalue())
            return json.loads(output.getvalue())
        with open_package(FIXTURES / 'direct-mono') as package:
            report, design, matrix, logic, _ = inspect(package)
        for name, value in (('design', design), ('matrix', matrix), ('logic', logic)):
            write_json(self.root / (name + '.json'), value)
        candidate = self.root / 'candidate.json'
        cli(ca, 'candidate', '--design', self.root/'design.json', '--matrix', self.root/'matrix.json',
            '--logic', self.root/'logic.json', '--puzzle-id', report['puzzle_id'], '--runtime-revision', 1, '--output', candidate)
        checked = self.root/'checked.json'; bundle = self.root/'cli-bundle'
        cli(ca, 'analyze', '--method', method.NEW, '--production-mode', 'mono', '--input', candidate,
            '--work-dir', bundle, '--output', checked)
        imported = self.root/'imported.json'
        cli(ca, 'import', '--input', candidate, '--bundle', bundle, '--output', imported)
        self.assertEqual(load_json(checked)['rating'], load_json(imported)['rating'])
        rebound = self.root/'rebound.json'
        cli(ca, 'rebind', '--input', self.checkout/self.definition, '--rating', imported,
            '--production-mode', 'mono', '--output', rebound)
        root = isolated_checkout(self.root/'cli-checkout'); activation = self.root/'activation.json'
        cli(method, 'plan', '--checkout', root, '--expected-method', method.OLD, '--target-method', method.NEW,
            '--target-method-hash', method.method_hash(method.NEW), '--output', activation)
        cli(method, 'adopt', '--checkout', root, '--plan', activation)
        self.assertEqual(cr.registration(self.exported, root, apply=True, difficulty=rebound)['status'], 'registered')
        work = self.root/'cli-preview'
        report = cli(ca, 'preview-checked', '--method', method.NEW, '--checkout', root, '--work-dir', work,
            '--run-id', 'cli-preview', '--source-commit', 'd'*40, '--all', '--checked', self.identifier, rebound)
        row = report['result']['entries'][0]
        self.assertEqual(row['assessment'], load_json(rebound)['rating']['result']['assessment'])
        self.assertIn(method.NEW + ' / L', (work/'report.md').read_text())
        before = stamps(root)
        cli(ca, 'plan-adoption', '--checkout', root, '--work-dir', work)
        self.assertEqual(stamps(root), before)
        cli(ca, 'adopt', '--checkout', root, '--work-dir', work)
        after = stamps(root)
        self.assertEqual(cli(ca, 'adopt', '--checkout', root, '--work-dir', work)['status'], 'no-op')
        self.assertEqual(stamps(root), after)

    def test_at_added_and_cleanup_preserve_mixed_authorities_without_analysis(self):
        from tests.puzzle_production import test_catalog_reveal as reveal_fixture
        from tools.puzzle_production import catalog_reveal as reveal, reveal_source, catalog_added, integrated_content
        shutil.copytree(self.full_base, self.checkout, dirs_exist_ok=True)
        # The same synthetic image request exercises the shared production path.
        self.request = lambda variant=1, append=None: reveal_fixture.RevealTests.request(self, variant, append)
        first = reveal_fixture.RevealTests.make_plan(self)
        reveal.adopt(self.checkout, first)
        before = fixtures.snapshot(self.checkout)
        self.preview(); ca.adopt(self.checkout, self.root/'sd2-test', apply=True)
        for name, raw in before.items():
            if name not in (cr.RUNTIME, self.rating_path): self.assertEqual((self.checkout/name).read_bytes(), raw, name)
        self.activate()
        second = reveal_fixture.RevealTests.make_plan(self, variant=2)
        rating_bytes = (self.checkout/self.rating_path).read_bytes()
        added_bytes = (self.checkout/catalog_added.path(self.identifier)).read_bytes()
        reveal.adopt(self.checkout, second); cr.sync_runtime(self.checkout)
        self.assertEqual((self.checkout/self.rating_path).read_bytes(), rating_bytes)
        self.assertEqual((self.checkout/catalog_added.path(self.identifier)).read_bytes(), added_bytes)
        write_json(self.checkout/'content/authoring/index.json', {'format':'picross-authoring-index-v1','entries':[]})
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.checkout), *args], stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q'); git('add', '.')
        git('-c','user.name=Synthetic SD2-C','-c','user.email=sd2-c@example.invalid','commit','-qm','synthetic integrated source')
        commit = git('rev-parse','HEAD'); git('update-ref','refs/remotes/origin/main',commit)
        authorities = {name:(self.checkout/name).read_bytes() for name in
                       (self.rating_path, catalog_added.path(self.identifier), reveal_source.path(self.identifier), method.PATH, cr.RUNTIME)}
        with patch.object(ca, 'analyze_single', side_effect=AssertionError('implicit analysis')), \
                patch('tools.puzzle_production.target_adapter.verify_export', side_effect=AssertionError('retirement replay')):
            integrated_content.retire(self.checkout, [self.identifier], commit)
            cr.check_checkout(self.checkout, replay=True); cr.sync_runtime(self.checkout)
        for name, raw in authorities.items(): self.assertEqual((self.checkout/name).read_bytes(), raw, name)
        self.assertEqual(cr.registration(self.exported, self.checkout, apply=True)['status'], 'no-op')

    def test_default_path_alias_invalid_data_and_work_output_are_fail_closed(self):
        from tools.puzzle_production import catalog_io
        before = fixtures.snapshot(self.checkout)
        with self.assertRaises(ValueError): ca.work_directory(self.checkout/method.PATH, self.checkout)
        alias = self.checkout/'content/Difficulty-Method.json'
        alias.write_bytes(b'{}\n')
        invalid = stamps(self.checkout)
        with self.assertRaises(ValueError): tx.capture(self.checkout)
        self.assertEqual(stamps(self.checkout), invalid); alias.unlink()
        for raw, error in ((b'{"format":1,"format":2}', ValueError), (b'NaN', ValueError),
                           (b' '*(method.LIMIT+1), Aborted), (b'{}', ValueError)):
            path = self.checkout/method.PATH; path.write_bytes(raw)
            invalid = stamps(self.checkout)
            for action in (lambda: cr.check_checkout(self.checkout),lambda: cr.sync_runtime(self.checkout),lambda: cr.registration(self.exported,self.checkout,apply=True)):
                with self.assertRaises(error): action()
                self.assertEqual(stamps(self.checkout), invalid)
            path.unlink()
        self.assertEqual(fixtures.snapshot(self.checkout), before)

    def test_added_history_adoption_binds_sd2_and_default(self):
        from tools.puzzle_production import catalog_added as added, catalog_added_history as history
        self.preview(); ca.adopt(self.checkout,self.root/'sd2-test',apply=True)
        (self.checkout/added.path(self.identifier)).unlink()
        cr.sync_runtime(self.checkout)
        self.activate()
        def git(*args):
            return subprocess.check_output(['git','-C',str(self.checkout),*args],stderr=subprocess.DEVNULL).decode().strip()
        git('init','-q'); git('add','.')
        git('-c','user.name=Synthetic SD2-C','-c','user.email=sd2-c@example.invalid','commit','-qm','synthetic visible catalog')
        value = history.plan(self.checkout,'sd2-added',git('rev-parse','HEAD'))
        self.assertEqual(value['format'],history.FORMAT)
        self.assertIn(method.PATH,value['sources'])
        path = self.root/'added-plan.json'; write_json(path,value)
        preserved = {n:(self.checkout/n).read_bytes() for n in (self.rating_path,method.PATH,self.definition)}
        history.adopt(self.checkout,path,apply=True)
        after = stamps(self.checkout)
        self.assertEqual(history.adopt(self.checkout,path,apply=True)['status'],'no-op')
        self.assertEqual(stamps(self.checkout),after)
        for name, raw in preserved.items(): self.assertEqual((self.checkout/name).read_bytes(),raw,name)
        self.assertEqual(load_json(self.checkout/cr.RUNTIME)['entries'][0]['added_at'],
                         load_json(self.checkout/added.path(self.identifier))['added_at'])


class UpdateTests(unittest.TestCase):
    from tests.puzzle_production import test_content_update as update_fixture
    setUpClass = classmethod(update_fixture.UpdateTests.setUpClass.__func__)
    setUp = update_fixture.UpdateTests.setUp
    make_export = update_fixture.UpdateTests.make_export
    snapshot = update_fixture.UpdateTests.snapshot

    def test_historical_metadata_rebind_then_new_logic_mixed_catalog_and_recovery(self):
        from tools.puzzle_production.content_update import update
        from tools.puzzle_production.authoring_package import file_hash
        from tools.puzzle_production import catalog_added
        value = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        method.adopt(self.checkout, value)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'complete 0.4'):
            update(self.second,self.checkout,self.expected,apply=True)
        with self.assertRaisesRegex(ValueError, 'Rebind changes'):
            update(self.second,self.checkout,self.expected,apply=True,rebind_difficulty=True)
        self.assertEqual(self.snapshot(), before)
        metadata = self.make_export('metadata','pz-test-update','r03',2,5)
        prior = load_json(self.checkout/rating.path('pz-test-update'))
        update(metadata,self.checkout,self.expected,apply=True,rebind_difficulty=True)
        rebound = load_json(self.checkout/rating.path('pz-test-update'))
        self.assertEqual(rebound['rating'],prior['rating'])
        changed = self.make_export('changed','pz-test-update','r04',3,8)
        manifest = load_json(changed/'manifest.json')
        checked = ca.analyze_single(changed/manifest['definition'],self.root/'changed-analysis',production_mode='color',method=method.NEW)
        expected = file_hash(self.checkout/self.definition)
        old_method = ca.analyze_single(changed/manifest['definition'],self.root/'changed-old',production_mode='color')
        with self.assertRaisesRegex(ValueError, 'active production method'):
            update(changed,self.checkout,expected,apply=True,difficulty=old_method)
        before = self.snapshot()
        with self.assertRaises(InterruptedError):
            update(changed,self.checkout,expected,apply=True,difficulty=checked,fail_step='crash-runtime')
        cr.recover(self.checkout); self.assertEqual(self.snapshot(), before)
        with patch.object(ca, 'analyze_single', side_effect=AssertionError('implicit analysis')):
            update(changed,self.checkout,expected,apply=True,difficulty=checked)
            cr.sync_runtime(self.checkout); cr.check_checkout(self.checkout)
        values = {e['id']: e['difficulty']['method'] for e in load_json(self.checkout/cr.RUNTIME)['entries']}
        self.assertEqual(values, {'pz-test-other':method.OLD,'pz-test-update':method.NEW})
        self.assertEqual((self.checkout/'saves/untouched.json').read_bytes(),before['saves/untouched.json'])
        for name, raw in before.items():
            if name.startswith(('content/added/','content/packages/')): self.assertEqual((self.checkout/name).read_bytes(),raw,name)


class ProjectionTests(unittest.TestCase):
    def test_old_sync_rejects_v5_but_retains_opaque_stale_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = isolated_checkout(Path(directory)/'checkout')
            cr.sync_runtime(root)
            snapshot = tx.capture(root)
            current = tx.prepare(root,snapshot,{},operation='sync')
            for formats in (tx.AT_FORMATS,tx.PREVIOUS_FORMATS,tx.LEGACY_FORMATS):
                old = deepcopy(current); old['format'] = formats['sync']
                for side in ('old','new'): old[side].pop(method.PATH)
                if formats != tx.AT_FORMATS: old.pop('replacements')
                old['new'][tx.RUNTIME] = tx.projection(old['new'],snapshot['registry'],version=3 if formats == tx.LEGACY_FORMATS else 4).decode()
                (root/tx.RUNTIME).write_text(old['old'][tx.RUNTIME],encoding='utf-8',newline='\n')
                with self.subTest(format=old['format']), self.assertRaisesRegex(ValueError,'runtime v5'):
                    tx.validate_journal(root,old,before_write=True)
                old['old'][tx.RUNTIME] = 'opaque stale projection\n'
                (root/tx.RUNTIME).write_bytes(old['old'][tx.RUNTIME].encode())
                tx.validate_journal(root,old,before_write=True)

    def test_oversized_definition_stops_before_analysis_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root/'oversized.json'
            source.write_bytes(b' ' * (2 * 1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                ca.analyze_single(source,root/'output',production_mode='mono',method=method.NEW)
            self.assertFalse((root/'output').exists())

    def test_required_r4_import_and_unproved_prefix_stay_distinct(self):
        from tests.puzzle_production.test_paired import MONO, wire
        from tools.puzzle_production.contract import Budget, validate_logic
        from tools.puzzle_production.solver import solve
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = load_json(Path(__file__).parent/'fixtures/sd-runtime.json')
            runtime['width'] = runtime['height'] = 4
            runtime['solution'] = [[int(v == 'ink') for v in row] for row in MONO]
            logic = wire(MONO)
            for name, clues in (('rows',logic['row_clues']),('columns',logic['column_clues'])):
                runtime[name] = [[{'length':c['length'],'color':1} for c in line] for line in clues]
            source = root/'source.json'; write_json(source,runtime)
            puzzle = rating.definition(source.read_bytes())[1]
            proof, baseline = root/'proof.json', root/'baseline.json'
            write_json(proof,solve(puzzle,profile='paired-lines-color'))
            write_json(baseline,solve(puzzle))
            checked = ca.analyze_single(source,root/'rated',production_mode='mono',method=method.NEW,proof=proof,baseline=baseline)
            self.assertTrue(rating.project(checked)['r4_required'])
            self.assertEqual(checked['rating']['result']['assessment']['level'],5)
            rating.validate(rating.active_record(checked),definition_bytes=source.read_bytes())
            write_json(baseline,solve(puzzle,Budget(max_lines=0)))
            incomplete = ca.analyze_single(source,root/'unproved',production_mode='mono',method=method.NEW,proof=proof,baseline=baseline)
            self.assertTrue(incomplete['compact_analysis']['deduction_complete'])
            self.assertEqual(incomplete['rating']['result']['reason'],'r4_necessity_unproven')
            with self.assertRaises(ValueError): rating.active_record(incomplete)
            stalled = ca.analyze_single(source,root/'stalled',production_mode='mono',method=method.NEW)
            self.assertEqual(stalled['rating']['result']['reason'],'incomplete_line')

    def test_exact_runtime_method_matrix_and_all_five_labels(self):
        for name in method.METHODS:
            for level in ('L1', 'L2', 'L3', 'L4', 'L5'):
                value = dict(method=name, level=level, assessment_type='instrumented', confidence='medium',
                             plausible_range=[level, level], r4_required=False)
                display.validate_projection(value, version=5)
                if name == method.NEW:
                    for version in (2, 3, 4):
                        with self.assertRaises(ValueError): display.validate_projection(value, version=version)
                for field, invalid in (('confidence', 'high'), ('r4_required', 1), ('score', [1, 1]), ('plausible_range', ['L1', 'L5'])):
                    altered = {**value, field: invalid}
                    with self.subTest(method=name, level=level, field=field), self.assertRaises(ValueError):
                        display.validate_projection(altered, version=5)
                value['r4_required'] = True
                if level == 'L5': display.validate_projection(value, version=5)
                else:
                    with self.assertRaises(ValueError): display.validate_projection(value, version=5)
        self.assertIsNone(display.validate_projection(None, version=5))
        for version in (1, 6, True, 5.0, '5'):
            with self.assertRaises(ValueError): display.validate_projection(None, version=version)

    def test_both_method_hashes_remain_pinned(self):
        self.assertEqual(method.method_hash(method.OLD), '8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79')
        self.assertEqual(method.method_hash(method.NEW), '5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf')


if __name__ == '__main__':
    unittest.main()
