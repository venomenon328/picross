"""Fail-closed lifecycle declarations for changed test/CI surfaces (no test execution)."""
import argparse
import ast
from datetime import date, datetime, timezone
import hashlib
import json
import math
import os
from pathlib import PurePosixPath
import re
import subprocess
import urllib.request

from ci_scope import classify, content_path

MANIFEST = 'tools/ci_lifecycle.json'
FORMAT = 'picross-ci-lifecycle-v1'
REPO = 'https://github.com/venomenon328/picross/'
COST_KEYS = {'cpu_seconds', 'wall_seconds', 'files', 'bytes', 'pngs'}
SMALL = dict(cpu_seconds=10, wall_seconds=5, files=20, bytes=1048576, pngs=0)
PROSE = {'.md', '.txt'}


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate lifecycle key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def digest(raw):
    return hashlib.sha256(raw).hexdigest() if raw is not None else None


def guarded(path, *, added=False):
    """Closed change boundary, independent of test names, optional labels or output suffixes.

    Existing product sources and prose retain their own review contracts. New
    unknown file classes require a declaration, even outside conventional tools.
    Canonical puzzle deliveries retain the metadata-only content route.
    """
    if path == MANIFEST or content_path(path) or PurePosixPath(path).suffix.lower() in PROSE:
        return False
    return path.startswith(('tools/', 'tests/', 'game/tests/', '.github/')) or added


def cost(value):
    if not isinstance(value, dict) or set(value) != COST_KEYS:
        raise ValueError('Missing CPU/wall/file/byte/PNG costs')
    for key, number in value.items():
        if (isinstance(number, bool) or not isinstance(number, (int, float)) or
                not math.isfinite(number) or number < 0 or
                (key in {'files', 'bytes', 'pngs'} and not isinstance(number, int))):
            raise ValueError('Invalid lifecycle cost: ' + key)
    return value


def feature_url(value):
    if not isinstance(value, str) or not re.fullmatch(re.escape(REPO) + r'(issues|pull)/[1-9][0-9]*', value):
        raise ValueError('Lifecycle needs a repository feature/issue URL')
    return value


def deadline(value, today):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError('Missing concrete ISO lifecycle deadline') from None
    if parsed.isoformat() != value or parsed <= today:
        raise ValueError('Expired lifecycle decision: ' + value)
    return parsed


def executable_anchor(path, raw, anchor):
    """Check the declared reader at its executable entrypoint, not in prose/fixtures."""
    source = raw.decode('utf-8')
    if path.startswith('.github/workflows/') and PurePosixPath(path).suffix in {'.yml', '.yaml'}:
        if anchor in {'on:\n  pull_request:', 'on:\n  workflow_dispatch:', 'on:\n  workflow_call:'}:
            return source.startswith(anchor) or '\n' + anchor in source
        regions, active, indent = [], [], 0
        for line in source.splitlines():
            match = re.match(r'^(\s*)(?:-\s+)?(?:run|uses):\s*(.*)$', line)
            if match:
                if active:
                    regions.append('\n'.join(active))
                active, indent = [match[2]], len(match[1])
            elif active and (not line.strip() or len(line) - len(line.lstrip()) > indent):
                if not line.lstrip().startswith('#'):
                    active.append(line.strip())
            elif active:
                regions.append('\n'.join(active)); active = []
        if active:
            regions.append('\n'.join(active))
        return any(anchor in region for region in regions)
    if path.endswith('.py'):
        return any(anchor in (ast.get_source_segment(source, node) or '') for node in ast.walk(ast.parse(source))
                   if isinstance(node, (ast.Import, ast.ImportFrom)) or
                   (isinstance(node, ast.Call) and
                    (node.func.id if isinstance(node.func, ast.Name) else
                     node.func.attr if isinstance(node.func, ast.Attribute) else '') in
                    {'run', 'run_phase', 'check_call', 'check_output', 'Popen', 'read_text', 'read_bytes', 'open', 'load'}))
    if path.endswith('.gd'):
        return any(anchor in line and re.search(r'\b(?:preload|load)\s*\(', line)
                   for line in source.splitlines() if not line.lstrip().startswith('#'))
    return False


