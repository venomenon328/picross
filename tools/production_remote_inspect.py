"""Read one current publication, stage the requested views and confirm the Actions upload."""
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import tempfile
from contextlib import ExitStack
from time import monotonic, sleep
from urllib.parse import quote

from . import production_remote_delivery as delivery, production_remote_pr as prs, publish_git, work_publish as pw, work_refs
from .puzzle_production import catalog_io as io, current_authoring as current, github_rest, work_assets
from .puzzle_production.authoring_package import require


def bound(root, req, *, publication=None):
    job = req['job']
    info = pw.api('')
    require(info['full_name'] == pw.REPO == req['repository'] and info['id'] == delivery.REPOSITORIES[pw.REPO],
            'Different repository identity')
    work = req['expected'] if publication is None else publication['commit']['sha']
    require(publish_git.remote_head(root, 'refs/heads/main') == req['main']
            and publish_git.remote_head(root, 'refs/heads/content/pw/' + job) == work, 'Stale main or job')
    raw = pw.remote_record(work, job)
    require(raw == publication['record'] if publication else io.checksum(raw) == req['record_sha256'], 'Stale record')
    record = pw.bound_record(raw, job)
    require(record['test_only'] is work_refs.FIXTURE and (not work_refs.FIXTURE or job == work_refs.TEST_JOB),
            'Wrong production/test boundary')
    tag = 'work-prod-' + job
    binding = record['work_release']
    release = pw.api('releases/' + str(binding['id']))
    require(release['id'] == binding['id'] and release['tag_name'] == tag and release['prerelease']
            and not release['draft'] and release['body'] == 'Picross production job ' + job
            and release['target_commitish'] == binding['anchor']
            and publish_git.remote_head(root, 'refs/tags/' + tag) == binding['anchor'], 'Different release generation')
    if req['operation'] == 'inspect-product':
        from .production_remote import owner
        product = req['product']
        owner_id = owner(product, parent=req['main'])
        require(owner(req['expected']) == owner_id and publish_git.remote_head(
            root, 'refs/heads/' + prs.product_branch(job)) == product, 'Different product or work owner')
        prs.associated(req, pw.api('pulls/' + str(req['pr'])), product, owner_id)
    for spec in delivery.sources(req, record):
        ref = spec['source']
        if 'asset' in ref:
            a = ref['asset']
            rows = [r for r in release['assets'] if r['id'] == a['asset_id']]
            require(len(rows) == 1 and rows[0]['size'] == ref['bytes'] and rows[0]['state'] == 'uploaded'
                    and rows[0]['name'] == 'original-' + ref['sha256']
                    and rows[0].get('digest') in (None, 'sha256:' + ref['sha256']), 'Different bound asset')
    return raw, record, release


def result_publication(root, req):
    expected = req['expected']
    work = publish_git.remote_head(root, 'refs/heads/content/pw/' + req['job'])
    require(work and work != expected, 'Expected the published result on the live work ref')
    require(publish_git.remote_head(root, 'refs/heads/' + pw.release_catalog.LOCK_BRANCH) is None,
            'Catalog lease occupied during result delivery')
    raw = pw.remote_record(expected, req['job'])
    result = {'input_commit': pw.api('git/commits/' + expected), 'commit': pw.api('git/commits/' + work),
              'record': pw.remote_record(work, req['job'])}
    before, after, successor = delivery.publication(req, result['input_commit'], result['commit'], raw, result['record'])
    require(delivery.result_available(req, before, after), 'No requested result was published')
    return raw, successor, result


def read_git(commit, ref):
    endpoint = github_rest.API + '/contents/' + quote(ref['file'], safe='/') + '?ref=' + commit
    with github_rest.open_api(endpoint, {'Accept': 'application/vnd.github.raw+json',
                                         'User-Agent': 'picross-pw-inspect'}, timeout=30) as response:
        data = response.read(ref['bytes'] + 1)
    require(len(data) == ref['bytes'] and io.checksum(data) == ref['sha256'], 'Different committed bytes')
    return data


