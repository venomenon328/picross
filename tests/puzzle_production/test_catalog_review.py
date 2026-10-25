"""SD-C-R01/C1 R1 regressions, using only generated synthetic packages."""
from copy import deepcopy
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import catalog_analysis as ca, catalog_rating as rating
from tools.puzzle_production import content_registry as cr
from tools.puzzle_production.content_update import update
from tools.puzzle_production.authoring_package import file_hash
from tools.puzzle_production.contract import InvalidInput, canonical_bytes, digest, load_json, write_json
from tools.puzzle_production.target_adapter import export
from tools.puzzle_production.za1_fixtures import make, seal, approve, isolated_checkout, difficulty_for_export


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class ReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = isolated_checkout(self.home / 'checkout')

    def exported(self, mode, revision):
        package = make(self.home / f'{mode}-{revision}', 'pz-review', 4, 3, mode, colors=1)
        handoff = load_json(package / 'handoff.json')
        handoff['revision'] = f'r{revision}'
        seal(package, handoff)
        approval = self.home / f'approval-{revision}.json'
        approve(package, approval)
        result = self.home / f'export-{revision}'
        export(package, result, name='TEST ONLY', revision=revision, stem='review', save_slot='review',
               approval_path=approval, category_id='voegel', categories_path=self.root / 'content/categories.json')
        return result

    def register(self):
        exported = self.exported('mono', 1)
        checked = difficulty_for_export(exported)
        cr.registration(exported, self.root, apply=True, difficulty=checked)
        return exported, checked

    def test_r1_01_mode_change_cannot_rebind_active_rating(self):
        for old_mode, new_mode in (('mono', 'color'), ('color', 'mono')):
            self.setUp()
            with self.subTest(old=old_mode, new=new_mode):
                first = self.exported(old_mode, 1)
                checked = difficulty_for_export(first)
                cr.registration(first, self.root, apply=True, difficulty=checked)
                second = self.exported(new_mode, 2)
                old = self.root / 'game/data/content/review.json'
                new = second / load_json(second / 'manifest.json')['definition']
                self.assertEqual(rating.definition(old.read_bytes())[3], rating.definition(new.read_bytes())[3])
                before = snapshot(self.root)
                for apply in (False, True):
                    for kwargs in ({'rebind_difficulty': True}, {'difficulty': checked, 'rebind_difficulty': True},
                                   {'difficulty': checked}):
                        with self.subTest(kwargs=kwargs, apply=apply), self.assertRaisesRegex(InvalidInput, 'mode|Modus'):
                            update(second, self.root, file_hash(old), apply=apply, **kwargs)
                        self.assertEqual(snapshot(self.root), before)
                for value in (checked, rating.checked_from_active(load_json(self.root / rating.path('pz-review')))):
                    with self.assertRaisesRegex(InvalidInput, 'mode'):
                        rating.rebind_checked(value, new.read_bytes(), production_mode=new_mode)
                fresh = difficulty_for_export(second)
                self.assertEqual(fresh['production_mode'], new_mode)
                with patch('tools.puzzle_production.analysis_io.check_bundle', side_effect=AssertionError('hidden replay')):
                    update(second, self.root, file_hash(old), apply=True, difficulty=fresh)
                    cr.check_checkout(self.root)
                self.assertEqual(load_json(self.root / rating.path('pz-review'))['production_mode'], new_mode)

    def test_r1_02_orphan_is_not_missing_with_legacy_fallback(self):
        self.register()
        source = self.root / rating.path('pz-review')
        target = self.root / rating.path('pz-typo')
        target.parent.mkdir(parents=True)
        source.rename(target)
        before = snapshot(self.root)
        with self.assertRaisesRegex(InvalidInput, 'difficulty|Difficulty|Sidecar'):
            cr.sync_runtime(self.root)
        self.assertEqual(snapshot(self.root), before)

    def test_r1_03_repeated_adoption_after_category_sync_is_stale(self):
        _, checked = self.register()
        work = self.home / 'preview'
        ca.preview(self.root, work, 'review', 'a' * 40, ids=['pz-review'], checked_inputs={'pz-review': checked})
        ca.adopt(self.root, work, apply=True)
        categories = load_json(self.root / 'content/categories.json')
        categories['categories'][0]['name'] += ' changed'
        write_json(self.root / 'content/categories.json', categories)
        cr.sync_runtime(self.root)
        before = snapshot(self.root)
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaisesRegex(InvalidInput, 'changed|Stale'):
                ca.adopt(self.root, work, apply=apply)
            self.assertEqual(snapshot(self.root), before)

    def test_namespace_rejects_misplaced_and_unknown_sources_at_every_entry(self):
        exported, checked = self.register()
        work = self.home / 'preview'
        ca.preview(self.root, work, 'review', 'a' * 40, ids=['pz-review'], checked_inputs={'pz-review': checked})
        original = (self.root / rating.path('pz-review')).read_bytes()
        for name in ('pz-unknown/rating.json', 'pz-review/nested/rating.json', 'rating.json',
                     'pz-review/Rating.json', 'PZ-review/rating.json', 'reports/valid/rating.json'):
            # Isolate each alias, also on case-insensitive Windows filesystems.
            checkout = self.home / ('case-' + str(len(list(self.home.glob('case-*')))))
            shutil.copytree(self.root, checkout)
            (checkout / rating.path('pz-review')).unlink()
            (checkout / rating.path('pz-review')).parent.rmdir()
            target = checkout / 'content/difficulty' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
            before = snapshot(checkout)
            for operation in (lambda: cr.check_checkout(checkout), lambda: cr.sync_runtime(checkout),
                              lambda: cr.registration(exported, checkout, apply=True, difficulty=checked),
                              lambda: update(exported, checkout, checked['current_source']['definition_sha256'], apply=True),
                              lambda: ca.adopt(checkout, work, apply=True)):
                with self.subTest(path=name), self.assertRaises(InvalidInput): operation()
                self.assertEqual(snapshot(checkout), before)

    def test_orphan_appearing_during_transaction_blocks_recovery_and_keeps_bytes(self):
        exported, _ = self.register()
        (self.root / rating.path('pz-review')).unlink()
        cr.sync_runtime(self.root)
        work = self.home / 'preview'
        ca.preview(self.root, work, 'review', 'a' * 40, ids=['pz-review'])
        with self.assertRaises(InterruptedError):
            ca.adopt(self.root, work, apply=True, fail_step='crash-runtime')
        orphan = self.root / rating.path('pz-foreign')
        orphan.parent.mkdir(parents=True)
        orphan.write_bytes(b'foreign bytes')
        before = snapshot(self.root)
        with self.assertRaisesRegex(InvalidInput, 'Unregistered difficulty'):
            cr.recover(self.root)
        self.assertEqual(snapshot(self.root), before)
        orphan.unlink()
        cr.recover(self.root)
        cr.check_checkout(self.root)

    def test_real_repeat_is_read_only_after_changed_projection_and_with_reports(self):
        _, checked = self.register()
        (self.root / rating.path('pz-review')).unlink()
        cr.sync_runtime(self.root)
        before_runtime = (self.root / cr.RUNTIME).read_bytes()
        work = self.home / 'preview'
        ca.preview(self.root, work, 'review', 'a' * 40, ids=['pz-review'], checked_inputs={'pz-review': checked})
        ca.adopt(self.root, work, apply=True)
        self.assertNotEqual(before_runtime, (self.root / cr.RUNTIME).read_bytes())
        before = snapshot(self.root)
        for apply in (False, True):
            self.assertEqual(ca.adopt(self.root, work, apply=apply)['status'], 'no-op')
            self.assertEqual(snapshot(self.root), before)
        cr.check_checkout(self.root)  # Durable reports are not active sidecars.
        # Same projection, different valid rating provenance is still stale.
        active_path = self.root / rating.path('pz-review')
        active = load_json(active_path)
        active['rating_revision'] += 1
        active['adoption']['report'] = None
        active['record_hash'] = digest({k: v for k, v in active.items() if k != 'record_hash'})
        write_json(active_path, active)
        cr.check_checkout(self.root)
        foreign = snapshot(self.root)
        for apply in (False, True):
            with self.assertRaisesRegex(InvalidInput, 'changed'):
                ca.adopt(self.root, work, apply=apply)
            self.assertEqual(snapshot(self.root), foreign)

    def test_context_is_explicit_and_legacy_cannot_acquire_a_mode_by_rebind(self):
        _, checked = self.register()
        raw = (self.root / 'game/data/content/review.json').read_bytes()
        legacy = deepcopy(checked)
        legacy['format'] = rating.LEGACY_CHECKED
        legacy.pop('production_mode')
        legacy['checked_hash'] = digest({k: v for k, v in legacy.items() if k != 'checked_hash'})
        rating.validate(legacy, active=False, definition_bytes=raw)
        for mode in ('mono', 'color'):
            with self.assertRaisesRegex(InvalidInput, 'mode'):
                rating.rebind_checked(legacy, raw, production_mode=mode)
        active = rating.active_record(legacy)
        write_json(self.root / rating.path('pz-review'), active)
        cr.check_checkout(self.root)
        self.assertEqual(rating.checked_from_active(active), legacy)
        source = self.home / 'source.json'
        source.write_bytes(raw)
        bundle = self.home / 'bundle'
        current = ca.analyze_single(source, bundle, production_mode='mono')
        self.assertEqual(rating.import_bundle(source, bundle), current)
        (bundle / 'catalog-context.json').unlink()
        old_import = rating.import_bundle(source, bundle)
        self.assertEqual(old_import['format'], rating.LEGACY_CHECKED)
        with self.assertRaisesRegex(InvalidInput, 'mode'):
            rating.rebind_checked(old_import, raw, production_mode='color')

    def test_repeated_adoption_after_valid_registry_sync_is_stale(self):
        _, checked = self.register()
        work = self.home / 'preview'
        ca.preview(self.root, work, 'review', 'a' * 40, ids=['pz-review'], checked_inputs={'pz-review': checked})
        ca.adopt(self.root, work, apply=True)
        registry = load_json(self.root / cr.REGISTRY)
        registry['entries'][0]['visible'] = False
        write_json(self.root / cr.REGISTRY, registry)
        cr.sync_runtime(self.root)
        cr.check_checkout(self.root)
        before = snapshot(self.root)
        for apply in (False, True):
            with self.assertRaisesRegex(InvalidInput, 'changed'):
                ca.adopt(self.root, work, apply=apply)
            self.assertEqual(snapshot(self.root), before)

    def test_standalone_cli_requires_mode_and_rejects_switch_before_output(self):
        _, checked = self.register()
        source = self.root / 'game/data/content/review.json'
        checked_path = self.home / 'checked.json'
        write_json(checked_path, checked)
        output = self.home / 'rebound.json'
        args = [sys.executable, '-m', 'tools.puzzle_production.catalog_analysis', 'rebind',
                '--input', str(source), '--rating', str(checked_path), '--output', str(output)]
        for extra in ([], ['--production-mode', 'color']):
            result = subprocess.run(args + extra, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(output.exists())
        result = subprocess.run(args + ['--production-mode', 'mono'], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(load_json(output), checked)

    def test_legacy_report_adoption_and_recovery_keep_exact_old_schema(self):
        _, checked = self.register()
        (self.root / rating.path('pz-review')).unlink()
        cr.sync_runtime(self.root)
        runtime = load_json(self.root / cr.RUNTIME)
        runtime['format'] = 'picross-runtime-registry-v4'
        write_json(self.root / cr.RUNTIME, runtime)
        work = self.home / 'legacy-preview'
        report = ca.preview(self.root, work, 'legacy', 'a' * 40, ids=['pz-review'], checked_inputs={'pz-review': checked})
        report['format'] = ca.LEGACY_FORMAT
        report['result'].pop('sources')
        report['result'].pop('method')
        for row in report['result']['entries']:
            row.pop('previous_rating_revision'); row.pop('assessment')
        report['result_hash'] = digest(report['result'])
        write_json(work / 'report.json', report)
        (work / 'report.md').write_bytes(ca.markdown(report).encode())
        before = snapshot(self.root)
        with self.assertRaises(InterruptedError):
            ca.adopt(self.root, work, apply=True, fail_step='crash-runtime')
        cr.recover(self.root)
        self.assertEqual(snapshot(self.root), before)
        ca.adopt(self.root, work, apply=True)
        after = snapshot(self.root)
        for apply in (False, True):
            self.assertEqual(ca.adopt(self.root, work, apply=apply)['status'], 'no-op')
            self.assertEqual(snapshot(self.root), after)

    def test_namespace_rejects_links_without_following_them(self):
        outside = self.home / 'foreign'
        outside.mkdir()
        (outside / 'rating.json').write_bytes(b'foreign bytes')
        link = self.root / 'content/difficulty/pz-foreign'
        link.parent.mkdir(parents=True)
        try:
            os.symlink(outside, link, target_is_directory=True)
        except OSError as exc:
            self.skipTest('Host cannot create a directory symlink: ' + str(exc))
        with self.assertRaisesRegex(InvalidInput, 'Unsafe'):
            cr.check_checkout(self.root)
        self.assertEqual((outside / 'rating.json').read_bytes(), b'foreign bytes')
