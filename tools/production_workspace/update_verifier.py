"""Shared Ed25519 authority verifier. No network, settings or installer execution.

Public entry points always use the reviewed, packaged trust resource. Underscore
helpers are shared with the isolated diagnostic adapter, never configuration APIs.
"""
import base64
import binascii
from dataclasses import dataclass
from pathlib import Path

from .payload import canonical
from .release import release, version_tuple
from .release_manifest import (SIGNED_FORMAT, digest, hex_string, require, shape,
                               strict_json, validate_manifest, verify_files)

SIGNATURE = 'manifest.sig.json'
DOMAIN = b'picross-pw-release-v2\0'
MANIFEST_LIMIT = 64 * 1024
SIGNATURE_LIMIT = 4 * 1024


def _base64(value, size):
    require(type(value) is str, 'Expected strict Base64 text')
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError('Invalid Base64 encoding') from None
    require(len(raw) == size and base64.b64encode(raw).decode('ascii') == value, 'Invalid Base64 length/encoding')
    return raw


def _trust(value):
    shape(value, 'format accepted blocked active_signer', 'Invalid trust configuration')
    require(value['format'] == 'picross-pw-trust-v1' and type(value['accepted']) is dict and
            type(value['blocked']) is list, 'Invalid trust configuration types')
    require(all(hex_string(key, 64) for key in value['blocked']) and
            len(set(value['blocked'])) == len(value['blocked']), 'Invalid blocked key IDs')
    for key, encoded in value['accepted'].items():
        require(hex_string(key, 64) and digest(_base64(encoded, 32)) == key, 'Public key ID mismatch')
    active = value['active_signer']
    require((not value['accepted'] and active is None) or
            (hex_string(active, 64) and active in value['accepted']), 'Invalid active signer')
    # A blocked accepted key is permitted: revocation always takes precedence.
    return value


def production_trust():
    """Fixed resource in the program payload; no caller path or environment root."""
    return _trust(strict_json(Path(__file__).with_name('update-trust.json').read_bytes()))


def _public_key(trust, key_id):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    _trust(trust)
    require(key_id not in trust['blocked'], 'Signing key is blocked')
    require(key_id in trust['accepted'], 'Unknown signing key; trust is not provisioned for this candidate')
    return Ed25519PublicKey.from_public_bytes(_base64(trust['accepted'][key_id], 32))


def _manifest(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MANIFEST_LIMIT, 'Manifest exceeds 64 KiB or is missing')
    value = validate_manifest(strict_json(raw))
    require(value['format'] == SIGNED_FORMAT, 'Legacy provenance is not signed update authority')
    require(canonical(value) == raw, 'Noncanonical manifest bytes')
    return value


@dataclass(frozen=True)
class VerifiedCandidate:
    """Immutable binding returned only after signature AND all asset checks."""
    manifest_bytes: bytes
    signature_bytes: bytes
    version: str
    source_commit: str
    payload_fingerprint: str
    signing_key_id: str
    msi_sha256: str
    msi_bytes: int

    @property
    def binding(self):
        return digest(self.manifest_bytes)


def _verify(manifest_raw, signature_raw, files, trust):
    from cryptography.exceptions import InvalidSignature
    manifest = _manifest(manifest_raw)
    require(type(signature_raw) is bytes and 0 < len(signature_raw) <= SIGNATURE_LIMIT,
            'Signature exceeds 4 KiB or is missing')
    signature = strict_json(signature_raw)
    shape(signature, 'format algorithm key_id signature', 'Invalid signature shape')
    require(canonical(signature) == signature_raw, 'Noncanonical signature bytes')
    require(signature['format'] == 'picross-pw-signature-v1' and signature['algorithm'] == 'Ed25519' and
            signature['key_id'] == manifest['signing_key_id'], 'Signature algorithm/key mismatch')
    key = _public_key(trust, manifest['signing_key_id'])
    try:
        key.verify(_base64(signature['signature'], 64), DOMAIN + manifest_raw)
    except InvalidSignature:
        raise ValueError('Invalid Ed25519 update signature') from None
    verify_files(manifest, files)
    msi = manifest['assets'][release(version=manifest['version'])['filename']]
    return VerifiedCandidate(manifest_raw, signature_raw, manifest['version'], manifest['source_commit'],
                             manifest['payload_fingerprint'], manifest['signing_key_id'], msi['sha256'], msi['bytes'])


def verify_candidate(manifest_raw, signature_raw, files):
    """Authenticate v2 and the five exact asset bytes against packaged roots."""
    return _verify(manifest_raw, signature_raw, files, production_trust())


def assess_update(candidate, local_version, local_binding=None):
    """Pure decision. Same-version no-op requires a known manifest SHA-256.

    The caller supplies its previously authenticated binding, never guessed from
    untrusted metadata. B1 neither reads nor persists installation state.
    """
    require(type(candidate) is VerifiedCandidate, 'Verified candidate required')
    current = version_tuple(local_version)
    require(current[:2] == (0, 1), 'Unsupported local application version')
    incoming = version_tuple(candidate.version)
    require(incoming >= current, 'Downgrade rejected')
    if incoming == current:
        require(hex_string(local_binding, 64) and local_binding == candidate.binding,
                'Same-version candidate has no identical known content binding')
        return 'noop'
    return 'update'


def _sign(provenance, files, secret, trust):
    """Publisher primitive. Secret is canonical Base64 of a raw 32-byte seed."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    _trust(trust)
    active = trust['active_signer']
    require(active is not None, 'Production signing trust is unprovisioned')
    public = _public_key(trust, active)
    require(bool(secret), 'PW_UPDATE_SIGNING_KEY is missing')
    try:
        private = Ed25519PrivateKey.from_private_bytes(_base64(secret, 32))
        require(private.public_key().public_bytes_raw() == public.public_bytes_raw(), 'Signing key pair mismatch')
    except ValueError:
        # Never include supplied secret or library decoding details in logs.
        raise ValueError('Invalid PW_UPDATE_SIGNING_KEY encoding or key pair') from None
    validate_manifest(provenance)
    require(provenance['format'] == 'picross-pw-release-v1', 'Expected verified v1 build provenance')
    verify_files(provenance, files)
    value = {**provenance, 'format': SIGNED_FORMAT, 'platform': 'windows-x64', 'channel': 'stable',
             'signing_key_id': active}
    raw = canonical(value)
    signed = canonical({'format': 'picross-pw-signature-v1', 'algorithm': 'Ed25519', 'key_id': active,
                        'signature': base64.b64encode(private.sign(DOMAIN + raw)).decode('ascii')})
    _verify(raw, signed, files, trust)
    return raw, signed


def sign_candidate(provenance, files, secret):
    """Production signing uses the same immutable application trust source."""
    return _sign(provenance, files, secret, production_trust())