def collect(req, ctx, record, release, result):
    from . import production_remote as remote

    def fields(row, names):
        return {key: row[key] for key in names.split()}

    def run(endpoint, *, worker=False):
        row = pw.api(endpoint)
        selected = fields(row, 'id run_attempt workflow_id event path head_branch head_sha status conclusion')
        if worker:
            selected['display_title'] = row['display_title']
        for key in ('repository', 'head_repository'):
            selected[key] = fields(row[key], 'id full_name')
        return selected

    def contents(commit):
        # Exclude URL fields unrelated to exact Git Contents authentication.
        return fields(pw.api(f'contents/{current.path(req["job"])}?ref={commit}'),
                      'type path url size sha encoding content')

    selected = {ref['asset']['asset_id'] for spec in delivery.sources(req, record)
                for ref in [spec['source']] if 'asset' in ref}
    endpoint = f'actions/runs/{ctx["run"]}'
    data = dict(request_commit=pw.api('git/commits/' + ctx['commit']), main_commit=pw.api('git/commits/' + req['main']),
                input_commit=result['input_commit'] if result else pw.api('git/commits/' + req['expected']),
                input_record=contents(req['expected']), trigger=run(f'actions/runs/{ctx["trigger"]}'),
                run=run(endpoint, worker=True), attempt=run(endpoint + f'/attempts/{ctx["attempt"]}', worker=True),
                release=fields(release, 'id target_commitish tag_name body draft prerelease immutable'),
                tag=pw.api('git/ref/tags/' + release['tag_name']),
                assets=[fields(a, 'id name size digest label state') for a in release['assets'] if a['id'] in selected])
    if result:
        data.update(result_commit=result['commit'], result_record=contents(result['commit']['sha']))
    if req['operation'] == 'inspect-product':
        pr = pw.api('pulls/' + str(req['pr']))
        data.update(product_commit=pw.api('git/commits/' + req['product']), pr=fields(pr, 'number state body'))
        for key in ('head', 'base'):
            data['pr'][key] = {**fields(pr[key], 'ref sha'), 'repo': fields(pr[key]['repo'], 'full_name id')}
    # Compare the actual staged inputs with the bound live request before upload.
    checked_req, _, _, checked_ctx, _ = delivery.original_binding(data)
    require(req == checked_req and ctx == checked_ctx, 'Collected a different request or publication')
    files = {name: publish_git.git(remote.TOOLS, 'show', 'HEAD:tools/' + name)
             for name in (delivery.READER, delivery.COMMON)}
    files[delivery.ORIGINALS] = current.encoded(data)
    require(all(0 < len(raw) <= delivery.LIMITS[name] for name, raw in files.items()), 'Oversized original input')
    return files


def stage(req, record, ctx, output, read, recheck, *, transport=None):
    """Only selected references are materialized. Never infer a visual decision."""
    specs, missing = delivery.resolve_sources(req, record)
    v2 = req.get('format') == delivery.WIRE_V2
    manifest = {'format': delivery.FORMAT_V2 if v2 else delivery.FORMAT, 'context': ctx, 'release': record['work_release'],
                'purpose': 'authoring-review', 'expires': (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=23, minutes=59)).isoformat(),
                'files': []}
    if v2:
        manifest['missing'] = missing
    cache = {}
    rendered = {}
    renderer = None
    engine_metrics = {}
    seconds = {'originals': 0.0, 'preparation': 0.0}
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp, ExitStack() as resources:
        private = Path(tmp)
        files = private / 'delivery'
        files.mkdir(mode=0o700)
        if transport is not None:
            manifest['transport'] = delivery.identities(transport)
            for name, data in transport.items():
                (files / name).write_bytes(data)
        for spec in specs:
            ref = spec['source']
            key = ((ref['asset']['release_id'], ref['asset']['asset_id']) if 'asset' in ref else ref['file'],
                   ref['bytes'], ref['sha256'])
            if key not in cache:
                start = monotonic()
                data = read(ref)
                require(len(data) == ref['bytes'] and io.checksum(data) == ref['sha256'], 'Different original')
                cache[key] = data
                seconds['originals'] += monotonic() - start
            data = cache[key]
            start = monotonic()
            if spec['derive'] == 'prepare-background':
                with tempfile.TemporaryDirectory(dir=private, prefix='background-') as scratch:
                    original, prepared = Path(scratch) / 'original', Path(scratch) / 'prepared.png'
                    original.write_bytes(data)
                    current.prepare_background(original, prepared, profile_id=spec['profile'])
                    data = prepared.read_bytes()
            elif spec['derive'] == 'cells-clues':
                if renderer is None:
                    from .production_remote_view import open_renderer
                    renderer = resources.enter_context(open_renderer(private, engine_metrics))
                if key not in rendered:
                    rendered[key] = renderer(data)
                data = rendered[key]
            seconds['preparation'] += monotonic() - start
            (files / spec['file']).write_bytes(data)
            manifest['files'].append({**spec, 'bytes': len(data), 'sha256': io.checksum(data)})
        (files / 'manifest.json').write_bytes(current.encoded(manifest))
        recheck()
        from .puzzle_production.catalog_publication import rename
        rename(files, output, replace=False)
    return {'original_count': len(cache), 'original_bytes': sum(map(len, cache.values())), 'seconds': seconds,
            'editor': engine_metrics, 'artifact': delivery.artifact_name(ctx), 'members': len(specs) + 1 + len(transport or {})}


def github_context(req, source, successor=None):
    event = io.json_bytes(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes(), current.LIMIT)
    trigger = event['workflow_run']
    return delivery.context(req, source, int(os.environ['GITHUB_RUN_ID']), int(os.environ['GITHUB_RUN_ATTEMPT']),
                            trigger['id'], trigger['run_attempt'], successor)


