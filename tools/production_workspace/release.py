"""Stable packaging identity/start anchor and explicitly injected build version."""
import json
from pathlib import Path
import re
import uuid

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
    value['filename'] = app.msi_title + '-' + value['version'] + '-windows-x64.msi'
    return value
