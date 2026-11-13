"""Fixed-repository PW release planner and draft-first publisher; no client updater.

GET failures fail closed. Mutations are never blindly retried: the next run
reconciles a bound draft and byte-identical assets without overwriting anything.
"""
import argparse
import hashlib
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

REPOSITORY = 'venomenon328/picross'
REPOSITORY_ID = 1381196633
FORMAT = 'picross-pw-release-v1'
MANIFEST = 'manifest.json'
PREFIX = '/repos/' + REPOSITORY


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        require(target.scheme == 'https' and target.hostname == 'release-assets.githubusercontent.com',
                'Unexpected release asset redirect')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        redirected.remove_header('Authorization')
        return redirected


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
                return result if binary or upload else strict_json(result)
            except urllib.error.HTTPError as error:
                if method == 'GET' and error.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(attempt + 1)
                    continue
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


def validate_manifest(value):
    require(set(value) == {'format', 'repository', 'status', 'version', 'tag', 'source_commit',
                           'payload_fingerprint', 'product_code', 'upgrade_code', 'assets', 'inspection'},
            'Invalid release manifest shape')
    require(value['format'] == FORMAT and value['repository'] == REPOSITORY and value['status'] == 'production',
            'Foreign or nonproduction manifest')
    version = version_tuple(value['version'])
    require(version[:2] == (0, 1) and version > (0, 1, 0) and value['tag'] == 'pw-v' + value['version'],
            'Unsupported published version')
    require(re.fullmatch('[0-9a-f]{40}', value['source_commit']) and
            re.fullmatch('[0-9a-f]{64}', value['payload_fingerprint']), 'Invalid source/fingerprint')
    product = release(version=value['version'])
    require(all(value[k] == product[k] for k in ('product_code', 'upgrade_code')), 'Foreign product identity')
    names = {product['filename'], product['filename'] + '.sha256', 'delivery.json', 'START.txt', 'inputs.json'}
    require(set(value['assets']) == names, 'Incomplete release assets')
    for row in value['assets'].values():
        require(set(row) == {'bytes', 'sha256'} and type(row['bytes']) is int and row['bytes'] > 0 and
                re.fullmatch('[0-9a-f]{64}', row['sha256']), 'Invalid asset binding')
    inspection = value['inspection']
    require(inspection['commit'] == value['source_commit'] and inspection['version'] == value['version'] and
            inspection['payload_fingerprint'] == value['payload_fingerprint'] and inspection['compared_to_build'] is True and
            inspection['msi_sha256'] == value['assets'][product['filename']]['sha256'] and
            inspection['msi_bytes'] == value['assets'][product['filename']]['bytes'], 'Unbound MSI inspection')
    return value


def verify_files(manifest, files):
    validate_manifest(manifest)
    require(set(files) == set(manifest['assets']), 'Unexpected or missing candidate file')
    for name, row in manifest['assets'].items():
        require(len(files[name]) == row['bytes'] and digest(files[name]) == row['sha256'], 'Asset hash mismatch: ' + name)
    product = release(version=manifest['version'])
    report = strict_json(files['delivery.json'])
    require(all(report[k] == manifest[v] for k, v in (('version', 'version'), ('commit', 'source_commit'),
            ('payload_fingerprint', 'payload_fingerprint'), ('product_code', 'product_code'), ('upgrade_code', 'upgrade_code'))),
            'Unbound delivery report')
    msi = product['filename']
    require(report['msi_file'] == msi and report['msi_bytes'] == len(files[msi]) and report['msi_sha256'] == digest(files[msi]),
            'Unbound MSI delivery bytes')
    require(files[msi + '.sha256'] == (digest(files[msi]) + '  ' + msi + '\n').encode(), 'Invalid checksum sidecar')
    inputs = strict_json(files['inputs.json'])
    require(inputs['format'] == 'picross-app-inputs-v1' and inputs['sha256'] == manifest['payload_fingerprint'] and
            digest(canonical(inputs['files'])) == inputs['sha256'], 'Invalid input fingerprint inventory')


def release_files(api, entry):
    assets = api.pages('/releases/' + str(entry['id']) + '/assets')
    require(len({a['name'] for a in assets}) == len(assets), 'Duplicate release assets')
    by_name = {a['name']: a for a in assets}
    require(MANIFEST in by_name, 'Published PW release missing manifest')
    raw = api.asset(by_name[MANIFEST])
    manifest = validate_manifest(strict_json(raw))
    require(canonical(manifest) == raw and entry['tag_name'] == manifest['tag'] and
            entry['target_commitish'] == manifest['source_commit'] and not entry['prerelease'], 'Release identity mismatch')
    require(set(by_name) == set(manifest['assets']) | {MANIFEST}, 'Unexpected release assets')
    verify_tag(api, manifest, allow_missing=entry['draft'])
    verify_files(manifest, {name: api.asset(by_name[name]) for name in manifest['assets']})
    return manifest


def authority(api):
    entries = [r for r in api.pages('/releases') if r['tag_name'].startswith('pw-') and not r['draft']]
    seen = set()
    for entry in entries:
        require(re.fullmatch(r'pw-v0\.1\.(0|[1-9][0-9]*)', entry['tag_name']) and not entry['prerelease'],
                'Invalid published PW release')
        require(version_tuple(entry['tag_name'][4:]) > (0, 1, 0), 'Published version is not above the start anchor')
        require(entry['tag_name'] not in seen, 'Duplicate published version')
        seen.add(entry['tag_name'])
    if not entries:
        return None
    latest = max(entries, key=lambda r: version_tuple(r['tag_name'][4:]))
    manifest = release_files(api, latest)
    return {'id': latest['id'], 'manifest': manifest, 'sha256': digest(canonical(manifest))}


