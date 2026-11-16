"""Stable packaging identity/start anchor and explicitly injected build version."""
import json
from pathlib import Path
import re
import uuid
import subprocess

from tools.app_products import PW

SOURCE = Path(__file__).with_name('release.json')


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('Produktversion benötigt MAJOR.MINOR.PATCH ohne führende Nullen.')
    parts = tuple(map(int, value.split('.')))
    if parts == (0, 0, 0) or any(p > limit for p, limit in zip(parts, (255, 255, 65535))):
        raise ValueError('Produktversion außerhalb des MSI-Bereichs.')
    return parts


def release(path=None, *, version=None, app=PW):
    path = path or (SOURCE if app == PW else app.source / "release.json")
    value = json.loads(path.read_text(encoding='utf-8'))
    version_tuple(value['version'])
    if version is not None:
        requested = version_tuple(version)
        if requested[:2] != app.line or requested < version_tuple(value['version']):
            raise ValueError('Publikationsversion muss in der monotonen Produktlinie bleiben.')
        value['version'] = version
    code = uuid.UUID(value['upgrade_code'])
    value['product_code'] = str(uuid.uuid5(code, value['version'])).upper()
    value['filename'] = app.title + '-' + value['version'] + '-windows-x64.msi'
    return value


def check_history(root, current, *, app=PW):
    """Reject a release version decrease or a changed product-line identity."""
    relative = SOURCE.relative_to(root).as_posix() if app == PW else app.package + '/release.json'
    commits = subprocess.check_output(['git', '-C', str(root), 'log', '--format=%H', 'HEAD', '--', relative], text=True).splitlines()
    for commit in commits:
        previous = json.loads(subprocess.check_output(['git', '-C', str(root), 'show', commit + ':' + relative], text=True))
        if previous['upgrade_code'] != current['upgrade_code']:
            raise ValueError('Upgradeidentität darf innerhalb der Produktlinie nicht wechseln.')
        if version_tuple(previous['version']) > version_tuple(current['version']):
            raise ValueError('Releaseversion muss monoton steigen; keine Rückstufung im Quellverlauf.')
