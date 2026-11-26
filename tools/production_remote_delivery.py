"""Closed Actions transport for selected PW originals. The record remains authoritative."""
from datetime import datetime, timedelta, timezone
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re
import stat
import tempfile
from zipfile import BadZipFile, ZipFile

if __package__:
    from . import production_remote_reader as shared
else:
    import production_remote_reader as shared

MIB = 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def exact_keys(value, keys):
    require(isinstance(value, dict) and set(value) == keys, 'Unexpected transport fields')
    return value


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, 'Invalid ' + label)
    return value


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':')).encode()
    return sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), 'Duplicate JSON key')
        return result
    require(len(raw) <= MIB, 'Oversized transport JSON')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique)

READS = ('inspect', 'inspect-product')
REPOSITORIES = {'venomenon328/picross': 1381196633, 'venomenon328/picross-remote-test': 1470169013}
ASSETS = {'reveal', 'motif', 'background'}
RASTERS = {'definition', 'preview', 'proof', 'difficulty', 'cells-clues', 'crop-before', 'crop-preview', 'crop-protection'}
PRODUCT = {'product-definition', 'product-reveal', 'product-background'}
FORMAT = 'pw-remote-delivery-v1'
FORMAT_V2 = 'pw-remote-delivery-v2'
WIRE_V2 = 'pw-remote-v2'


