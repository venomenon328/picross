"""Bounded, redirect-free REST reads for the fixed production repository."""
from contextlib import contextmanager
from datetime import datetime, timezone
import http.client
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

REPOSITORY = 'venomenon328/picross'
API = 'https://api.github.com/repos/' + REPOSITORY
TOKEN_NAMES = ('GH_TOKEN', 'GITHUB_TOKEN')
_workspace_token = None


def _windows_user_token():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
            for name in TOKEN_NAMES:
                try:
                    value, kind = winreg.QueryValueEx(key, name)
                except OSError:
                    continue
                if kind in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) and value.strip():
                    return value.strip()
    except OSError:
        pass
    return None


def load_workspace_token():
    """Snapshot the launch environment before Git, ShellExecute or update children."""
    global _workspace_token
    primary, fallback = (os.environ.pop(name, '').strip() for name in TOKEN_NAMES)
    # The clean update helper starts its successor without either environment key.
    _workspace_token = primary or fallback or (_windows_user_token() if os.name == 'nt' else None)


class Failure(ValueError):
    def __init__(self, kind, message, status=None):
        super().__init__(message)
        self.kind = kind
        self.status = status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def _secondary_limit(error):
    try:
        body = json.loads(error.read(16 * 1024))
    except (ValueError, OSError, http.client.HTTPException):
        return False
    message = body.get('message') if isinstance(body, dict) else None
    return isinstance(message, str) and 'secondary rate limit' in message.lower()


def _rate_limit_message(headers):
    retry = headers.get('Retry-After', '')
    if re.fullmatch(r'[0-9]{1,8}', retry):
        return 'GitHub-Anfragelimit erreicht. Frühestens in ' + retry + ' Sekunden erneut versuchen.'
    reset = headers.get('X-RateLimit-Reset', '')
    if headers.get('X-RateLimit-Remaining') == '0' and re.fullmatch(r'[0-9]{1,10}', reset):
        until = datetime.fromtimestamp(int(reset), timezone.utc).strftime('%H:%M:%S UTC')
        return 'GitHub-Anfragelimit erreicht. Ab ' + until + ' erneut versuchen.'
    return 'GitHub-Anfragelimit erreicht. Warte mindestens eine Minute vor dem nächsten Versuch.'


def _http_failure(error, *, api, authenticated):
    status = error.code
    headers = error.headers or {}
    if status == 429 or status == 403 and (
            headers.get('X-RateLimit-Remaining') == '0' or headers.get('Retry-After')
            or api and _secondary_limit(error)):
        return Failure('rate_limit', _rate_limit_message(headers), status)
    if api and status == 401:
        return Failure('auth', 'GitHub-Anmeldung fehlgeschlagen. GH_TOKEN bzw. GITHUB_TOKEN prüfen und den Assistenten neu starten.', status)
    if status == 403:
        message = 'GitHub hat den Abruf verweigert.'
        if api and authenticated:
            message += ' Gültigkeit und Leserechte des Tokens prüfen.'
        return Failure('access', message, status)
    if api and authenticated and status == 404:
        return Failure('access', 'GitHub meldet die Quelle als nicht verfügbar. Leserechte des Tokens und Verfügbarkeit prüfen.', status)
    if status in (404, 410):
        return Failure('source', 'Die gebundene GitHub-Quelle fehlt. Veröffentlichung prüfen und neu laden.', status)
    if 300 <= status < 400:
        return Failure('network', 'GitHub hat den Abruf unerwartet umgeleitet.', status)
    return Failure('network', f'GitHub-Abruf fehlgeschlagen (HTTP {status}). Später erneut versuchen.', status)


@contextmanager
def transport_errors(*, api=False, authenticated=False):
    try:
        yield
    except HTTPError as error:
        try:
            failure = _http_failure(error, api=api, authenticated=authenticated)
        finally:
            error.close()
        raise failure from None
    except (OSError, http.client.HTTPException):
        raise Failure('network', 'GitHub ist derzeit nicht erreichbar. Verbindung prüfen und erneut versuchen.') from None


@contextmanager
def open_api(url, headers, *, timeout, use_workspace_token=True, token=None):
    parsed = urlsplit(url)
    repo_path = '/repos/' + REPOSITORY
    if (parsed.scheme != 'https' or parsed.netloc != 'api.github.com' or parsed.fragment or
            (parsed.path != repo_path and not parsed.path.startswith(repo_path + '/')) or
            re.search(r'[\s\x00-\x1f\x7f\\]', url)):
        raise ValueError('Unexpected GitHub API URL')
    if token is None and use_workspace_token:
        token = _workspace_token
    request = Request(url, headers=headers, method='GET')
    if token:
        if not re.fullmatch(r'[A-Za-z0-9._~+/\-]+=*', token):
            raise Failure('auth', 'GitHub-Token hat ein ungültiges Format. Windows-Umgebungsvariable prüfen und neu starten.')
        # Defense in depth: urllib never copies this header to a redirect request.
        request.add_unredirected_header('Authorization', 'Bearer ' + token)
    with transport_errors(api=True, authenticated=bool(token)):
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=timeout) as response:
            yield response
