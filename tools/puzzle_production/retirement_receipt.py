"""Closed technical receipt v4, preserving actual export rights and Git origins."""
from copy import deepcopy
import re
from . import catalog_io as io, catalog_background as bg, reveal_source as reveal
from . import content_registry as registry, categories
from .authoring_package import require, sha
from .contract import canonical_bytes, exact_keys, integer

FORMAT = 'picross-integrated-content-v4'
LIMIT = 8*1024*1024


def commit(value):
    require(isinstance(value,str) and re.fullmatch(r'[0-9a-f]{40}',value), 'Invalid retirement Git identity')
    return value


def validate(value, entry, notice_hash):
    exact_keys(value, {'format','entry','integrated_commit','notice_sha256','provenance'})
    require(value['format']==FORMAT and value['entry']==entry and value['notice_sha256']==sha(notice_hash), 'Retirement receipt identity differs')
    commit(value['integrated_commit'])
    p = exact_keys(value['provenance'], {'source_commit','main_commit','package_tree','export_manifest','notice','background'})
    for name in ('source_commit','main_commit','package_tree'): commit(p[name])
    ref = exact_keys(p['export_manifest'], {'file','sha256','bytes'})
    require(ref['file']==entry['production']['package']+'/manifest.json' and sha(ref['sha256'])==entry['production']['package_sha256'], 'Retirement export anchor differs')
    integer(ref['bytes'],1,LIMIT,'export manifest bytes')
    reveal.notice(p['notice'])
    require(p['notice']['sha256']==notice_hash,'Retirement original notice differs')
    if p['background'] is not None:
        bg._validate_v1(p['background'],entry)
        require(p['background']['origin']['export_manifest_sha256']==ref['sha256'], 'Retirement background original differs')
    require(len(canonical_bytes(value))+1<=LIMIT,'Retirement receipt exceeds limit')
    return value


def build(root, entry, manifest, notice_hash, integrated, main, source, git):
    from .reveal_retirement import index_rows, selection
    prefix = entry['production']['package']
    # Source/import equality uses tree metadata, never reads historical ZIP blobs.
    imported_tree = git('rev-parse', integrated+':'+prefix).decode().strip()
    require(git('cat-file','-t',imported_tree).strip()==b'tree', 'Missing imported package tree')
    require(git('rev-parse',source+':'+prefix).decode().strip()==imported_tree, 'Source/import package trees differ')
    def small(name, limit=LIMIT):
        require(int(git('cat-file','-s',source+':'+name))<=limit,'Historical retirement source exceeds limit')
        return io.json_bytes(git('show',source+':'+name),limit)
    historical = registry.validate(small(registry.REGISTRY), categories.validate(small(categories.PATH,categories.MAX_BYTES)))
    require(next((e for e in historical['entries'] if e['id']==entry['id']),None)==entry,'Original source registry differs')
    rows = index_rows(small('content/authoring/index.json'))
    selected = selection(entry['id'],entry['production']['revision'])
    require(selected in rows,'Missing original registered authoring source')
    record = small(rows[selected]['record'])
    require(record.get('format') in ('picross-authoring-record-v1','picross-authoring-record-v2','picross-authoring-record-v3','picross-authoring-record-v4') and
            record.get('puzzle_id')==entry['id'] and record.get('revision')==entry['production']['revision'] and
            record.get('state')=='registered' and record.get('blockers')==[], 'Original authoring source is not completed')
    from .content_update import notice_path
    notice = io.read(root,prefix+'/runtime/'+notice_path(entry).removeprefix('game/'),65536)
    require(io.checksum(notice)==notice_hash,'Original rights notice differs')
    exported = bg.build(io.safe(root,prefix),manifest,None,entry) if manifest['format']=='picross-target-export-v6' else None
    raw = io.read(root,prefix+'/manifest.json',LIMIT)
    return validate({'format':FORMAT,'entry':deepcopy(entry),'integrated_commit':integrated,'notice_sha256':notice_hash,
                     'provenance':{'source_commit':source,'main_commit':main,'package_tree':imported_tree,
                                   'export_manifest':bg.ref(prefix+'/manifest.json',raw),'notice':reveal.make_notice(notice),
                                   'background':exported}},entry,notice_hash)
