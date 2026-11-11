"""Small PW-B phase/selection/publication regressions, all synthetic originals."""
from copy import deepcopy
from pathlib import Path
import shutil
import unittest

from tools.puzzle_production import authoring_builder as builder, authoring_workflow as workflow
from tools.puzzle_production import authoring_finalization as finalizer
from tools.puzzle_production.contract import load_json
from tools.production_workspace import presentation as p
from tools.production_workspace.sources import git, GitSource
from tests.puzzle_production import test_authoring_finalization as finalization_tests
from tests.puzzle_production.background_fixtures import put, put_json, file_ref


class WorkflowFixture:
    """Reuse the existing independent small raster/background fixture producers."""
    def __init__(self, case, mode='mono'):
        self.helper = f = finalization_tests.AuthoringFinalizationTests()
        f.setUp()
        case.addCleanup(f.doCleanups)
        self.case, self.root = case, f.root
        if mode == 'color':
            f.source = f.content.content(mode='color', colors=['#cc3333', '#2678bd'], name='color')
            f.fixture, f.handoff = f.content.background(f.source, choice='offered', ready=True)
            f.content.review(f.source)
            f.handoff = load_json(f.source / 'handoff.json')
            (f.source / 'handoff.json').unlink(); (f.source / 'inventory.json').unlink()
        self.background_source = self.root / 'background-saved'
        shutil.copytree(f.source / 'background', self.background_source)
        shutil.rmtree(f.source / 'background')
        self.background_binding = deepcopy(f.handoff['background'])
        put(f.source, 'rulebook.md', b'**Version 0.8.0 \xc2\xb7 Dokumentrevision 1 \xc2\xb7 TEST ONLY**\n')
        h = f.handoff
        h.update(format=workflow.HANDOFF, revision='r01', state='raster_ready', background=None,
                 raster_selection=None, inventory=None, authorization='TEST ONLY', next_action='TEST ONLY', blockers=[], content_blockers=[])
        h['rulebook'] = {'version': '0.8.0', 'file': 'rulebook.md', 'sha256': file_ref(f.source, 'rulebook.md')['sha256']}
        for key in ('background_choice', 'background_asset'):
            h['gates'][key]='pending'; h['gate_evidence'][key]=None
        f.output = self.root / 'repository'; f.output.mkdir()
        git(f.output, 'init', '-q', '-b', 'content/pw/pz-hp-synthetic')
        put_json(f.output, builder.INDEX, {'format':'picross-authoring-index-v1','entries':[]})
        self.commit()
        self.staging = self.root / 'build-work'; self.staging.mkdir()
        self.request = {'format':workflow.REQUEST,'handoff':h,'document_revision':1,'files':[],
                        'target':'repository','category_id':'voegel','reveal_options':[],'external':{},
                        'presentation':{'title':'TEST ONLY · Raster und Kontext','raster_offers':[]}}

    def commit(self):
        f=self.helper
        git(f.output,'add','.')
        git(f.output,'-c','user.name=PW synthetic','-c','user.email=pw@example.invalid','commit','-qm','TEST ONLY synthetic phase')
        return git(f.output,'rev-parse','HEAD').decode().strip()

    def build(self):
        f=self.helper
        h=self.request['handoff']
        if h.get('palette_review'):
            # This synthetic judgment is issued for this exact test revision.
            review=load_json(f.source/h['palette_review']['file'])
            review['revision']=h['revision']
            ref=put_json(f.source,h['palette_review']['file'],review)
            h['palette_review']={k:ref[k] for k in ('file','sha256')}
        self.request['files']=[{'path':name,'source':name,**{k:ref[k] for k in ('sha256','bytes')}}
            for path in sorted(f.source.rglob('*')) if path.is_file()
            for name in [path.relative_to(f.source).as_posix()] for ref in [file_ref(f.source,name)]]
        result=builder.build(self.request,f.source,self.staging,f.output,history_repo=f.output)
        f.directory=Path(result['directory']); f.record_path=f.directory/'record.json'
        f.record_name=f.record_path.relative_to(f.output).as_posix()
        return result

    def select(self):
        f=self.helper
        record=load_json(f.record_path)
        projection_name=f.record_name.replace('record.json','workspace.json')
        projection=load_json(f.output/projection_name)
        commit=self.commit()
        copies={}
        for key,name in [('record',f.record_name),('projection',projection_name)]:
            ref=file_ref(f.output,name)
            copy='selected-source/'+key+'.json'
            put(f.source,copy,(f.output/name).read_bytes())
            copies[key]={**ref,'copy':copy}
        evidence=put(f.source,'raster-choice.txt',b'TEST ONLY explicit synthetic raster choice.\n')
        h=self.request['handoff']
        selection={'format':'picross-raster-selection-v1','puzzle_id':h['puzzle_id'],'source_commit':commit,
                   'option_id':next(o['id'] for o in projection['offers'] if o['kind']=='raster'),
                   **copies,'inventory_sha256':record['inventory_sha256'],
                   'candidate':{k:h['candidate'][k] for k in ('variant','matrix_hash','logic_hash')},
                   'reveal':{k:h['reveal'][k] for k in ('file','sha256')},
                   'motif':{k:h['motif'][k] for k in ('file','sha256')},
                   'human':{'actor':'TEST ONLY','timestamp_utc':'2026-11-11T12:00:00Z',
                            'statement':'Synthetic choice; no owner approval.',
                            'evidence':{k:evidence[k] for k in ('file','sha256')}},'test_only':True}
        ref=put_json(f.source,'raster-selection.json',selection)
        h.update(revision='r02',state='background_review',raster_selection={k:ref[k] for k in ('file','sha256')},
                 background=self.background_binding)
        shutil.copytree(self.background_source,f.source/'background')
        return selection

    def finalize(self, outcome='selected', approval=True):
        r=self.helper.request(outcome=outcome,approval=approval)
        r['format']='picross-authoring-finalize-request-v2'
        return r,builder.finalize_background(r,self.helper.payload,self.helper.output)


