"""Small Docs gate for new output/archive classes; tree metadata only."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

SHA = re.compile(r'[0-9a-f]{40}\Z')
ARCHIVES = {'.zip', '.gz', '.tgz', '.tar', '.7z', '.rar'}


def tree(commit, *, repository=None, token=None):
    if not commit or commit == '0' * 40:
        return {}
    if not SHA.fullmatch(commit):
        raise ValueError('Expected a complete tree commit ID')
    if repository:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository')
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(
            f'https://api.github.com/repos/{repository}/git/trees/{commit}?recursive=1', headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024:
            raise ValueError('Tree metadata exceeds bound')
        value = json.loads(raw)
        if value.get('truncated') is not False:
            raise ValueError('Incomplete GitHub tree metadata')
        rows = [(r['path'], r['mode'], r['sha'], r.get('size')) for r in value['tree'] if r['type'] != 'tree']
    else:
        # Missing size metadata in a partial clone must never trigger downloads.
        raw = subprocess.check_output(['git', '--no-lazy-fetch', 'ls-tree', '-rlz', commit])
        rows = []
        for item in raw.split(b'\0'):
            if item:
                meta, path = item.split(b'\t', 1)
                mode, kind, oid, size = meta.decode().split()
                if kind != 'blob' or not size.isdecimal():
                    raise ValueError('Missing blob size metadata; use GitHub tree metadata')
                rows.append((path.decode('utf-8'), mode, oid, int(size)))
    result = {}
    for path, mode, oid, size in rows:
        if path in result or not isinstance(size, int) or isinstance(size, bool) or size < 0 or not SHA.fullmatch(oid):
            raise ValueError('Invalid or incomplete file metadata')
        result[path] = {'mode': mode, 'oid': oid, 'bytes': size}
    return result


def forbidden(path):
    """Path classes, not file contents or a growing historic file manifest."""
    lower = path.lower()
    parts = lower.split('/')
    if (lower.startswith(('docs/evidence/', 'docs/design/at_b_integration/')) or
            re.match(r'content/authoring/[^/]+/at-b-r01/', lower)):
        return 'completed evidence/production class'
    if (lower.startswith(('artifacts/', 'game/build/', 'examples/rp5/baseline/')) or
            set(parts) & {'.godot', '.venv', '__pycache__', 'node_modules', 'screenshots', 'captures', 'runs'}):
        return 'generated output class'
    suffix = Path(lower).suffix
    if suffix in {'.log', '.pck', '.wasm', '.exe', '.dll', '.pyc', '.pyo'}:
        return 'runtime/build output'
    if suffix in ARCHIVES:
        # Open authoring/export namespaces remain possible. Their actual open
        # status needs production review, never binary inspection in this gate.
        if not re.fullmatch(r'content/(authoring|packages)/pz-[a-z0-9][a-z0-9-]{0,59}/'
                            r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}/[a-zA-Z0-9_./ -]+', path):
            return 'archive outside live production'
        if any(p in {'.', '..'} or p.startswith('.') for p in parts):
            return 'noncanonical production archive'
    return None


def compare(before, after):
    added = sorted(after.keys() - before.keys())
    blocked = {p: forbidden(p) for p in added if forbidden(p)}
    if blocked:
        raise ValueError('Disallowed new repository outputs: ' + json.dumps(blocked, sort_keys=True))
    def totals(files):
        return {'files': len(files), 'bytes': sum(f['bytes'] for f in files.values())}
    old, new = totals(before), totals(after)
    return {'format': 'picross-tree-growth-v1', 'before': old, 'after': new,
            'delta': {k: new[k] - old[k] for k in old},
            'added': {'files': len(added), 'bytes': sum(after[p]['bytes'] for p in added)},
            'removed': {'files': len(before.keys() - after.keys()),
                        'bytes': sum(before[p]['bytes'] for p in before.keys() - after.keys())},
            'modified_files': sum(before[p] != after[p] for p in before.keys() & after.keys())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    remote = {'repository': os.environ['GITHUB_REPOSITORY'], 'token': os.environ['GH_TOKEN']} if os.environ.get('GITHUB_ACTIONS') == 'true' else {}
    result = compare(tree(args.base, **remote), tree(args.head, **remote))
    result.update(base_commit=args.base, source_head=args.head)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
