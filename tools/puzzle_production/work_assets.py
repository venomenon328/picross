"""Read published production originals by an immutable GitHub asset identity."""
import json
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from . import current_content as content
from . import github_rest
from .authoring_package import require, ID
from .contract import exact_keys

FORMAT = 'picross-authoring-current-v2'
REPOSITORY = github_rest.REPOSITORY
API = github_rest.API
FIELDS = {'repository', 'job', 'release_id', 'asset_id'}


def local_ref(ref):
    return {k: ref[k] for k in ('file', 'bytes', 'sha256')}


def validate(ref, job, limit):
    exact_keys(ref, {'file', 'bytes', 'sha256', 'asset'})
    content.reference(local_ref(ref), limit=limit)
    identity = ref['asset']
    exact_keys(identity, FIELDS)
    require(identity['repository'] == REPOSITORY and identity['job'] == job and ID.fullmatch(job)
            and ref['file'].startswith('content/authoring/' + job + '/')
            and ref['file'].split('/')[-1] not in ('record.json', '.current-operation.json'),
            'Foreign production asset')
    for key in ('release_id', 'asset_id'):
        require(type(identity[key]) is int and 0 < identity[key] < 2**63, 'Invalid release/asset identity')


class AssetRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urlsplit(newurl)
        require(url.scheme == 'https' and url.netloc == 'release-assets.githubusercontent.com',
                'Unexpected asset redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(path, limit, *, binary=False):
    # A byte request is derived from a validated release row and a hash-based
    # name. Browser downloads do not consume one API request per offered file.
    headers = {'Accept': 'application/octet-stream' if binary else 'application/vnd.github+json',
               'Accept-Encoding': 'identity', 'User-Agent': 'picross-work-assets'}
    deadline = time.monotonic() + 60
    if binary and path.startswith('/releases/assets/'):
        with github_rest.open_api(API + path, headers, timeout=10, redirect=AssetRedirect()) as response:
            return _read_response(response, limit, deadline)
    if binary:
        request = Request('https://github.com/' + REPOSITORY + path, headers=headers)
        with github_rest.transport_errors():
            with build_opener(ProxyHandler({}), AssetRedirect()).open(request, timeout=10) as response:
                return _read_response(response, limit, deadline)
    with github_rest.open_api(API + path, headers, timeout=10) as response:
        return _read_response(response, limit, deadline)


def _read_response(response, limit, deadline):
    result = bytearray()
    while len(result) <= limit and time.monotonic() < deadline:
        part = response.read(min(65536, limit + 1 - len(result)))
        if not part:
            return bytes(result)
        result.extend(part)
    raise ValueError('Production asset exceeds its byte/time budget')


def read(ref, limit, *, releases=None):
    ident = ref['asset']
    validate(ref, ident['job'], limit)
    tag = 'work-prod-' + ident['job']
    releases = {} if releases is None else releases
    if tag not in releases:
        releases[tag] = json.loads(get('/releases/tags/' + tag, 4 * 1024**2))
    release = releases[tag]
    require(release['id'] == ident['release_id'] and release['tag_name'] == 'work-prod-' + ident['job']
            and release['prerelease'] and not release['draft'], 'Original work release missing')
    rows = [a for a in release['assets'] if a['id'] == ident['asset_id']]
    if not rows:
        # GitHub may cache the tag response across an upload. A new physical ID
        # has a distinct metadata lookup; never substitute a similarly named file.
        fresh = json.loads(get('/releases/tags/' + tag + '?asset_id=' + str(ident['asset_id']), 4 * 1024**2))
        require(fresh['id'] == release['id'] and fresh['tag_name'] == tag and fresh['prerelease']
                and not fresh['draft'], 'Work release changed')
        releases[tag] = fresh
        rows = [a for a in fresh['assets'] if a['id'] == ident['asset_id']]
    require(len(rows) == 1 and rows[0]['size'] == ref['bytes'] and rows[0]['state'] == 'uploaded',
            'Original asset missing from bound release')
    name = 'original-' + ref['sha256']
    require(rows[0]['name'] == name, 'Unexpected physical asset name')
    if github_rest.publisher_token():
        path = '/releases/assets/' + str(ident['asset_id'])
    else:
        path = '/releases/download/' + tag + '/' + name
    raw = get(path, ref['bytes'], binary=True)
    require(content.ref(ref['file'], raw) == local_ref(ref), 'Original asset bytes differ')
    return raw