class WorkflowTests(unittest.TestCase):
    def test_early_background_is_rejected_and_raster_is_qualified_without_it(self):
        f=WorkflowFixture(self,mode='color')
        from tools.puzzle_production import background_package
        legacy=deepcopy(f.request['handoff']);legacy['rulebook']['version']='0.7.0'
        with self.assertRaisesRegex(ValueError,'0.8.0'):
            background_package.validate(f.helper.source,legacy)
        for state in workflow.EARLY:
            h=deepcopy(f.request['handoff']);h['state']=state;workflow.phase(h)
            h['background']=f.background_binding
            with self.assertRaisesRegex(ValueError,'explicitly selected'):
                workflow.phase(h)
        result=f.build()
        self.assertEqual(result['record']['state'],'raster_ready')
        self.assertEqual(result['record']['format'],workflow.RECORD)
        self.assertIsNone(result['record']['background'])
        self.assertFalse(any(b.startswith('background') for b in result['record']['blockers']))
        self.assertIn('workspace.json',result['files'])
        self.assertEqual(f.build()['status'],'reused')
        f.select()
        result=f.build()
        self.assertEqual(result['record']['state'],'background_review')
        self.assertEqual(len(load_json(f.helper.directory/'workspace.json')['offers']),3)
        request,final=f.finalize()
        self.assertEqual(final['status'],'updated',final)
        self.assertEqual(final['record']['state'],'editorially_approved')
        again=builder.finalize_background(request,f.helper.payload,f.helper.output)
        self.assertEqual(again['status'],'reused',again)
        sha=f.commit()
        view=load_json(f.helper.directory/'workspace.json')
        self.assertEqual(p.inspect(GitSource(f.helper.output),sha,view)['state'],'editorially_approved')

    def test_missing_selection_stale_source_and_changed_context_fail_before_publication(self):
        f=WorkflowFixture(self)
        f.build();selection=f.select()
        h=f.request['handoff'];expected=deepcopy(h['raster_selection'])
        h['raster_selection']=None
        with self.assertRaisesRegex(ValueError,'recorded qualified'):
            f.build()
        h['raster_selection']=expected
        bad=deepcopy(selection);bad['candidate']['matrix_hash']='f'*64
        ref=put_json(f.helper.source,'raster-selection.json',bad)
        h['raster_selection']={k:ref[k] for k in ('file','sha256')}
        with self.assertRaisesRegex(ValueError,'Selected raster changed'):
            f.build()
        ref=put_json(f.helper.source,'raster-selection.json',selection)
        h['raster_selection']={k:ref[k] for k in ('file','sha256')}
        put(f.helper.output,'new-source.txt',b'unrelated work');f.commit()
        workflow.selection(f.helper.source,h,history_repo=f.helper.output,verify_git=True)
        original=f.helper.record_path.read_bytes()
        f.helper.record_path.write_bytes(original+b'\n');f.commit()
        with self.assertRaisesRegex(ValueError,'stale'):
            f.build()
        self.assertFalse((f.helper.output/'content/authoring/pz-hp-synthetic/r02').exists())
