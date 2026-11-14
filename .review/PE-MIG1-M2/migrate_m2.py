"""PE-MIG1/M2 one-off external plan/apply/rollback; never shipped in the editor.

Run with the trusted main tools on PYTHONPATH and PYTHONDONTWRITEBYTECODE=1.
The closed plan contains the entire pre-state inventory and exact changed bytes.
The shared writer lock contains the complete plan, so a lost external plan is
recoverable with this script's rollback command. Unknown locks are never removed.
No general catalog-recovery dispatch is added for this temporary generation.
"""
import argparse
import base64
from copy import deepcopy
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

from tools.puzzle_production import catalog_io as io, editor_change as edit
from tools.puzzle_production import catalog_background as bg, reveal_source as reveal
from tools.puzzle_production import catalog_publication as pub
from tools.puzzle_production.contract import digest, exact_keys
from tools.puzzle_production.authoring_package import require

FORMAT = 'picross-oneoff-641-m2-plan-v1'
JOURNAL = 'picross-oneoff-641-m2-journal-v1'
BASE = '15ceb9b8fe54e2003883d623d1358d3cfc2d062d'
RUNTIME = 'game/data/registry.json'
REGISTRY = 'content/registry.json'
LOCK = edit.LOCK
STAGE = 'content/.registration-journal-641-m2.tmp'
LIMIT = 128 * 1024 * 1024


def read(root, name, missing=False):
    return io.read(root, name, LIMIT, missing=missing)


def obj(raw): return io.json_bytes(raw, LIMIT)
def encode(value): return edit.encoded(value)
def pack(raw): return base64.b64encode(raw).decode('ascii') if raw is not None else None


def unpack(value):
    if value is None: return None
    require(isinstance(value, str) and len(value) <= 16*1024*1024, 'Oversized plan side')
    raw = base64.b64decode(value, validate=True)
    require(pack(raw) == value, 'Noncanonical plan side')
    return raw


def files(root, exclude=()):
    result, folded = {}, set()
    for directory, folders, names in os.walk(root, followlinks=False):
        folders[:] = [n for n in folders if n != '.git']
        for n in folders + names:
            p = Path(directory) / n
            name = p.relative_to(root).as_posix()
            io.safe(root, name)
            require(name.casefold() not in folded, 'Inventory alias')
            folded.add(name.casefold())
        for n in names:
            p = Path(directory) / n
            name = p.relative_to(root).as_posix()
            if name == '.git' or name in exclude: continue
            raw = read(root, name)
            result[name] = {'sha256': io.checksum(raw), 'bytes': len(raw)}
    return dict(sorted(result.items()))


def no_pending(root):
    require(not edit.pending(root), 'Existing lock/staging/recovery: preserve it')


def hashed(value, key):
    result = deepcopy(value)
    result[key] = digest(value)
    return result


def source(entry, definition, previous, kind, current):
    old_record = previous.get('record_revision', 0) if previous else 0
    old_image = (previous['current']['image_revision'] if kind == 'reveal'
                 else previous['image_revision']) if previous else 0
    value = {'format': edit.REVEAL if kind == 'reveal' else edit.BACKGROUND,
             'id': entry['id'], 'record_revision': max(old_record, old_image)+1,
             'binding': {'entry': deepcopy(entry), 'identity': edit.identity(entry, definition)},
             'current': current}
    return edit.validate_source(hashed(value, 'record_hash'), entry)


