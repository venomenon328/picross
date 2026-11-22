"""One current production job. No manufacturing archive is read or written."""
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import os
import re
import tempfile

from . import authoring_package as ap, catalog_io as io, current_content as content
from .contract import exact_keys, canonical_bytes, digest, Budget, integer

FORMAT = 'picross-authoring-current-v1'
from . import raster_parameters, work_assets
FORMATS = (FORMAT, work_assets.FORMAT)
REQUEST = 'picross-authoring-current-request-v1'
LIMIT = 1024 * 1024
INDEX = 'content/authoring/index.json'
FIELDS = set('format puzzle_id revision source_commit operation target title category_id state brief parameters assets rasters selected decisions budgets blockers test_only integration'.split())
PHASES = ('brief_ready', 'reveal_review', 'motif_review', 'motif_approved', 'raster_review',
          'raster_ready', 'background_review', 'content_ready', 'editorially_approved', 'registered')
SCOPES = ('reveal', 'motif', 'raster', 'background', 'final', 'integration', 'budget')
CRITERIA = {'reveal': {'Q-B01','Q-B02','Q-B03'}, 'motif': {'Q-M01','Q-M02','Q-M03'},
            'background': {'Q-HG01','Q-HG02','Q-HG03','Q-HG04','H-07'},
            'raster': {'Q-R01','Q-R02','Q-R03','Q-R04','Q-H01','Q-H02','Q-H03'}}
OPTION = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')


def encoded(value):
    return canonical_bytes(value) + b'\n'


def path(identifier):
    ap.require(isinstance(identifier,str) and ap.ID.fullmatch(identifier), 'Invalid job identity')
    return 'content/authoring/' + identifier + '/current/record.json'


def own(identifier, name):
    return name.startswith('content/authoring/' + identifier + '/')


def text(value, label, maximum=4096):
    ap.string(value, label, maximum)
    ap.require('\0' not in value, 'NUL in '+label)
    return value


def human(value):
    for key in ('actor','statement'):
        text(value[key], key)
    ap.timestamp(value['timestamp_utc'])


def identifier(value):
    ap.require(isinstance(value,str) and OPTION.fullmatch(value) and value not in ('none','standard'), 'Invalid candidate ID')


def identity(item):
    return {'id':item['id'], 'sha256':item['file']['sha256'], 'bytes':item['file']['bytes']}


def binding(job, scope):
    """Content identity excludes paths, labels, publication bytes and other history."""
    assets = {a['id']:a for a in job['assets']}
    rasters = {a['id']:a for a in job['rasters']}
    selected = job['selected']
    def image(role):
        chosen = selected[role]
        return chosen if chosen in (None,'none','standard') else identity(assets[chosen])
    reveal = image('reveal')
    motif = {'reveal':reveal,'motif':image('motif'),'parameters':job['parameters']['approved']}
    def raster_content(r):
        return {'id':r['id'],'definition':{k:r['definition'][k] for k in ('sha256','bytes')},
                'difficulty':None if r['difficulty'] is None else {k:r['difficulty'][k] for k in ('sha256','bytes')}}
    chosen = selected['raster']
    raster = {'motif':motif,'raster':None if chosen is None else
              raster_content(rasters[chosen]),
              'offers':[raster_content(r) for r in job['rasters']] if chosen is None else []}
    if job['operation']=='background':
        raster={'target':{k:{f:job['target'][k][f] for f in ('sha256','bytes')} for k in ('definition','reveal')}}
    background = {'raster':raster,'background':image('background')}
    chosen_reviews={a['id']:{k:{f:v[f] for f in ('result','accepted','reason')} for k,v in a['review'].items()}
                    for a in job['assets'] if a['id'] in selected.values()}
    chosen_reviews.update({r['id']:{k:{f:v[f] for f in ('result','accepted','reason')} for k,v in r['review'].items()}
                           for r in job['rasters'] if r['id']==selected['raster']})
    final={'selection':background,'metadata':{k:job[k] for k in ('title','category_id','brief')},
           'rights':{a['id']:a['rights'] for a in job['assets'] if a['id'] in selected.values()},'judgments':chosen_reviews,
           'exceptions':[{**{k:v for k,v in e.items() if k!='evidence'},
                          'evidence':{k:e['evidence'][k] for k in ('sha256','bytes')}}
                         for r in job['rasters'] if r['id']==selected['raster'] for e in r['exceptions']]}
    values = {'reveal':reveal,'motif':motif,'raster':raster,'background':background,
              'final':final,'integration':final,'budget':job['budgets']['limits']}
    ap.require(scope in values, 'Unknown decision scope')
    return digest(values[scope])


def references(job):
    refs = [a['file'] for a in job['assets']]
    if job['target'] is not None: refs.extend(job['target'][k] for k in ('definition','reveal'))
    for raster in job['rasters']:
        refs.extend(raster[k] for k in ('definition','proof','difficulty','preview') if raster[k] is not None)
        refs.extend(e['evidence'] for e in raster['exceptions'])
    return refs


