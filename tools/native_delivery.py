"""Stage current native success evidence or purpose-bound failure diagnostics."""
import argparse
import json
from pathlib import Path
import shutil

from native_contract import GROUPS
from native_results import bind_files, read, safe, verify_file
from p1_evidence import native_failure_sources, source_identity


def stage(output, destination, outcome, identity):
    """Never turn a partial/failed producer into a new successful evidence seal."""
    if destination.exists():
        raise ValueError('Native delivery destination must not exist')
    technical = output / 'technical'
    destination.mkdir(parents=True)
    issues, copied = [], set()

    def source(root, name):
        path = safe(root, name)
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Linked native diagnostic source')
        return path

    def copy(root, name, target=None):
        try:
            path = source(root, name)
            if not path.is_file():
                raise ValueError('Missing native diagnostic source: ' + name)
            target = target or name
            dest = safe(destination, target)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
            copied.add(target)
        except (OSError, ValueError) as error:
            issues.append(str(error))

    result, foreign = None, False
    try:
        result = read(source(technical, 'native-result.json'))
        if not isinstance(result, dict):
            raise ValueError('Invalid native result object')
        if result.get('identity') != identity:
            foreign = True
            raise ValueError('Native delivery source/run/attempt binding mismatch')
        groups, rows = result.get('groups'), result.get('results')
        if (not isinstance(groups, list) or not groups or
                any(g not in GROUPS for g in groups) or len(set(groups)) != len(groups) or
                not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows)):
            raise ValueError('Invalid native group status')
    except (OSError, ValueError, TypeError) as error:
        issues.append(str(error))
        result = None

    if outcome == 'success' and result and result.get('status') == 'success':
        # Exact existing payload/name, including aliases, reports and pixel inputs.
        for path in sorted(technical.rglob('*')):
            if path.is_file() or path.is_symlink():
                copy(technical, path.relative_to(technical).as_posix())
        if issues:
            raise ValueError('; '.join(issues))
        return {'status': 'success', 'files': len(copied)}

    diagnostics = dict(format='picross-native-diagnostics-v1', status='failure',
                       accepted=False, producer_outcome=outcome, identity=identity,
                       groups=[], issues=issues)
    if result:
        copy(technical, 'native-result.json')  # Original bytes, never resealed.
    rows = {r.get('group'): r for r in (result or {}).get('results', [])}
    validation_groups = set((result or {}).get('validation_groups', []))
    if (result or {}).get('validation_group'):
        validation_groups.add(result['validation_group'])
    if (result or {}).get('validation_error') and not validation_groups:
        # Inventory validation can fail before an oracle is entered. Preserve
        # the damaged/missing originals' group, without accepting extra files.
        listed = {r['file']: r for r in result.get('files', [])}
        actual = {p.relative_to(technical).as_posix() for p in technical.rglob('*')
                  if p.is_file() and p.name != 'native-result.json'}
        differences = actual ^ set(listed)
        for name, row in listed.items():
            try:
                source(technical, name)
                verify_file(technical, row)
            except (OSError, ValueError):
                differences.add(name)
        diagnostics['validation_paths'] = sorted(differences)
        validation_groups.update(name.split('/')[0] for name in differences
                                 if name.split('/')[0] in GROUPS)
    for group in (result or {}).get('groups', () if foreign else GROUPS):
        if group not in GROUPS:
            issues.append('Unknown native group')
            continue
        row = rows.get(group, {})
        failed = row.get('status') != 'success' or row.get('exit_code') != 0
        failed |= group in validation_groups
        diagnostics['groups'].append(dict(group=group, process=row, diagnostics=failed))
        if not failed:
            continue
        copy(technical, group + '-process.log')
        directory = technical / group
        # Reports and complete logs explain phase order, import failures, kills,
        # nested workers and missing reports. Successful *other* groups stay out.
        for path in sorted(directory.rglob('*')):
            if path.suffix in {'.json', '.gz', '.log'}:
                copy(technical, path.relative_to(technical).as_posix())
        phase, selected = '', []
        try:
            report = read(source(directory, 'product-report.json'))
            selected = report.get('selected_evidence', {}).get('files', [])
            # A validation failure needs the affected group's required originals;
            # runtime failures use the producer's actual oracle/phase nomination.
            for entry in selected:
                if entry.get('failure_priority') or group in validation_groups:
                    copy(directory / 'selected', entry['file'], group + '/selected/' + entry['file'])
            phase = report.get('active_phase') or next(
                (r['name'] for r in reversed(report.get('checks', [])) if r.get('status') != 'success'), '')
        except (OSError, ValueError, KeyError, TypeError) as error:
            issues.append(group + ': ' + str(error))
        if phase == 'current-vs2-complete':
            try:
                worker = read(source(directory, 'vs2-worker/technical/product-report.json'))
                phase = worker.get('active_phase') or next(
                    (r['name'] for r in reversed(worker.get('checks', [])) if r.get('status') != 'success'), phase)
            except (OSError, ValueError, KeyError, TypeError) as error:
                issues.append(group + ': ' + str(error))
        try:
            raw = output / 'groups' / group
            nominated = [safe(raw, r['file']) for r in selected if r.get('failure_priority')]
            reports, priority = native_failure_sources(raw, phase, nominated)
            # Recover partial originals if the process died before retain_files.
            for path in reports:
                if path.suffix == '.json' or path in priority:
                    name = path.relative_to(raw).as_posix()
                    target = group + '/selected/' + name
                    if target not in copied:
                        copy(raw, name, target)
        except (OSError, ValueError, KeyError, TypeError) as error:
            issues.append(group + ': ' + str(error))
    # Alias originals may physically live in another group after validation failed.
    for alias in (result or {}).get('image_aliases', []):
        target = alias.get('file', '')
        if any(r['diagnostics'] and target.startswith(r['group'] + '/') for r in diagnostics['groups']):
            try:
                name = alias['source']
                if not target.endswith('.png') or not name.endswith('.png'):
                    raise ValueError('Invalid diagnostic image alias')
                source(technical, name)
                verify_file(technical, dict(file=name, bytes=alias['bytes'], sha256=alias['sha256']))
                copy(technical, name, target)
            except (OSError, ValueError, KeyError, TypeError) as error:
                issues.append(str(error))
    diagnostics['files'] = bind_files(destination)
    (destination / 'diagnostics.json').write_text(json.dumps(diagnostics, indent=2) + '\n', encoding='utf-8')
    if outcome == 'success':
        raise ValueError('Successful producer lacks valid successful delivery')
    return diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--outcome', required=True)
    args = parser.parse_args()
    result = stage(args.output_dir, args.destination, args.outcome,
                   source_identity(Path(__file__).resolve().parents[1]))
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}))


if __name__ == '__main__':
    main()
