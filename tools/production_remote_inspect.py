"""Read one current publication, stage the requested views and confirm the Actions upload."""
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
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


def stage(req, record, ctx, output, read, recheck):
    """Only selected references are materialized. Never infer a visual decision."""
    specs, missing = delivery.resolve_sources(req, record)
    v2 = req.get('format') == delivery.WIRE_V2
    manifest = {'format': delivery.FORMAT_V2 if v2 else delivery.FORMAT, 'context': ctx, 'release': record['work_release'],
                'purpose': 'authoring-review', 'expires': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
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
                original, prepared = private / 'original', private / 'prepared.png'
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
            'editor': engine_metrics, 'artifact': delivery.artifact_name(ctx), 'members': len(specs) + 1}


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


def download_uploaded(artifact_id, archive):
    # Fresh metadata can precede the availability of the binary endpoint.
    for delay in (0, 2, 5, 10):
        if delay:
            sleep(delay)
        with archive.open('wb') as stream:
            result = subprocess.run(['gh', 'api', f'repos/{pw.REPO}/actions/artifacts/{artifact_id}/zip'],
                                    stdout=stream, stderr=subprocess.PIPE, timeout=180,
                                    env={**os.environ, 'GH_TOKEN': github_rest.publisher_token()})
        if result.returncode == 0:
            return
        transient = any(f'HTTP {status}'.encode() in result.stderr for status in (404, 502, 503, 504))
        require(transient and delay < 10, f'Cannot download uploaded Actions artifact {artifact_id}')


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
        return stage(req, record, ctx, root / 'pw-delivery', read, recheck)
    if mode == 'preflight':
        require(action == 'inspect-ack', 'Preflight produces no artifact')
        check()
        pw.delete_ref(Path(__file__).resolve().parents[1], ref, source)
        return {'status': 'preflight', 'request_ref_removed': True}
    row = upload_record(req, ctx)
    if action == 'inspect-verify':
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            archive = Path(tmp) / 'artifact.zip'
            download_uploaded(row['id'], archive)
            manifest = delivery.verify_archive(archive, row, ctx, req, raw, artifact_id=row['id'], result=result)
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