def selectors(req):
    items = exact_keys(req['input'], {'items'})['items'] if req['operation'] in READS else req['delivery']
    roles = PRODUCT if req['operation'] == 'inspect-product' else ASSETS | RASTERS | {'prepared'}
    multi = req.get('format') == WIRE_V2
    require(isinstance(items, list) and 0 < len(items) <= (300 if multi else len(roles)),
            'Explicit delivery roles required')
    seen = set()
    groups = {}
    for item in items:
        exact_keys(item, {'role', 'candidate'})
        role, candidate = item['role'], item['candidate']
        require(isinstance(candidate, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', candidate)
                and candidate not in ('none', 'standard'), 'Invalid candidate')
        key = (candidate.casefold(), role) if multi else role
        require(isinstance(role, str) and role in roles and key not in seen, 'Unknown or duplicate delivery role')
        seen.add(key)
        if not multi:
            group = 'raster' if role in RASTERS else 'background' if role == 'prepared' else role
            require(groups.setdefault(group, candidate) == candidate, 'Different candidates in one view')
    return items


def result_selection(req):
    """Constrain delivery to the explicitly requested result and its bound references."""
    items = selectors(req)
    data = req['input']
    source = None
    if req['operation'] == 'step4' and 'prepare' in data:
        ids = set(data['prepare'])
        require(all(i['role'] in ('background', 'prepared') and i['candidate'] in ids for i in items),
                'Preparation delivery requires requested background IDs and roles')
        return {i['candidate'] for i in items}
    require(req['operation'] == 'step3', 'This operation does not publish a deliverable result')
    if 'design' in data:
        target = data['design']['variants'][0]['id']
    else:
        require(len(data) == 1, 'Expected one result-producing operation')
        kind, = data
        require(kind in ('fixed', 'profile_check', 'repair'), 'This raster operation does not publish a deliverable result')
        plan = data[kind]
        source = plan['source']['candidate']
        target = source if kind == 'profile_check' else plan['output']
    require(any(i['role'] in RASTERS and i['candidate'] == target for i in items)
            and all(i['role'] in ('reveal', 'motif') or i['role'] in RASTERS
                    and i['candidate'] in (source, target) for i in items), 'Delivery must name the planned raster result')
    return {target}


def result_available(req, before, after):
    targets = result_selection(req)
    if req['operation'] == 'step4':
        offered = {a['id']: a['prepared'] for a in after['assets'] if a['role'] == 'background'}
        original = {a['id']: a['prepared'] for a in before['assets'] if a['role'] == 'background'}
        return all(offered.get(i) for i in targets) and any(offered[i] != original.get(i) for i in targets)
    target, = targets
    new = next((r for r in after['rasters'] if r['id'] == target), None)
    old = next((r for r in before['rasters'] if r['id'] == target), None)
    return new is not None and new != old


def publication(req, before_commit, after_commit, before_bytes, after_bytes):
    """Authenticate the immediate publication independently of the delivered archive."""
    expected, successor = req['expected'], after_commit['sha']
    require(before_commit['sha'] == expected and re.fullmatch('[a-f0-9]{40}', successor)
            and [p['sha'] for p in after_commit['parents']] == [expected]
            and re.fullmatch(r'.+\n\nPW-Remote: ' + digest(req) + r'\n?', after_commit['message']),
            'Different result parent or request')
    require(sha256(before_bytes).hexdigest() == req['record_sha256'], 'Different input record')
    before, after = parse(before_bytes), parse(after_bytes)
    require(all(r['format'] in ('picross-authoring-current-v2', 'picross-authoring-current-v3')
                and r['puzzle_id'] == req['job'] and r['operation'] == 'production'
                and r['test_only'] is (req['repository'] == 'venomenon328/picross-remote-test')
                for r in (before, after))
            and before['work_release'] == after['work_release'], 'Different delivered job or release generation')
    binding = {'work': successor, 'record_sha256': sha256(after_bytes).hexdigest()}
    return before, after, binding


def resolve_sources(req, record):
    """Resolve role/candidate pairs solely from the caller's pinned record."""
    require(record['operation'] == 'production' and record['puzzle_id'] == req['job'], 'Different production job')
    rows, missing = [], []
    for item in selectors(req):
        role, candidate = item['role'], item['candidate']
        profile = derive = None
        if role in PRODUCT:
            require(record['state'] == 'registered' and record['integration']['commit'] == req['product'],
                    'Different integration commit')
            result = record['integration']['result']
            part = role.removeprefix('product-')
            selected = record['selected']['raster' if part == 'definition' else part]
            require(candidate == selected, 'Different product selection')
            runtime = result['runtime']
            require(runtime['id'] == result['entry']['id'] == req['job'], 'Different product identity')
            if part == 'background':
                asset = runtime['background']['asset']
                require(isinstance(asset, dict) and asset['file'] == 'art/backgrounds/' + req['job'] + '.png',
                        'Foreign product background')
                path = asset['file']
            else:
                path = runtime[part]
                require(result['entry'][part] == path, 'Different registered product selection')
            # Completion binds these data files. Never read an arbitrary path from result.files.
            prefix = {'definition': 'data/content/', 'background': 'art/backgrounds/', 'reveal': 'art/content/'}[part]
            require(isinstance(path, str) and path.startswith(prefix) and re.fullmatch(
                r'[a-zA-Z0-9_-]+\.(json|png|svg)', path[len(prefix):]), 'Foreign product path')
            ref = result['files']['game/' + path]
            require(ref['file'] == 'game/' + path, 'Different product file')
        elif role in RASTERS:
            raster = next((r for r in record['rasters'] if r['id'] == candidate), None)
            require(raster is not None and record['selected']['raster'] in (None, candidate), 'Different raster')
            if role.startswith('crop-'):
                ref = (raster.get('crop_diagnosis') or {}).get(role.removeprefix('crop-'))
            elif role == 'cells-clues':
                ref, derive = raster['definition'], 'cells-clues'
            else:
                ref = raster[role]
        else:
            kind = 'background' if role == 'prepared' else role
            asset = next((a for a in record['assets'] if a['role'] == kind and a['id'] == candidate), None)
            require(asset and record['selected'][kind] in (None, candidate), 'Different image role or choice')
            require(asset['rights'], 'Original has no recorded usage basis')
            ref = asset['file']
            profile = asset.get('profile')
            if role == 'prepared':
                require(record['format'] == 'picross-authoring-current-v3' and profile, 'Bound background profile required')
                if asset['prepared']:
                    ref = asset['prepared']['file']
                else:
                    derive = 'prepare-background'
        if ref is None and req.get('format') == WIRE_V2 and (role in ('proof', 'difficulty') or role.startswith('crop-')):
            reason = ('No certified difficulty is attached to this revision' if role == 'difficulty'
                      else 'No proof is attached to this revision' if role == 'proof'
                      else 'No crop is attached to this revision')
            missing.append({**item, 'reason': reason})
            continue
        require(isinstance(ref, dict), 'Requested original unavailable')
        if role not in PRODUCT:
            require(ref['file'].startswith('content/authoring/' + req['job'] + '/') and 'asset' in ref,
                    'Expected a release original belonging to this production job')
        suffix = Path(ref['file']).suffix.lower() if derive is None else '.png'
        if role in ('proof', 'difficulty', 'definition', 'product-definition', 'crop-before', 'crop-protection'):
            allowed = {'.json'}
        elif role == 'crop-preview':
            allowed = {'.png'}
        else:
            allowed = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}
        require(suffix in allowed, 'Unexpected delivery media type')
        name = (candidate + '--' if req.get('format') == WIRE_V2 else '') + role + suffix
        rows.append({**item, 'file': name, 'source': ref, 'derive': derive, 'profile': profile})
    return rows, missing