def upload_record(req, ctx):
    artifact_id = int(os.environ['PW_ARTIFACT_ID'])
    for delay in (0, 2, 5, 10):
        if delay:
            sleep(delay)
        try:
            row = pw.api('actions/artifacts/' + str(artifact_id))
            break
        except github_rest.Failure as exc:
            if exc.status == 400:
                rows = pw.api(f'actions/runs/{ctx["run"]}/artifacts?name=' + quote(delivery.artifact_name(ctx)))['artifacts']
                matches = [r for r in rows if r['id'] == artifact_id]
                require(len(matches) == 1, 'Cannot identify the uploaded artifact in the run')
                row, = matches
                break
            if delay == 10 or exc.status not in (404, 502, 503, 504):
                raise
    delivery.metadata(row, ctx, artifact_id, datetime.now(timezone.utc))
    require(row['digest'] == 'sha256:' + os.environ['PW_ARTIFACT_DIGEST'].removeprefix('sha256:'),
            'Upload and Actions metadata differ')
    return row


def download_uploaded(artifact_id, archive, *, size):
    from urllib.request import Request
    from .production_remote_continuation import signed_location, signed_opener

    require(type(artifact_id) is int and artifact_id > 0 and type(size) is int and size > 0,
            'Expected a bound artifact ID and byte length')
    for delay in (0, 2, 5, 10):
        if delay:
            sleep(delay)
        signed = False
        try:
            location = signed_location(f'actions/artifacts/{artifact_id}/zip')
            signed = True
            with github_rest.transport_errors(), signed_opener().open(Request(location), timeout=30) as response:
                require(response.status == 200, 'Expected Actions ZIP download')
                remaining = size
                with archive.open('wb') as stream:
                    while remaining:
                        block = response.read(min(1024 * 1024, remaining))
                        require(block, 'Incomplete Actions ZIP')
                        stream.write(block)
                        remaining -= len(block)
                    require(not response.read(1), 'Oversized Actions ZIP')
            return
        except github_rest.Failure as error:
            if delay < 10 and (error.status in (404, 502, 503, 504) or signed and error.status == 403
                               or error.kind == 'network' and error.status is None):
                continue
            raise ValueError(f'Cannot download Actions artifact {artifact_id} ({error.status or error.kind})') from None


def process(action, root, req, mode, ref, source, check):
    require(req['operation'] in delivery.READS or 'delivery' in req and mode == 'execute', 'Expected a delivery request')
    raw, successor, result = result_publication(root, req) if 'delivery' in req else (None, None, None)
    ctx = github_context(req, source, successor)
    published_raw, record, release = bound(root, req, publication=result)
    raw = raw if result else published_raw
    def recheck():
        check()
        if result:
            require(result_publication(root, req) == (raw, successor, result), 'Published result changed during delivery')
        bound(root, req, publication=result)
    if action == 'inspect-stage':
        require(mode == 'execute', 'Expected an executable delivery')
        cache = {release['tag_name']: release}
        def read(ref):
            if 'asset' in ref:
                return work_assets.read(ref, 64 * current.LIMIT, releases=cache)
            return read_git(req.get('product', req['expected']), ref)
        return stage(req, record, ctx, root / 'pw-delivery', read, recheck,
                     transport=collect(req, ctx, record, release, result))
    if mode == 'preflight':
        require(action == 'inspect-ack', 'Preflight produces no artifact')
        check()
        pw.delete_ref(Path(__file__).resolve().parents[1], ref, source)
        return {'status': 'preflight', 'request_ref_removed': True}
    row = upload_record(req, ctx)
    if action == 'inspect-verify':
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            archive = Path(tmp) / 'artifact.zip'
            download_uploaded(row['id'], archive, size=row['size_in_bytes'])
            from . import production_remote as remote
            run = pw.api(f'actions/runs/{ctx["run"]}')
            pins = {name: remote.ws.git(remote.TOOLS, 'rev-parse', 'HEAD:tools/' + name)
                    for name in (delivery.READER, delivery.COMMON)}
            manifest = delivery.verify_originals(archive, row, {**run, 'repository_id': run['repository']['id']},
                                                 tools=req['tools'], pins=pins, staging=True)
            require(current.encoded(manifest) == (root / 'pw-delivery/manifest.json').read_bytes(),
                    'Uploaded manifest differs from staging')
        recheck()
        return {'status': 'upload-verified', 'artifact_id': row['id'], 'digest': row['digest'],
                'bytes': row['size_in_bytes'], 'expires': row['expires_at'], 'files': manifest['files'], 'context': ctx}
    require(action == 'inspect-ack', 'Unexpected delivery action')
    recheck()
    pw.delete_ref(Path(__file__).resolve().parents[1], ref, source)
    require(publish_git.remote_head(root, ref) is None, 'Request acknowledgement not confirmed')
    _, missing = delivery.resolve_sources(req, record)
    return {'status': 'delivered-with-unavailable-roles' if missing else 'delivered', 'artifact_id': row['id'],
            'request_ref_removed': True, 'context': ctx, 'missing': missing}
