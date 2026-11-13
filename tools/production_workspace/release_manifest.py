"""Closed v1 build provenance / v2 signed metadata and byte bindings (no I/O)."""
import hashlib
import json
import re

from .payload import canonical
from .release import release, version_tuple

REPOSITORY = 'venomenon328/picross'
FORMAT = 'picross-pw-release-v1'
SIGNED_FORMAT = 'picross-pw-release-v2'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('Non-finite JSON number')
    # Explicit UTF-8: json.loads(bytes) also accepts UTF-16/32, which we forbid.
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=nonfinite)


def shape(value, fields, message):
    require(type(value) is dict and set(value) == set(fields.split()), message)


def hex_string(value, length):
    return type(value) is str and re.fullmatch('[0-9a-f]{' + str(length) + '}', value) is not None


def validate_manifest(value):
    require(type(value) is dict, 'Invalid release manifest')
    signed = value.get('format') == SIGNED_FORMAT
    shape(value, 'format repository status version tag source_commit payload_fingerprint product_code '
          'upgrade_code assets inspection' + (' platform channel signing_key_id' if signed else ''),
          'Invalid release manifest shape')
    require(value['format'] in (FORMAT, SIGNED_FORMAT) and value['repository'] == REPOSITORY and value['status'] == 'production',
            'Foreign or nonproduction manifest')
    if signed:
        require(value['platform'] == 'windows-x64' and value['channel'] == 'stable' and
                hex_string(value['signing_key_id'], 64), 'Invalid platform/channel/signing key')
    version = version_tuple(value['version'])
    require(version[:2] == (0, 1) and version > (0, 1, 0) and value['tag'] == 'pw-v' + value['version'],
            'Unsupported published version')
    require(hex_string(value['source_commit'], 40) and hex_string(value['payload_fingerprint'], 64),
            'Invalid source/fingerprint')
    product = release(version=value['version'])
    require(all(value[k] == product[k] for k in ('product_code', 'upgrade_code')), 'Foreign product identity')
    names = {product['filename'], product['filename'] + '.sha256', 'delivery.json', 'START.txt', 'inputs.json'}
    require(type(value['assets']) is dict and set(value['assets']) == names, 'Incomplete release assets')
    for row in value['assets'].values():
        shape(row, 'bytes sha256', 'Invalid asset binding')
        require(type(row['bytes']) is int and row['bytes'] > 0 and hex_string(row['sha256'], 64), 'Invalid asset binding')
    inspection = value['inspection']
    shape(inspection, 'format commit version payload_fingerprint msi_sha256 msi_bytes product_code upgrade_code '
          'inventory_files license_files compared_to_build limits', 'Invalid inspection shape')
    require(inspection['format'] == 'picross-installer-inspection-v1' and
            all(inspection[k] == value[k] for k in ('version', 'product_code', 'upgrade_code')) and
            type(inspection['inventory_files']) is int and inspection['inventory_files'] > 0 and
            type(inspection['license_files']) is int and inspection['license_files'] >= 2 and
            type(inspection['msi_bytes']) is int and type(inspection['limits']) is str and bool(inspection['limits']) and
            inspection['commit'] == value['source_commit'] and inspection['version'] == value['version'] and
            inspection['payload_fingerprint'] == value['payload_fingerprint'] and inspection['compared_to_build'] is True and
            inspection['msi_sha256'] == value['assets'][product['filename']]['sha256'] and
            inspection['msi_bytes'] == value['assets'][product['filename']]['bytes'], 'Unbound MSI inspection')
    return value


def verify_files(manifest, files):
    validate_manifest(manifest)
    require(set(files) == set(manifest['assets']), 'Unexpected or missing candidate file')
    for name, row in manifest['assets'].items():
        require(type(files[name]) is bytes and len(files[name]) == row['bytes'] and digest(files[name]) == row['sha256'],
                'Asset hash mismatch: ' + name)
    product = release(version=manifest['version'])
    report = strict_json(files['delivery.json'])
    require(type(report) is dict, 'Invalid delivery report')
    require(all(report[k] == manifest[v] for k, v in (('version', 'version'), ('commit', 'source_commit'),
            ('payload_fingerprint', 'payload_fingerprint'), ('product_code', 'product_code'), ('upgrade_code', 'upgrade_code'))),
            'Unbound delivery report')
    msi = product['filename']
    require(report['msi_file'] == msi and type(report['msi_bytes']) is int and
            report['msi_bytes'] == len(files[msi]) and report['msi_sha256'] == digest(files[msi]),
            'Unbound MSI delivery bytes')
    require(files[msi + '.sha256'] == (digest(files[msi]) + '  ' + msi + '\n').encode(), 'Invalid checksum sidecar')
    inputs = strict_json(files['inputs.json'])
    shape(inputs, 'format sha256 files', 'Invalid input inventory shape')
    require(inputs['format'] == 'picross-app-inputs-v1' and inputs['sha256'] == manifest['payload_fingerprint'] and
            type(inputs['files']) is list and bool(inputs['files']) and
            digest(canonical(inputs['files'])) == inputs['sha256'], 'Invalid input fingerprint inventory')

