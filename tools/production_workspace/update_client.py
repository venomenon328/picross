"""Bounded anonymous public GitHub channel. No installer or browser API here."""
from io import BytesIO
import hashlib
import re
import threading
import time
import urllib.parse
import urllib.request

from .release import version_tuple
from .release_manifest import REPOSITORY, require, strict_json
from . import update_verifier as verifier
from .update_storage import no_links

API = 'https://api.github.com/repos/' + REPOSITORY + '/releases'
DOWNLOAD = 'https://github.com/' + REPOSITORY + '/releases/download/'
PAGE_LIMIT = 4
PAGE_BYTES = 4 * 1024 * 1024
TOTAL_BYTES = 512 * 1024 * 1024  # Functional resource bound, not a CI artifact gate.
SIDECAR_BYTES = 8 * 1024 * 1024


class Cancelled(ValueError):
    pass


def checkpoint(cancel, deadline):
    if cancel.is_set():
        raise Cancelled('Update abgebrochen.')
    if time.monotonic() > deadline:
        raise TimeoutError('Update time budget exceeded')


def allowed_url(url, *, initial):
    p = urllib.parse.urlsplit(url)
    require(p.scheme == 'https' and p.port in (None, 443) and not p.username and not p.password and
            not p.fragment and not any(c in url for c in '\r\n\\'), 'Untrusted update URL')
    if initial:
        require(url == initial, 'Update source changed')
        return
    require(p.hostname == 'release-assets.githubusercontent.com' and
            re.fullmatch(r'/github-production-release-asset/[0-9]+/[A-Za-z0-9-]+', p.path),
            'Untrusted release redirect')


class Redirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 2
    max_repeats = 1

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        require(request.full_url.startswith(DOWNLOAD) or
                urllib.parse.urlsplit(request.full_url).hostname == 'release-assets.githubusercontent.com',
                'Release API redirect rejected')
        allowed_url(newurl, initial=None)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class Transport:
    def __init__(self):
        # No environment proxies, .netrc, cookies, credentials or private token.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), Redirects())

    def transfer(self, url, output, limit, cancel, deadline, *, expected=None):
        require(url.startswith(API + '?') or url.startswith(DOWNLOAD), 'Foreign channel')
        allowed_url(url, initial=url)
        checkpoint(cancel, deadline)
        request = urllib.request.Request(url, headers={'Accept': 'application/octet-stream',
            'User-Agent': 'Picross-ProductionWorkspace-Updater', 'Accept-Encoding': 'identity'})
        with self.opener.open(request, timeout=min(10, max(0.1, deadline - time.monotonic()))) as response:
            final = response.geturl()
            allowed_url(final, initial=url if final == url else None)
            require(response.status == 200 and response.headers.get('Content-Encoding', 'identity') == 'identity',
                    'Unexpected HTTP response')
            length = response.headers.get('Content-Length')
            if length is not None:
                require(length.isascii() and length.isdecimal() and int(length) <= limit and
                        (expected is None or int(length) == expected), 'Invalid HTTP length')
            count = 0
            while True:
                checkpoint(cancel, deadline)
                chunk = response.read(min(64 * 1024, limit + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                require(count <= limit, 'Update response exceeds limit')
                output.write(chunk)
            checkpoint(cancel, deadline)
            require((length is None or count == int(length)) and (expected is None or count == expected),
                    'Truncated update response')

    def read(self, url, limit, cancel, deadline):
        buffer = BytesIO()
        self.transfer(url, buffer, limit, cancel, deadline)
        return buffer.getvalue()


def latest_release(transport, cancel, deadline):
    candidates, ids = {}, set()
    for page in range(1, PAGE_LIMIT + 1):
        rows = strict_json(transport.read(API + '?per_page=100&page=' + str(page), PAGE_BYTES, cancel, deadline))
        require(type(rows) is list and len(rows) <= 100, 'Invalid release catalog')
        for row in rows:
            require(type(row) is dict and type(row.get('tag_name')) is str and
                    type(row.get('draft')) is bool and type(row.get('prerelease')) is bool, 'Invalid release row')
            if row['draft'] or row['prerelease'] or not row['tag_name'].startswith('pw-v0.1.'):
                continue
            version = row['tag_name'].removeprefix('pw-v')
            key = version_tuple(version)
            require(key not in candidates and type(row.get('id')) is int and row['id'] > 0 and
                    row['id'] not in ids, 'Ambiguous release authority')
            candidates[key] = row; ids.add(row['id'])
        if len(rows) < 100:
            break
    else:
        raise ValueError('Release catalog limit reached; freshness is unknown')
    require(candidates, 'No published application release available')
    return candidates[max(candidates)]


def release_assets(row):
    require(row.get('url') == API + '/' + str(row['id']) and
            row.get('html_url') == 'https://github.com/' + REPOSITORY + '/releases/tag/' + row['tag_name'] and
            isinstance(row.get('published_at'), str) and row['published_at'] and
            type(row.get('assets')) is list, 'Foreign/incomplete release')
    assets, ids = {}, set()
    for asset in row['assets']:
        require(type(asset) is dict and type(asset.get('name')) is str, 'Invalid release asset')
        name = asset['name']
        require(re.fullmatch(r'[A-Za-z0-9.-]+', name) and name not in assets and
                type(asset.get('id')) is int and asset['id'] > 0 and asset['id'] not in ids and
                type(asset.get('size')) is int and asset['size'] > 0 and asset.get('state') == 'uploaded' and
                asset.get('url') == 'https://api.github.com/repos/' + REPOSITORY + '/releases/assets/' + str(asset['id']) and
                asset.get('browser_download_url') == DOWNLOAD + row['tag_name'] + '/' + name,
                'Unbound/duplicate release asset')
        assets[name] = asset; ids.add(asset['id'])
    return assets


def discover(local_version, cancel, *, transport=None):
    return _discover(local_version, cancel, transport or Transport(), verifier.verify_metadata)


def _discover(local_version, cancel, transport, authenticate):
    """Internal seam used by the excluded synthetic adapter, never user settings."""
    deadline = time.monotonic() + 60
    row = latest_release(transport, cancel, deadline)
    assets = release_assets(row)
    for name, limit in (('manifest.json', verifier.MANIFEST_LIMIT), (verifier.SIGNATURE, verifier.SIGNATURE_LIMIT)):
        require(name in assets and assets[name]['size'] <= limit, 'Signed release metadata missing/too large')
    raw = transport.read(assets['manifest.json']['browser_download_url'], verifier.MANIFEST_LIMIT, cancel, deadline)
    signature = transport.read(assets[verifier.SIGNATURE]['browser_download_url'], verifier.SIGNATURE_LIMIT, cancel, deadline)
    metadata = authenticate(raw, signature)
    manifest = strict_json(metadata.manifest_bytes)
    require(row['tag_name'] == manifest['tag'] and
            set(assets) == set(manifest['assets']) | {'manifest.json', verifier.SIGNATURE} and
            len(raw) == assets['manifest.json']['size'] and len(signature) == assets[verifier.SIGNATURE]['size'],
            'Release/manifest identity changed')
    for name, binding in manifest['assets'].items():
        require(assets[name]['size'] == binding['bytes'] and
                binding['bytes'] <= (TOTAL_BYTES if name.endswith('.msi') else SIDECAR_BYTES), 'Asset size mismatch/limit')
    require(sum(a['bytes'] for a in manifest['assets'].values()) <= TOTAL_BYTES, 'Candidate size limit')
    verifier.assess_update(metadata, local_version)  # Same/old without known binding is not authorized.
    return metadata, assets


def download(metadata, assets, stage, cancel, *, transport=None):
    return _download(metadata, assets, stage, cancel, transport or Transport(), verifier.verify_candidate)


def _download(metadata, assets, stage, cancel, transport, authenticate):
    require(type(metadata) is verifier.VerifiedMetadata, 'Authenticated metadata required')
    manifest = strict_json(metadata.manifest_bytes)
    deadline = time.monotonic() + 300
    stage.write('manifest.json', metadata.manifest_bytes)
    stage.write(verifier.SIGNATURE, metadata.signature_bytes)
    files = {}
    for name, binding in manifest['assets'].items():
        checkpoint(cancel, deadline)
        path = stage.target(name)
        with path.open('xb') as stream:
            transport.transfer(assets[name]['browser_download_url'], stream, binding['bytes'], cancel, deadline,
                               expected=binding['bytes'])
            stream.flush()
        no_links(path)
        raw = path.read_bytes()
        require(len(raw) == binding['bytes'] and hashlib.sha256(raw).hexdigest() == binding['sha256'], 'Download hash mismatch')
        files[name] = raw
    checkpoint(cancel, deadline)
    candidate = authenticate(metadata.manifest_bytes, metadata.signature_bytes, files)
    require(type(candidate) is verifier.VerifiedCandidate and candidate.binding == metadata.binding, 'Candidate changed')
    return candidate
