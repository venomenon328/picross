"""APP-B2-T02 only: signed real candidate + exact standalone helper, no install."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import sys
from tools.app_products import PW, PE

from . import update_client as client, update_verifier as verifier
from .update_storage import Stage
from .payload import canonical
from .release import release
from .release_manifest import require, strict_json, digest
from .update_diagnostic import test_identity


class SyntheticChannel:
    """No sockets, URL override, private key file or production trust change."""
    def __init__(self, manifest, signature, files):
        value = strict_json(manifest)
        self.files = {**files, 'manifest.json': manifest, 'manifest.sig.json': signature}
        tag = value['tag']
        self.row = {'id': 1, 'tag_name': tag, 'draft': False, 'prerelease': False,
                    'url': client.API + '/1', 'html_url': 'https://github.com/venomenon328/picross/releases/tag/' + tag,
                    'published_at': 'synthetic-diagnostic', 'assets': []}
        for i, (name, raw) in enumerate(self.files.items(), 1):
            self.row['assets'].append({'id': i, 'name': name, 'size': len(raw), 'state': 'uploaded',
                'url': 'https://api.github.com/repos/venomenon328/picross/releases/assets/' + str(i),
                'browser_download_url': client.DOWNLOAD + tag + '/' + name})
        self.calls = []

    def read(self, url, limit, cancel, deadline):
        self.calls.append(url); client.checkpoint(cancel, deadline)
        raw = canonical([self.row]) if url.startswith(client.API + '?') else self.files[url.rsplit('/', 1)[1]]
        require(len(raw) <= limit, 'Synthetic response limit')
        return raw

    def transfer(self, url, output, limit, cancel, deadline, *, expected=None, received=None):
        raw = self.read(url, limit, cancel, deadline)
        require(len(raw) == expected, 'Synthetic length mismatch')
        for offset in range(0, len(raw), 65536):
            client.checkpoint(cancel, deadline)
            size = output.write(raw[offset:offset+65536])
            if received:
                received(size)


def run(build, output, *, app=PW):
    require(os.name == 'nt' and not output.exists(), 'New Windows diagnosis output required')
    output.mkdir(parents=True)
    product = strict_json((build / 'manifest.json').read_bytes())
    files = {name: (build / name).read_bytes() for name in product['assets']}
    trust, secret = test_identity(app=app)
    raw, signature = verifier._sign(product, files, secret, trust, app=app)
    del secret
    transport = SyntheticChannel(raw, signature, files)
    cancel = threading.Event()
    metadata, assets = client._discover(app.anchor, cancel, transport,
        lambda raw, sig: verifier._verify_metadata(raw, sig, trust, app=app), app=app)
    require(len(transport.calls) == 3 and not any(u.endswith('.msi') for u in transport.calls), 'Downloaded before signature decision')
    with tempfile.TemporaryDirectory(prefix='b2-', dir=output) as temp:
        root = Path(temp)
        stage = Stage(root / ('.launcher' if app == PW else '.updates'))
        try:
            candidate = client._download(metadata, assets, stage, cancel, transport,
                lambda raw, sig, files: verifier._verify(raw, sig, files, trust, app=app))
            require(candidate.binding == metadata.binding, 'Changed client candidate')
        finally:
            stage.cleanup()
        helper = build / 'dist' / app.executable / '_internal' / app.package / 'UpdateHelper.exe'
        components = strict_json((build / 'dist' / app.executable / 'components.json').read_bytes())
        require(digest(helper.read_bytes()) == components['resources']['UpdateHelper.exe'], 'Unbound actual helper')
        detached = root / 'UpdateHelper.exe'; shutil.copyfile(helper, detached)
        compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        driver = root / 'HelperDiagnostic.exe'
        subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64', '/reference:System.Web.Extensions.dll',
                        '/out:' + str(driver), str(Path(__file__).parent / 'packaging/HelperDiagnostic.cs')], check=True)
        identity = release(version=product['version'], app=app)
        from .instance import StateLock
        from .runtime import Runtime
        from .repository import configure
        from .sources import git
        repository = root / 'synthetic-repo'; repository.mkdir()
        git(repository, 'init', '-q', '-b', 'main')
        git(repository, '-c', 'user.name=synthetic', '-c', 'user.email=test@example.invalid',
            'commit', '--allow-empty', '-qm', 'synthetic')
        state = root / 'Zustand ü'
        lock = StateLock(state, app=app); require(lock.acquire(), 'Synthetic state locked')
        runtime = None
        marker = None
        try:
            if app == PW:
                configure(repository, state, refs=['main'], launcher=True)
                runtime = Runtime(lock, product['source_commit'], no_browser=True)
                runtime.start()
            else:
                from tools.puzzle_editor.settings import Settings
                from .update_storage import Preferences
                Settings(state).update(checkout=str(repository), port=43123, theme="dark")
                Preferences(state / '.updates').write(True)
                # The native restarted process acquires this same real global marker.
                from .install_interlock import InstallInterlock
                marker = InstallInterlock(app=PE); marker.acquire()
            environment = {**os.environ, 'PYTHONPATH': str(Path(sys.prefix) / 'Lib/site-packages')}
            result = subprocess.run([str(driver), str(detached), str(build / identity['filename']), product['version'],
                                     product['product_code'], product['upgrade_code'], str(state), product['source_commit'],
                                     str(os.getpid()), app.key, sys._base_executable, str(Path(__file__).resolve().parents[2])], env=environment, capture_output=True, timeout=90)
            require(result.returncode == 0, result.stderr.decode('utf-8', errors='replace'))
            helper_result = strict_json(result.stdout)
        finally:
            if runtime and runtime.thread:
                runtime.request_stop(); require(runtime.stopped.wait(10) and not runtime.error, 'Diagnostic drain incomplete')
            lock.close()
            if marker: marker.close()
    try:
        verifier.verify_metadata(raw, signature, app=app)
    except ValueError:
        pass
    else:
        raise ValueError('Production roots accepted synthetic key')
    result = {'format': 'picross-update-client-diagnostic-v1', 'test_only': True,
              'app': app.key, 'source_commit': product['source_commit'], 'version': product['version'],
              'metadata_before_assets': True, 'full_candidate_verified': True, 'production_root_rejected': True,
              'manifest_sha256': digest(raw), 'helper_bytes': helper.stat().st_size,
              'helper_sha256': digest(helper.read_bytes()), 'helper': helper_result}
    for name, data in {'client-result.json': canonical(result), 'client-manifest.json': raw,
                       'client-signature.json': signature, 'client-public-test-trust.json': canonical(trust)}.items():
        (output / name).write_bytes(data)
    print(canonical(result).decode(), end='')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--app', choices=['pw', 'pe'], default='pw')
    args = parser.parse_args()
    run(args.build, args.output, app=PE if args.app == 'pe' else PW)
