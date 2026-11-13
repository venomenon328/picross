"""APP-B1-T01: real signatures, fixed production roots and closed update decisions."""
import base64
import copy
from dataclasses import FrozenInstanceError
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from tools import test_production_installer as fixtures
from tools.production_workspace import update_verifier as verifier
from tools.production_workspace import update_diagnostic as diagnostic
from tools.production_workspace.payload import canonical
from tools.production_workspace.release_manifest import digest, strict_json


class UpdateVerifierTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='app-b1-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.api = fixtures.MemoryGitHub()
        self.trust, self.secret = diagnostic.test_identity()
        self.planned, self.provenance = fixtures.AppReleaseTests.candidate(self)
        self.files = {name: (self.root / name).read_bytes() for name in self.provenance['assets']}
        self.raw, self.signature = verifier._sign(self.provenance, self.files, self.secret, self.trust)

    def verify(self, raw=None, signature=None, files=None, trust=None):
        return verifier._verify(self.raw if raw is None else raw, self.signature if signature is None else signature,
                                self.files if files is None else files, self.trust if trust is None else trust)

    def resign(self, value):
        raw = canonical(value)
        key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(self.secret))
        sig = {**strict_json(self.signature), 'signature': base64.b64encode(key.sign(verifier.DOMAIN + raw)).decode()}
        return raw, canonical(sig)

    def test_rfc8032_empty_message_known_vector_and_negative(self):
        # RFC 8032 section 7.1 TEST 1; a published vector, not a production key.
        public = bytes.fromhex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
        signature = bytes.fromhex('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f'
                                  'b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
        key = Ed25519PublicKey.from_public_bytes(public)
        key.verify(signature, b'')
        with self.assertRaises(InvalidSignature):
            key.verify(signature, b'changed')

    def test_verified_result_binds_all_bytes_and_is_immutable(self):
        result = self.verify()
        self.assertEqual(result.binding, digest(self.raw))
        self.assertEqual(result.manifest_bytes, self.raw)
        self.assertEqual(result.signature_bytes, self.signature)
        self.assertEqual(result.source_commit, self.planned['source_commit'])
        with self.assertRaises(FrozenInstanceError):
            result.version = '0.1.9'
        for name in self.files:
            with self.subTest(asset=name), self.assertRaises(ValueError):
                self.verify(files={**self.files, name: self.files[name] + b'tamper'})
        with self.assertRaises(ValueError):
            self.verify(files={**self.files, 'extra.exe': b'unbound'})

    def test_fixed_production_root_rejects_test_key_environment_and_missing_signature(self):
        with patch.dict(os.environ, {'PW_UPDATE_TRUST': str(self.root), 'PW_UPDATE_TEST_KEY': self.secret}):
            with self.assertRaisesRegex(ValueError, 'Unknown signing key'):
                verifier.verify_candidate(self.raw, self.signature, self.files)
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.verify(signature=b'')
        with self.assertRaisesRegex(ValueError, 'Legacy'):
            self.verify(raw=canonical(self.provenance))

    def test_canonical_utf8_duplicates_unknown_fields_nonfinite_and_bounds(self):
        for raw in (self.raw.rstrip(b'\n'), b' ' + self.raw, self.raw.replace(b'"format":', b'"format" :'),
                    self.raw.replace(b'{', b'{"format":"duplicate",', 1),
                    self.raw.replace(b'"production"', b'NaN'), self.raw.replace(b'"production"', b'Infinity'),
                    self.raw.decode().encode('utf-16'), b'\xff', b'x' * (verifier.MANIFEST_LIMIT + 1)):
            with self.subTest(raw=raw[:30]), self.assertRaises(ValueError):
                self.verify(raw=raw)
        for signature in (b' ' + self.signature, self.signature.rstrip(b'\n'),
                          self.signature.replace(b'{', b'{"algorithm":"Ed25519",', 1),
                          b'x' * (verifier.SIGNATURE_LIMIT + 1), b'\xff'):
            with self.subTest(signature=signature[:20]), self.assertRaises(ValueError):
                self.verify(signature=signature)

    def test_closed_shape_types_channel_platform_source_and_product(self):
        manifest = strict_json(self.raw)
        changes = [('format', 'picross-pw-release-v99'), ('repository', 'foreign/repo'), ('platform', 'linux-x64'),
                   ('channel', 'preview'), ('source_commit', 'main'), ('payload_fingerprint', 1),
                   ('product_code', 'wrong'), ('upgrade_code', 'wrong'), ('signing_key_id', ''),
                   ('download_url', 'https://untrusted.invalid/app.msi'), ('assets', []), ('inspection', []),
                   ('version', True), ('version', '1.0.0'), ('version', '0.1.01')]
        for name, value in changes:
            raw, signature = self.resign({**manifest, name: value})
            with self.subTest(field=name, value=value), self.assertRaises(ValueError):
                self.verify(raw=raw, signature=signature)
        for name, value in [('compared_to_build', 1), ('inventory_files', True), ('license_files', 2.0),
                            ('limits', []), ('msi_bytes', True), ('commit', 'b' * 40)]:
            changed = copy.deepcopy(manifest); changed['inspection'][name] = value
            with self.subTest(inspection=name), self.assertRaises(ValueError):
                self.verify(*self.resign(changed))

    def test_signature_algorithm_key_id_domain_base64_and_actual_bytes(self):
        sig = strict_json(self.signature)
        for name, value in [('algorithm', 'RSA'), ('key_id', 'f' * 64), ('signature', 'AA=='),
                            ('signature', sig['signature'] + '\n'), ('signature', '*' * 88),
                            ('extra', True), ('format', 'unknown')]:
            with self.subTest(field=name), self.assertRaises(ValueError):
                self.verify(signature=canonical({**sig, name: value}))
        private = Ed25519PrivateKey.from_private_bytes(base64.b64decode(self.secret))
        for message in (self.raw, b'picross-pw-release-v2' + self.raw, verifier.DOMAIN + b'\0' + self.raw):
            signed = canonical({**sig, 'signature': base64.b64encode(private.sign(message)).decode()})
            with self.assertRaisesRegex(ValueError, 'Invalid Ed25519'):
                self.verify(signature=signed)
        # Still canonical and semantically valid, but signature binds different bytes.
        with self.assertRaisesRegex(ValueError, 'Invalid Ed25519'):
            self.verify(raw=self.raw.replace(b'"stable"', b'"stable"', 1).replace(b'a' * 40, b'b' * 40))

    def test_rotation_blocking_and_offline_old_root_have_no_implicit_bridge(self):
        new, secret = diagnostic.test_identity()
        raw, signed = verifier._sign(self.provenance, self.files, secret, new)
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            self.verify(raw=raw, signature=signed)  # Offline client missed the new root.
        transition = {**self.trust, 'accepted': {**self.trust['accepted'], **new['accepted']}}
        self.verify(raw=raw, signature=signed, trust=transition)
        blocked = {**transition, 'blocked': [self.trust['active_signer']]}
        with self.assertRaisesRegex(ValueError, 'blocked'):
            self.verify(trust=blocked)
        with self.assertRaisesRegex(ValueError, 'blocked'):
            verifier._sign(self.provenance, self.files, self.secret, blocked)
        bad = {**self.trust, 'accepted': {self.trust['active_signer']: base64.b64encode(b'x' * 32).decode()}}
        with self.assertRaisesRegex(ValueError, 'ID mismatch'):
            self.verify(trust=bad)

    def test_monotone_decision_noop_needs_known_binding(self):
        candidate = self.verify()
        self.assertEqual(verifier.assess_update(candidate, '0.1.0'), 'update')
        self.assertEqual(verifier.assess_update(candidate, '0.1.1', candidate.binding), 'noop')
        for version, binding in [('0.1.1', None), ('0.1.1', '0' * 64), ('0.1.2', candidate.binding),
                                 ('0.2.0', None), ('0.1.01', None)]:
            with self.subTest(version=version, binding=binding), self.assertRaises(ValueError):
                verifier.assess_update(candidate, version, binding)

    def test_signing_failures_do_not_echo_secrets(self):
        for secret in (None, '', 'sensitive-invalid-secret', base64.b64encode(b'x' * 32).decode()):
            with self.subTest(secret_present=bool(secret)), self.assertRaises(ValueError) as caught:
                verifier._sign(self.provenance, self.files, secret, self.trust)
            if secret:
                self.assertNotIn(secret, str(caught.exception))
        with self.assertRaisesRegex(ValueError, 'unprovisioned'):
            verifier.sign_candidate(self.provenance, self.files, self.secret)


if __name__ == '__main__':
    unittest.main()