def validate(before, after, old, current, read, *, today, decision, feature_open):
    """before/after: Git blob IDs; read: exact head blobs. No working-tree scan.

    Declarations attest the complete delta, not inferred program complexity.
    Cost estimates and coverage justification remain independently reviewable.
    """
    if not isinstance(current, dict) or set(current) != {'format', 'records', 'closeout'} or current['format'] != FORMAT:
        raise ValueError('Missing lifecycle registry')
    records = current['records']
    if not isinstance(records, list):
        raise ValueError('Invalid lifecycle records')
    closeout = current['closeout']
    if not isinstance(closeout, dict) or set(closeout) != {'feature', 'status', 'added', 'removed', 'temporary', 'cost_change'}:
        raise ValueError('Missing feature closeout/test and artifact accounting')
    feature_url(closeout['feature'])
    if closeout['status'] not in {'in-progress', 'complete'}:
        raise ValueError('Invalid feature closeout status')
    for key in ('added', 'removed', 'cost_change'):
        if not isinstance(closeout[key], str) or not closeout[key].strip():
            raise ValueError('Missing closeout ' + key)
    if not isinstance(closeout['temporary'], list):
        raise ValueError('Missing temporary remainder')
    changed = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    required = {p for p in changed if guarded(p, added=p not in before)}
    covered, ids, report = set(), set(), []
    prior = {r['id']: r for r in old.get('records', [])} if old else {}
    for record in records:
        fields = {'id', 'kind', 'purpose', 'level', 'feature', 'owner', 'sources', 'readers',
                  'selection', 'cost', 'coverage', 'expires', 'retire_when', 'owner_decision'}
        if not isinstance(record, dict) or set(record) != fields:
            raise ValueError('Incomplete or unknown lifecycle fields')
        key = record['id']
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', key) or key in ids:
            raise ValueError('Duplicate/invalid lifecycle ID')
        ids.add(key)
        for field in ('purpose', 'level', 'owner', 'coverage'):
            if not isinstance(record[field], str) or not record[field].strip():
                raise ValueError('Missing lifecycle ' + field)
        feature_url(record['feature'])
        kind = record['kind']
        if kind not in {'permanent-small', 'temporary', 'permanent-heavy'}:
            raise ValueError('Unclassified lifecycle kind')
        costs = cost(record['cost'])
        if kind == 'permanent-small':
            if any(costs[k] > SMALL[k] for k in SMALL) or record['expires'] is not None or record['retire_when'] is not None:
                raise ValueError('Small regression cannot authorize image/large/temporary work')
        else:
            deadline(record['expires'], today)
            if record['retire_when'] != 'feature-closeout-or-deadline':
                raise ValueError('Missing feature-bound retirement/review decision')
            if kind == 'temporary' and (not feature_open(record['feature']) or
                    (closeout['feature'] == record['feature'] and closeout['status'] == 'complete')):
                raise ValueError('Feature complete: temporary check must be retired')
        sources = record['sources']
        if not isinstance(sources, dict) or not sources:
            raise ValueError('Missing source delta binding')
        for path, binding in sources.items():
            if (not isinstance(binding, dict) or set(binding) != {'before', 'after'} or
                    path == MANIFEST or not guarded(path, added=True)):
                raise ValueError('Invalid lifecycle source binding')
            if binding['after'] != after.get(path) or (path in changed and binding['before'] != before.get(path)):
                raise ValueError('Stale source/delta binding: ' + path)
            if path in covered:
                raise ValueError('Duplicate source classification: ' + path)
            covered.add(path)
        live = [p for p in sources if p in after]
        if not live and not any(p in changed for p in sources):
            raise ValueError('Retired lifecycle record must leave active registry')
        expected = classify(list(sources))
        selection = {k: expected[k] for k in ('selected', 'native_groups', 'production_groups', 'browser_request')}
        if record['selection'] != selection:
            raise ValueError('Lifecycle selection differs from actual CI classifier')
        readers = record['readers']
        if not isinstance(readers, list) or (live and not readers):
            raise ValueError('Missing actual lifecycle readers')
        reader_bindings = []
        for reader in readers:
            if not isinstance(reader, dict) or set(reader) != {'path', 'anchor', 'sources'}:
                raise ValueError('Invalid lifecycle reader')
            path, anchor = reader['path'], reader['anchor']
            if path not in after or not isinstance(anchor, str) or not anchor.strip():
                raise ValueError('Missing actual reader entrypoint')
            raw = read(path)
            if not executable_anchor(path, raw, anchor):
                raise ValueError('Reader anchor absent: ' + path)
            targets = reader['sources']
            workflow_event = (path.startswith('.github/workflows/') and PurePosixPath(path).suffix in {'.yml', '.yaml'} and
                              anchor in {'on:\n  pull_request:', 'on:\n  workflow_dispatch:', 'on:\n  workflow_call:'})
            if not isinstance(targets, list) or not targets or any(p not in live or (p == path and not workflow_event) for p in targets):
                raise ValueError('Reader must bind distinct live sources')
            for target in targets:
                if workflow_event and target == path:
                    continue
                name = PurePosixPath(target).name
                discovered = (name.startswith('test_') and name.endswith('.py') and
                              "unittest discover -s tools -p 'test_*.py'" in anchor and target.startswith('tools/'))
                if name not in anchor and target not in anchor and name.removesuffix('.py') not in anchor and not discovered:
                    raise ValueError('Reader does not reference classified source: ' + target)
            reader_bindings.append({'path': path, 'sha256': digest(raw), 'anchor': anchor})
        if set(live) - {p for reader in readers for p in reader['sources']}:
            raise ValueError('Unbound lifecycle source reader')
        previous = prior.get(key)
        extending = previous and (any(previous[field] != record[field] for field in ('kind', 'feature', 'owner', 'retire_when')) or
                                   (previous['expires'] and record['expires'] and record['expires'] > previous['expires']))
        if kind == 'permanent-heavy' or extending:
            decision(record)  # Authored owner comment, exact record fingerprint.
        elif record['owner_decision'] is not None:
            decision(record)
        report.append({'id': key, 'kind': kind, 'cost': costs, 'expires': record['expires'],
                       'sources': sources, 'readers': reader_bindings})
    for key, previous in prior.items():
        if key not in ids and previous['kind'] != 'permanent-small' and any(p in after for p in previous['sources']):
            raise ValueError('Cannot drop active temporary/heavy record without removing its sources')
    if required - covered:
        raise ValueError('Unclassified test/CI/output delta: ' + ', '.join(sorted(required - covered)))
    temporary = sorted(r['id'] for r in records if r['kind'] == 'temporary')
    if closeout['temporary'] != temporary:
        raise ValueError('Closeout hides temporary remainder')
    return {'format': FORMAT, 'accepted': True, 'changed_surfaces': sorted(required),
            'records': report, 'closeout': closeout}


