"""PE-EDIT2 current editor API/CLI. External migrations are separate commands."""
import argparse
import json
from pathlib import Path
import tempfile

from . import editor_change as edit, catalog_io as io, operation_diagnostics as diagnostic
from . import editor_image_input, target_adapter, content_registry
from .authoring_package import require, relative
from .contract import exact_keys

REQUEST = 'picross-editor-request-v2'


def read(path, limit=edit.LIMIT):
    path = io.external(path)
    return io.json_bytes(io.read(path.parent, path.name, limit), limit)


def plan_file(root, request_path, output):
    root, request_path = io.external(root), io.external(request_path)
    output = diagnostic.report_target(output, [root, request_path])
    request = read(request_path, 256*1024)
    exact_keys(request, {'format', 'id', 'metadata', 'text', 'profile', 'reveal', 'background', 'imports'})
    require(request.pop('format') == REQUEST, 'Use picross-editor-request-v2 without provenance fields')
    imports = request.pop('imports')
    require(isinstance(imports, dict) and len(imports) <= 2, 'At most two image imports')
    used = {part['upload']: kind for kind in ('reveal', 'background')
            if (part := request[kind]) is not None and part.get('upload') is not None}
    require(set(imports) == set(used), 'Unrelated or missing image import')
    uploads = {}
    with tempfile.TemporaryDirectory(prefix='pe-edit2-plan-') as temporary:
        work = io.external(temporary)
        require(not work.is_relative_to(root), 'Private preparation must be outside checkout')
        for index, (key, name) in enumerate(imports.items()):
            relative(name)
            source = io.safe(request_path.parent, name)
            require(not source.is_relative_to(root), 'New imports must be outside content checkout')
            suffix = source.suffix
            require(suffix in ('.png', '.svg') and (used[key] != 'background' or suffix == '.png'), 'Unsupported image type')
            raw = io.read(request_path.parent, name, 32*1024*1024)
            checked = (editor_image_input.validate_background(raw) if used[key] == 'background'
                       else editor_image_input.validate_reveal(raw, suffix))
            require(checked['sha256'] == io.checksum(raw), 'Prepared import changed')
            uploads[key] = {'raw': raw, 'suffix': suffix[1:], 'checked': checked}
        value = edit.plan(root, request, uploads=uploads, work=work)
        diagnostic.write_report(output, value)
        return {'status': 'prepared', 'output': str(output), 'files': sorted(value['changes']), 'before': value['before'], 'after': value['after']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('list', 'detail', 'plan', 'apply', 'recover'):
        p = commands.add_parser(name); p.add_argument('--target-root', required=True, type=Path)
        if name == 'detail': p.add_argument('--id', required=True)
        if name == 'plan':
            p.add_argument('--request', required=True, type=Path); p.add_argument('--output', required=True, type=Path)
        if name == 'apply': p.add_argument('--plan', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'list': result = edit.listing(args.target_root)
        elif args.command == 'detail':
            result = edit.detail(args.target_root, args.id); result.pop('_resources')
        elif args.command == 'plan': result = plan_file(args.target_root, args.request, args.output)
        elif args.command == 'apply': result = edit.apply(args.target_root, read(args.plan))
        else: result = content_registry.recover(args.target_root)
        print(json.dumps(result, ensure_ascii=True)); return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=True)); return 2


if __name__ == '__main__': raise SystemExit(main())
