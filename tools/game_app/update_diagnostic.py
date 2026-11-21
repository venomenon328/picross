"""Excluded Windows diagnosis of the actual PG candidate, launcher and helper."""
import argparse
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from PyInstaller.archive.readers import CArchiveReader

from tools import p1_preflight as toolchain
from tools.game_app.gate_diagnostic import probe as gate_probe
from tools.app_products import PE, PG
from tools.production_workspace import update_client as client, update_verifier as verifier
from tools.production_workspace.helper_diagnostic import SyntheticChannel
from tools.production_workspace.payload import canonical
from tools.production_workspace.release import release
from tools.production_workspace.release_manifest import digest, require, strict_json
from tools.production_workspace.update_diagnostic import test_identity
from tools.production_workspace.update_storage import Preferences, Stage, atomic_json


def rejected(operation, description):
    try:
        operation()
    except ValueError:
        return
    raise ValueError('Unexpected acceptance: ' + description)


def frozen_module(archive, module):
    copy = ModuleType(module.__name__)
    copy.__package__ = module.__package__
    copy.__file__ = module.__file__
    with patch.dict(sys.modules, {copy.__name__: copy}):
        exec(archive.extract(copy.__name__), vars(copy))
    return copy


def client_probe(build, work, output, introduction):
    launcher = build / 'dist' / PG.executable / (PG.executable + '.exe')
    archive = CArchiveReader(str(launcher)).open_embedded_archive('PYZ.pyz')
    update_client = frozen_module(archive, client)
    update_verifier = frozen_module(archive, verifier)
    update_client.verifier = update_verifier
    return verify_client_bytes(build, work, output, update_client, update_verifier, introduction)


def verify_client_bytes(build, work, output, client, verifier, introduction):
    provenance = strict_json((build / 'manifest.json').read_bytes())
    files = {name: (build / name).read_bytes() for name in provenance['assets']}
    trust, secret = test_identity(app=PG)
    try:
        raw, signature = verifier._sign(provenance, files, secret, trust, app=PG)
    finally:
        del secret
    authenticate = lambda body, sig: verifier._verify_metadata(body, sig, trust, app=PG)
    verify = lambda body, sig, assets: verifier._verify(body, sig, assets, trust, app=PG)
    transport = SyntheticChannel(raw, signature, files)
    cancel = threading.Event()
    metadata, assets = client._discover(PG.anchor, cancel, transport, authenticate, app=PG)
    require(len(transport.calls) == 3, 'Downloaded payload before metadata authorization')
    stage = Stage(work / '.updates')
    try:
        whole = client._download(metadata, assets, stage, cancel, transport, verify)
    finally:
        stage.cleanup()
    require(whole.binding == metadata.binding and not stage.path.exists(), 'Incomplete PG stage cleanup')
    local = SimpleNamespace(version=metadata.version, commit=metadata.source_commit,
                            payload_fingerprint=metadata.payload_fingerprint,
                            product_code=provenance['product_code'], upgrade_code=provenance['upgrade_code'])
    transport.calls.clear()
    client._discover(local.version, cancel, transport, authenticate, installation=local, app=PG)
    require(len(transport.calls) == 3, 'Equal PG version downloaded payload bytes')
    local.commit = '0' * 40
    rejected(lambda: client._discover(local.version, cancel, transport, authenticate, installation=local, app=PG),
             'mismatched same-version installation')
    rejected(lambda: client._discover('0.1.65535', cancel, transport, authenticate, app=PG), 'older PG release')
    rejected(lambda: verifier.verify_metadata(raw, signature, app=PG), 'test root in production')
    rejected(lambda: verifier._verify_metadata(raw, signature, {**trust, 'format': PE.trust}, app=PE), 'PG in PE')
    msi = release(version=whole.version, app=PG)['filename']
    rejected(lambda: verify(raw, signature, {**files, msi: files[msi][:-1] + bytes([files[msi][-1] ^ 1])}),
             'tampered real MSI')
    for name, body in {'client-manifest.json': raw, 'client-signature.json': signature,
                       'client-public-test-trust.json': canonical(trust)}.items():
        (output / name).write_bytes(body)
    def download_offer(meta, links, stage, cancelled, *, progress, app):
        return client._download(meta, links, stage, cancelled, transport, verify, progress=progress)

    gate = gate_probe(work / 'gate', output, metadata, assets, download_offer, capture=introduction)
    (output / 'native-gate.json').write_bytes(canonical(gate))
    return {'commit': whole.source_commit, 'candidate_bytes': sum(map(len, files.values())),
            'msi_bytes': whole.msi_bytes, 'msi_sha256': whole.msi_sha256, 'manifest_sha256': whole.binding,
            'positive': 'embedded PYZ client and verifier verified and staged real candidate bytes', 'same_version': 'metadata only',
            'rejected': ['foreign product', 'synthetic key in production', 'tampered MSI', 'local identity mismatch', 'older release']}


