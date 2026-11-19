"""Post-publication diagnostic, using GitHub commit metadata without a history clone."""
import json
import os
import subprocess

from publish_git import CLEAN_MAIN
from ci_growth import forbidden, SHA


def api(path):
    raw = subprocess.check_output(['gh', 'api', 'repos/' + os.environ['GITHUB_REPOSITORY'] + '/' + path])
    return json.loads(raw)


def check(base, head):
    if not all(SHA.fullmatch(s) for s in (base, head)):
        raise ValueError('Invalid event commits')
    if base == '0' * 40:
        base = api('commits/main')['sha']
    if head == base:
        return 0
    if api(f'compare/{CLEAN_MAIN}...{head}?per_page=1')['status'] not in ('ahead', 'identical'):
        raise ValueError('Working ref uses an unclean base')
    page = 1
    seen = set()
    while True:
        comparison = api(f'compare/{base}...{head}?per_page=100&page={page}')
        for row in comparison['commits']:
            commit = row['sha']
            if commit in seen or not row['parents']:
                raise ValueError('Unexpected or imported history')
            seen.add(commit)
            n = 1
            while True:
                files = api(f'commits/{commit}?per_page=100&page={n}')['files']
                for file in files:
                    if file['status'] != 'removed' and forbidden(file['filename']):
                        raise ValueError(commit + ': ' + file['filename'])
                if len(files) < 100:
                    break
                if n == 30:
                    raise ValueError('GitHub commit metadata may be truncated')
                n += 1
        if len(seen) == comparison['total_commits']:
            return len(seen)
        if not comparison['commits']:
            raise ValueError('Incomplete GitHub comparison')
        page += 1


if __name__ == '__main__':
    print('Inspected commits:', check(os.environ['BEFORE'], os.environ['HEAD']))