def build(root):
    no_pending(root)
    inputs = edit.Inputs(root)
    index, cats, runtime = inputs.indices()
    require(len(index['entries']) == 56 and runtime['format'] == 'picross-runtime-registry-v8',
            'Unexpected basis: reassess before mutation')
    ids = [e['id'] for e in index['entries']]
    require({p.name for p in (root/'content/reveals').glob('*.json')} <= {n+'.json' for n in ids}, 'Foreign reveal')
    require({p.name for p in (root/'content/backgrounds').glob('*.json')} <= {n+'.json' for n in ids}, 'Foreign background')
    changes, rows = {}, []
    target_index, target_runtime = deepcopy(index), deepcopy(runtime)
    target_index['backgrounds'] = []
    def put(name, raw):
        before = read(root, name, True)
        if before != raw: changes[name] = {'old': pack(before), 'new': pack(raw)}
    for entry, row in zip(index['entries'], target_runtime['entries']):
        identifier = entry['id']
        definition = read(root, 'game/'+entry['definition'])
        require(io.checksum(definition) == entry['production']['definition_sha256'], 'Definition mismatch')
        edit.parsed_definition(definition)
        rn, bn = reveal.path(identifier), bg.path(identifier)
        old_r, old_b = read(root, rn, True), read(root, bn, True)
        r, b = obj(old_r) if old_r else None, obj(old_b) if old_b else None
        asset = edit.ref('game/'+row['reveal'], read(root, 'game/'+row['reveal']))
        if edit.slim(r):
            edit.source(inputs, entry, 'reveal')
            require(r['current']['asset'] == asset and r['binding']['identity'] == edit.identity(entry, definition), 'Reveal mismatch')
            new_r = r
        else:
            require(r is None or r['format'] == reveal.FORMAT, 'Unexpected old reveal generation')
            if r:
                reveal.validate(r, cats)
                require(r['identity']['reveal'] == asset['file'] and r['bindings'][-1]['runtime_revision'] == obj(definition)['revision']
                        and r['bindings'][-1]['entry']['production']['definition_sha256'] == io.checksum(definition)
                        and r['revisions'][-1]['reveal_sha256'] == asset['sha256'], 'Old reveal live binding mismatch')
                revision = r['current']['image_revision']
            else:
                require(asset['file'] == 'game/'+entry['reveal'] and asset['sha256'] == entry['production']['reveal_sha256'], 'Source-free reveal mismatch')
                revision = 1  # Initial technical source generation, no new image decision.
            new_r = source(entry, definition, r, 'reveal', {'image_revision': revision, 'asset': asset})
        if edit.slim(b):
            edit.source(inputs, entry, 'background')
            require(b['binding']['identity'] == edit.identity(entry, definition), 'Background identity mismatch')
            new_b = b
        else:
            require(b is None or b['format'] == bg.FORMAT, 'Unexpected old background generation')
            if b:
                # Existing full reader verifies compact receipt/selection/live refs.
                bg.load(root, index, entry)
                require(row['background']['status'] == 'selected' and b['decision']['outcome'] == 'selected', 'Unexpected selected basis')
                active = {'image_revision': b['image_revision'], 'status': 'selected', 'asset': deepcopy(b['asset'])}
                projected = deepcopy(active)
                projected['asset']['file'] = projected['asset']['file'].removeprefix('game/')
                require(projected == row['background'], 'Selected projection mismatch')
            else:
                require(row['background'] == {'status': 'legacy', 'image_revision': None, 'asset': None}, 'Unexpected source-free background')
                require(not io.safe(root, bg.asset_path(identifier)).exists() and not io.safe(root, bg.notice_path(identifier)).exists(), 'Foreign legacy background asset')
                active = {'image_revision': 1, 'status': 'standard', 'asset': None}
            new_b = source(entry, definition, b, 'background', active)
        if new_b['current']['asset']:
            a = new_b['current']['asset']
            require(edit.ref(a['file'], read(root, a['file'])) == a, 'Background live asset mismatch')
        nr, nb = encode(new_r), encode(new_b)
        put(rn, nr); put(bn, nb)
        target_index['backgrounds'].append({'id': identifier, 'source': edit.ref(bn, nb)})
        projected = deepcopy(new_b['current'])
        if projected['asset']: projected['asset']['file'] = projected['asset']['file'].removeprefix('game/')
        row['background'] = projected
        rows.append({'id': identifier, 'binding': new_r['binding'], 'reveal': new_r['current'], 'background': new_b['current'],
                     'old_reveal_format': r['format'] if r else None, 'old_background_format': b['format'] if b else None,
                     'reveal_record_revision': new_r['record_revision'], 'background_record_revision': new_b['record_revision']})
    put(REGISTRY, encode(target_index)); put(RUNTIME, encode(target_runtime))
    inventory = files(root)
    result = {'format': FORMAT, 'base': BASE, 'inventory': inventory, 'changes': dict(sorted(changes.items())), 'bindings': rows}
    return hashed(result, 'plan_hash')