def helper_probe(build, work):
    image = build / 'dist' / PG.executable
    helper = image / '_internal' / PG.package / 'UpdateHelper.exe'
    components = strict_json((image / 'components.json').read_bytes())
    sha = digest(helper.read_bytes())
    require(sha == components['resources']['UpdateHelper.exe'], 'Unbound PG helper')
    product = release(version=components['version'], app=PG)
    driver = work / 'GameUpdateDiagnostic.exe'
    compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64',
                    '/out:' + str(driver), str(Path(__file__).with_name('GameUpdateDiagnostic.cs'))], check=True)
    probe = subprocess.run([str(driver), str(helper), str(build / product['filename']), product['version'],
                            product['product_code'], product['upgrade_code']], check=True, capture_output=True,
                           encoding='utf-8', timeout=45)
    return {'sha256': sha, 'bytes': helper.stat().st_size, 'process_and_msi': probe.stdout.splitlines()}, driver


def legacy_helper(build, work):
    # The compatibility case uses the helper that actually shipped with 0.1.3.
    name = 'Picross-Spiel-0.1.3-windows-x64.msi'
    msi = work / name
    urllib.request.urlretrieve('https://github.com/venomenon328/picross/releases/download/pg-v0.1.3/' + name, msi)
    require(toolchain.sha256_file(msi) == 'd84d33d25264371512b9c58160f3a3bae7f23037054810a8688e12bb4b9a7927',
            'Wrong legacy MSI')
    source = work / 'legacy.wxs'
    extracted = work / 'legacy'
    subprocess.run([str(build / 'work/wix/dark.exe'), '-nologo', '-x', str(extracted),
                    '-o', str(source), str(msi)], check=True)
    files = ET.parse(source).findall('.//{*}File[@Name="UpdateHelper.exe"]')
    require(len(files) == 1, 'Ambiguous legacy helper')
    path = Path(files[0].get('SourceFile')).resolve()
    require(path.is_relative_to(extracted.resolve()), 'Unexpected legacy member')
    return path


def restart_probe(build, work, driver, output, *, introduction):
    image = build / 'dist' / PG.executable
    helper = image / '_internal' / PG.package / 'UpdateHelper.exe'
    components = strict_json((image / 'components.json').read_bytes())
    state = work / 'pg-state'
    preferences = Preferences(state / '.updates')
    preferences.write(True)
    before = preferences.path.read_bytes()
    env = toolchain.isolated_environment(work, 'Windows')
    profile = work / 'appdata/Godot/app_userdata/picross · P1'
    save = profile / 'p1/saves/sentinel'
    save.parent.mkdir(parents=True)
    save.write_bytes(b'isolated PG save')
    settings = profile / 'isolated-settings.json'
    settings.write_bytes(b'isolated PG preferences')
    results = []
    modes = ['confirmed', 'identity', 'challenge', 'pid', 'window', 'missing']
    if introduction:
        modes.append('legacy')
    for index, mode in enumerate(modes):
        nonce = str(index) * 48
        stage = state / '.updates/update-staging' / nonce
        stage.mkdir(parents=True)
        adapted = stage / 'UpdateHelper.exe'
        shutil.copyfile(driver, adapted)
        atomic_json(state / '.updates/update-accepted.json', {'nonce': nonce})
        tested_helper = legacy_helper(build, work) if mode == 'legacy' else helper
        msi = release(version=components['version'], app=PG)['filename']
        files = [msi, msi + '.sha256', 'START.txt', 'delivery.json', 'inputs.json',
                 'manifest.json', 'manifest.sig.json', 'UpdateHelper.exe', 'active']
        atomic_json(state / '.updates/update-pending.json', {'format': 'picross-update-pending-v1',
                    'stage': nonce, 'nonce': nonce, 'version': components['version'], 'files': files})
        result = output / f'restart-{mode}.json'
        probe = subprocess.run(
            [str(adapted), '--restart', str(tested_helper), sys._base_executable, str(state), str(image), str(result), mode,
             components['commit'], components['version'], components['payload_fingerprint']],
            env=env, capture_output=True, encoding='utf-8', timeout=100)
        require(probe.returncode == 0, probe.stderr)
        deadline = time.monotonic() + 50
        while not result.is_file() and time.monotonic() < deadline:
            time.sleep(0.1)
        require(strict_json(result.read_bytes())['child_start_count'] == int(mode == 'legacy'),
                'Unexpected restart play count')
        if mode == 'legacy':
            results.append('pg-v0.1.3 UpdateHelper.exe SHA-256 ' + toolchain.sha256_file(tested_helper))
        results.append(probe.stdout.strip())
    require(save.read_bytes() == b'isolated PG save' and settings.read_bytes() == b'isolated PG preferences'
            and preferences.path.read_bytes() == before, 'Protected state changed')
    return results


def run(build, output):
    output.mkdir(exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='pg-update-', dir=output) as folder:
        work = Path(folder)
        plan = strict_json((Path(__file__).resolve().parents[2] / '.ci/package.json').read_bytes())
        introduction = plan['package'] == 'GAME-APP-E' and os.environ.get('GITHUB_REF_NAME') != 'main'
        candidate = client_probe(build, work, output, introduction)
        helper, driver = helper_probe(build, work)
        helper['restart'] = restart_probe(build, work, driver, output, introduction=introduction)
    value = {'client': candidate, 'helper': helper, 'limits': 'Actual MSI and helper methods. Isolated adapter supplies simulated post-MSI context; real PG IPC, child and window.'}
    (output / 'update-client-helper.json').write_bytes(canonical(value))
    print(canonical(value).decode(), end='')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.build.resolve(), args.output.resolve())
