"""APP-B2-T02 only: signed real candidate + exact standalone helper, no install."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

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

    def transfer(self, url, output, limit, cancel, deadline, *, expected=None):
        raw = self.read(url, limit, cancel, deadline)
        require(len(raw) == expected, 'Synthetic length mismatch')
        for offset in range(0, len(raw), 65536):
            client.checkpoint(cancel, deadline); output.write(raw[offset:offset+65536])


def run(build, output):
    require(os.name == 'nt' and not output.exists(), 'New Windows diagnosis output required')
    output.mkdir(parents=True)
    product = strict_json((build / 'manifest.json').read_bytes())
    files = {name: (build / name).read_bytes() for name in product['assets']}
    trust, secret = test_identity()
    raw, signature = verifier._sign(product, files, secret, trust)
    del secret
    transport = SyntheticChannel(raw, signature, files)
    cancel = threading.Event()
    metadata, assets = client._discover('0.1.0', cancel, transport,
        lambda raw, sig: verifier._verify_metadata(raw, sig, trust))
    require(len(transport.calls) == 3 and not any(u.endswith('.msi') for u in transport.calls), 'Downloaded before signature decision')
    with tempfile.TemporaryDirectory(prefix='b2-', dir=output) as temp:
        root = Path(temp)
        stage = Stage(root / '.launcher')
        try:
            candidate = client._download(metadata, assets, stage, cancel, transport,
                lambda raw, sig, files: verifier._verify(raw, sig, files, trust))
            require(candidate.binding == metadata.binding, 'Changed client candidate')
        finally:
            stage.cleanup()
        helper = build / 'dist/Picross-Start/_internal/tools/production_workspace/UpdateHelper.exe'
        components = strict_json((build / 'dist/Picross-Start/components.json').read_bytes())
        require(digest(helper.read_bytes()) == components['resources']['UpdateHelper.exe'], 'Unbound actual helper')
        detached = root / 'UpdateHelper.exe'; shutil.copyfile(helper, detached)
        compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        driver = root / 'HelperDiagnostic.exe'
        subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64', '/reference:System.Web.Extensions.dll',
                        '/out:' + str(driver), str(Path(__file__).parent / 'packaging/HelperDiagnostic.cs')], check=True)
        identity = release(version=product['version'])
        result = subprocess.run([str(driver), str(detached), str(build / identity['filename']), product['version'],
                                 product['product_code'], product['upgrade_code']], check=True, capture_output=True, timeout=60)
        helper_result = strict_json(result.stdout)
    try:
        verifier.verify_metadata(raw, signature)
    except ValueError:
        pass
    else:
        raise ValueError('Production roots accepted synthetic key')
    result = {'format': 'picross-update-client-diagnostic-v1', 'test_only': True,
              'source_commit': product['source_commit'], 'version': product['version'],
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
    args = parser.parse_args()
    run(args.build, args.output)