def validate(value):
    exact_keys(value, {'format', 'base', 'inventory', 'changes', 'bindings', 'plan_hash'})
    require(value['format'] == FORMAT and value['base'] == BASE and value['plan_hash'] == digest({k:v for k,v in value.items() if k != 'plan_hash'}), 'Invalid plan binding')
    require(len(value['bindings']) == 56, 'Invalid binding count')
    ids = [r['id'] for r in value['bindings']]
    require(ids == sorted(set(ids)), 'Invalid IDs')
    allowed = {REGISTRY, RUNTIME} | {f'content/{kind}/{i}.json' for i in ids for kind in ('reveals','backgrounds')}
    require(set(value['changes']) <= allowed, 'Foreign write path')
    for name, pair in value['changes'].items():
        exact_keys(pair, {'old', 'new'})
        old, new = unpack(pair['old']), unpack(pair['new'])
        require(new is not None and new != old, 'Invalid changed side')
        require((edit.ref(name, old) if old else None) == ({'file':name, **value['inventory'][name]} if name in value['inventory'] else None), 'Old bytes differ from inventory')
    return value


def journal(value): return encode({'format': JOURNAL, 'plan': value})
def temp(name, value): return (Path(name).parent / ('.registration-'+value['plan_hash']+'-m2.tmp')).as_posix()
def order(value): return sorted(set(value['changes'])-{RUNTIME}) + ([RUNTIME] if RUNTIME in value['changes'] else [])


def expected(value, new=False):
    result = deepcopy(value['inventory'])
    if new:
        for name,pair in value['changes'].items():
            raw = unpack(pair['new']); result[name] = {'sha256':io.checksum(raw), 'bytes':len(raw)}
    return dict(sorted(result.items()))


def guard(root, value, states, raw):
    require(read(root, LOCK) == raw, 'Lock changed: preserve journal')
    for name, side in states.items(): require(read(root,name,True) == unpack(value['changes'][name][side]), 'Foreign target bytes: '+name)


@io.bounded
def apply(root, value, fail_step=None):
    value = validate(value); no_pending(root)
    current = files(root)
    if current == expected(value, True):
        require(not build(root)['changes'], 'Reached bytes fail fresh reader')
        return {'status':'noop', 'files':[], 'plan_hash':value['plan_hash']}
    require(current == expected(value), 'Stale inventory')
    require(build(root) == value, 'Plan differs from fresh independent reconstruction')
    require(bool(value['changes']), 'Unexpected empty non-noop plan')
    raw = journal(value)
    # Complete durable journal is published exclusively under the common lock.
    def acquire_guard():
        require(read(root,LOCK,True) is None, 'Concurrent writer: preserve lock')
        require(pub.staging(root) == [STAGE] and read(root,STAGE) == raw, 'Foreign journal staging')
    pub.write(root, LOCK, raw, STAGE, acquire_guard, replace=False)
    states = {n:'old' for n in value['changes']}
    guard(root,value,states,raw)
    require(files(root, {LOCK}) == expected(value), 'Inventory changed under lock')
    if fail_step == 0: raise RuntimeError('Injected stop after journal publication')
    for step,name in enumerate(order(value),1):
        pub.write(root,name,unpack(value['changes'][name]['new']),temp(name,value),
                  lambda: guard(root,value,{name:states[name]},raw),replace=value['changes'][name]['old'] is not None)
        states[name] = 'new'
        if fail_step == step: raise RuntimeError('Injected stop after '+name)
    guard(root,value,states,raw)
    require(files(root,{LOCK}) == expected(value,True), 'Final inventory differs')
    # Read all changed sources/indices before releasing the lock.
    for name,pair in value['changes'].items(): require(read(root,name) == unpack(pair['new']), 'Readback differs')
    io.safe(root,LOCK).unlink(); pub.sync_directory(root/'content')
    require(not build(root)['changes'], 'Fresh final reader/plan is not noop')
    return {'status':'migrated', 'files':order(value), 'plan_hash':value['plan_hash']}


