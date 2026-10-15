"""Manually install or roll back a validated static bundle over OpenSSH/SFTP."""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, quote
from urllib.request import Request, urlopen
import uuid

import web_bundle


def config(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or set(value) - {'host', 'user', 'port', 'root', 'url', 'ssh_config'} or not {'host', 'root', 'url'} <= value.keys():
        raise ValueError('Invalid local configuration fields')
    for key in ('host', 'user'):
        if key in value and (not isinstance(value[key], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value[key])):
            raise ValueError('Invalid SSH alias/user')
    port = value.get('port', 22)
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Invalid SSH port')
    root = value['root']
    if (not isinstance(root, str) or not re.fullmatch(r'/[A-Za-z0-9_./-]+/picross-web', root)
            or len(PurePosixPath(root).parts) < 4 or any(p in {'.', '..'} for p in root.split('/'))
            or '//' in root):
        raise ValueError('Root must be an absolute dedicated .../picross-web directory without traversal')
    if not isinstance(value['url'], str):
        raise ValueError('Invalid URL')
    url = urlsplit(value['url'])
    if (not url.hostname or url.username or url.password or url.query or url.fragment or not value['url'].endswith('/')
            or not (url.scheme == 'https' or (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1'}))):
        raise ValueError('URL must be HTTPS with trailing slash (loopback HTTP allowed for reference tests)')
    if 'ssh_config' in value:
        value['ssh_config'] = str(Path(value['ssh_config']).resolve(strict=True))
    return value


class Remote:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.token = uuid.uuid4().hex
        self.locked = False

    def options(self, sftp=False) -> list[str]:
        result = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                  '-o', 'ConnectTimeout=15', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3',
                  '-P' if sftp else '-p', str(self.cfg.get('port', 22))]
        if 'ssh_config' in self.cfg:
            result += ['-F', self.cfg['ssh_config']]
        return result

    def host(self) -> str:
        return (self.cfg['user']+'@' if 'user' in self.cfg else '') + self.cfg['host']

    def run(self, script: str) -> str:
        # The script is stdin, never a locally interpreted shell command.
        result = subprocess.run(['ssh', *self.options(), self.host(), 'sh -s'],
                                input='set -eu\n'+script, text=True, capture_output=True, timeout=180)
        if result.returncode:
            # No SSH config, host, key path or server output is copied into public reports.
            raise RuntimeError(f'SSH operation failed (exit {result.returncode}); inspect local connection/target configuration')
        return result.stdout.strip()

    def prefix(self) -> str:
        return f'cd {shlex.quote(self.cfg["root"])}\n'

    def preflight(self) -> None:
        root = shlex.quote(self.cfg['root'])
        self.run(f'''for command in sh mkdir rmdir mv cp sha256sum find sed cmp cat grep cut rm; do command -v "$command" >/dev/null; done
test -d {root} && test ! -L {root}
cd {root}
test "$(pwd -P)" = {root}
test -f .picross-web && test ! -L .picross-web
test "$(cat .picross-web)" = picross-web-v1
test -w . && test -x .
for name in releases index.html .previous; do test ! -L "$name"; done
if test -e releases; then test -d releases && test -w releases; fi
if test -e index.html; then test -f index.html && grep -q 'data-build="[0-9a-f]' index.html; fi
mv --version >/dev/null
''')

    def acquire(self) -> None:
        self.run(self.prefix()+f'mkdir .deploy-lock\nprintf %s {self.token} > .deploy-lock/owner\n')
        self.locked = True

    def owned(self) -> str:
        return self.prefix()+f'test "$(cat .deploy-lock/owner)" = {self.token}\n'

    def release(self) -> None:
        if self.locked:
            self.run(self.owned()+'rm .deploy-lock/owner\nrmdir .deploy-lock\n')
            self.locked = False

    def current(self) -> str:
        return self.run(self.prefix()+r'''if test -f index.html; then sed -n 's/.*data-build="\([^"]*\)".*/\1/p' index.html; fi
''')

    def validate_release(self, build: str) -> dict:
        if not web_bundle.BUILD_ID.fullmatch(build) or '-player-' not in build:
            raise ValueError('Invalid retained version ID')
        raw = self.run(self.prefix()+f'''test -d releases/{build} && test ! -L releases/{build}
test -z "$(find releases/{build} -type l -print)"
cat releases/{build}/build-manifest.json
''')
        manifest = web_bundle.validate_manifest(json.loads(raw))
        if manifest['build_id'] != build:
            raise ValueError('Retained manifest mismatch')
        checks = []
        for name, entry in manifest['files'].items():
            target = f'releases/{build}/entry.html' if name == 'index.html' else name
            checks.append(f'test "$(sha256sum {shlex.quote(target)} | cut -d " " -f 1)" = {entry["sha256"]}')
        self.run(self.prefix()+'\n'.join(checks)+'\n')
        return manifest

    def upload(self, bundle: Path, manifest: dict) -> None:
        stage = '.staging-'+self.token
        self.run(self.owned()+f'mkdir {stage}\nmkdir -p releases\n')
        with tempfile.TemporaryDirectory(prefix='picross-sftp-') as temporary:
            batch = Path(temporary)/'batch.txt'
            def quoted(value):
                return '"'+str(value).replace('\\', '/').replace('"', '\\"')+'"'
            directories = set()
            for name in manifest['files']:
                directories.update(p.as_posix() for p in PurePosixPath(name).parents if p.as_posix() != '.')
            lines = ['mkdir '+quoted(self.cfg['root']+'/'+stage+'/'+n) for n in sorted(directories, key=lambda n:(n.count('/'), n))]
            lines += ['put '+quoted(bundle/n)+' '+quoted(self.cfg['root']+'/'+stage+'/'+n) for n in manifest['files']]
            lines += ['put '+quoted(bundle/'build-manifest.json')+' '+quoted(self.cfg['root']+'/'+stage+'/build-manifest.json')]
            batch.write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
            result = subprocess.run(['sftp', *self.options(True), '-b', str(batch), self.host()], capture_output=True, timeout=300)
            if result.returncode:
                raise RuntimeError(f'SFTP upload failed (exit {result.returncode}); current version unchanged')
        checks = '\n'.join(f'test "$(sha256sum {shlex.quote(stage+"/"+n)} | cut -d " " -f 1)" = {entry["sha256"]}' for n,entry in manifest['files'].items())
        build = manifest['build_id']
        # Existing releases are immutable. Retrying the same bundle checks every byte.
        compare = '\n'.join(f'cmp {shlex.quote(stage+"/"+n)} {shlex.quote(n)}' for n in manifest['files'] if n.startswith('releases/'))
        self.run(self.owned()+checks+f'''
if test -e releases/{build}; then
  test -d releases/{build} && test ! -L releases/{build}
  test -z "$(find releases/{build} -type l -print)"
  {compare}
  cmp {stage}/build-manifest.json releases/{build}/build-manifest.json
else
  mv -T {stage}/releases/{build} releases/{build}
  cp {stage}/build-manifest.json releases/{build}/build-manifest.json
fi
''')

    def activate(self, build: str) -> None:
        if not web_bundle.BUILD_ID.fullmatch(build) or '-player-' not in build:
            raise ValueError('Invalid player version for activation')
        old = self.current()
        if old and not web_bundle.BUILD_ID.fullmatch(old):
            raise ValueError('Unrecognized active entry')
        previous = f'printf %s {old} > .previous-next\nmv -Tf .previous-next .previous\n' if old and old != build else ''
        self.run(self.owned()+f'''test -d releases/{build} && test ! -L releases/{build}
test -f releases/{build}/entry.html && test ! -L releases/{build}/entry.html
cp releases/{build}/entry.html .entry-{self.token}
{previous}mv -Tf .entry-{self.token} index.html
''')


def check_http(url: str, manifest: dict) -> None:
    import hashlib
    for name, expected in manifest['files'].items():
        with urlopen(Request(url+quote(name), headers={'Cache-Control':'no-cache'}), timeout=30) as response:
            if response.status != 200 or hashlib.sha256(response.read()).hexdigest() != expected['sha256']:
                raise RuntimeError('HTTP resource integrity check failed: '+name)
            media = response.headers.get_content_type()
            required = {'html':'text/html', 'js':'text/javascript', 'wasm':'application/wasm', 'pck':'application/octet-stream'}.get(name.rsplit('.',1)[-1])
            if required and media != required and not (required == 'text/javascript' and media == 'application/javascript'):
                raise RuntimeError('Wrong HTTP MIME type: '+name)
            cache = response.headers.get('Cache-Control', '')
            if (name == 'index.html' and 'no-cache' not in cache and 'no-store' not in cache) or (name != 'index.html' and ('immutable' not in cache or 'max-age=' not in cache)):
                raise RuntimeError('Wrong HTTP cache policy: '+name)


def deploy(cfg: dict, bundle: Path | None, *, dry_run=False, rollback: str | None = None) -> str:
    manifest = web_bundle.validate(bundle) if bundle else None
    remote = Remote(cfg)
    remote.preflight()
    if rollback:
        if not web_bundle.BUILD_ID.fullmatch(rollback) or '-player-' not in rollback:
            raise ValueError('Invalid rollback ID')
        manifest = remote.validate_release(rollback)
    if not manifest:
        raise ValueError('A build or rollback ID is required')
    if dry_run:
        return 'DRY RUN: validated bundle/configuration and read-only target preflight; no files changed'
    before = remote.current()
    try:
        remote.acquire()
        # Recheck the root after acquiring, then bind the previous entry under the lock.
        remote.preflight()
        before = remote.current()
        if before:
            remote.validate_release(before)
        if bundle:
            remote.upload(bundle, manifest)
        else:
            remote.validate_release(manifest['build_id'])
        remote.activate(manifest['build_id'])
        check_http(cfg['url'], manifest)
        return 'DEPLOY PASS: '+manifest['build_id']
    except Exception as error:
        active = remote.current()
        if remote.locked and before and before != manifest['build_id'] and active == manifest['build_id']:
            remote.activate(before)
            active = remote.current()
        raise RuntimeError(f'Deployment failed; active={active or "none"}; prior={before or "none"}. {error}') from error
    finally:
        remote.release()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('web-deploy.local.json'))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', type=Path)
    group.add_argument('--rollback', help='Previously retained build ID')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        print(deploy(config(args.config), args.build.resolve() if args.build else None, dry_run=args.dry_run, rollback=args.rollback))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('DEPLOY FAILED:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
