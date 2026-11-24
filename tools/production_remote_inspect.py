"""Read one current publication, stage the requested views and confirm the Actions upload."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
import os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic
from urllib.parse import quote

from . import production_remote_delivery as delivery, production_remote_pr as prs, publish_git, work_publish as pw, work_refs
from .puzzle_production import catalog_io as io, current_authoring as current, github_rest, work_assets
from .puzzle_production.authoring_package import require


def bound(root, req):
    job = req['job']
    info = pw.api('')
    require(info['full_name'] == pw.REPO == req['repository'] and info['id'] == delivery.REPOSITORIES[pw.REPO],
            'Different repository identity')
    require(publish_git.remote_head(root, 'refs/heads/main') == req['main']
            and publish_git.remote_head(root, 'refs/heads/content/pw/' + job) == req['expected'], 'Stale main or job')
    raw = pw.remote_record(req['expected'], job)
    require(io.checksum(raw) == req['record_sha256'], 'Stale record')
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


def read_git(commit, ref):
    endpoint = github_rest.API + '/contents/' + quote(ref['file'], safe='/') + '?ref=' + commit
    with github_rest.open_api(endpoint, {'Accept': 'application/vnd.github.raw+json',
                                         'User-Agent': 'picross-pw-inspect'}, timeout=30) as response:
        data = response.read(ref['bytes'] + 1)
    require(len(data) == ref['bytes'] and io.checksum(data) == ref['sha256'], 'Different committed bytes')
    return data


def clue_view(raw, record):
    from PIL import Image, ImageDraw
    from .puzzle_production import catalog_rating
    definition, _, _, _ = catalog_rating.definition(raw)
    modes = current.findings.matching_modes(record['parameters']['approved'], definition, len(definition['palette']))
    require(len(modes) == 1, 'Ambiguous raster mode')
    neutral = modes == {'mono'}
    palette = {p['id']: '#202020' if neutral else '#' + p['color'] for p in definition['palette']}
    rows, columns = definition['rows'], definition['columns']
    step = 22
    left = max(map(len, rows), default=0)
    top = max(map(len, columns), default=0)
    view = Image.new('RGB', ((left + len(columns)) * step + 1, (top + len(rows)) * step + 1), 'white')
    draw = ImageDraw.Draw(view)
    def hint(x, y, clue):
        draw.text(((x + 0.5) * step, (y + 0.5) * step), str(clue['length']), fill=palette[clue['color']], anchor='mm')
    for y, clues in enumerate(rows, top):
        for x, clue in enumerate(clues, left - len(clues)):
            hint(x, y, clue)
    for x, clues in enumerate(columns, left):
        for y, clue in enumerate(clues, top - len(clues)):
            hint(x, y, clue)
    for y, row in enumerate(definition['solution'], top):
        for x, color in enumerate(row, left):
            draw.rectangle((x*step, y*step, (x+1)*step, (y+1)*step), fill=palette.get(color, 'white'), outline='#aaaaaa')
    stream = BytesIO()
    view.save(stream, format='PNG')
    return stream.getvalue()


def stage(req, record, ctx, output, read, recheck):
    """Only selected references are materialized. Never infer a visual decision."""
    specs = delivery.sources(req, record)
    manifest = {'format': delivery.FORMAT, 'context': ctx, 'release': record['work_release'],
                'purpose': 'authoring-review', 'expires': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                'files': []}
    cache = {}
    seconds = {'originals': 0.0, 'preparation': 0.0}
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        private = Path(tmp)
        files = private / 'delivery'
        files.mkdir(mode=0o700)
        for spec in specs:
            ref = spec['source']
            if ref['file'] not in cache:
                start = monotonic()
                data = read(ref)
                require(len(data) == ref['bytes'] and io.checksum(data) == ref['sha256'], 'Different original')
                cache[ref['file']] = data
                seconds['originals'] += monotonic() - start
            data = cache[ref['file']]
            start = monotonic()
            if spec['derive'] == 'prepare-background':
                original, prepared = private / 'original', private / 'prepared.png'
                original.write_bytes(data)
                current.prepare_background(original, prepared, profile_id=spec['profile'])
                data = prepared.read_bytes()
            elif spec['derive'] == 'cells-clues':
                data = clue_view(data, record)
            seconds['preparation'] += monotonic() - start
            (files / spec['file']).write_bytes(data)
            manifest['files'].append({**spec, 'bytes': len(data), 'sha256': io.checksum(data)})
        (files / 'manifest.json').write_bytes(current.encoded(manifest))
        recheck()
        from .puzzle_production.catalog_publication import rename
        rename(files, output, replace=False)
    return {'original_count': len(cache), 'original_bytes': sum(map(len, cache.values())), 'seconds': seconds,
            'artifact': delivery.artifact_name(ctx), 'members': len(specs) + 1}


def github_context(req, source):
    event = io.json_bytes(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes(), current.LIMIT)
    trigger = event['workflow_run']
    return delivery.context(req, source, int(os.environ['GITHUB_RUN_ID']), int(os.environ['GITHUB_RUN_ATTEMPT']),
                            trigger['id'], trigger['run_attempt'])


def upload_record(req, ctx):
    artifact_id = int(os.environ['PW_ARTIFACT_ID'])
    row = pw.api('actions/artifacts/' + str(artifact_id))
    delivery.metadata(row, ctx, artifact_id, datetime.now(timezone.utc))
    require(row['digest'] == 'sha256:' + os.environ['PW_ARTIFACT_DIGEST'].removeprefix('sha256:'),
            'Upload and Actions metadata differ')
    return row


def process(action, root, req, mode, ref, source, check):
    require(req['operation'] in delivery.READS, 'Only delivery requests are accepted here')
    ctx = github_context(req, source)
    raw, record, release = bound(root, req)
    def recheck():
        check()
        bound(root, req)
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
            with archive.open('xb') as stream:
                subprocess.run(['gh', 'api', f'repos/{pw.REPO}/actions/artifacts/{row["id"]}/zip'], stdout=stream,
                               check=True, timeout=180, env={**os.environ, 'GH_TOKEN': github_rest.publisher_token()})
            manifest = delivery.verify_archive(archive, row, ctx, req, raw, artifact_id=row['id'])
            require(current.encoded(manifest) == (root / 'pw-delivery/manifest.json').read_bytes(),
                    'Uploaded manifest differs from staging')
        recheck()
        return {'status': 'upload-verified', 'artifact_id': row['id'], 'digest': row['digest'],
                'bytes': row['size_in_bytes'], 'expires': row['expires_at'], 'files': manifest['files'], 'context': ctx}
    require(action == 'inspect-ack', 'Unexpected delivery action')
    recheck()
    pw.delete_ref(Path(__file__).resolve().parents[1], ref, source)
    require(publish_git.remote_head(root, ref) is None, 'Request acknowledgement not confirmed')
    return {'status': 'delivered', 'artifact_id': row['id'], 'request_ref_removed': True, 'context': ctx}