@io.bounded
def rollback(root):
    raw = read(root, LOCK, True)
    if raw is None:
        require(not pub.staging(root), 'Unknown staging: preserve it')
        return {'status':'noop'}
    j = exact_keys(obj(raw), {'format','plan'})
    require(j['format'] == JOURNAL, 'Unknown journal: preserve it')
    value = validate(j['plan'])
    require(raw == journal(value), 'Noncanonical journal')
    states, temps = {}, []
    for name,pair in value['changes'].items():
        live = read(root,name,True)
        require(live in (unpack(pair['old']),unpack(pair['new'])), 'Foreign recovery bytes: '+name)
        states[name] = 'old' if live == unpack(pair['old']) else 'new'
        temporary = temp(name,value)
        data = read(root,temporary,True)
        if data is not None:
            require(any(side is not None and unpack(side).startswith(data) for side in pair.values()), 'Foreign temporary: preserve journal')
            temps.append(temporary)
    # Validate the entire retained inventory before the first rollback mutation.
    actual = files(root,{LOCK,*temps})
    allowed = deepcopy(value['inventory'])
    for name,side in states.items():
        data = unpack(value['changes'][name][side])
        if data is None: allowed.pop(name,None)
        else: allowed[name] = {'sha256':io.checksum(data),'bytes':len(data)}
    require(actual == dict(sorted(allowed.items())), 'Foreign recovery inventory: preserve journal')
    # Reconstruct and validate the complete old input before recovery mutation.
    with tempfile.TemporaryDirectory(prefix='m2-recovery-') as directory:
        shadow = io.external(directory)
        require(not shadow.is_relative_to(root), 'Recovery shadow must be external')
        for name, item in value['inventory'].items():
            data = unpack(value['changes'][name]['old']) if name in value['changes'] else read(root,name)
            require(data is not None and io.checksum(data) == item['sha256'] and len(data) == item['bytes'], 'Old shadow mismatch')
            target=io.safe(shadow,name); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        require(build(shadow) == value, 'Independent old recovery reconstruction differs')
    for temporary in temps:
        guard(root,value,states,raw)
        io.safe(root,temporary).unlink(); pub.sync_directory((root/temporary).parent)
    for name in order(value):
        if states[name] == 'old': continue
        pub.write(root,name,unpack(value['changes'][name]['old']),temp(name,value),
                  lambda: guard(root,value,{name:states[name]},raw),replace=True)
        states[name]='old'
    guard(root,value,states,raw)
    require(files(root,{LOCK}) == expected(value), 'Rollback inventory differs')
    io.safe(root,LOCK).unlink(); pub.sync_directory(root/'content')
    return {'status':'rolled_back', 'plan_hash':value['plan_hash']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['plan','apply','rollback']); p.add_argument('--root',type=Path,required=True)
    p.add_argument('--plan',type=Path); p.add_argument('--fail-step',type=int)
    a=p.parse_args(); root=io.external(a.root)
    with io.budget():
        if a.command == 'plan':
            value=build(root); path=io.external(a.plan)
            require(not path.is_relative_to(root), 'Plan must be external')
            with path.open('xb') as stream: stream.write(encode(value)); stream.flush(); os.fsync(stream.fileno())
            result={'status':'planned','files':sorted(value['changes']),'plan_hash':value['plan_hash']}
        elif a.command == 'apply': result=apply(root,obj(io.read(a.plan.parent,a.plan.name,LIMIT)),a.fail_step)
        else: result=rollback(root)
    print(json.dumps(result,ensure_ascii=True))


if __name__ == '__main__': main()
