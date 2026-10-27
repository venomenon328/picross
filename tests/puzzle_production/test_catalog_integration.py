"""SD-C1: fixed synthetic inputs only, never the real registry or catalog."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import catalog_analysis as ca, catalog_rating as rating, catalog_transaction as tx
from tools.puzzle_production import content_registry as cr
from tools.puzzle_production.analysis_contract import AnalysisBudget
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, canonical_bytes, digest, load_json, write_json
from tools.puzzle_production.difficulty_rating import frozen_method
from tools.puzzle_production.target_adapter import export, inspect
from tools.puzzle_production.za1_fixtures import ROOT, FIXTURES, approve, isolated_checkout, difficulty_for_export


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.home = Path(cls.temporary.name)
        from tests.puzzle_production.catalog_fixtures import registered
        cls.checked = registered(cls.home, stem='sd_test', save_slot='sd_test')
        cls.base = cls.home/'base'
        cls.exported = cls.home/'export'
        cls.identifier = cls.checked['current_source']['id']
        cls.entry = cr.check_checkout(cls.base)['entries'][0]
        cls.definition = 'game/'+cls.entry['definition']
        cls.rating_path = rating.path(cls.identifier)
        # Metadata, source and journal tests also support a genuinely integrated
        # catalog. Keep full export inputs for new registrations and replay tests;
        # never cache their verification or a mutable per-test checkout.
        cls.full_base = cls.home/'full-base'

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root/'checkout'
        # Visibility changes require a full export: a compact receipt binds the
        # exact original entry and would make the intended hidden source invalid.
        full = self._testMethodName == 'test_direct_priority_conflict_and_never_visible_unknown'
        shutil.copytree(self.full_base if full else self.base, self.checkout)

    def legacy(self):
        (self.checkout/self.rating_path).unlink()
        index = load_json(self.checkout/cr.REGISTRY)
        catalog = load_json(self.checkout/'content/categories.json')
        write_json(self.checkout/cr.RUNTIME, cr.projection(index,catalog,self.checkout))

    def preview(self, *, run='test-run', checked=True, all_entries=False):
        return ca.preview(self.checkout,self.root/run,run,'a'*40,
                          ids=None if all_entries else [self.identifier], all_entries=all_entries,
                          checked_inputs={self.identifier:self.checked} if checked else None)

    def test_priority_no_fallback_and_unchanged_original_sources(self):
        active = load_json(self.checkout/self.rating_path)
        projected = load_json(self.checkout/cr.RUNTIME)['entries'][0]['difficulty']
        self.assertEqual(projected, rating.project(active))
        self.assertEqual(set(projected), {'method','level','assessment_type','confidence','plausible_range','r4_required'})
        self.assertNotIn('waves', active['compact_analysis']['metrics'])
        self.assertEqual(active['rating'], self.checked['rating'])
        self.legacy()
        self.assertEqual(load_json(self.checkout/cr.RUNTIME)['entries'][0]['difficulty']['method'], 'picross-difficulty-0.1')
        before = snapshot(self.checkout)
        # Existing legacy repeat remains a no-op with no new analysis/input.
        with patch.object(ca,'analyze_single', side_effect=AssertionError('hidden analysis')):
            self.assertEqual(cr.registration(self.exported,self.checkout,apply=True)['status'],'no-op')
        self.assertEqual(before,snapshot(self.checkout))
        (self.checkout/self.rating_path).write_bytes(b'{"format":"wrong"}\n')
        invalid = snapshot(self.checkout)
        for operation in (lambda: cr.check_checkout(self.checkout),lambda: cr.sync_runtime(self.checkout),
                          lambda: cr.registration(self.exported,self.checkout,apply=True)):
            with self.assertRaises(InvalidInput): operation()
            self.assertEqual(invalid,snapshot(self.checkout))

    def test_new_registration_requires_checked_complete_input_before_mutation(self):
        checkout = isolated_checkout(self.root/'empty')
        before = snapshot(checkout)
        with self.assertRaisesRegex(InvalidInput,'complete 0.3'):
            cr.registration(self.exported,checkout,apply=True)
        self.assertEqual(snapshot(checkout),before)
        bad = deepcopy(self.checked);bad['current_source']['definition_sha256']='0'*64
        bad.pop('checked_hash');bad=rating.hashed(bad,'checked_hash')
        with self.assertRaisesRegex(InvalidInput,'Stale'):
            cr.registration(self.exported,checkout,apply=True,difficulty=bad)
        self.assertEqual(snapshot(checkout),before)
        with patch('tools.puzzle_production.analysis_io.check_bundle', side_effect=AssertionError('hidden SD replay')):
            cr.registration(self.exported,checkout,apply=True,difficulty=self.checked)
            cr.sync_runtime(checkout)
            cr.check_checkout(checkout)

    def test_prepared_journal_bounds_repeated_projection_and_preserves_live_guards(self):
        from tools.puzzle_production import catalog_publication as pub, catalog_io as io
        checkout = isolated_checkout(self.root/'prepared')
        with self.assertRaises(InterruptedError):
            cr.registration(self.exported, checkout, apply=True, difficulty=self.checked, fail_step='crash-runtime')
        raw = (checkout/tx.LOCK).read_bytes()
        journal = io.json_bytes(raw, pub.NORMAL_LIMIT)
        tx.validate_journal(checkout, journal)
        with patch.object(tx, 'projection', wraps=tx.projection) as projection, \
                patch.object(io, 'checksum', wraps=io.checksum) as checksum:
            view = pub._JournalView(journal, raw)
            for _ in range(5): pub.guard(checkout, journal, raw=raw, _view=view)
            # C journals retain the already validated old runtime bytes exactly.
            self.assertEqual(projection.call_count, 0)
            self.assertEqual(view.restore, journal['old'][tx.RUNTIME])
            self.assertEqual(sum(c.args[0] is raw for c in checksum.call_args_list), 1)
        self.assertGreater(len(view.temps), 10)
        names = sorted(set(journal['additions']) | {n for n in journal['old'] if journal['old'][n] != journal['new'][n]} | {tx.RUNTIME})
        self.assertEqual(view.temps, {n:(Path(n).parent/('.registration-'+hashlib.sha256(raw).hexdigest()+'-'+str(i)+'.tmp')).as_posix()
                                      for i,n in enumerate(names)})
        # The prepared view must never reuse a previous observation of live bytes.
        targets = [tx.LOCK, self.definition, self.rating_path, next(iter(journal['additions']))]
        for name in targets:
            path = checkout/name; before = path.read_bytes(); path.write_bytes(b'FOREIGN DATA')
            changed = snapshot(checkout)
            with self.subTest(name=name), self.assertRaises(ValueError):
                pub.guard(checkout, journal, raw=raw, _view=view)
            self.assertEqual(changed, snapshot(checkout)); path.write_bytes(before)
        temporary = checkout/next(iter(view.temps.values()))
        temporary.write_bytes(b'FOREIGN TEMP')
        with self.assertRaises(ValueError): pub.guard(checkout, journal, raw=raw, _view=view)
        temporary.unlink()
        foreign = checkout/'content/difficulty/pz-foreign/rating.json'
        foreign.parent.mkdir(); foreign.write_bytes(b'FOREIGN NAMESPACE')
        with self.assertRaises(ValueError): pub.guard(checkout, journal, raw=raw, _view=view)
        foreign.unlink(); foreign.parent.rmdir()
        cr.recover(checkout)
        self.assertEqual(cr.check_checkout(checkout)['entries'], [])

    def test_recovery_rechecks_foreign_source_after_unchanged_target(self):
        from tools.puzzle_production import catalog_publication as pub
        # A sync journal has many unchanged targets. It must still check all live
        # sources before the next write, even after passing an unchanged target.
        (self.checkout/cr.RUNTIME).write_bytes(b'stale projection\n')
        captured = tx.capture(self.checkout, allow_stale=True)
        journal = tx.prepare(self.checkout, captured, {}, operation='sync')
        with self.assertRaises(InterruptedError): tx.execute(self.checkout, journal, fail_step='crash-runtime')
        target = self.checkout/next(iter(journal['retained']))
        original = target.read_bytes(); changed = []
        def inject(phase, name=None):
            if phase == 'R1-text' and not changed:
                target.write_bytes(b'FOREIGN RETAINED SOURCE')
                changed.append(snapshot(self.checkout))
        with patch.object(pub, 'checkpoint', side_effect=inject), self.assertRaises(ValueError):
            cr.recover(self.checkout)
        self.assertEqual(snapshot(self.checkout), changed[0])
        target.write_bytes(original)
        cr.recover(self.checkout)
        cr.check_checkout(self.checkout)

    def test_nested_schema_types_hashes_and_source_attacks(self):
        original = load_json(self.checkout/self.rating_path)
        attacks = [lambda d: d.update(extra=1), lambda d:d.update(rating_revision=True),
                   lambda d:d['current_source'].update(runtime_revision=2),
                   lambda d:d['logic_binding'].update(matrix_hash='a'*64),
                   lambda d:d['logic_binding'].update(analysis_hash='a'*64),
                   lambda d:d['rating']['result'].update(confidence='high'),
                   lambda d:d['rating']['result'].update(level=5),
                   lambda d:d['rating']['result']['uncertainty'].update(human_calibration='performed'),
                   lambda d:d['compact_analysis'].update(deduction_complete=False),
                   lambda d:d['compact_analysis']['metrics'].update(waves=[]),
                   lambda d:d['compact_analysis']['metrics']['family_line_applications'].update(R0=0),
                   lambda d:d['compact_analysis']['metrics']['workload'].update(cells=True),
                   lambda d:d['rating']['source'].update(definition_id='pz-other'),
                   lambda d:d['rating']['method']['configuration'].update(unapproved=0)]
        for change in attacks:
            value=deepcopy(original);change(value)
            value['rating']['rating_hash']=digest({k:v for k,v in value['rating'].items() if k!='rating_hash'})
            value['record_hash']=digest({k:v for k,v in value.items() if k!='record_hash'})
            (self.checkout/self.rating_path).write_bytes(canonical_bytes(value)+b'\n')
            with self.subTest(change=change),self.assertRaises(InvalidInput): cr.check_checkout(self.checkout)
        for raw in (b'{"format":1,"format":2}', b'NaN', b' '*(rating.LIMIT+1)):
            with self.assertRaises(ValueError): rating.bytes_json(raw)

    def test_candidate_remapping_matches_final_export_before_editorial_approval(self):
        for fixture in ('direct-mono','direct-color'):
            with open_package(FIXTURES/fixture) as p:
                report,design,matrix,logic,approval=inspect(p)
            self.assertIsNone(approval)
            candidate=ca.candidate(design,matrix,logic,report['puzzle_id'],1)
            from tools.puzzle_production.target_adapter import definition
            final,_=definition(report,design,matrix,logic,'Final title',9,'final.png')
            first=rating.definition(canonical_bytes(candidate)+b'\n')
            later=rating.definition(canonical_bytes(final)+b'\n')
            self.assertEqual(first[3],later[3])
            source=self.root/(fixture+'.json');write_json(source,candidate)
            checked=ca.analyze_single(source,self.root/(fixture+'-bundle'),production_mode=design['mode'])
            rebound=rating.rebind_checked(checked,canonical_bytes(final)+b'\n',production_mode=design['mode'])
            self.assertEqual(rebound['rating'],checked['rating'])
            self.assertEqual(rebound['current_source']['runtime_revision'],9)
            final['solution'][0][0]=999
            with self.assertRaises(InvalidInput):rating.rebind_checked(checked,canonical_bytes(final)+b'\n',production_mode=design['mode'])

    def test_rebind_preserves_original_rating_source_and_no_op_revision(self):
        value=deepcopy(load_json(self.checkout/self.definition));value['revision']=2;value['reveal']['name']='New title'
        rebound=rating.rebind_checked(self.checked,canonical_bytes(value)+b'\n',production_mode='mono')
        prior=load_json(self.checkout/self.rating_path)
        active=rating.active_record(rebound,prior,kind='rebind')
        self.assertEqual(active['rating_revision'],2)
        self.assertEqual(active['rating']['source'],prior['rating']['source'])
        self.assertEqual(rating.active_record(rebound,active),active)
        changed=deepcopy(rebound);changed['current_source']['id']='pz-other';changed['checked_hash']=digest({k:v for k,v in changed.items() if k!='checked_hash'})
        with self.assertRaises(InvalidInput):rating.rebind_checked(changed,canonical_bytes(value)+b'\n',production_mode='mono')
        value['id']='pz-other'
        with self.assertRaises(InvalidInput):rating.rebind_checked(self.checked,canonical_bytes(value)+b'\n',production_mode='mono')

    def test_full_import_rejects_corrupt_bundle_and_remapped_proof_mismatch(self):
        source=self.checkout/self.definition; bundle=self.root/'analysis'
        ca.analyze_single(source,bundle,production_mode='mono')
        value=load_json(bundle/'rating.json');value['result']['level']=5;write_json(bundle/'rating.json',value)
        with self.assertRaises((InvalidInput,InvalidProof)):rating.import_bundle(source,bundle)
        from test_paired import MONO, wire
        from tools.puzzle_production.contract import Budget, validate_logic
        from tools.puzzle_production.certification import configuration, produce
        puzzle=validate_logic(wire(MONO))
        proofdir=self.root/'proof';proofdir.mkdir()
        produce(puzzle,proofdir,'',configuration(puzzle,'paired-lines-mono'),Budget())
        with self.assertRaises((InvalidInput,InvalidProof)):
            ca.analyze_single(source,self.root/'wrong-r4',production_mode='mono',baseline=proofdir/'baseline-proof.json',proof=proofdir/'proof.json')

    def test_repeat_from_runtime_only_has_same_rating_identity(self):
        source=self.root/'runtime-only.json';source.write_bytes((self.checkout/self.definition).read_bytes())
        first=ca.analyze_single(source,self.root/'one',production_mode='mono')
        second=ca.analyze_single(source,self.root/'two',production_mode='mono')
        for field in rating.FIELDS:self.assertEqual(first[field],second[field],field)
        self.assertEqual(first['checked_hash'],second['checked_hash'])
        # Different clocks/work budgets are checked, but never become result identity.
        report=load_json(self.root/'two/report.json');report['operation']['elapsed_seconds']+=100
        write_json(self.root/'two/report.json',report)
        self.assertEqual(rating.import_bundle(source,self.root/'two')['checked_hash'],first['checked_hash'])
        active=rating.active_record(first)
        self.assertEqual(rating.active_record(second,active),active)
        one=self.preview(run='repeat-one',checked=False)
        two=self.preview(run='repeat-two',checked=False)
        self.assertEqual(one['result_hash'],two['result_hash'])

    def test_explicit_multiple_ids_keeps_unrated_and_error_rows(self):
        # A second independent sealed synthetic package; no real catalog source.
        approval=self.root/'color-approval.json';approve(FIXTURES/'direct-color',approval)
        exported=self.root/'color'
        export(FIXTURES/'direct-color',exported,name='TEST ONLY',revision=1,stem='sd_color',save_slot='sd_color',
               approval_path=approval,category_id='voegel',categories_path=self.checkout/'content/categories.json')
        color=difficulty_for_export(exported);identifier=color['current_source']['id']
        cr.registration(exported,self.checkout,apply=True,difficulty=color)
        # Registration above exercises the full export. The following metadata
        # report/adoption only needs the valid integrated prerequisite.
        from tests.puzzle_production.catalog_fixtures import compact
        compact(self.checkout, [identifier])
        incomplete=ca.analyze_single(self.checkout/self.definition,self.root/'abort-bundle',production_mode='mono',budget=AnalysisBudget(max_waves=0))
        before=snapshot(self.checkout)
        report=ca.preview(self.checkout,self.root/'multiple','multiple','c'*40,ids=[identifier,self.identifier],
                          checked_inputs={self.identifier:incomplete})
        self.assertEqual({row['status'] for row in report['result']['entries']},{'unrated','invalid_input'})
        self.assertEqual(report['result']['distribution']['proposed']['unrated'],2)
        ca.adopt(self.checkout,self.root/'multiple',apply=True)
        for n,b in before.items():self.assertEqual((self.checkout/n).read_bytes(),b,n)

    def test_stalled_and_budget_abort_remain_unrated_never_five(self):
        raw=load_json(ROOT/'tests/puzzle_production/fixtures/sd-runtime.json')
        raw.update(id='pz-ambiguous',width=2,height=2,solution=[[1,0],[0,1]],rows=[[{'color':1,'length':1}]]*2,columns=[[{'color':1,'length':1}]]*2)
        raw['reveal']['definition_id']=raw['id']
        source=self.root/'ambiguous.json';write_json(source,raw)
        for name,budget in [('stalled',None),('abort',AnalysisBudget(max_waves=0))]:
            with patch('tools.puzzle_production.solver.solve',side_effect=AssertionError('implicit R4')):
                value=ca.analyze_single(source,self.root/name,production_mode='mono',budget=budget)
            self.assertEqual(value['rating']['result']['status'],'unrated')
            self.assertIsNone(value['rating']['result']['level'])
            with self.assertRaises(InvalidInput):rating.active_record(value)

    def test_report_adoption_preserves_definitions_manifests_saves_and_noop(self):
        self.legacy();before=snapshot(self.checkout)
        (self.checkout/'synthetic-save.json').write_bytes(b'not a user save')
        method=digest(frozen_method())
        report=self.preview(all_entries=True)
        self.assertEqual(report['result']['entries'][0]['status'],'rated')
        self.assertEqual(report['result']['distribution']['proposed']['L1'],1)
        self.assertEqual(snapshot(self.checkout),{**before,'synthetic-save.json':b'not a user save'})
        self.assertEqual(ca.adopt(self.checkout,self.root/'test-run')['status'],'planned-adoption')
        with patch('tools.puzzle_production.analysis_io.check_bundle',side_effect=AssertionError('hidden SD replay')):
            self.assertEqual(ca.adopt(self.checkout,self.root/'test-run',apply=True)['status'],'adopted')
            cr.check_checkout(self.checkout)
        after=snapshot(self.checkout)
        for n,b in before.items():
            if n!=cr.RUNTIME:self.assertEqual(after[n],b,n)
        self.assertEqual(ca.adopt(self.checkout,self.root/'test-run',apply=True)['status'],'no-op')
        self.assertEqual(after,snapshot(self.checkout))
        self.assertEqual(digest(frozen_method()),method)

    def test_report_keeps_missing_input_and_existing_rating(self):
        before=snapshot(self.checkout)
        report=ca.preview(self.checkout,self.root/'errors','errors','b'*40,ids=[self.identifier],checked_inputs={})
        self.assertEqual(len(report['result']['entries']),1)
        self.assertEqual(report['result']['entries'][0]['status'],'invalid_input')
        self.assertIn('Missing checked input',report['result']['entries'][0]['reason'])
        ca.adopt(self.checkout,self.root/'errors',apply=True)
        for n,b in before.items():self.assertEqual((self.checkout/n).read_bytes(),b,n)
        self.assertEqual(ca.adopt(self.checkout,self.root/'errors',apply=True)['status'],'no-op')

    def test_preview_selection_and_stale_adoption_reject_before_mutation(self):
        for kwargs in ({},{'ids':[self.identifier,self.identifier]},{'ids':['pz-missing']},{'ids':[self.identifier],'all_entries':True}):
            with self.assertRaises(InvalidInput):ca.preview(self.checkout,self.root/'invalid','invalid','a'*40,**kwargs)
        self.legacy();self.preview()
        cat=self.checkout/'content/categories.json';cat.write_bytes(cat.read_bytes()+b' ')
        before=snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput,'changed since preview'):ca.adopt(self.checkout,self.root/'test-run',apply=True)
        self.assertEqual(before,snapshot(self.checkout))

    def test_adoption_crashes_recover_every_publication_phase_without_sync(self):
        self.legacy();self.preview();before=snapshot(self.checkout)
        for n in (self.rating_path,'content/difficulty/reports/test-run/report.json','content/difficulty/reports/test-run/report.md',cr.RUNTIME):
            with self.subTest(n=n),self.assertRaises(InterruptedError):
                ca.adopt(self.checkout,self.root/'test-run',apply=True,fail_step='crash-'+n)
            with self.assertRaises(InvalidInput):cr.check_checkout(self.checkout)
            with patch('tools.puzzle_production.analysis_io.check_bundle',side_effect=AssertionError('hidden replay')):
                cr.recover(self.checkout)
            cr.check_checkout(self.checkout)
            self.assertEqual(snapshot(self.checkout),before)

    def test_recovery_preserves_foreign_sidecar_report_and_journal(self):
        self.legacy();self.preview()
        with self.assertRaises(InterruptedError):ca.adopt(self.checkout,self.root/'test-run',apply=True,fail_step='crash-runtime')
        for name in (self.rating_path,'content/difficulty/reports/test-run/report.md',cr.RUNTIME,'content/categories.json'):
            p=self.checkout/name;old=p.read_bytes();p.write_bytes(old+b'foreign')
            before=snapshot(self.checkout)
            with self.subTest(name=name),self.assertRaises(InvalidInput):cr.recover(self.checkout)
            self.assertEqual(before,snapshot(self.checkout));p.write_bytes(old)
        j=load_json(self.checkout/tx.LOCK);old=(self.checkout/tx.LOCK).read_bytes()
        j['new'][self.rating_path]=j['old'][self.rating_path];write_json(self.checkout/tx.LOCK,j)
        before=snapshot(self.checkout)
        with self.assertRaises(InvalidInput):cr.recover(self.checkout)
        self.assertEqual(before,snapshot(self.checkout));(self.checkout/tx.LOCK).write_bytes(old)
        cr.recover(self.checkout);cr.check_checkout(self.checkout)

    def test_sync_recovery_from_stale_runtime_is_immediately_valid(self):
        (self.checkout/cr.RUNTIME).write_bytes(b'stale projection\n')
        snap=tx.capture(self.checkout,allow_stale=True)
        journal=tx.prepare(self.checkout,snap,{},operation='sync')
        with self.assertRaises(InterruptedError):tx.execute(self.checkout,journal,fail_step='crash-runtime')
        cr.recover(self.checkout);cr.check_checkout(self.checkout)

    def test_recovery_can_resume_its_own_interruption(self):
        self.legacy();self.preview();before=snapshot(self.checkout)
        with self.assertRaises(InterruptedError):ca.adopt(self.checkout,self.root/'test-run',apply=True,fail_step='crash-runtime')
        from tools.puzzle_production import catalog_publication as publication
        def killed(phase,name=None):
            if phase=='R1-runtime':raise InterruptedError('recovery killed')
        with patch.object(publication,'checkpoint',side_effect=killed),self.assertRaises(InterruptedError):cr.recover(self.checkout)
        cr.recover(self.checkout);cr.check_checkout(self.checkout)
        self.assertEqual(snapshot(self.checkout),before)

    def test_work_paths_and_sidecar_aliases_are_rejected(self):
        for run in ('con','nul','com1','lpt9','../escape','Upper'):
            with self.assertRaises(InvalidInput):ca.run_id(run)
        for path in (self.checkout/'game/work',self.checkout/'content/difficulty/work',self.root/'..'/'alias'):
            with self.assertRaises(InvalidInput):ca.work_directory(path,self.checkout)
        p=self.checkout/self.rating_path;renamed=p.with_name('Rating.json');p.rename(renamed)
        with self.assertRaisesRegex(InvalidInput,'collision'):cr.check_checkout(self.checkout)

    def test_cli_requires_explicit_selection_and_supports_checked_plan(self):
        args=[sys.executable,'-m','tools.puzzle_production.catalog_analysis','preview-checked','--checkout',str(self.checkout),
              '--work-dir',str(self.root/'cli'),'--run-id','cli','--source-commit','a'*40,
              '--checked',self.identifier,str(self.root/'input.json')]
        write_json(self.root/'input.json',self.checked)
        missing=subprocess.run(args,capture_output=True,text=True,timeout=30)
        self.assertEqual(missing.returncode,2)
        result=subprocess.run(args+['--id',self.identifier],capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertEqual(load_json(self.root/'cli/report.json')['result']['entries'][0]['status'],'rated')
