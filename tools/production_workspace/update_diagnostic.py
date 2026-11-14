"""Explicit synthetic test adapter; excluded from the installed application.

Keys exist only in process memory. Only public roots, signed real-candidate
metadata and checked results are delivered for APP-B1-T02 review.
"""
import argparse
import base64
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from . import update_verifier as verifier
from .payload import canonical
from .release_manifest import digest, require, strict_json, verify_files


def test_identity():
    """Fresh synthetic identity; never a production trust source."""
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes_raw()
    key_id = digest(public)
    trust = {'format': 'picross-pw-trust-v1', 'accepted': {key_id: base64.b64encode(public).decode('ascii')},
             'blocked': [], 'active_signer': key_id}
    return trust, base64.b64encode(private.private_bytes_raw()).decode('ascii')


def run(build, output):
    require(not output.exists(), 'Use a new dedicated diagnosis directory')
    provenance = strict_json((build / 'manifest.json').read_bytes())
    files = {name: (build / name).read_bytes() for name in provenance['assets']}
    verify_files(provenance, files)
    trust, secret = test_identity()
    try:
        raw, signature = verifier._sign(provenance, files, secret, trust)
    finally:
        del secret  # No disk key, artifact key, diagnostic log or exception echo.
    candidate = verifier._verify(raw, signature, files, trust)
    msi = next(name for name in files if name.endswith('.msi'))
    modified = {**files, msi: files[msi] + b'APP-B1 synthetic byte corruption'}
    try:
        verifier._verify(raw, signature, modified, trust)
    except ValueError:
        tampered_rejected = True
    else:
        raise ValueError('Tampered actual MSI candidate accepted')
    try:
        verifier.verify_candidate(raw, signature, files)
    except ValueError:
        production_rejected = True
    else:
        raise ValueError('Synthetic key accepted by production roots')
    result = {'format': 'picross-pw-signature-diagnostic-v1', 'test_only': True,
              'source_commit': candidate.source_commit, 'payload_fingerprint': candidate.payload_fingerprint,
              'version': candidate.version, 'msi_bytes': candidate.msi_bytes, 'msi_sha256': candidate.msi_sha256,
              'manifest_sha256': candidate.binding, 'signature_sha256': digest(signature),
              'test_key_id': candidate.signing_key_id, 'valid_signature': True,
              'tampered_msi_rejected': tampered_rejected, 'production_root_rejected': production_rejected,
              'limits': 'Synthetic key / actual MSI bytes. No publication, installation or update client.'}
    output.mkdir(parents=True)
    for name, value in {'manifest.json': raw, 'manifest.sig.json': signature,
                        'public-test-trust.json': canonical(trust), 'signature-result.json': canonical(result)}.items():
        (output / name).write_bytes(value)
    print(canonical(result).decode('utf-8'), end='')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.build, args.output)