def sources(req, record):
    return resolve_sources(req, record)[0]


def context(req, source, run, attempt, trigger, trigger_attempt, successor=None):
    for number in (run, attempt, trigger, trigger_attempt):
        integer(number, 1, 2**53 - 1, 'Actions identity')
    require(isinstance(source, str) and re.fullmatch('[a-f0-9]{40}', source), 'Invalid invocation commit')
    invocation = digest({'mode': 'execute', 'request': req})
    require(('delivery' in req) == (successor is not None), 'Expected a bound result successor')
    ctx = {'request': digest(req), 'ref': f'work-prod-control/remote/{req["job"]}/{invocation}', 'commit': source,
            'repository': req['repository'], 'repository_id': REPOSITORIES[req['repository']], 'job': req['job'],
            'work': req['expected'], 'record_sha256': req['record_sha256'], 'main': req['main'], 'tools': req['tools'],
            'product': req.get('product'), 'pr': req.get('pr'), 'operation': req['operation'], 'run': run,
            'attempt': attempt, 'trigger': trigger, 'trigger_attempt': trigger_attempt}
    if successor is not None:
        ctx['successor'] = successor
    return ctx


def artifact_name(ctx):
    return f'pw-{ctx["operation"]}-{ctx["request"]}-{ctx["run"]}-{ctx["attempt"]}'