def fingerprint(record):
    payload = {k: v for k, v in record.items() if k != 'owner_decision'}
    return digest(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())


def api(path):
    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request('https://api.github.com/repos/venomenon328/picross/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(1048577)
    if len(raw) > 1048576:
        raise ValueError('Oversized lifecycle decision response')
    return strict_json(raw)


def owner_decision(record):
    url = record['owner_decision']
    match = re.fullmatch(re.escape(REPO) + r'(?:issues|pull)/[1-9][0-9]*#issuecomment-([1-9][0-9]*)', url or '')
    if not match:
        raise ValueError('Separate authored owner decision required')
    comment = api('issues/comments/' + match[1])
    marker = 'CI-LIFECYCLE-APPROVE ' + fingerprint(record)
    if (comment.get('user', {}).get('login') != 'venomenon328' or
            marker not in comment.get('body', '').splitlines() or comment.get('html_url') != url):
        raise ValueError('Owner decision does not approve exact lifecycle/cost/source record')


def is_feature_open(url):
    return api('issues/' + url.rsplit('/', 1)[1]).get('state') == 'open'


def git(*args):
    return subprocess.check_output(['git', *args])


def snapshot(commit):
    if commit == '0' * 40:
        return {}
    if not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('Expected exact lifecycle commit')
    result = {}
    for item in git('ls-tree', '-rz', commit).split(b'\0'):
        if item:
            meta, path = item.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            result[path.decode()] = oid if kind == 'blob' and mode in {'100644', '100755'} else 'unsupported-mode'
    return result


def verify(base, head):
    before, after = snapshot(base), snapshot(head)
    def read(path):
        if after[path] == 'unsupported-mode':
            raise ValueError('Lifecycle source/reader must be regular: ' + path)
        return git('show', head + ':' + path)
    current = strict_json(read(MANIFEST))
    old = strict_json(git('show', base + ':' + MANIFEST)) if MANIFEST in before else None
    result = validate(before, after, old, current, read, today=datetime.now(timezone.utc).date(),
                      decision=owner_decision, feature_open=is_feature_open)
    result.update(base_commit=base, source_head=head, tested_checkout=git('rev-parse', 'HEAD').decode().strip(),
                  run_id=os.environ.get('GITHUB_RUN_ID'), run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = verify(args.base, args.head)
    with open(args.output, 'w', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
