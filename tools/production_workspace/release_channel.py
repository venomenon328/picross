"""Fixed-repository PW release planner and draft-first publisher; no client updater.

GET failures fail closed. Mutations are never blindly retried: the next run
reconciles a bound draft and byte-identical assets without overwriting anything.
"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from .payload import canonical, fingerprint, git
from .release import release, version_tuple
from .release_manifest import (FORMAT, SIGNED_FORMAT, REPOSITORY, require, digest, strict_json,
                               validate_manifest, verify_files)
from . import release_catalog, update_verifier

from tools.app_products import PG, PW, PRODUCTS

REPOSITORY_ID = 1381196633
MANIFEST = 'manifest.json'
PREFIX = '/repos/' + REPOSITORY

# Published release ID and SHA-256 of its original manifest -> tree-identical source.
# Frozen REPO-SLIM-A transition, never consulted for a draft or a new publication.
MIGRATED_RELEASE_TAGS = {
    # pw-v0.1.23
    (450092258, 'a8565cf78cd45369a3d5264456b5b0af89553a15e0b955ff507c4b2d3e493ea7'):
        '00371996be76e525df8dfa7c93304d6c23273a94',
    # pe-v0.2.3
    (450092461, '9f1303e218a92f44b53f04ae30b4f28e34b76fd821fa356fc1ae6bfb49f97817'):
        '00371996be76e525df8dfa7c93304d6c23273a94',
    # pw-v0.1.22
    (448846180, '566c8d969a4aefbcc2fceeb3f96546ca914b7636c86c0b6bc81a865a3a5a7e49'):
        'a5d0e56b2628a12fcc6e3591f5f158db2bd427a5',
    # pw-v0.1.21
    (448598655, '78590f8208f8444cd4a431bcc7cb88f6809ba17a0ab7e2b8c55efa1fb918fc55'):
        'd8c7009d79cd2521a37bfe9645916560f5f0ce05',
    # pw-v0.1.20
    (447829175, '46a7ed660c4acf43468a56852efbfb4c84349c89e621f4f09b1d2caa039cc98f'):
        '761ca50ccf22f297329e8f1950cadae3d3542e0a',
    # pe-v0.2.2
    (448599104, '4bad747dcda7dcf5b0c0cf3fc238466a9726fb7becc3c31a0ff4be68175d4757'):
        'd8c7009d79cd2521a37bfe9645916560f5f0ce05',
    # pe-v0.2.1
    (448454776, '742a9d1c6cbe5ec20656b1ae88ca3796a7f3b0fc851d11dc0b39e5f288f177f9'):
        '6dbd58352c0db6713997a68fbae2f57d162fe6d3',
    # pw-v0.1.19
    (447760701, '981adc440ac80487c0a4a5e151bc3260cc00b25552d6a5b97a9588736d109f21'):
        'a210423eedab26890925873bfe971ef32d2b9fda',
    # pw-v0.1.18
    (447683712, '0c2a4d2795b95fb56eaad9e2f676e086f916b62c8e3b29efdde8e5a536bb8bfe'):
        '37f5eeb105ff38f05d038c6ac9a6262e5cd06917',
    # pw-v0.1.17
    (447333168, 'c63fe5ba76999eaf5872ed801b90a86773a87b20054f731d5e35c00372d68d2e'):
        '794856ede73bfaedeefd9b3f20c76c52bd271b3e',
    # pw-v0.1.16
    (447294688, '8811f888b872cbff6aefe555b60b20926afc66b0e4a99e0ee709903d5bb82a12'):
        'fe2afcca3e66e5a42d2f78420690a4a22c64ea4f',
    # pw-v0.1.15
    (446414366, '9674647f56a304068ca88ba3dd172ff63204cc7438c6f7a43b93a599d6767a04'):
        '0d2ea7a012246b2c0861e985b16c91d9a7f48b34',
    # pw-v0.1.14
    (446207747, 'c7d0bf05b738304743dde05abd37ac5d1192b8919caa68496c55728e420cb868'):
        '2b1faff4f9ad8fd03cd7b26681e26a4509543f85',
    # pw-v0.1.13
    (446069948, 'b03f7c42b11e831ae8198d4d1cc634bef401268db3cbb6687aec3d6c908ecfe5'):
        '0c2a194493c69de7045d0b5b01844f8e99e167c2',
    # pw-v0.1.12
    (446002618, 'a06ea9edf4bab5d0d90ca3365e287f3fcf78d146be216132a9e10fc0c44e2b37'):
        'd625c5aa3afee61d0e296bb29371678bb430b57f',
    # pw-v0.1.11
    (445924596, '027d10aea315e60bde6800a0f7abbfe7b0dce6786ce88d8b2d8600ec1360434c'):
        'd015bc0e694832d90c6a2232ff1a782c24bd69da',
    # pw-v0.1.10
    (445731468, 'f0c7f4a6367ab1c54b76705285a7cb5a315761f5c3d34b4c77c4e1447848b497'):
        '52dea4dae83a968f0e43243c31d1562b25986449',
    # pw-v0.1.9
    (445660244, '3660a390f66f871d3fe05eadbb43679e1819933bc8252625bafcee8caf1fc3d0'):
        '71f63f906837aee5880f6001f4bc9d585f964794',
    # pw-v0.1.8
    (445621888, '2a0c4e4411ba8934d89a0187b406e197902249b7be976c1962799db57d497049'):
        '694a894072e66f17bf7ea93e80edd3fdd8c9f46f',
    # pw-v0.1.7
    (445588978, 'bba409894fef07fc415177fa060766da4b36467b24626f97c4a46df952a1ba0d'):
        '26a0c5fa53fe9c90f8cebc2b0a672676eb0d70db',
    # pw-v0.1.6
    (445565018, 'aacc8a8752fb1c806da146ee3cf9bf3d88f0b8d2fcef8c7e4f500ed4cf565323'):
        'c9a97a7b5d0491195001e32d607eed0f694ae749',
    # pw-v0.1.5
    (445434781, '7565d876ed43a7ba9d00654e7d93678c76a8397a6ca2248a25c91d2aa46af2ea'):
        'f186c94b36475fd886d069923f81c79d54edbca7',
    # pw-v0.1.4
    (445343199, '8b60e3c8beb2259eb48da3aafc41481e2850288c0f442e38d5eafa33e76a3991'):
        'e462c6fc3e5841c621540f43dcfc8762f2bba3d0',
    # pw-v0.1.3
    (444653544, 'f4209df64ab24be18f3642a26b9f2ca1875af829c52ac111c7e87ec29af1adfd'):
        '0be7ee188e8ef1d28d03ed80476cbc237d87ba8e',
    # pw-v0.1.2
    (444471369, '8f64a83b79e6b4bcdcad430a5128dcf7c7f7af6a6eb3e689f4670aac60f517b3'):
        '3d97baecb32dd7da451aec785d32c2086627cd1a',
    # pw-v0.1.1
    (444365769, '522941cc8d1e4beadcf482ebc14e1f971f0e746110e0371a261a26738cc5e6a9'):
        '3579c9004770fd055c8a4ff62492570e405f121c',
}


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        require(target.scheme == 'https' and target.hostname == 'release-assets.githubusercontent.com',
                'Unexpected release asset redirect')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        redirected.remove_header('Authorization')
        return redirected


class RefAlreadyExists(RuntimeError):
    """A competing publisher won atomic creation of the catalog ref."""


class GitHub:
    def __init__(self, token):
        require(bool(token), 'GitHub token required')
        self.token = token

    def request(self, path, *, method='GET', value=None, raw=None, binary=False, upload=False):
        require(path.startswith(PREFIX + '/'), 'Fixed repository API only')
        host = 'https://uploads.github.com' if upload else 'https://api.github.com'
        headers = {'Authorization': 'Bearer ' + self.token, 'X-GitHub-Api-Version': '2022-11-28',
                   'Accept': 'application/octet-stream' if binary else 'application/vnd.github+json',
                   'User-Agent': 'picross-pw-release'}
        data = raw if raw is not None else (canonical(value) if value is not None else None)
        if data is not None:
            headers['Content-Type'] = 'application/octet-stream' if upload else 'application/json'
        req = urllib.request.Request(host + path, data=data, headers=headers, method=method)
        for attempt in range(3):
            try:
                with urllib.request.build_opener(SafeRedirect()).open(req, timeout=90) as response:
                    result = response.read()
                return result if binary or upload else (strict_json(result) if result else None)
            except urllib.error.HTTPError as error:
                if method == 'GET' and error.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(attempt + 1)
                    continue
                if method == 'POST' and path == PREFIX + '/git/refs' and error.code == 422:
                    # Only a positively identified collision is eligible for waiting.
                    if strict_json(error.read(8192)).get('message') == 'Reference already exists':
                        raise RefAlreadyExists('Catalog ref already exists') from None
                if error.code == 404 and method == 'GET':
                    return None
                raise RuntimeError(f'GitHub {method} failed ({error.code}); state must be reconciled on rerun') from None
            except (TimeoutError, urllib.error.URLError):
                if method == 'GET' and attempt < 2:
                    time.sleep(attempt + 1)
                    continue
                raise RuntimeError('GitHub request failed; no publication success assumed') from None

    def pages(self, path, key=None):
        rows = []
        for page in range(1, 10001):
            result = self.request(PREFIX + path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
            require(result is not None, 'Missing GitHub collection')
            batch = result[key] if key else result
            require(isinstance(batch, list), 'Invalid GitHub collection')
            rows.extend(batch)
            if len(batch) < 100:
                return rows
        raise ValueError('Unbounded GitHub collection')

    def asset(self, row):
        require(type(row['id']) is int and row['id'] > 0 and row['state'] == 'uploaded', 'Incomplete release asset')
        raw = self.request(PREFIX + '/releases/assets/' + str(row['id']), binary=True)
        require(isinstance(raw, bytes) and len(raw) == row['size'], 'Release asset byte count mismatch')
        require(row.get('digest') == 'sha256:' + digest(raw), 'Release asset digest mismatch')
        return raw


def trusted_run(api, run_id, source):
    require(type(run_id) is int and run_id > 0 and re.fullmatch('[0-9a-f]{40}', source), 'Invalid CI source binding')
    workflow = api.request(PREFIX + '/actions/workflows/ci-modular.yml')
    run = api.request(PREFIX + '/actions/runs/' + str(run_id))
    require(run is not None and workflow is not None, 'Missing source CI')
    require(run['workflow_id'] == workflow['id'] and run['path'] == '.github/workflows/ci-modular.yml' and
            run['name'] == 'Package CI' and run['event'] == 'push' and run['head_branch'] == 'main' and
            run['head_sha'] == source and run['status'] == 'completed' and run['conclusion'] == 'success',
            'Only successful completed Package CI main pushes are publication sources')
    for key in ('repository', 'head_repository'):
        require(run[key]['full_name'] == REPOSITORY and run[key]['id'] == REPOSITORY_ID,
                'Foreign CI repository')
    jobs = api.pages(f'/actions/runs/{run_id}/attempts/{run["run_attempt"]}/jobs', 'jobs')
    for name in ('docs', 'ci-required'):
        matches = [j for j in jobs if j['name'] == name]
        require(len(matches) == 1 and matches[0]['conclusion'] == 'success' and matches[0]['status'] == 'completed',
                'Missing successful required check: ' + name)
    main = api.request(PREFIX + '/git/ref/heads/main')
    require(main is not None and main['object']['type'] == 'commit' and main['object']['sha'] == source,
            'Source has been superseded on main')
    return run['run_attempt']


def release_files(api, entry, *, app=PW):
    assets = api.pages('/releases/' + str(entry['id']) + '/assets')
    require(len({a['name'] for a in assets}) == len(assets), 'Duplicate release assets')
    by_name = {a['name']: a for a in assets}
    require(MANIFEST in by_name, 'Published application release missing manifest')
    raw = api.asset(by_name[MANIFEST])
    manifest = validate_manifest(strict_json(raw), app=app)
    require(canonical(manifest) == raw and entry['tag_name'] == manifest['tag'] and
            entry['target_commitish'] == manifest['source_commit'] and not entry['prerelease'], 'Release identity mismatch')
    signed = manifest['format'] == app.signed
    require(app != PG or signed, 'PG authority requires signed releases')
    require(set(by_name) == set(manifest['assets']) | {MANIFEST} |
            ({update_verifier.SIGNATURE} if signed else set()), 'Unexpected release assets')
    migrated = None
    if signed and not entry['draft']:
        migrated = MIGRATED_RELEASE_TAGS.get((entry['id'], digest(raw)))
    verify_tag(api, manifest, allow_missing=entry['draft'], migrated_source=migrated)
    files = {name: api.asset(by_name[name]) for name in manifest['assets']}
    if signed:
        update_verifier.verify_candidate(raw, api.asset(by_name[update_verifier.SIGNATURE]), files, app=app)
    else:
        verify_files(manifest, files, app=app)  # Historical version authority, never installation authority.
    return manifest


def authority(api, *, app=PW):
    entries = [r for r in api.pages('/releases') if r['tag_name'].startswith(app.key + '-') and not r['draft']]
    seen = set()
    for entry in entries:
        require(re.fullmatch(re.escape(app.prefix + '.'.join(map(str, app.line)) + '.') + r'(0|[1-9][0-9]*)', entry['tag_name']) and not entry['prerelease'],
                'Invalid published application release')
        require(version_tuple(entry['tag_name'][len(app.prefix):]) > version_tuple(app.anchor), 'Published version is not above the start anchor')
        require(entry['tag_name'] not in seen, 'Duplicate published version')
        seen.add(entry['tag_name'])
    if not entries:
        return None
    latest = max(entries, key=lambda r: version_tuple(r['tag_name'][len(app.prefix):]))
    manifest = release_files(api, latest, app=app)
    return {'id': latest['id'], 'manifest': manifest, 'sha256': digest(canonical(manifest))}


def next_version(inputs, previous, *, app=PW):
    require(release(app=app)['version'] == app.anchor, 'The release start anchor must remain ' + app.anchor)
    if previous:
        require(version_tuple(previous['manifest']['version'])[:2] == app.line, 'Foreign version authority')
    if previous and previous['manifest']['payload_fingerprint'] == inputs['sha256']:
        return None
    current = previous['manifest']['version'] if previous else release(app=app)['version']
    major, minor, patch = version_tuple(current)
    require((major, minor) == app.line and patch < 65535, 'Application publication line exhausted')
    return f'{major}.{minor}.{patch + 1}'


def plan(api, root, source, run_id=None, *, app=PW):
    require(git(root, 'rev-parse', 'HEAD').decode().strip() == source and not git(root, 'status', '--porcelain'),
            'Clean pinned source checkout required')
    attempt = trusted_run(api, run_id, source) if run_id else None
    inputs = fingerprint(root, app=app)
    previous = None if app == PG and run_id is None else authority(api, app=app)
    version = next_version(inputs, previous, app=app)
    return {'format': 'picross-' + app.key + '-plan-v1', 'source_commit': source, 'run_id': run_id, 'run_attempt': attempt,
            'payload_fingerprint': inputs['sha256'], 'authority': previous, 'version': version,
            'diagnostic': run_id is None, 'trust_sha256': digest(canonical(update_verifier.production_trust(app=app)))}


def seal(build, inspection, planned, *, app=PW):
    require(planned['version'] is not None, 'No changed payload to seal')
    product = release(version=planned['version'], app=app)
    names = (product['filename'], product['filename'] + '.sha256', 'delivery.json', 'START.txt', 'inputs.json')
    files = {name: (build / name).read_bytes() for name in names}
    manifest = {'format': app.provenance, 'repository': REPOSITORY, 'status': 'production',
                'version': planned['version'], 'tag': app.prefix + planned['version'],
                'source_commit': planned['source_commit'], 'payload_fingerprint': planned['payload_fingerprint'],
                'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
                'assets': {name: {'bytes': len(raw), 'sha256': digest(raw)} for name, raw in files.items()},
                'inspection': strict_json(inspection.read_bytes())}
    verify_files(manifest, files, app=app)
    (build / MANIFEST).write_bytes(canonical(manifest))
    return manifest


def verify_tag(api, manifest, *, allow_missing, migrated_source=None):
    ref = api.request(PREFIX + '/git/ref/tags/' + manifest['tag'])
    if ref is None:
        require(allow_missing, 'Published release tag missing')
        return
    obj = ref['object']
    # The publisher only creates lightweight tags; reject foreign/annotated refs.
    expected = {manifest['source_commit']}
    if migrated_source is not None:
        expected.add(migrated_source)
    require(obj['type'] == 'commit' and obj['sha'] in expected, 'Conflicting application release tag')


def _candidate(build, planned, *, app=PW):
    manifest_raw = (build / MANIFEST).read_bytes()
    manifest = validate_manifest(strict_json(manifest_raw), app=app)
    require(manifest['format'] == app.provenance and manifest_raw == canonical(manifest), 'Noncanonical v1 build provenance')
    require(all(manifest[k] == planned[k] for k in ('source_commit', 'version', 'payload_fingerprint')), 'Candidate differs from plan')
    files = {name: (build / name).read_bytes() for name in manifest['assets']}
    verify_files(manifest, files, app=app)
    return manifest, files


def _fresh(api, planned, *, app=PW):
    require(trusted_run(api, planned['run_id'], planned['source_commit']) == planned['run_attempt'], 'Source CI attempt changed')
    require(authority(api, app=app) == planned['authority'], 'Published release authority changed; replan')
    require(next_version({'sha256': planned['payload_fingerprint']}, planned['authority'], app=app) == planned['version'],
            'Candidate version is not the next changed-payload version')
    require(digest(canonical(update_verifier.production_trust(app=app))) == planned['trust_sha256'],
            'Signing/trust configuration changed; replan')


def authorize(api, build, planned, *, enabled, signing_enabled, app=PW):
    """Secret-free checks BEFORE a job may reference the signing environment."""
    require(enabled and signing_enabled and not planned['diagnostic'], 'Publication activation/source gate is closed')
    manifest, _ = _candidate(build, planned, app=app)
    _fresh(api, planned, app=app)
    verify_tag(api, manifest, allow_missing=True)
    trust = update_verifier.production_trust(app=app)
    require(trust['active_signer'] is not None, 'Production signing trust is unprovisioned')
    update_verifier._public_key(trust, trust['active_signer'], app=app)
    environment = api.request(PREFIX + '/environments/' + app.environment)
    require(environment is not None and environment.get('name') == app.environment and
            environment.get('deployment_branch_policy') == {'protected_branches': False, 'custom_branch_policies': True},
            'Pre-existing signing environment with explicit main-only policy required')
    rules = api.pages('/environments/' + app.environment + '/deployment-branch-policies', 'branch_policies')
    require(len(rules) == 1 and rules[0].get('name') == 'main' and rules[0].get('type') == 'branch',
            'Signing environment must allow only the main branch')


@contextmanager
def app_catalog_writer(api, source):
    ref = 'heads/' + release_catalog.LOCK_BRANCH
    deadline = time.monotonic() + 300
    while True:
        if api.request(PREFIX + '/git/ref/' + ref) is None:
            try:
                # The pinned main commit is already on GitHub. Creating this ref
                # uploads no objects and cannot replace a work or app owner's ref.
                api.request(PREFIX + '/git/refs', method='POST', value={'ref': 'refs/' + ref, 'sha': source})
                break
            except RefAlreadyExists:
                pass
        require(time.monotonic() < deadline, 'Catalog lease busy; retry publication')
        time.sleep(2)
    try:
        yield
    finally:
        owner = api.request(PREFIX + '/git/ref/' + ref)
        require(owner and owner['object']['sha'] == source, 'Catalog lease changed')
        api.request(PREFIX + '/git/refs/' + ref, method='DELETE')


def publish(api, build, planned, *, enabled, signing_enabled=False, secret=None, app=PW):
    authorize(api, build, planned, enabled=enabled, signing_enabled=signing_enabled, app=app)
    provenance, files = _candidate(build, planned, app=app)
    manifest_raw, signature_raw = update_verifier.sign_candidate(provenance, files, secret, app=app)
    manifest = validate_manifest(strict_json(manifest_raw), app=app)

    with app_catalog_writer(api, manifest['source_commit']):
        return _publish_locked(api, build, planned, enabled, signing_enabled, app,
                               manifest, manifest_raw, signature_raw, files)


def _publish_locked(api, build, planned, enabled, signing_enabled, app, manifest, manifest_raw, signature_raw, files):
    def fresh():
        authorize(api, build, planned, enabled=enabled, signing_enabled=signing_enabled, app=app)
        # The signed bytes must still be trusted at the final publication check.
        update_verifier.verify_candidate(manifest_raw, signature_raw, files, app=app)
        verify_tag(api, manifest, allow_missing=True)

    fresh()
    rows, elapsed = release_catalog.catalog(lambda path: api.request(PREFIX + '/' + path))
    # Read by tag including drafts. Never overwrite or delete a foreign draft/tag.
    matches = [r for r in rows if r['tag_name'] == manifest['tag']]
    require(len(matches) <= 1, 'Ambiguous release candidate')
    stage = 'APP-A' if app == PG else 'APP-B1'
    body = (f'{app.key.upper()} {stage} {manifest["tag"]}\nSource: {manifest["source_commit"]}\n'
            f'Fingerprint: {manifest["payload_fingerprint"]}\nManifest: {digest(manifest_raw)}\n'
            f'Trust: {planned["trust_sha256"]}\nSignature: {digest(signature_raw)}')
    uploads = {**files, MANIFEST: manifest_raw, update_verifier.SIGNATURE: signature_raw}
    present = {a['name'] for a in matches[0]['assets']} if matches else set()
    reserved_apps = len(PRODUCTS) - 1
    release_catalog.capacity(rows, elapsed, manifest['tag'], len(uploads.keys() - present), reserved_apps=reserved_apps)
    if matches:
        entry = matches[0]
        require(entry['draft'] is True and entry['target_commitish'] == manifest['source_commit'] and
                entry['body'] == body and not entry['prerelease'], 'Existing release is not this recoverable draft')
    else:
        entry = api.request(PREFIX + '/releases', method='POST', value={'tag_name': manifest['tag'],
            'target_commitish': manifest['source_commit'], 'name': manifest['tag'], 'body': body,
            'draft': True, 'prerelease': False, 'make_latest': 'false'})
    release_id = entry['id']
    existing = api.pages(f'/releases/{release_id}/assets')
    require(len({a['name'] for a in existing}) == len(existing), 'Duplicate draft assets')
    existing = {a['name']: a for a in existing}
    require(set(existing) <= set(uploads), 'Foreign assets on candidate draft')
    for name, raw in uploads.items():
        if name in existing:
            require(api.asset(existing[name]) == raw, 'Conflicting existing asset; no overwrite')
        else:
            api.request(PREFIX + f'/releases/{release_id}/assets?name=' + urllib.parse.quote(name),
                        method='POST', raw=raw, upload=True)
    # Round-trip every uploaded byte before publication, not only metadata.
    current = api.request(PREFIX + f'/releases/{release_id}')
    require(current['draft'] is True and current['body'] == body, 'Draft changed during upload')
    require(release_files(api, current, app=app) == manifest,
            'Candidate round-trip mismatch')
    fresh()
    rows, elapsed = release_catalog.catalog(lambda path: api.request(PREFIX + '/' + path))
    release_catalog.capacity(rows, elapsed, manifest['tag'], 0, reserved_apps=reserved_apps)
    published = api.request(PREFIX + f'/releases/{release_id}', method='PATCH',
                            value={'draft': False, 'make_latest': 'true'})
    require(not published['draft'] and release_files(api, published, app=app) == manifest, 'Publication not confirmed')
    return published['html_url']


def main(*, app=PW):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'seal', 'authorize', 'publish'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--build', type=Path)
    parser.add_argument('--inspection', type=Path)
    args = parser.parse_args()
    if args.command == 'plan':
        source = git(args.root, 'rev-parse', 'HEAD').decode().strip()
        event = strict_json(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes())
        run_id = None
        require(os.environ['GITHUB_REPOSITORY'] == REPOSITORY, 'Foreign workflow repository')
        if os.environ['GITHUB_EVENT_NAME'] == 'workflow_run':
            run_id = event['workflow_run']['id']
            require(event['action'] == 'completed' and event['workflow_run']['head_sha'] == source,
                    'Wrong triggering source')
        else:
            require(os.environ['GITHUB_EVENT_NAME'] == 'workflow_dispatch', 'Unsupported release event')
        result = plan(GitHub(os.environ['GH_TOKEN']), args.root, source, run_id, app=app)
        args.plan.write_bytes(canonical(result))
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write('version=' + (result['version'] or '') + '\n')
            output.write('changed=' + str(result['version'] is not None).lower() + '\n')
        print(json.dumps({k: result[k] for k in ('source_commit', 'payload_fingerprint', 'version', 'diagnostic')}))
    elif args.command == 'seal':
        seal(args.build, args.inspection, strict_json(args.plan.read_bytes()), app=app)
    else:
        require(os.environ['GITHUB_EVENT_NAME'] == 'workflow_run' and os.environ['GITHUB_REF'] == 'refs/heads/main' and
                os.environ['GITHUB_REPOSITORY'] == REPOSITORY, 'Publisher must run from repository main')
        operation = authorize if args.command == 'authorize' else publish
        planned = strict_json(args.plan.read_bytes())
        require(git(args.root, 'rev-parse', 'HEAD').decode().strip() == planned['source_commit'],
                'Publisher code must match the pinned main source')
        options = {'enabled': os.environ.get(app.key.upper() + '_RELEASE_ENABLED') == 'true',
                   'signing_enabled': os.environ.get(app.key.upper() + '_UPDATE_SIGNING_ENABLED') == 'true'}
        if args.command == 'publish':
            options['secret'] = os.environ.get(app.key.upper() + '_UPDATE_SIGNING_KEY')
        result = operation(GitHub(os.environ['GH_TOKEN']), args.build, planned, app=app, **options)
        if args.command == 'authorize':
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
                output.write('authorized=true\n')
        else:
            print(result)


if __name__ == '__main__':
    main()