def expiry(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(date.tzinfo is not None, 'Expected UTC expiry')
    return date


def metadata(row, ctx, artifact_id, now):
    run = row['workflow_run']
    require(row['id'] == artifact_id and type(artifact_id) is int and artifact_id > 0
            and row['name'] == artifact_name(ctx) and row['expired'] is False and run['id'] == ctx['run']
            and run['head_sha'] == ctx['main'] and run['head_branch'] == 'main'
            and run['repository_id'] == run['head_repository_id'] == ctx['repository_id'],
            'Foreign or expired Actions artifact')
    require(expiry(row['created_at']) <= now < expiry(row['expires_at'])
            and expiry(row['expires_at']) <= expiry(row['created_at']) + timedelta(days=1, minutes=5),
            'Expired or unexpected Actions retention')
    require(re.fullmatch(r'sha256:[0-9a-f]{64}', row['digest']) and type(row['size_in_bytes']) is int
            and row['size_in_bytes'] > 0, 'Missing artifact digest or length')
    return row


def verify_archive(archive, row, ctx, req, record_bytes, *, artifact_id, output=None, now=None, result=None,
                   transport=None):
    """Compare independently read bindings, then expose a new directory of verified bytes."""
    now = now or datetime.now(timezone.utc)
    metadata(row, ctx, artifact_id, now)
    require(sha256(record_bytes).hexdigest() == req['record_sha256'], 'Different pinned record bytes')
    record = parse(record_bytes)
    successor = None
    if result is not None:
        before, record, successor = publication(req, result['input_commit'], result['commit'], record_bytes, result['record'])
        require(result_available(req, before, record), 'No requested result was published')
    require(record['format'] in ('picross-authoring-current-v2', 'picross-authoring-current-v3') and ctx == context(
        req, ctx['commit'], ctx['run'], ctx['attempt'], ctx['trigger'], ctx['trigger_attempt'], successor), 'Wrong delivery context')
    expected, missing = resolve_sources(req, record)
    v2 = req.get('format') == WIRE_V2
    require(archive.stat().st_size == row['size_in_bytes'], 'Artifact length differs')
    with archive.open('rb') as stream:
        require('sha256:' + file_digest(stream, 'sha256').hexdigest() == row['digest'], 'Artifact digest differs')
        stream.seek(0)
        with ZipFile(stream) as bundle:
            names = [s['file'] for s in expected] + ['manifest.json']
            if transport is not None:
                names.extend(transport)
            entries = bundle.infolist()
            require(len(entries) == len(names) and {e.orig_filename for e in entries} == set(names)
                    and all(e.orig_filename == e.filename and not e.is_dir() and not e.flag_bits & 1
                            and stat.S_IFMT(e.external_attr >> 16) in (0, stat.S_IFREG)
                            and not (e.external_attr & 0x410) for e in entries), 'Unsafe or extra archive members')
            require(bundle.getinfo('manifest.json').file_size <= MIB, 'Oversized manifest')
            manifest = exact_keys(parse(bundle.read('manifest.json')),
                                  {'format', 'context', 'release', 'purpose', 'expires', 'files'} | ({'missing'} if v2 else set())
                                  | ({'transport'} if transport is not None else set()))
            require(manifest['format'] == (FORMAT_V2 if v2 else FORMAT) and manifest.get('missing', []) == missing
                    and manifest['context'] == ctx and manifest['purpose'] == 'authoring-review'
                    and manifest['release'] == record['work_release'] and now < expiry(manifest['expires'])
                    <= expiry(row['created_at']) + timedelta(days=1, minutes=5)
                    and isinstance(manifest['files'], list) and len(manifest['files']) == len(expected),
                    'Manifest does not bind this request, release and attempt')
            if transport is not None:
                require(manifest['transport'] == transport and expiry(manifest['expires']) <= expiry(row['expires_at']),
                        'Different original inputs or delivery expiry')
                for name, identity in transport.items():
                    require(bundle.getinfo(name).file_size == identity['bytes']
                            and sha256(bundle.read(name)).hexdigest() == identity['sha256'],
                            'Different transport member')
            with tempfile.TemporaryDirectory(dir=output.parent if output else None) as scratch:
                staged = Path(scratch) / 'checked'
                staged.mkdir()
                for spec, entry in zip(expected, manifest['files'], strict=True):
                    exact_keys(entry, set(spec) | {'bytes', 'sha256'})
                    require(all(entry[k] == v for k, v in spec.items()), 'Different source or semantic role')
                    size = integer(entry['bytes'], 1, 64 * MIB, 'delivery length')
                    require(bundle.getinfo(spec['file']).file_size == size, 'Different member length')
                    if not spec['derive']:
                        require(all(entry[k] == spec['source'][k] for k in ('bytes', 'sha256')), 'Different original')
                    raw = bundle.read(spec['file'])
                    require(len(raw) == size and sha256(raw).hexdigest() == entry['sha256'], 'Different member bytes')
                    if output:
                        (staged / spec['file']).write_bytes(raw)
                if output:
                    # Reserve a new directory only after every member has passed.
                    output.mkdir(mode=0o700)
                    try:
                        for spec in expected:
                            (staged / spec['file']).rename(output / spec['file'])
                    except BaseException:
                        for spec in expected:
                            (output / spec['file']).unlink(missing_ok=True)
                        output.rmdir()
                        raise
    return manifest


def run_context(req, record, trigger, worker, result, *, collecting=False):
    """The caller supplies fresh Connector REST metadata independently of the ZIP."""
    require((req['operation'] in READS or 'delivery' in req) and req['tools'] == req['main'], 'Expected a bound delivery request')
    repo = req['repository']
    for run in (trigger, worker):
        require(run['repository']['full_name'] == run['head_repository']['full_name'] == repo
                and run['repository']['id'] == run['head_repository']['id'] == REPOSITORIES[repo]
                and ((run['status'], run['conclusion']) == ('completed', 'success') or
                     collecting and run is worker and (run['status'], run['conclusion']) == ('in_progress', None)),
                'Unconfirmed workflow run')
    successor = publication(req, result['input_commit'], result['commit'], record, result['record'])[2] if result else None
    ctx = context(req, trigger['head_sha'], worker['id'], worker['run_attempt'], trigger['id'], trigger['run_attempt'], successor)
    require(trigger['event'] == 'push' and trigger['path'] == '.github/workflows/work-growth.yml'
            and trigger['head_branch'] == ctx['ref'] and worker['event'] == 'workflow_run'
            and worker['path'] == '.github/workflows/pw-remote.yml' and worker['head_sha'] == req['main']
            and worker['head_branch'] == 'main' and worker['display_title'] == 'PW remote ' + ctx['ref'],
            'Foreign trigger or worker')
    return ctx


def consume(req, record, trigger, worker, artifact, archive, output, *, result=None):
    ctx = run_context(req, record, trigger, worker, result)
    return verify_archive(archive, artifact, ctx, req, record, artifact_id=artifact['id'], output=output, result=result)


READER = 'production_remote_delivery.py'
COMMON = 'production_remote_reader.py'
ORIGINALS = 'originals.json'
LIMITS = {READER: 131072, COMMON: 131072, ORIGINALS: 16 * MIB}


def identities(files):
    return {name: {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()} for name, raw in files.items()}


def unpack_bindings(archive, artifact, pins):
    from hashlib import sha1
    require(set(pins) == {READER, COMMON}, 'Expected trusted reader blobs')
    require(archive.stat().st_size == artifact['size_in_bytes'], 'Different downloaded length')
    with ZipFile(archive) as bundle:
        files = {}
        for name, limit in LIMITS.items():
            rows = [r for r in bundle.infolist() if r.orig_filename == name]
            require(len(rows) == 1 and rows[0].filename == name and 0 < rows[0].file_size <= limit,
                    'Missing or oversized original binding')
            raw = bundle.read(rows[0])
            if name in pins:
                require(sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == pins[name],
                        'Different trusted Reader Git blob')
            files[name] = raw
    return identities(files), shared.parse(files[ORIGINALS])


def original_binding(data):
    request = data['request_commit']
    title, separator, message = request['message'].rstrip('\n').partition('\n\n')
    envelope = shared.parse(message)
    req = exact_keys(envelope, {'request', 'mode'})['request']
    require(title == 'PW remote request v1' and separator and envelope['mode'] == 'execute'
            and shared.canonical(envelope) == message, 'Different canonical request')
    repo, job, main = req['repository'], req['job'], req['main']
    path = f'content/authoring/{job}/current/record.json'
    fields = {'request_commit', 'main_commit', 'input_commit', 'input_record', 'trigger', 'run', 'attempt',
              'release', 'tag', 'assets'}
    is_result = 'delivery' in req
    product = req['operation'] == 'inspect-product'
    exact_keys(data, fields | ({'result_commit', 'result_record'} if is_result else set())
               | ({'product_commit', 'pr'} if product else set()))
    require(shared.JOB.fullmatch(job) and req['tools'] == main and req['format'] in ('pw-remote-v1', WIRE_V2)
            and data['main_commit']['sha'] == main and data['main_commit']['tree']['sha'] == request['tree']['sha'],
            'Different job, tool revision or invocation tree')
    shared.commit_parents(request, data['trigger']['head_sha'], [main])
    work = req['expected']
    require(data['input_commit']['sha'] == work, 'Different input work commit')
    raw = shared.record_bytes(data['input_record'], repo, work, path)
    require(sha256(raw).hexdigest() == req['record_sha256'], 'Different input record')
    result = None
    live_record = data['input_record']
    if is_result:
        work = data['result_commit']['sha']
        live_record = data['result_record']
        result = dict(input_commit=data['input_commit'], commit=data['result_commit'],
                      record=shared.record_bytes(live_record, repo, work, path))
    record = parse(result['record'] if result else raw)
    require(record['test_only'] is (repo == 'venomenon328/picross-remote-test'), 'Different production boundary')
    trigger, run = data['trigger'], data['run']
    require(data['attempt'] == run and (run['status'], run['conclusion']) == ('in_progress', None),
            'Different collection attempt')
    ctx = run_context(req, raw, trigger, run, result, collecting=True)
    release, tag = data['release'], 'work-prod-' + job
    anchor = shared.ref(data['tag'], 'tags/' + tag)
    require(record['work_release'] == dict(id=release['id'], anchor=anchor) and release['target_commitish'] == anchor
            and release['tag_name'] == tag and release['body'] == 'Picross production job ' + job
            and release['draft'] is False and release['prerelease'] is True and release['immutable'] is False,
            'Different release generation')
    fresh = dict(ack='absent', main=main, work=work, record=live_record['sha'], tag=anchor,
                 repository=str(ctx['repository_id']), request=request['sha'],
                 trigger=f"{trigger['id']}:{trigger['run_attempt']}:{trigger['head_sha']}:completed:success",
                 release=shared.canonical(release))
    refs = {}
    for spec in sources(req, record):
        ref = spec['source']
        if 'asset' in ref:
            asset = ref['asset']
            require(asset['repository'] == repo and asset['job'] == job and asset['release_id'] == release['id'],
                    'Foreign original asset')
            expected = (ref['bytes'], ref['sha256'])
            require(refs.setdefault(asset['asset_id'], expected) == expected, 'Conflicting original asset')
    assets = data['assets']
    require(len(assets) == len(refs) and {a['id'] for a in assets} == refs.keys(), 'Missing original asset')
    for asset in assets:
        size, checksum = refs[asset['id']]
        require(asset['name'] == 'original-' + checksum and asset['size'] == size and asset['state'] == 'uploaded'
                and asset['label'] == 'picross-original:' + tag and asset['digest'] in (None, 'sha256:' + checksum),
                'Different release asset')
        fresh['asset-' + str(asset['id'])] = shared.canonical(asset)
    if product:
        head = req['product']
        owner = shared.owner(data['product_commit'], head, main)
        parents = data['input_commit']['parents']
        require(len(parents) == 1 and shared.owner(data['input_commit'], work, parents[0]['sha']) == owner,
                'Different product owner')
        pr = shared.associated(req, data['pr'], head, owner, repository_id=ctx['repository_id'])
        fresh.update(product=head, pr=shared.canonical(pr))
    return req, raw, result, ctx, fresh


def verify_originals(archive, artifact, collection, *, tools, pins, observations=None, output=None, staging=False):
    transport, data = unpack_bindings(archive, artifact, pins)
    req, raw, result, ctx, fresh = original_binding(data)
    require(tools == ctx['tools'] and shared.matching_fields(collection, dict(id=ctx['run'], run_attempt=ctx['attempt'],
            head_sha=tools, head_branch='main', path='.github/workflows/pw-remote.yml', repository_id=ctx['repository_id'])),
            'Different collection identity')
    state = (collection['status'], collection['conclusion'])
    require(state == (('in_progress', None) if staging else ('completed', 'success')), 'Unconfirmed collection')
    if observations is not None:
        shared.confirm_fresh({'expected_fresh': fresh}, observations)
    require(output is None or observations is not None and not staging, 'Fresh readbacks required before opening')
    manifest = verify_archive(archive, artifact, ctx, req, raw, artifact_id=artifact['id'], output=output,
                              transport=transport, result=result)
    if staging or observations is not None:
        return manifest
    return dict(status='read-live', context=ctx, release=data['release']['id'], sources=sorted(fresh))


def originals_cli(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Open bound originals using independent Connector readbacks.')
    shared.arguments(parser)
    parser.add_argument('--common-blob', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        artifact, collection = shared.connector_metadata(args)
        result = verify_originals(args.archive, artifact, collection, tools=args.tools,
                                  pins={READER: args.reader_blob, COMMON: args.common_blob},
                                  observations=args.fresh or None, output=args.output)
        print(json.dumps(result, ensure_ascii=False))
    except (BadZipFile, KeyError, TypeError, ValueError, OSError) as error:
        parser.exit(1, f'Original delivery blocked ({type(error).__name__}). Check the bound inputs.\n')


if __name__ == '__main__':
    import sys
    if sys.argv[1:2] == ['originals']:
        originals_cli(sys.argv[2:])
        sys.exit(0)
    import argparse
    parser = argparse.ArgumentParser(description='Verify a connector download and open a fresh inspection directory.')
    for option in ('request', 'record', 'trigger', 'worker', 'artifact', 'archive', 'output'):
        parser.add_argument('--' + option, type=Path, required=True)
    for option in ('input-commit', 'result-commit', 'result-record'):
        parser.add_argument('--' + option, type=Path)
    args = parser.parse_args()
    result_paths = (args.input_commit, args.result_commit, args.result_record)
    require(not any(result_paths) or all(result_paths), 'Supply all three independently read publication inputs')
    publication_args = dict(input_commit=parse(args.input_commit.read_bytes()), commit=parse(args.result_commit.read_bytes()),
                            record=args.result_record.read_bytes()) if all(result_paths) else None
    result = consume(parse(args.request.read_bytes()), args.record.read_bytes(), parse(args.trigger.read_bytes()),
                     parse(args.worker.read_bytes()), parse(args.artifact.read_bytes()), args.archive, args.output,
                     result=publication_args)
    print(json.dumps(result, ensure_ascii=False))
