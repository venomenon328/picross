"""Closed Actions transport for selected PW originals. The record remains authoritative."""
from datetime import datetime, timedelta, timezone
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re
import stat
import tempfile
from zipfile import ZipFile

# The invoking chat can load this single trusted file at the pinned tool SHA.
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


def selectors(req):
    items = exact_keys(req['input'], {'items'})['items']
    roles = PRODUCT if req['operation'] == 'inspect-product' else ASSETS | RASTERS | {'prepared'}
    require(isinstance(items, list) and 0 < len(items) <= len(roles), 'Explicit delivery roles required')
    seen = set()
    groups = {}
    for item in items:
        exact_keys(item, {'role', 'candidate'})
        role, candidate = item['role'], item['candidate']
        require(isinstance(candidate, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', candidate)
                and candidate not in ('none', 'standard'), 'Invalid candidate')
        require(role in roles and role not in seen, 'Unknown or duplicate delivery role')
        seen.add(role)
        group = 'raster' if role in RASTERS else 'background' if role == 'prepared' else role
        require(groups.setdefault(group, candidate) == candidate, 'Different candidates in one view')
    return items


def sources(req, record):
    """Resolve role/candidate pairs solely from the caller's pinned record."""
    require(record['operation'] == 'production' and record['puzzle_id'] == req['job'], 'Different production job')
    rows = []
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
                ref = raster.get('crop_diagnosis', {}).get(role.removeprefix('crop-'))
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
        rows.append({**item, 'file': role + suffix, 'source': ref, 'derive': derive, 'profile': profile})
    return rows


def context(req, source, run, attempt, trigger, trigger_attempt):
    for number in (run, attempt, trigger, trigger_attempt):
        integer(number, 1, 2**53 - 1, 'Actions identity')
    require(isinstance(source, str) and re.fullmatch('[a-f0-9]{40}', source), 'Invalid invocation commit')
    invocation = digest({'mode': 'execute', 'request': req})
    return {'request': digest(req), 'ref': f'work-prod-control/remote/{req["job"]}/{invocation}', 'commit': source,
            'repository': req['repository'], 'repository_id': REPOSITORIES[req['repository']], 'job': req['job'],
            'work': req['expected'], 'record_sha256': req['record_sha256'], 'main': req['main'], 'tools': req['tools'],
            'product': req.get('product'), 'pr': req.get('pr'), 'operation': req['operation'], 'run': run,
            'attempt': attempt, 'trigger': trigger, 'trigger_attempt': trigger_attempt}


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


def verify_archive(archive, row, ctx, req, record_bytes, *, artifact_id, output=None, now=None):
    """Compare independently read bindings, then expose a new directory of verified bytes."""
    now = now or datetime.now(timezone.utc)
    metadata(row, ctx, artifact_id, now)
    require(sha256(record_bytes).hexdigest() == req['record_sha256'], 'Different pinned record bytes')
    record = parse(record_bytes)
    require(record['format'] in ('picross-authoring-current-v2', 'picross-authoring-current-v3') and ctx == context(
        req, ctx['commit'], ctx['run'], ctx['attempt'], ctx['trigger'], ctx['trigger_attempt']), 'Wrong delivery context')
    expected = sources(req, record)
    require(archive.stat().st_size == row['size_in_bytes'], 'Artifact length differs')
    with archive.open('rb') as stream:
        require('sha256:' + file_digest(stream, 'sha256').hexdigest() == row['digest'], 'Artifact digest differs')
        stream.seek(0)
        with ZipFile(stream) as bundle:
            names = [s['file'] for s in expected] + ['manifest.json']
            entries = bundle.infolist()
            require(len(entries) == len(names) and {e.orig_filename for e in entries} == set(names)
                    and all(e.orig_filename == e.filename and not e.is_dir() and not e.flag_bits & 1
                            and stat.S_IFMT(e.external_attr >> 16) in (0, stat.S_IFREG)
                            and not (e.external_attr & 0x410) for e in entries), 'Unsafe or extra archive members')
            require(bundle.getinfo('manifest.json').file_size <= MIB, 'Oversized manifest')
            manifest = exact_keys(parse(bundle.read('manifest.json')),
                                  {'format', 'context', 'release', 'purpose', 'expires', 'files'})
            require(manifest['format'] == FORMAT and manifest['context'] == ctx and manifest['purpose'] == 'authoring-review'
                    and manifest['release'] == record['work_release'] and now < expiry(manifest['expires'])
                    <= expiry(row['created_at']) + timedelta(days=1, minutes=5)
                    and isinstance(manifest['files'], list) and len(manifest['files']) == len(expected),
                    'Manifest does not bind this request, release and attempt')
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


def consume(req, record, trigger, worker, artifact, archive, output):
    """The caller supplies fresh Connector REST metadata independently of the ZIP."""
    require(req['operation'] in READS and req['tools'] == req['main'], 'Expected a bound delivery request')
    repo = req['repository']
    for run in (trigger, worker):
        require(run['repository']['full_name'] == run['head_repository']['full_name'] == repo
                and run['repository']['id'] == run['head_repository']['id'] == REPOSITORIES[repo]
                and run['status'] == 'completed' and run['conclusion'] == 'success', 'Unconfirmed workflow run')
    ctx = context(req, trigger['head_sha'], worker['id'], worker['run_attempt'], trigger['id'], trigger['run_attempt'])
    require(trigger['event'] == 'push' and trigger['path'] == '.github/workflows/work-growth.yml'
            and trigger['head_branch'] == ctx['ref'] and worker['event'] == 'workflow_run'
            and worker['path'] == '.github/workflows/pw-remote.yml' and worker['head_sha'] == req['main']
            and worker['head_branch'] == 'main' and worker['display_title'] == 'PW remote ' + ctx['ref'],
            'Foreign trigger or worker')
    return verify_archive(archive, artifact, ctx, req, record, artifact_id=artifact['id'], output=output)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify a connector download and open a fresh inspection directory.')
    for option in ('request', 'record', 'trigger', 'worker', 'artifact', 'archive', 'output'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    result = consume(parse(args.request.read_bytes()), args.record.read_bytes(), parse(args.trigger.read_bytes()),
                     parse(args.worker.read_bytes()), parse(args.artifact.read_bytes()), args.archive, args.output)
    print(json.dumps(result, ensure_ascii=False))