def validate(job):
    published = job.get('format') == work_assets.FORMAT
    exact_keys(job, FIELDS | ({'work_release'} if published else set()))
    if published:
        release = job['work_release']
        exact_keys(release, {'id', 'anchor'})
        ap.require(type(release['id']) is int and 0 < release['id'] < 2**63 and
                   isinstance(release['anchor'],str) and re.fullmatch('[0-9a-f]{40}',release['anchor']),
                   'Invalid work release binding')
    ap.require(job['format'] in FORMATS and job['revision'] == 'current', 'Current job format required; legacy originals are not migrated')
    path(job['puzzle_id'])
    ap.require(job['operation'] in ('production','background'), 'Unknown current operation')
    if job['operation']=='background':
        exact_keys(job['target'], {'definition','reveal','mode'})
        ap.require(job['target']['mode'] in ('mono','color') and not job['rasters'] and
                   job['state'] in ('background_review','content_ready','editorially_approved','registered'), 'Invalid background job')
    else: ap.require(job['target'] is None, 'Unexpected active target')
    ap.require(isinstance(job['source_commit'],str) and re.fullmatch('[0-9a-f]{40}',job['source_commit']), 'Full current source commit required')
    text(job['title'],'title',128); text(job['brief'],'brief',16384)
    ap.require(job['category_id'] is None or isinstance(job['category_id'],str) and
               re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',job['category_id']), 'Invalid category')
    ap.require(job['state'] in PHASES and type(job['test_only']) is bool, 'Invalid current state/scope')
    exact_keys(job['budgets'], {'limits','used'})
    for counters in job['budgets'].values():
        exact_keys(counters, {'raster_candidates','repair_rounds','image_corrections'})
        for count in counters.values(): integer(count,0,1000000,'current budget counter')
    ap.require(all(job['budgets']['used'][k]<=v for k,v in job['budgets']['limits'].items()), 'Current operation budget exceeded')
    exact_keys(job['parameters'], {'proposed','approved'})
    for role, values in job['parameters'].items():
        ap.require(isinstance(values,list) and len(values)<=8, 'Invalid parameters')
        for value in values:
            ap.require(isinstance(value,dict), 'Invalid parameter object')
            if value.get('format') == raster_parameters.FORMAT:
                raster_parameters.validate(value)
            else:
                keys = {'width','height','foreground_colors','size_constraint','foreground_color_constraint'}
                exact_keys(value, keys | ({'mode'} if role == 'approved' or 'mode' in value else set()))
                for axis in ('width','height'): integer(value[axis],1,50,axis)
                ap.require(value['size_constraint'] in ('exact','approximate') and
                           value['foreground_color_constraint'] in ('exact','approximate'), 'Invalid raster parameters')
                mode = value.get('mode')
                if (mode is None and role == 'proposed' and value['foreground_color_constraint'] == 'exact'
                        and value['foreground_colors'] == 1):
                    mode = 'mono'
                raster_parameters.require_color_count(mode, value['foreground_colors'])
    for key, maximum in (('assets',100),('rasters',20),('decisions',8),('blockers',64)):
        ap.require(isinstance(job[key],list) and len(job[key])<=maximum, 'Too many '+key)
    for message in job['blockers']: text(message,'blocker')
    ids=set()
    for asset in job['assets']:
        exact_keys(asset, {'id','role','label','file','rights','review'})
        identifier(asset['id']); text(asset['label'],'label',512)
        ap.require(asset['id']!='active-raster', 'Reserved active preview identity')
        ap.require(asset['id'] not in ids and asset['role'] in ('reveal','motif','background','input'), 'Invalid/duplicate image')
        ids.add(asset['id'])
        if asset['rights'] is not None:
            from .reveal_source import provenance
            provenance(asset['rights'])
        review(asset['review'], CRITERIA.get(asset['role'],set()), ready=False)
    raster_ids=set()
    for raster in job['rasters']:
        exact_keys(raster, {'id','label','definition','proof','difficulty','preview','review','exceptions'})
        identifier(raster['id']); text(raster['label'],'raster label',512)
        ap.require(raster['id'] not in raster_ids and raster['id'] not in ids, 'Duplicate raster ID')
        raster_ids.add(raster['id'])
        review(raster['review'],CRITERIA['raster'],ready=False)
        ap.require(isinstance(raster['exceptions'],list) and len(raster['exceptions'])<=29, 'Invalid exceptions')
        for exception in raster['exceptions']:
            exact_keys(exception, {'criterion','actor','timestamp_utc','statement','evidence'})
            text(exception['criterion'],'criterion'); human(exception)
    exact_keys(job['selected'], {'reveal','motif','raster','background'})
    for role, selected in job['selected'].items():
        if selected is None: continue
        ap.require(isinstance(selected,str), 'Invalid selected identity')
        if role == 'raster':
            ap.require(selected in raster_ids, 'Selected raster missing')
        elif role == 'background' and selected in ('none','standard'): continue
        else:
            ap.require(any(a['id']==selected and a['role']==role for a in job['assets']), 'Selected image missing or swapped')
    seen=set()
    for decision in job['decisions']:
        exact_keys(decision, {'scope','binding','actor','timestamp_utc','statement'})
        scope=decision['scope']; ap.require(scope in SCOPES and scope not in seen, 'Invalid/duplicate decision scope')
        seen.add(scope); human(decision)
        ap.require(decision['binding']==binding(job,scope), 'Stale decision: '+scope)
    for role,selected in job['selected'].items():
        if selected is None or job['operation']=='background' and role=='reveal':continue
        ap.require(role in seen, 'Actual '+role+' choice required before selection')
    all_refs={}
    for ref in references(job):
        if job['format'] == work_assets.FORMAT and own(job['puzzle_id'], ref['file']):
            work_assets.validate(ref, job['puzzle_id'], 64*LIMIT)
            ap.require(ref['asset']['release_id'] == release['id'], 'Foreign release identity')
        else:
            content.reference(ref,limit=64*LIMIT)
        ap.require(own(job['puzzle_id'],ref['file']) or ref['file'].startswith(('game/art/content/','game/art/backgrounds/','game/data/content/')),
                   'Foreign production source')
        ap.require(all_refs.setdefault(ref['file'],ref)==ref, 'Conflicting file bindings')
    from .authoring_build_contract import names
    names(list(all_refs))
    ap.require(len(all_refs)<=2048 and sum(r['bytes'] for r in all_refs.values())<=512*LIMIT, 'Current data exceeds resources')
    ap.require(len(encoded(job))<=LIMIT, 'Current metadata exceeds 1 MiB')
    if job['integration'] is not None:
        exact_keys(job['integration'], {'commit','result'})
        ap.require(isinstance(job['integration']['commit'],str) and re.fullmatch('[0-9a-f]{40}',job['integration']['commit']), 'Invalid registration commit')
        ap.require(job['state']=='registered', 'Unexpected completion')
    return job


def review(value, criteria, *, ready, decisions=()):
    ap.require(isinstance(value,dict) and set(value)<=criteria, 'Unknown visual criterion')
    if ready: ap.require(set(value)==criteria, 'Missing current visual judgments')
    for criterion, finding in value.items():
        exact_keys(finding, {'result','accepted','reason','method','actor','timestamp_utc'})
        ap.require(finding['result'] in ('erfüllt','Warnung','nicht erfüllt','nicht geprüft') and type(finding['accepted']) is bool, 'Invalid visual result')
        for key in ('reason','method','actor'): text(finding[key],key)
        if finding['timestamp_utc'] is not None: ap.timestamp(finding['timestamp_utc'])
        if ready:
            recorded=list(decisions.values()) if isinstance(decisions,dict) else list(decisions)
            accepted=any(criterion in d['statement'] for d in recorded if d.get('scope') in ('background','final','motif','raster'))
            ap.require(finding['result']!='nicht geprüft', 'Visual criterion not checked: '+criterion)
            ap.require(finding['result']=='erfüllt' or criterion not in ('H-07','Q-HG01') and finding['accepted'] and accepted,
                       'Actual editorial acceptance required: '+criterion)


class Checked:
    """Fresh current files only. UI can omit proof execution but never byte checks."""
    def __init__(self, job, read, *, technical=True):
        self.job=validate(deepcopy(job)); self.read=read; self.raw={}; self.rasters={}; self.releases={}
        self.legacy_previews = set()
        j=self.job; phase=PHASES.index(j['state']); selected=j['selected']
        decisions={d['scope']:d for d in j['decisions']}
        for ref in references(j): self.bound(ref,64*LIMIT)
        if phase>=2 and j['operation']=='production':
            ap.require(selected['reveal'] is not None and 'reveal' in decisions, 'Actual reveal approval required')
            ap.require(any(a['role']=='motif' for a in j['assets']), 'Current motif required')
        if phase>=3 and j['operation']=='production':
            ap.require(selected['motif'] is not None and j['parameters']['approved'] and 'motif' in decisions,
                       'Actual motif and parameter approval required')
        for asset in j['assets']:
            raw=self.bound(asset['file'],32*LIMIT)
            # Existing bounded decoder; does not execute data or alter originals.
            image_info(raw,asset['file']['file'],j)
            ready=(asset['id'] in (selected['reveal'],selected['motif']) and phase>=5 and j['operation']=='production' or
                   asset['role']=='background' and phase>=7 and asset['id']==selected['background'])
            if ready:
                ap.require(asset['rights'] is not None, 'Current image rights unresolved')
                review(asset['review'],CRITERIA[asset['role']],ready=True,decisions=decisions)
        for raster in j['rasters']:
            self.raster(raster, technical=technical, ready=phase>=5)
        if phase>=5 and j['operation']=='production': ap.require(j['rasters'], 'Qualified raster offer required')
        if phase>=6 and j['operation']=='production':
            ap.require(selected['raster'] is not None and 'raster' in decisions, 'Actual qualified raster choice required')
        if j['operation']=='background':
            from . import catalog_rating
            registry=io.json_bytes(read(content.REGISTRY,8*LIMIT),8*LIMIT)
            entries=[e for e in registry['entries'] if e['id']==j['puzzle_id']]
            runtime=io.json_bytes(read(content.RUNTIME,8*LIMIT),8*LIMIT)
            rows=[r for r in runtime['entries'] if r['id']==j['puzzle_id']]
            ap.require(len(entries)==len(rows)==1 and entries[0]['mode']==j['target']['mode'] and
                       'game/'+entries[0]['definition']==j['target']['definition']['file'] and
                       'game/'+rows[0]['reveal']==j['target']['reveal']['file'], 'Background target is not current active content')
            reveal_source=content.validate_source(io.json_bytes(read(content.source_path(j['puzzle_id'],'reveal'),LIMIT),LIMIT),entries[0])
            ap.require(reveal_source['current']['asset']==j['target']['reveal'] and
                       reveal_source['binding']['identity']['definition']==j['target']['definition'], 'Active target binding differs')
            definition,_,_,_=catalog_rating.definition(self.bound(j['target']['definition'],2*LIMIT))
            ap.require(definition['id']==j['puzzle_id'], 'Background target differs')
            ap.require(selected['reveal'] is not None and next(a for a in j['assets'] if a['id']==selected['reveal'])['file']==j['target']['reveal'], 'Active reveal reference differs')
        if phase>=7:
            ap.require(selected['background'] is not None and 'background' in decisions, 'Actual background choice or none/standard required')
            if selected['background'] not in ('none','standard'):
                from .catalog_publication import _validate_background_image
                asset=next(a for a in j['assets'] if a['id']==selected['background'])
                with tempfile.TemporaryDirectory(prefix='current-image-') as temp:
                    p=Path(temp)/'background.png'; p.write_bytes(self.bound(asset['file'],32*LIMIT))
                    _validate_background_image(p)
        if phase>=8:
            ap.require('final' in decisions and 'integration' in decisions and not j['blockers'], 'Actual final content/integration decisions required')
        if phase==9:
            ap.require(j['integration'] is not None, 'Registration result missing')
            self.matches(j['integration']['result'])

    def bound(self, ref, limit):
        expected = work_assets.local_ref(ref)
        content.reference(expected,limit=limit)
        name=ref['file']
        if 'asset' in ref and name not in self.raw:
            self.raw[name] = work_assets.read(ref, limit, releases=self.releases)
        if name not in self.raw: self.raw[name]=self.read(name,limit)
        raw=self.raw[name]
        ap.require(len(raw)<=limit and content.ref(name,raw)==expected, 'Current source missing/stale: '+name)
        return raw

    def raster(self, raster, *, technical, ready):
        from . import catalog_rating, current_rating, verifier, palette_quality
        from .editor_raster import check_end
        raw=self.bound(raster['definition'],2*LIMIT)
        definition,puzzle,_,_=catalog_rating.definition(raw)
        ap.require(definition['id']==self.job['puzzle_id'] and definition['width']<=50 and definition['height']<=50, 'Invalid current raster identity/size')
        used = raster_parameters.used_foreground(definition['solution'])
        params=self.job['parameters']['approved']
        values={'width':definition['width'],'height':definition['height'],'foreground_colors':len(used)}
        def accepts_option(p):
            if 'constraints' in p:
                return all(raster_parameters.accepts(p['constraints'][k],v) for k,v in values.items())
            return (all(p['size_constraint']!='exact' or p[axis]==values[axis] for axis in ('width','height')) and
                    (p['foreground_color_constraint']!='exact' or p['foreground_colors']==len(used)))
        matching=[p for p in params if accepts_option(p)]
        modes={p.get('mode') or p['imports'][0]['mode'] for p in matching}
        rating_value=(current_rating.validate(io.json_bytes(self.bound(raster['difficulty'],8*LIMIT),8*LIMIT),
                    definition_bytes=raw,active=False) if raster['difficulty'] is not None else None)
        mode=rating_value.get('production_mode') if rating_value is not None else next(iter(modes)) if len(modes)==1 else None
        ap.require(mode in ('mono','color') and mode in modes, 'Raster requires one complete approved parameter option and an unambiguous explicit mode')
        raster_parameters.require_color_count(mode, len(used))
        ap.require(used == {p['id'] for p in definition['palette']}, 'Palette must contain exactly used colors')
        ap.require(not ready or raster['proof'] is not None and raster['difficulty'] is not None, 'Qualified raster needs proof and difficulty')
        proof=io.json_bytes(self.bound(raster['proof'],64*LIMIT),64*LIMIT) if raster['proof'] is not None else None
        if technical and proof is not None:
            result=verifier.verify(puzzle,proof,Budget(300,1000000))
            ap.require(result['proof_verified'] and (result['certified'] or not ready), 'Complete independently checked current proof required')
            if result['certified']: check_end(definition,proof)
        checked=rating_value
        if ready:
            review(raster['review'],CRITERIA['raster'],ready=True,decisions=self.job['decisions'])
            matrix=definition['solution']
            frame=(any(row[0] for row in matrix) or any(row[-1] for row in matrix)) and (any(matrix[0]) or any(matrix[-1]))
            findings=[] if frame else ['frame']
            for a,b in combinations(definition['palette'],2):
                qa,qb=(palette_quality.quantized_oklab('#'+p['color']) for p in (a,b))
                if palette_quality.pair_status(sum((x-y)**2 for x,y in zip(qa,qb)))=='negative':
                    findings.append('palette:'+str(a['id'])+':'+str(b['id']))
            ap.require(sorted(e['criterion'] for e in raster['exceptions'])==sorted(findings), 'Exact current frame/palette exceptions required')
            for exception in raster['exceptions']:
                ap.require(self.bound(exception['evidence'],65536).decode('utf8').strip(), 'Empty exception evidence')
        self.rasters[raster['id']]={'definition':definition,'mode':mode,'difficulty':checked}
        from tools.production_workspace.presentation import image
        preview=self.bound(raster['preview'],32*LIMIT)
        image(preview)
        from io import BytesIO
        from PIL import Image
        with Image.open(BytesIO(preview)) as actual:
            ap.require(actual.format == 'PNG' and actual.size == (definition['width'] * 12, definition['height'] * 12),
                       'Raster preview differs from current definition')
            pixels = actual.convert('RGBA').tobytes()
        if pixels != raster_image(definition, neutral=mode == 'mono').tobytes():
            ap.require(mode == 'mono' and pixels == raster_image(definition, neutral=False).tobytes(),
                       'Raster preview differs from current definition')
            self.legacy_previews.add(raster['id'])

    def check_new_previews(self, previous):
        # Reusing an established binding is allowed even when publishing a later phase.
        def identity(raster):
            return (raster['id'], raster['definition']['sha256'], raster['preview']['sha256'])
        old = {identity(raster) for raster in previous['rasters']} if previous else set()
        for raster in self.job['rasters']:
            if raster['id'] in self.legacy_previews:
                ap.require(identity(raster) in old, 'New mono raster preview must use neutral black')

    def matches(self,result):
        rating=self.rasters[self.job['selected']['raster']]['difficulty'] if self.job['operation']=='production' else None
        return matches(self.job,result,rating=rating)

    def recheck(self):
        external = {r['file'] for r in references(self.job) if 'asset' in r}
        for name,raw in self.raw.items():
            if name not in external:
                ap.require(self.read(name,max(len(raw),1))==raw, 'Current input changed: '+name)


def checkpoint(name):
    io.tick()


def _atomic(root, name, raw):
    from .authoring_builder import write_new
    target=io.safe(root,name); target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.current-write-',dir=target.parent) as temporary:
        stage=Path(temporary)/'data'; write_new(stage,raw)
        ap.require(stage.read_bytes()==raw, 'Staged current bytes differ')
        os.replace(stage,io.safe(root,name))


@io.bounded
def build(request, source_root, root):
    """Current publication, compare-and-swap and bounded recovery under one writer."""
    from .authoring_builder import writer, git_root, index_value, write_new
    exact_keys(request, {'format','record','expected','files'})
    ap.require(request['format']==REQUEST, 'Current publication request required')
    # Roundtrip rejects NaN, duplicate/schema surprises and caller mutation.
    request=io.json_bytes(encoded(request),4*LIMIT)
    validate(request['record'])
    ap.require(isinstance(request['files'],list) and len(request['files'])<=2048, 'Invalid current payload')
    for item in request['files']:exact_keys(item, {'path','source','sha256','bytes'})
    original_refs={r['file'] for r in references(request['record'])}
    job=validate(compact(request['record'])); request['record']=job
    retained={r['file'] for r in references(job)}
    ap.require(all(i['path'] in original_refs for i in request['files']), 'Unreferenced current payload')
    request['files']=[i for i in request['files'] if i['path'] in retained]
    name=path(job['puzzle_id'])
    root=io.external(root); source_root=io.external(source_root)
    ap.require(root.is_dir() and source_root.is_dir(), 'Explicit roots required')
    ap.require(request['expected'] is None or isinstance(request['expected'],str) and re.fullmatch('[0-9a-f]{64}',request['expected']), 'Invalid expected record')
    ap.require(isinstance(request['files'],list) and len(request['files'])<=2048, 'Invalid current payload')
    wanted={ref['file']:ref for ref in references(job)}; payload={}; observed={}
    for item in request['files']:
        exact_keys(item, {'path','source','sha256','bytes'})
        ap.relative(item['source']); ap.relative(item['path'])
        ap.require(item['path'] in wanted and own(job['puzzle_id'],item['path']) and item['path']!=name, 'Only declared own current files may be published')
        ref={'file':item['path'],'sha256':item['sha256'],'bytes':item['bytes']}
        ap.require(ref==wanted[item['path']] and item['path'] not in payload, 'Payload binding differs')
        raw=io.read(source_root,item['source'],64*LIMIT)
        ap.require(content.ref(item['path'],raw)==ref, 'Changed current payload')
        payload[item['path']]=raw; observed[item['source']]=raw
    with writer(git_root(root)/'authoring-builder.lock'):
        journal_name='content/authoring/'+job['puzzle_id']+'/.current-operation.json'
        pending_raw=io.read(root,journal_name,20*LIMIT,missing=True)
        before=io.read(root,name,LIMIT,missing=True); after=encoded(job)
        index_raw=io.read(root,INDEX,8*LIMIT,missing=True)
        index=index_value(index_raw) if index_raw is not None else {'format':'picross-authoring-index-v1','entries':[]}
        row={'puzzle_id':job['puzzle_id'],'revision':'current','record':name}
        next_index={**index,'entries':[r for r in index['entries'] if r['record']!=name]+[row]}
        next_index['entries'].sort(key=lambda r:(r['puzzle_id'],r['revision']))
        index_after=encoded(next_index)
        if pending_raw is not None:
            journal=io.json_bytes(pending_raw,20*LIMIT)
            exact_keys(journal, {'format','request_sha256','before','after','index_before','index_after','remove','writes'})
            ap.require(journal['format']=='picross-current-authoring-operation-v1' and journal['request_sha256']==digest(request) and journal['after']==job,
                       'Another current operation requires its identical request')
            old=journal['before']; prior=encoded(old) if old is not None else None
            ap.require(io.checksum(prior)==request['expected'], 'Journal predecessor does not match request')
            if old is not None: validate(old)
            expected_remove={r['file']:r for r in references(old) if own(job['puzzle_id'],r['file']) and r['file'] not in wanted} if old else {}
            ap.require(all(r==expected_remove.get(r['file']) for r in journal['remove']) and
                       journal['writes']==[wanted[n] for n in sorted(payload)], 'Foreign current journal paths')
            old_index=journal['index_before'] or {'format':'picross-authoring-index-v1','entries':[]}
            index_value(encoded(old_index)); index_value(encoded(journal['index_after']))
            allowed_index={**old_index,'entries':sorted([r for r in old_index['entries'] if r['record']!=name]+[row],key=lambda r:(r['puzzle_id'],r['revision']))}
            ap.require(journal['index_after']==allowed_index, 'Foreign current index delta')
            ap.require(before in (prior,after) and index_raw in (None if journal['index_before'] is None else encoded(journal['index_before']),encoded(journal['index_after'])), 'Foreign current operation bytes')
            next_index=journal['index_after']; index_after=encoded(next_index)
        else:
            ap.require(io.checksum(before)==request['expected'] or before==after, 'Current record conflict')
            old=io.json_bytes(before,LIMIT) if before is not None else None
            if old is not None:
                validate(old); ap.require(old['test_only']==job['test_only'], 'Cannot change production scope')
                ap.require(old['operation']==job['operation'] and all(job['budgets']['used'][k]>=v for k,v in old['budgets']['used'].items()), 'Current job cannot reset consumed budgets')
                if any(job['budgets']['limits'][k]>v for k,v in old['budgets']['limits'].items()):
                    ap.require(any(d['scope']=='budget' and d['binding']==binding(job,'budget') for d in job['decisions']), 'Budget increase needs actual authorization')
            remove={ref['file']:ref for ref in references(old) if own(job['puzzle_id'],ref['file']) and 'asset' not in ref and ref['file'] not in wanted} if old else {}
            # Other current jobs may intentionally share an input; never delete their refs.
            for other in index['entries']:
                if other['record']==name: continue
                other_raw=io.read(root,other['record'],LIMIT)
                other_value=io.json_bytes(other_raw,LIMIT)
                if other_value.get('format')==FORMAT:
                    for ref in references(validate(other_value)): remove.pop(ref['file'],None)
            journal={'format':'picross-current-authoring-operation-v1','request_sha256':digest(request),'before':old,'after':job,
                     'index_before':index if index_raw is not None else None,'index_after':next_index,
                     'remove':list(remove.values()),'writes':[wanted[n] for n in sorted(payload)]}
        def read(n,limit): return payload[n] if n in payload else io.read(root,n,limit)
        checked=Checked(job,read)
        # Local resume mirrors the exact remote record before editing. For a
        # retry, the journal above supplies the original predecessor.
        checked.check_new_previews(old)
        for source,raw in observed.items(): ap.require(io.read(source_root,source,max(len(raw),1))==raw, 'Payload source changed')
        for ref in journal['remove']:
            raw=io.read(root,ref['file'],64*LIMIT,missing=True)
            ap.require(raw is None and pending_raw is not None or raw is not None and content.ref(ref['file'],raw)==ref, 'Retired current file changed')
        for n,raw in payload.items():
            existing=io.read(root,n,64*LIMIT,missing=True)
            ap.require(existing is None or existing==raw, 'Existing current payload conflict')
        if before==after and index_raw==index_after and pending_raw is None:
            checked.recheck(); return {'format':FORMAT,'status':'reused','record':name}
        checked.recheck()
        if pending_raw is None:
            target=io.safe(root,journal_name); target.parent.mkdir(parents=True,exist_ok=True)
            pending_raw=encoded(journal); _create(root,journal_name,pending_raw)
        checkpoint('journal')
        for n,raw in payload.items():
            target=io.safe(root,n); existing=io.read(root,n,64*LIMIT,missing=True)
            ap.require(existing is None or existing==raw, 'Current payload changed')
            if existing is None:
                target.parent.mkdir(parents=True,exist_ok=True); _create(root,n,raw)
            ap.require(io.read(root,n,len(raw))==raw, 'Written current file differs')
        checkpoint('files')
        checked.recheck()
        ap.require(io.read(root,name,LIMIT,missing=True)==before, 'Current record changed')
        if before!=after: _atomic(root,name,after)
        checkpoint('record')
        ap.require(io.read(root,name,LIMIT)==after, 'Published current record changed')
        for ref in references(job):
            if 'asset' not in ref: ap.require(content.ref(ref['file'],io.read(root,ref['file'],64*LIMIT))==ref,'Published current input changed')
        ap.require(io.read(root,INDEX,8*LIMIT,missing=True)==index_raw, 'Current index changed')
        if index_raw!=index_after: _atomic(root,INDEX,index_after)
        checkpoint('index')
        ap.require(io.read(root,name,LIMIT)==after and io.read(root,INDEX,8*LIMIT)==index_after,'Published current state changed')
        for ref in references(job):
            if 'asset' not in ref: ap.require(content.ref(ref['file'],io.read(root,ref['file'],64*LIMIT))==ref,'Published current input changed')
        for ref in journal['remove']:
            raw=io.read(root,ref['file'],64*LIMIT,missing=True)
            if raw is not None:
                ap.require(content.ref(ref['file'],raw)==ref, 'Foreign discarded file'); io.safe(root,ref['file']).unlink()
        checkpoint('pruned')
        ap.require(io.read(root,journal_name,20*LIMIT)==pending_raw, 'Operation journal changed')
        io.safe(root,journal_name).unlink()
        return {'format':job['format'],'status':'built','record':name}


def projection(job, record_raw):
    """Transient view only: no workspace or pointer file, no second data authority."""
    validate(job)
    from tools.production_workspace import presentation as p
    ref={'commit':None,**content.ref(path(job['puzzle_id']),record_raw)}
    assets=[]; offers=[]
    for asset in job['assets']:
        if asset['role']=='input': continue
        assets.append({'id':asset['id'],'role':asset['role'],'caption':asset['label'],
                       'location':{'commit':None,'storage':'repository','container':None,**asset['file']}})
        if asset['role'] in ('reveal','background') and job['selected'][asset['role']] is None:
            offers.append({'id':asset['id'],'kind':asset['role'],'label':asset['label'],'record':ref,'asset_ids':[asset['id']]})
    if job['operation']=='background':
        assets.append({'id':'active-raster','role':'raster','caption':'Aktives unverändertes Raster',
                       'location':{'commit':None,'storage':'definition','container':None,**job['target']['definition']}})
    qualified=PHASES.index(job['state'])>=5
    for raster in job['rasters']:
        assets.append({'id':raster['id'],'role':'raster' if qualified else 'raster_draft','caption':raster['label'],
                       'location':{'commit':None,'storage':'definition','container':None,**raster['definition']}})
        if qualified and job['selected']['raster'] is None:
            offers.append({'id':raster['id'],'kind':'raster','label':raster['label'],'record':ref,'asset_ids':[raster['id']]})
    return {'format':p.CURRENT_FORMAT,'puzzle_id':job['puzzle_id'],'revision':'current','record':ref,
            'title':job['title'],'assets':assets,'offers':offers}


def detail(source, commit, value):
    raw=source.read(commit,value['record']['file'],LIMIT)
    ap.require(content.ref(value['record']['file'],raw)=={k:value['record'][k] for k in ('file','sha256','bytes')}, 'Current view changed')
    job=io.json_bytes(raw,LIMIT)
    ap.require(projection(job,raw)==value, 'View does not match current offers')
    checked=Checked(job,lambda n,limit:source.read(commit,n,limit),technical=False)
    selected=job['selected']; raster=checked.rasters.get(selected['raster'])
    if raster is None and len(checked.rasters)==1: raster=next(iter(checked.rasters.values()))
    from . import catalog_rating
    metadata=dict.fromkeys(('width','height','mode','used_colors','difficulty'))
    if raster:
        d=raster['definition']; metadata.update(width=d['width'],height=d['height'],mode=raster['mode'],
                used_colors=len(d['palette']),difficulty=catalog_rating.project(raster['difficulty']) if raster['difficulty'] else None)
    from tools.production_workspace.motifs import PHASES as labels
    composition=None
    if selected['raster'] is not None or job['operation']=='background':
        composition={'raster':'active-raster' if job['operation']=='background' else selected['raster'],'reveal':selected['reveal'],
                     'background':None if selected['background'] in (None,'none','standard') else selected['background']}
    raster_modes = {identifier: raster['mode'] for identifier, raster in checked.rasters.items()}
    if job['operation'] == 'background':
        raster_modes['active-raster'] = job['target']['mode']
    checked.recheck()
    return {'state':job['state'],'blockers':job['blockers'],'raster_modes':raster_modes,
            'published':{'brief':{'text':job['brief']},'role':'approved' if job['parameters']['approved'] else 'proposed' if job['parameters']['proposed'] else 'absent',
                         'approved':job['parameters']['approved'],'proposed':job['parameters']['proposed']},
            'metadata':metadata,'composition':composition,'originals':{'record':job},'authoring_version':'0.8.0',
            'background_status':'pending' if selected['background'] is None else 'ready',
            'background_choice':selected['background'],'next_step':labels[job['state']],
            'test_only':job['test_only'],'verification':'Aktuelle Datei-/Angebotsbindungen geprüft; keine neue Bildfreigabe.'}


def compact(job):
    """Retain offered alternatives until an actual choice, then just active inputs."""
    result=deepcopy(job)
    for role in ('reveal','motif','background'):
        selected=result['selected'][role]
        if selected is not None:
            result['assets']=[a for a in result['assets'] if a['role']!=role or a['id']==selected]
    if result['selected']['raster'] is not None:
        result['rasters']=[r for r in result['rasters'] if r['id']==result['selected']['raster']]
    return result


@io.bounded
def prepare(root, record_path, output, *, entry=None):
    """Derive the sole RI-ONE input from the chosen current result and real decisions."""
    from . import integration_input
    root=io.external(root); output=io.external(output)
    raw=io.read(root,record_path,LIMIT); job=io.json_bytes(raw,LIMIT)
    ap.require(record_path==path(job['puzzle_id']) and job['state'] in ('editorially_approved','registered'), 'Final approved current job required')
    checked=Checked(job,lambda n,limit:io.read(root,n,limit))
    if job['operation']=='background':
        return prepare_background_change(job,checked,output)
    selected=job['selected']; raster=next(r for r in job['rasters'] if r['id']==selected['raster'])
    facts=checked.rasters[raster['id']]; definition=facts['definition']
    reveal=next(a for a in job['assets'] if a['id']==selected['reveal'])
    if entry is None:
        entry={'id':job['puzzle_id'],'key':job['puzzle_id'],'save_slot':job['puzzle_id'],
               'definition':'data/content/'+job['puzzle_id']+'.json',
               'reveal':definition['reveal']['image'].removeprefix('res://'),'visible':True,
               'mode':facts['mode'],'category_id':job['category_id']}
    content.entries([entry])
    ap.require(entry['id']==job['puzzle_id'] and entry['mode']==facts['mode'] and entry['category_id']==job['category_id'], 'Integration target differs')
    ap.require(not output.exists(), 'Integration output already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.current-export-',dir=output.parent) as temporary:
        stage=Path(temporary)/'input';stage.mkdir()
        def put(name,data):
            (stage/name).write_bytes(data); return content.ref(name,data)
        def image(asset,stem):
            rights=asset['rights']; ap.require(rights is not None,'Actual usage basis required')
            # These are the supplied actual rights, not invented provenance.
            notice='\n'.join(k+': '+rights[k] for k in sorted(rights)).encode('utf8')+b'\n'
            ext=Path(asset['file']['file']).suffix
            return {'asset':put(stem+ext,checked.bound(asset['file'],32*LIMIT)),
                    'notice':put(stem+'.txt',notice),'rights':rights}
        bg=selected['background']; background={'status':bg if bg in ('none','standard') else 'selected','image':None}
        if background['status']=='selected':
            background['image']=image(next(a for a in job['assets'] if a['id']==bg),'background')
        decisions={d['scope']:d for d in job['decisions']}; final=decisions['final']; order=decisions['integration']
        quality={'criteria':{k:{'result':{'erfüllt':'fulfilled','Warnung':'borderline','nicht erfüllt':'failed'}[raster['review'][k]['result']],
                                  'accepted':raster['review'][k]['accepted'],'reason':raster['review'][k]['reason']}
                             for k in ('Q-R04','Q-H01','Q-H02')},
                 **{k:final[k] for k in ('actor','timestamp_utc','statement')}}
        exceptions=[]
        for i,e in enumerate(raster['exceptions']):
            exceptions.append({**e,'evidence':put('exception-'+str(i)+'.txt',checked.bound(e['evidence'],65536))})
        manifest={'format':integration_input.FORMAT,'entry':entry,
                  'metadata':{'id':job['puzzle_id'],'name':job['title'],'category_id':job['category_id']},
                  'definition':put('definition.json',checked.bound(raster['definition'],2*LIMIT)),
                  'reveal':image(reveal,'reveal'),'background':background,
                  'proof':put('proof.json',checked.bound(raster['proof'],64*LIMIT)),
                  'difficulty':put('difficulty.json',checked.bound(raster['difficulty'],8*LIMIT)),
                  'quality':{'review':put('review.json',encoded(quality)),'exceptions':exceptions},'test_only':job['test_only']}
        manifest['approval']={**{k:order[k] for k in ('actor','timestamp_utc','statement')},
                              'selection_sha256':integration_input.selection(manifest),
                              'evidence':put('approval.txt',(final['statement']+'\n'+order['statement']+'\n').encode('utf8')),
                              'checks':dict.fromkeys(integration_input.CHECKS,True)}
        put('manifest.json',encoded(manifest))
        integration_input.Input(stage)
        checked.recheck(); ap.require(io.read(root,record_path,LIMIT)==raw,'Current job changed during export')
        from .catalog_publication import rename
        rename(stage,output,replace=False)
    return {'status':'exported','id':job['puzzle_id'],'output':str(output)}


def matches(job, result, *, rating=None):
    """A completion is bound to current selected bytes, never an arbitrary same-ID result."""
    selected=job['selected']
    raster=({'definition':job['target']['definition']} if job['operation']=='background' else next(r for r in job['rasters'] if r['id']==selected['raster']))
    reveal=next(a for a in job['assets'] if a['id']==selected['reveal'])
    ap.require(result['entry']['id']==job['puzzle_id'] and result['metadata']==
               {'id':job['puzzle_id'],'name':job['title'],'category_id':job['category_id']}, 'Completion metadata differs')
    def same(ref, path):
        actual=result['files'].get(path)
        return actual is not None and all(actual[k]==ref[k] for k in ('sha256','bytes'))
    ap.require(same(raster['definition'],'game/'+result['entry']['definition']) and
               same(reveal['file'],'game/'+result['runtime']['reveal']), 'Completion contains different selected bytes')
    if job['operation']=='production':
        from . import catalog_rating
        ap.require(rating is not None,'Current selected assessment required')
        mode=rating['production_mode']
        rights=reveal['rights'];ap.require(rights is not None,'Current reveal rights missing')
        notice=('\n'.join(k+': '+rights[k] for k in sorted(rights))+'\n').encode('utf8')
        notice_path=content.notice_path(result['entry'])
        ap.require(same(content.ref(notice_path,notice),notice_path),'Completion reveal rights differ')
        rating_path=catalog_rating.path(job['puzzle_id'])
        rating_bytes=catalog_rating.encoded(catalog_rating.active_record(rating))
        ap.require(same(content.ref(rating_path,rating_bytes),rating_path) and
                   result['runtime']['difficulty']==catalog_rating.project(rating),'Completion assessment differs')
    else:mode=job['target']['mode']
    ap.require(result['mode']==mode, 'Completion mode differs')
    bg=selected['background']; actual=result['runtime']['background']
    ap.require(actual['status']==(bg if bg in ('none','standard') else 'selected'), 'Completion background differs')
    if actual['status']=='selected':
        a=next(a for a in job['assets'] if a['id']==bg)
        ap.require(same(a['file'],'game/'+actual['asset']['file']), 'Completion selected another background')
        rights=a['rights']
        ap.require(rights is not None,'Current background rights missing')
        notice=('\n'.join(k+': '+rights[k] for k in sorted(rights))+'\n').encode('utf8')
        notice_path='game/art/backgrounds/'+job['puzzle_id']+'.txt'
        ap.require(same(content.ref(notice_path,notice),notice_path),'Completion background rights differ')
    return True


@io.bounded
def complete(root, record_path, commit, *, current_input):
    from . import catalog_integration, integration_input, current_delivery
    from tools.production_workspace.sources import LocalSource, check_commit
    root=io.external(root); check_commit(commit)
    source=LocalSource(root)
    raw=source.read(None,record_path); job=io.json_bytes(raw,LIMIT)
    ap.require(record_path==path(job['puzzle_id']) and job['state'] in ('editorially_approved','registered'), 'Current final approval required')
    checked=Checked(job,lambda n,limit:source.read(None,n,limit))
    incoming=None
    if job['operation']=='production':
        incoming=integration_input.Input(current_input)
        ap.require(incoming.entry['id']==job['puzzle_id'], 'Selected input belongs to another job')
        with tempfile.TemporaryDirectory(prefix='current-completion-') as temporary:
            expected=Path(temporary)/'input'
            prepare(root,record_path,expected,entry=incoming.entry)
            ap.require(incoming.value==integration_input.Input(expected).value, 'Input differs from current approved result')
    else:
        prepared=io.json_bytes(io.read(io.external(current_input),'request.json',LIMIT),LIMIT)
        with tempfile.TemporaryDirectory(prefix='current-completion-') as temporary:
            expected=Path(temporary)/'input'
            prepare(root,record_path,expected)
            ap.require(prepared==io.json_bytes((expected/'request.json').read_bytes(),LIMIT), 'Background handoff differs')
            for name in prepared['imports'].values():
                ap.require(io.read(io.external(current_input),name,32*LIMIT)==(expected/name).read_bytes(), 'Background input changed')
    result=current_delivery.snapshot(lambda n,limit,missing=False:source.read(commit,n,limit,missing),job['puzzle_id'])
    checked.matches(result)
    if incoming is not None:
        registry=io.json_bytes(source.read(commit,content.REGISTRY,8*LIMIT),8*LIMIT)
        actual=content.selected(None,registry,job['puzzle_id'],read=lambda n,limit,missing=False:source.read(commit,n,limit,missing))
        ap.require(catalog_integration.same(actual,incoming), 'Commit differs from selected current integration input')
    if job['integration'] is not None:
        ap.require(job['integration']=={'commit':commit,'result':result}, 'Conflicting current completion')
    after=deepcopy(job);after.update(state='registered',integration={'commit':commit,'result':result},blockers=[])
    if incoming is not None: incoming.recheck()
    source.recheck()
    request={'format':REQUEST,'record':after,'expected':io.checksum(raw),'files':[]}
    return build(request,root,root)


@io.bounded
def retire(root, ids, integrated_commit, *, source_commits=None):
    """Close selected work at its own work ref; require only final product in main."""
    from tools.production_workspace.sources import git, check_commit
    from .authoring_builder import writer, git_root, index_value
    from . import current_delivery
    root=io.external(root); check_commit(integrated_commit)
    ap.require(ids and len(ids)==len(set(ids)), 'Select unique current jobs')
    git(root,'merge-base','--is-ancestor',integrated_commit,'origin/main')
    main=git(root,'rev-parse','origin/main').decode().strip()
    index_raw=io.read(root,INDEX,8*LIMIT); index=index_value(index_raw)
    removals={}; selected=[]
    source_commits=source_commits or {}
    ap.require(set(source_commits)<=set(ids), 'Foreign work source')
    with writer(git_root(root)/'authoring-builder.lock'):
        for identity_id in ids:
            record_path=path(identity_id)
            rows=[r for r in index['entries'] if r['puzzle_id']==identity_id]
            if not rows:
                ap.require(io.read(root,record_path,LIMIT,missing=True) is None, 'Unindexed current work remains')
                continue
            ap.require(rows==[{'puzzle_id':identity_id,'revision':'current','record':record_path}], 'Legacy or other open work requires explicit treatment')
            ap.require(io.read(root,'content/authoring/'+identity_id+'/.current-operation.json',20*LIMIT,missing=True) is None, 'Current publication is incomplete')
            work_commit=source_commits.get(identity_id,git(root,'rev-parse','HEAD').decode().strip())
            check_commit(work_commit); git(root,'merge-base','--is-ancestor',work_commit,'HEAD')
            # Optional background TXT is genuinely allowed to be absent.
            from tools.production_workspace.sources import GitSource
            source=GitSource(root)
            result=current_delivery.snapshot(lambda n,limit,missing=False:source.read(main,n,limit,missing),identity_id)
            raw=io.read(root,record_path,LIMIT,missing=True)
            if raw is None: raw=source.read(work_commit,record_path,LIMIT)
            job=io.json_bytes(raw,LIMIT)
            validate(job); ap.require(job['state']=='registered' and job['integration'] is not None, 'Current work has not completed')
            ap.require(current_delivery.same(result,job['integration']['result']), 'Confirmed main contains different selected data')
            def current_work(name,limit):
                data=io.read(root,name,limit,missing=True)
                if data is None:
                    ap.require(own(identity_id,name),'Missing active retirement input: '+name)
                    data=source.read(work_commit,name,limit)
                return data
            checked=Checked(job,current_work,technical=False)
            checked.matches(result);checked.recheck()
            expected={record_path:io.read(root,record_path,LIMIT,missing=True)}
            for ref in references(job):
                if own(identity_id,ref['file']) and 'asset' not in ref:
                    data=io.read(root,ref['file'],64*LIMIT,missing=True)
                    # A prior interrupted removal may have deleted only own declared files.
                    if data is not None: ap.require(content.ref(ref['file'],data)==ref,'Completed current file changed')
                    expected[ref['file']]=data
            directory=io.safe(root,'content/authoring/'+identity_id)
            for child in directory.rglob('*'):
                name=child.relative_to(root).as_posix(); checked=io.safe(root,name)
                if checked.is_file(): ap.require(name in expected,'Unknown/open file in selected work: '+name)
            for name,data in expected.items():
                saved=source.read(work_commit,name,64*LIMIT)
                if data is not None: ap.require(data==saved,'Work differs from its committed source')
            ap.require(not git(root,'diff','--cached','--name-only','--','content/authoring/'+identity_id).strip(), 'Staged work edit')
            removals.update({n:b for n,b in expected.items() if b is not None}); selected.append(identity_id)
        if not selected: return {'status':'no-op','main_commit':main,'retired':[],'registered':True}
        ap.require(io.read(root,INDEX,8*LIMIT)==index_raw,'Current index changed')
        # Delete data first, records last; retry can verify missing declared data against work_commit.
        for name in sorted(removals,key=lambda n:n.endswith('/record.json')):
            ap.require(io.read(root,name,64*LIMIT)==removals[name],'Completed work changed')
            io.safe(root,name).unlink()
        updated={**index,'entries':[r for r in index['entries'] if r['puzzle_id'] not in selected]}
        ap.require(io.read(root,INDEX,8*LIMIT)==index_raw,'Current index changed')
        _atomic(root,INDEX,encoded(updated))
    return {'status':'retired','main_commit':main,'retired':sorted(removals),'registered':True}


def image_info(raw, name, job):
    if (job['operation']=='background' and name==job['target']['reveal']['file'] and name.endswith('.svg')):
        from .editor_image_input import validate_reveal
        result=validate_reveal(raw,'.svg')
        return {'width':result['width'],'height':result['height'],'mime':'image/svg+xml'}
    from tools.production_workspace.presentation import image
    return image(raw)


def raster_image(definition, *, neutral):
    from PIL import Image
    palette = {p['id']: (0, 0, 0, 255) if neutral else tuple(bytes.fromhex(p['color'])) + (255,)
               for p in definition['palette']}
    palette[0] = (0, 0, 0, 0)
    image = Image.new('RGBA', (definition['width'], definition['height']))
    image.putdata([palette[cell] for row in definition['solution'] for cell in row])
    return image.resize((image.width * 12, image.height * 12), Image.Resampling.NEAREST)


def raster_preview(definition, *, mode):
    from io import BytesIO
    ap.require(mode in ('mono', 'color'), 'Raster preview requires a bound production mode')
    stream = BytesIO()
    raster_image(definition, neutral=mode == 'mono').save(stream, format='PNG')
    return stream.getvalue()


def prepare_background_change(job, checked, output):
    """Existing content uses the shared current editor, never a second integrator."""
    ap.require(not output.exists(), 'Background handoff already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    choice=job['selected']['background']; status=choice if choice in ('none','standard') else 'selected'
    request={'format':'picross-editor-request-v2','id':job['puzzle_id'],'metadata':None,'text':None,'profile':None,
             'reveal':None,'background':{'status':status,'upload':'background' if status=='selected' else None},'imports':{}}
    with tempfile.TemporaryDirectory(prefix='.current-background-',dir=output.parent) as temporary:
        stage=Path(temporary)/'input';stage.mkdir()
        if status=='selected':
            asset=next(a for a in job['assets'] if a['id']==choice)
            (stage/'background.png').write_bytes(checked.bound(asset['file'],32*LIMIT))
            request['imports']={'background':'background.png'}
            request['background']['rights']=asset['rights']
        (stage/'request.json').write_bytes(encoded(request))
        checked.recheck()
        from .catalog_publication import rename
        rename(stage,output,replace=False)
    return {'status':'exported','operation':'background','id':job['puzzle_id'],'output':str(output)}


@io.bounded
def prepare_background(source, output, *, profile_id='picross-background-png2304x768-v1'):
    """Prepare current image bytes only; no generation/derivation/provenance archive."""
    from .background_render import _render
    from .background_contract import PROFILES
    from .authoring_builder import write_new
    source=io.external(source);output=io.external(output)
    raw=io.read(source.parent,source.name,32*LIMIT)
    ap.require(profile_id in PROFILES, 'Unknown explicit background profile')
    profile=PROFILES[profile_id]
    class Deadline:
        def check(self): io.tick()
    rendered,_=_render(raw,Deadline(),profile)
    ap.require(not output.exists() and output.parent.is_dir(), 'New explicit current image path required')
    ap.require(io.read(source.parent,source.name,32*LIMIT)==raw,'Source changed during current preparation')
    _create(output.parent,output.name,rendered)
    ap.require(io.read(output.parent,output.name,32*LIMIT)==rendered,'Current prepared image differs')
    return content.ref(output.name,rendered)


def _create(root, name, raw):
    """Atomic no-replace payload publication; a partial write never becomes active."""
    from .authoring_builder import write_new
    target=io.safe(root,name)
    with tempfile.TemporaryDirectory(prefix='.current-payload-',dir=target.parent) as temporary:
        stage=Path(temporary)/'payload';write_new(stage,raw)
        ap.require(stage.read_bytes()==raw,'Staged payload differs')
        os.link(stage,io.safe(root,name),follow_symlinks=False)
        stage.unlink()
