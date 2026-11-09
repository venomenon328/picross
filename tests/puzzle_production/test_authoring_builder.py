"""Small synthetic PB-A boundaries; no catalog puzzles or persistent archives."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.puzzle_production import authoring_builder as builder
from tools.puzzle_production import authoring_build_contract as bc
from tools.puzzle_production.authoring_package import file_hash, open_package
from tools.puzzle_production.contract import Aborted, load_json, write_json
from tools.puzzle_production.za1_fixtures import make, FIXTURES
from tools.puzzle_production.target_adapter import inspect


class AuthoringBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pb-a-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / 'source', self.root / 'output'
        self.source.mkdir()
        self.output.mkdir()
        self.h = {'format': 'picross-authoring-handoff-v2', 'puzzle_id': 'pz-builder-test', 'revision': 'r01',
                  'repo_commit': 'd65ffa78008b117bc4e2530b91d5f6821d3f9a00', 'state': 'brief_ready',
                  'inventory': None, 'brief': 'brief.txt', 'approved_parameters': [],
                  'reveal': None, 'motif': None, 'candidate': None, 'repair': None,
                  'gates': {'reveal_approval': 'pending', 'motif': 'pending', 'final_editorial': 'pending',
                            'target_export': 'blocked'}, 'blockers': [], 'test_only': True,
                  'next_action': 'Produce reveal options under the actual owner brief.',
                  'authorization': 'TEST ONLY synthetic development input'}
        (self.source / 'brief.txt').write_text('TEST ONLY synthetic brief.\n', encoding='utf-8')
        self.rulebook()
        self.request = {'format': bc.FORMAT, 'handoff': self.h, 'document_revision': 37, 'files': [],
                        'target': 'local', 'category_id': None, 'reveal_options': [], 'external': {}}
        self.refresh()

    def rulebook(self):
        (self.source / 'rulebook.md').write_text('**Version 0.6.0 · Dokumentrevision 37 · 09.11.2026**\nTEST ONLY.\n', encoding='utf-8')
        self.h['rulebook'] = {'version': '0.6.0', 'file': 'rulebook.md', 'sha256': file_hash(self.source / 'rulebook.md')}

    def refresh(self):
        self.request['files'] = [{'path': p.relative_to(self.source).as_posix(),
                                 'source': p.relative_to(self.source).as_posix(), 'sha256': file_hash(p), 'bytes': p.stat().st_size}
                                for p in sorted(self.source.rglob('*')) if p.is_file()]

    def run_build(self):
        return builder.build(self.request, self.source, self.output,
                             getattr(self, 'checkout', None))

    def image(self, name='a'):
        from PIL import Image
        target = self.source / (name + '.png')
        Image.new('RGBA', (4, 4), '#234567ff').save(target)
        write_json(self.source / (name + '.provenance.json'), {
            'puzzle_id': self.h['puzzle_id'], 'file': target.name, 'sha256': file_hash(target),
            'author': 'TEST ONLY', 'usage_basis': 'Repository-owned synthetic pixels'})
        return {'file': target.name, 'sha256': file_hash(target), 'approval': None}

    def approval(self, image, kind):
        image['approval'] = kind + '-approval.json'
        value = {'type': 'human_' + kind + '_approval', 'file': image['file'], 'sha256': image['sha256'],
                 'revision': 'synthetic-1', 'actor': 'TEST ONLY', 'timestamp_utc': '2026-11-09T00:00:00Z',
                 'statement': 'Synthetic test statement, not human approval.', 'evidence': 'brief.txt'}
        if kind == 'motif':
            value['derived_from_reveal_sha256'] = image['derived_from_reveal_sha256']
        write_json(self.source / image['approval'], value)

    def content(self, repaired=False):
        # Fixture generation creates its own sealed baseline. Extract its draft
        # in this explicitly synthetic producer setup, before invoking builder.
        make(self.source, 'pz-builder-test', 3 if repaired else 2, 3 if repaired else 2, 'mono', repaired=repaired)
        self.h = load_json(self.source / 'handoff.json')
        for name in ('handoff.json', 'inventory.json'):
            (self.source / name).unlink()
        self.h.update(inventory=None, authorization='Synthetic PB-A test only',
                      next_action='Obtain the separate final human decision.', blockers=[])
        self.rulebook()
        self.request['handoff'] = self.h
        self.refresh()

    def repository(self):
        self.checkout = self.root / 'checkout'
        self.checkout.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.checkout)], check=True, capture_output=True)
        path = self.checkout / builder.INDEX
        path.parent.mkdir(parents=True)
        write_json(path, {'format': 'picross-authoring-index-v1', 'entries': []})
        self.request['target'] = 'repository'

    def test_early_phase_has_no_adapter_or_fabricated_approvals(self):
        self.h['state'] = 'reveal_review'
        for name in ('a', 'b', 'c'):
            image = self.image(name)
            self.request['reveal_options'].append({'ID': name, 'Beschreibung': 'Synthetic ' + name,
                                                   'Datei': image['file'], 'SHA-256': image['sha256']})
        self.refresh()
        with patch('tools.puzzle_production.target_adapter.inspect', side_effect=AssertionError('early adapter call')):
            result = self.run_build()
        record = result['record']
        self.assertFalse(record['verification']['technical'])
        self.assertIsNone(record['final_editorial_approval'])
        self.assertIsNone(result['sheet']['Quellbranch / Commit'])
        self.assertEqual(len(result['sheet']['Abschlussbild-Optionen']), 3)
        self.assertEqual(record['state'], result['sheet']['Produktionsstatus'])
        target = Path(result['directory'])
        with zipfile.ZipFile(target / 'package.zip') as archive:
            self.assertEqual(archive.read('handoff.json'), (target / 'handoff.json').read_bytes())
            inv = json.loads(archive.read('inventory.json'))
            self.assertEqual(set(archive.namelist()), {f['path'] for f in inv['files']} | {'handoff.json', 'inventory.json'})
            self.assertNotIn('candidate', inv['files'])

    def test_written_content_zip_is_inspected_and_final_approval_stays_open(self):
        self.content()
        original = builder.inspect_zip
        paths = []
        def observed(path, external, state, deadline):
            paths.append(path)
            self.assertTrue(path.is_file())
            self.assertEqual(path.suffix, '.zip')
            return original(path, external, state, deadline)
        with patch.object(builder, 'inspect_zip', observed):
            result = self.run_build()
        self.assertEqual(len(paths), 1)
        self.assertTrue(result['record']['verification']['technical'])
        self.assertFalse(result['record']['verification']['editorial_approved'])
        self.assertIn('final_editorial: missing bound human final approval', result['record']['blockers'])
        self.assertEqual(result['record']['width'], 2)

    def test_complete_repair_bundle_and_all_parents_survive(self):
        self.content(repaired=True)
        result = self.run_build()
        with zipfile.ZipFile(Path(result['directory']) / 'package.zip') as archive:
            manifest = json.loads(archive.read('production/repair/repair.json'))
            for name in manifest['files']:
                self.assertIn('production/repair/' + name, archive.namelist())
            self.assertIn('production/import/area-proof.json', archive.namelist())

    def test_identical_rebuild_is_byte_and_mtime_noop(self):
        first = self.run_build()
        directory = Path(first['directory'])
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in directory.iterdir()}
        second = self.run_build()
        self.assertEqual(second['status'], 'reused')
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in directory.iterdir()})
        self.assertIsNone(self.h['inventory'])  # API did not mutate caller input.

    def test_content_rebuild_excludes_volatile_inspection_times(self):
        self.content()
        first = self.run_build()
        second = self.run_build()
        self.assertEqual(first['files'], second['files'])
        self.assertEqual(second['status'], 'reused')

    def test_missing_source_and_wrong_hash_are_errors(self):
        for change in ('missing', 'hash', 'bytes'):
            with self.subTest(change=change):
                r = deepcopy(self.request)
                if change == 'missing':
                    r['files'][0]['source'] = 'missing.txt'
                elif change == 'hash':
                    r['files'][0]['sha256'] = '0' * 64
                else:
                    r['files'][0]['bytes'] += 1
                with self.assertRaises(builder.BuildError):
                    builder.build(r, self.source, self.output)
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())

    def test_manifest_missing_or_tampered_member_is_error(self):
        self.content()
        original = deepcopy(self.request['files'])
        self.request['files'] = [f for f in original if f['path'] != 'production/import/index.html']
        with self.assertRaisesRegex(builder.BuildError, 'Missing'):
            self.run_build()
        (self.source / 'production/import/index.html').write_text('tampered', encoding='utf-8')
        self.refresh()
        with self.assertRaisesRegex(builder.BuildError, 'hash mismatch'):
            self.run_build()

    def test_invalid_proof_with_rebound_manifest_is_not_content_ready(self):
        self.content()
        path = self.source / 'production/import/area-proof.json'
        proof = load_json(path)
        proof['logic_hash'] = '0' * 64
        write_json(path, proof)
        manifest_path = path.parent / 'manifest.json'
        manifest = load_json(manifest_path)
        manifest['files'][path.name] = file_hash(path)
        write_json(manifest_path, manifest)
        self.refresh()
        with self.assertRaises(ValueError):
            self.run_build()
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())

    def test_unsafe_paths_aliases_and_file_directory_collisions(self):
        for name in ('../escape', '/escape', 'C:/escape', 'a\\b', 'CON.txt', 'x.', 'x/a:stream'):
            with self.subTest(name=name):
                r = deepcopy(self.request)
                r['files'][0]['path'] = name
                with self.assertRaises(builder.BuildError):
                    builder.build(r, self.source, self.output)
        for additions in (('A/x', 'a/y'), ('a', 'a/b'), ('x', 'X')):
            r = deepcopy(self.request)
            r['files'] = [{**r['files'][0], 'path': name} for name in additions]
            with self.assertRaises(builder.BuildError):
                builder.build(r, self.source, self.output)

    def test_link_input_is_rejected(self):
        # Hardlinks work without symlink privileges on Windows and are also forbidden.
        os.link(self.source / 'brief.txt', self.source / 'alias.txt')
        self.refresh()
        with self.assertRaisesRegex(builder.BuildError, 'hardlink'):
            self.run_build()

    def test_source_change_before_publication_is_detected(self):
        def inject(name):
            if name == 'before-publication':
                (self.source / 'brief.txt').write_text('changed source', encoding='utf-8')
        with patch.object(builder, 'checkpoint', inject), self.assertRaisesRegex(builder.BuildError, 'changed'):
            self.run_build()
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())
        self.assertFalse(list(self.output.rglob('.pb-a-build-*')))

    def test_revision_collision_preserves_existing_bytes(self):
        result = self.run_build()
        before = (Path(result['directory']) / 'package.zip').read_bytes()
        self.h['authorization'] = 'Changed plan with identical source files'
        with self.assertRaisesRegex(builder.BuildError, 'collision'):
            self.run_build()
        self.assertEqual(before, (Path(result['directory']) / 'package.zip').read_bytes())

    def test_even_empty_foreign_revision_is_not_replaced(self):
        target = self.output / 'pz-builder-test/r01'
        target.mkdir(parents=True)
        with self.assertRaisesRegex(builder.BuildError, 'collision'):
            self.run_build()
        self.assertEqual(list(target.iterdir()), [])

    def test_repository_index_and_record_agree(self):
        self.repository()
        result = self.run_build()
        row = load_json(self.checkout / builder.INDEX)['entries'][0]
        record = load_json(self.checkout / row['record'])
        self.assertEqual(record, result['record'])
        self.assertEqual(record['package']['sha256'], file_hash(self.checkout / record['package']['file']))
        before = (self.checkout / builder.INDEX).stat().st_mtime_ns
        self.assertEqual(self.run_build()['status'], 'reused')
        self.assertEqual(before, (self.checkout / builder.INDEX).stat().st_mtime_ns)

    def test_abort_after_revision_can_resume_without_partial_index(self):
        self.repository()
        def inject(name):
            if name == 'revision-published':
                raise Aborted('Synthetic publication interruption')
        with patch.object(builder, 'checkpoint', inject), self.assertRaises(builder.BuildError) as caught:
            self.run_build()
        self.assertTrue(caught.exception.aborted)
        self.assertTrue(Path(caught.exception.remaining).is_dir())
        self.assertEqual(load_json(self.checkout / builder.INDEX)['entries'], [])
        self.assertEqual(self.run_build()['status'], 'reused')
        self.assertEqual(len(load_json(self.checkout / builder.INDEX)['entries']), 1)

    def test_concurrent_index_is_preserved_and_explicit_retry_is_safe(self):
        self.repository()
        other = {'puzzle_id': 'pz-other', 'revision': 'r01', 'record': 'content/authoring/pz-other/r01/record.json'}
        def inject(name):
            if name == 'before-index-replace':
                write_json(self.checkout / builder.INDEX, {'format': 'picross-authoring-index-v1', 'entries': [other]})
        with patch.object(builder, 'checkpoint', inject), self.assertRaisesRegex(builder.BuildError, 'Concurrent index') as caught:
            self.run_build()
        self.assertIsNotNone(caught.exception.remaining)
        self.assertEqual(load_json(self.checkout / builder.INDEX)['entries'], [other])
        self.run_build()
        self.assertEqual(load_json(self.checkout / builder.INDEX)['entries'][0], other)

    def test_writer_lock_blocks_a_second_writer(self):
        lock = self.output / '.authoring-builder.lock'
        with builder.writer(lock), self.assertRaisesRegex(builder.BuildError, 'writer'):
            self.run_build()

    def test_bad_written_zip_is_rejected_before_publication(self):
        def inject(name):
            if name == 'zip-written':
                path = next(self.output.rglob('package.zip'))
                path.write_bytes(b'broken ZIP')
        with patch.object(builder, 'checkpoint', inject), self.assertRaises(builder.BuildError):
            self.run_build()
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())

    def test_unknown_technical_data_and_sealed_input_are_rejected(self):
        self.h['background'] = {'state': 'none'}
        with self.assertRaisesRegex(builder.BuildError, 'Unknown handoff'):
            self.run_build()
        del self.h['background']
        write_json(self.source / 'future.json', {'format': 'picross-background-v99', 'file': 'missing.png'})
        self.refresh()
        with self.assertRaisesRegex(builder.BuildError, 'Unsupported declared'):
            self.run_build()
        (self.source / 'future.json').unlink()
        write_json(self.source / 'handoff.json', self.h)
        with self.assertRaisesRegex(builder.BuildError, 'Sealed source'):
            self.run_build()

    def test_snapshot_revision_and_request_types_are_checked(self):
        for change in ('snapshot', 'bool', 'field'):
            r = deepcopy(self.request)
            if change == 'snapshot': r['document_revision'] = 38
            elif change == 'bool': r['files'][0]['bytes'] = True
            else: r['future'] = None
            with self.assertRaises(builder.BuildError):
                builder.build(r, self.source, self.output)

    def test_changed_snapshot_hash_and_false_early_pass_are_rejected(self):
        self.h['rulebook']['sha256'] = '0' * 64
        with self.assertRaises(builder.BuildError):
            self.run_build()
        self.rulebook()
        self.h['gates']['reveal_approval'] = 'pass'
        self.h['gate_evidence'] = {'reveal_approval': 'brief.txt'}
        with self.assertRaisesRegex(builder.BuildError, 'lacks original'):
            self.run_build()

    def test_embedded_archive_is_rejected_even_with_another_extension(self):
        with zipfile.ZipFile(self.source / 'old.bin', 'w') as archive:
            archive.writestr('old.txt', 'Do not embed old packages')
        self.refresh()
        with self.assertRaisesRegex(builder.BuildError, 'archive bytes'):
            self.run_build()

    def test_limits_and_deadline_do_not_publish(self):
        with patch.object(builder.ap, 'MAX_ZIP', 1), self.assertRaisesRegex(builder.BuildError, 'ZIP exceeds'):
            self.run_build()
        def abort(name):
            if name == 'before-publication':
                raise Aborted('Synthetic exhausted budget')
        with patch.object(builder, 'checkpoint', abort), self.assertRaises(builder.BuildError) as caught:
            self.run_build()
        self.assertTrue(caught.exception.aborted)
        self.assertIsNone(caught.exception.remaining)
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())

    def test_paired_manifest_keeps_baseline_and_assessment_bindings_in_draft(self):
        bundle = self.source / 'draft'
        bundle.mkdir()
        for name in ('baseline-proof.json', 'assessment.json'):
            write_json(bundle / name, {'synthetic': 'Binding test only, no claimed proof'})
        write_json(bundle / 'manifest.json', {'format': 'picross-image-manifest-v2', 'files': {
            name: file_hash(bundle / name) for name in ('baseline-proof.json', 'assessment.json')}})
        self.refresh()
        self.request['files'] = [f for f in self.request['files'] if not f['path'].endswith('baseline-proof.json')]
        with self.assertRaisesRegex(builder.BuildError, 'Missing package file'):
            self.run_build()

    def test_crc_corruption_and_inventory_corruption_are_detected(self):
        for corrupt in ('crc', 'inventory'):
            def inject(name):
                if name != 'zip-written':
                    return
                path = next(self.output.rglob('package.zip'))
                if corrupt == 'crc':
                    raw = path.read_bytes().replace(b'TEST ONLY synthetic brief.', b'FAIL ONLY synthetic brief.', 1)
                    path.write_bytes(raw)
                else:
                    with zipfile.ZipFile(path) as archive:
                        members = {n: archive.read(n) for n in archive.namelist()}
                    members['inventory.json'] = b'{}\n'
                    with zipfile.ZipFile(path, 'w') as archive:
                        for n, raw in members.items(): archive.writestr(n, raw)
            with self.subTest(corrupt=corrupt), patch.object(builder, 'checkpoint', inject), self.assertRaises(builder.BuildError):
                self.run_build()
        self.assertFalse((self.output / 'pz-builder-test/r01').exists())

    def test_actual_external_final_approval_is_checked_without_changing_handoff(self):
        self.content()
        from tools.puzzle_production.za1_fixtures import approve
        built = self.run_build()
        approval = self.root / 'approval.json'
        approve(Path(built['directory']), approval)
        # Request external evidence independently; package identity must stay the
        # same, but the outer record is a different publication plan.
        external_root = self.source / 'external'
        external_root.mkdir()
        target = external_root / 'approval.json'
        target.write_bytes(approval.read_bytes())
        self.request['external'] = {'approval.json': {'source': 'external/approval.json',
                                    'sha256': file_hash(target), 'bytes': target.stat().st_size}}
        new_output = self.root / 'approved-output'
        new_output.mkdir()
        result = builder.build(self.request, self.source, new_output)
        self.assertTrue(result['record']['verification']['editorial_approved'])
        self.assertEqual(built['files']['package.zip'], result['files']['package.zip'])
        self.assertEqual(result['record']['state'], 'content_ready')
        self.assertEqual(self.h['gates']['final_editorial'], 'pending')

    def test_motif_phase_requires_real_bound_reveal_decision(self):
        self.h['state'] = 'motif_review'
        reveal, motif = self.image('reveal'), self.image('motif')
        motif['derived_from_reveal_sha256'] = reveal['sha256']
        provenance_path = self.source / 'motif.provenance.json'
        provenance = load_json(provenance_path)
        provenance['derived_from'] = {'file': reveal['file'], 'sha256': reveal['sha256']}
        write_json(provenance_path, provenance)
        self.h.update(reveal=reveal, motif=motif)
        self.refresh()
        with self.assertRaises(builder.BuildError):
            self.run_build()
        self.approval(reveal, 'reveal')
        self.refresh()
        result = self.run_build()
        self.assertIn('motif: human decision pending', result['record']['blockers'])

    def test_legacy_sealed_packages_remain_readable(self):
        # Select a fixed synthetic fixture by its authoring phase, no real content.
        legacy = next(p for p in sorted(FIXTURES.iterdir()) if p.is_dir())
        with open_package(legacy) as package:
            report = inspect(package)[0]
        self.assertTrue(report['technical'])
        self.assertFalse(report['editorial_approved'])

    def test_cli_result_and_duplicate_json_rejection(self):
        request = self.root / 'request.json'
        write_json(request, self.request)
        command = [sys.executable, '-m', 'tools.puzzle_production.authoring_builder', 'build',
                   '--request', str(request), '--source-root', str(self.source), '--output-root', str(self.output)]
        run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertEqual(json.loads(run.stdout)['status'], 'built')
        request.write_text('{"format":"x","format":"y"}', encoding='utf-8')
        run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)['status'], 'invalid_input')


if __name__ == '__main__':
    unittest.main()