def next_version(inputs, previous):
    if previous and previous['manifest']['payload_fingerprint'] == inputs['sha256']:
        return None
    current = previous['manifest']['version'] if previous else release()['version']
    major, minor, patch = version_tuple(current)
    require((major, minor) == (0, 1) and patch < 65535, '0.1.x publication line exhausted')
    return f'{major}.{minor}.{patch + 1}'


def plan(api, root, source, run_id=None):
    require(git(root, 'rev-parse', 'HEAD').decode().strip() == source and not git(root, 'status', '--porcelain'),
            'Clean pinned source checkout required')
    attempt = trusted_run(api, run_id, source) if run_id else None
    inputs = fingerprint(root)
    previous = authority(api)
    version = next_version(inputs, previous)
    return {'format': 'picross-pw-plan-v1', 'source_commit': source, 'run_id': run_id, 'run_attempt': attempt,
            'payload_fingerprint': inputs['sha256'], 'authority': previous, 'version': version,
            'diagnostic': run_id is None}


def seal(build, inspection, planned):
    require(planned['version'] is not None, 'No changed payload to seal')
    product = release(version=planned['version'])
    names = (product['filename'], product['filename'] + '.sha256', 'delivery.json', 'START.txt', 'inputs.json')
    files = {name: (build / name).read_bytes() for name in names}
    manifest = {'format': FORMAT, 'repository': REPOSITORY, 'status': 'production',
                'version': planned['version'], 'tag': 'pw-v' + planned['version'],
                'source_commit': planned['source_commit'], 'payload_fingerprint': planned['payload_fingerprint'],
                'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
                'assets': {name: {'bytes': len(raw), 'sha256': digest(raw)} for name, raw in files.items()},
                'inspection': strict_json(inspection.read_bytes())}
    verify_files(manifest, files)
    (build / MANIFEST).write_bytes(canonical(manifest))
    return manifest


def verify_tag(api, manifest, *, allow_missing):
    ref = api.request(PREFIX + '/git/ref/tags/' + manifest['tag'])
    if ref is None:
        require(allow_missing, 'Published release tag missing')
        return
    obj = ref['object']
    # The publisher only creates lightweight tags; reject foreign/annotated refs.
    require(obj['type'] == 'commit' and obj['sha'] == manifest['source_commit'], 'Conflicting PW release tag')


def publish(api, build, planned, *, enabled):
    require(enabled and not planned['diagnostic'], 'Publication activation/source gate is closed')
    manifest_raw = (build / MANIFEST).read_bytes()
    manifest = validate_manifest(strict_json(manifest_raw))
    require(manifest_raw == canonical(manifest), 'Noncanonical candidate manifest')
    require(all(manifest[k] == planned[k] for k in ('source_commit', 'version', 'payload_fingerprint')), 'Candidate differs from plan')
    files = {name: (build / name).read_bytes() for name in manifest['assets']}
    verify_files(manifest, files)

    def fresh():
        require(trusted_run(api, planned['run_id'], planned['source_commit']) == planned['run_attempt'], 'Source CI attempt changed')
        require(authority(api) == planned['authority'], 'Published release authority changed; replan')
        verify_tag(api, manifest, allow_missing=True)

    fresh()
    # Read by tag including drafts. Never overwrite or delete a foreign draft/tag.
    matches = [r for r in api.pages('/releases') if r['tag_name'] == manifest['tag']]
    require(len(matches) <= 1, 'Ambiguous release candidate')
    body = f'PW APP-A {manifest["tag"]}\nSource: {manifest["source_commit"]}\nFingerprint: {manifest["payload_fingerprint"]}'
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
    uploads = {**files, MANIFEST: manifest_raw}  # Manifest last; draft stays invisible until all bytes match.
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
    require(release_files(api, current) == manifest,
            'Candidate round-trip mismatch')
    fresh()
    published = api.request(PREFIX + f'/releases/{release_id}', method='PATCH',
                            value={'draft': False, 'make_latest': 'true'})
    require(not published['draft'] and release_files(api, published) == manifest, 'Publication not confirmed')
    return published['html_url']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'seal', 'publish'))
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
        result = plan(GitHub(os.environ['GH_TOKEN']), args.root, source, run_id)
        args.plan.write_bytes(canonical(result))
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write('version=' + (result['version'] or '') + '\n')
            output.write('changed=' + str(result['version'] is not None).lower() + '\n')
        print(json.dumps({k: result[k] for k in ('source_commit', 'payload_fingerprint', 'version', 'diagnostic')}))
    elif args.command == 'seal':
        seal(args.build, args.inspection, strict_json(args.plan.read_bytes()))
    else:
        require(os.environ['GITHUB_EVENT_NAME'] == 'workflow_run' and os.environ['GITHUB_REF'] == 'refs/heads/main' and
                os.environ['GITHUB_REPOSITORY'] == REPOSITORY, 'Publisher must run from repository main')
        print(publish(GitHub(os.environ['GH_TOKEN']), args.build, strict_json(args.plan.read_bytes()),
                      enabled=os.environ.get('PW_RELEASE_ENABLED') == 'true'))


if __name__ == '__main__':
    main()
