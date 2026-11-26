"""Closed CI plan for one regular first integration, shared by both producers."""
import argparse
import json
from pathlib import Path
import re
import subprocess

FORMAT = 'production-ci-plan/v1'
PLAN_PATH = '.ci/package.json'
ID = re.compile(r'pz-[a-z0-9][a-z0-9-]{0,59}')
RUNTIME = 'game/data/registry.json'


def product_branch(job):
    return 'content/integrate-' + job


def package(job):
    if not isinstance(job, str) or not ID.fullmatch(job):
        raise ValueError('Expected regular puzzle ID')
    return {'format': FORMAT, 'puzzle_id': job, 'package': 'Integration-' + job, 'modules': [],
            'purpose': 'Gewählte finale Rätseldaten registrieren.',
            'omitted': 'Reine Inhaltsintegration. Adapter und registrierte Lieferung im Produktionslauf geprüft.',
            'test_changes': [], 'core_change': None,
            'evidence': {'mode': 'none', 'purpose': None, 'expires': None}}


def json_value(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def registry_additions(before, after, job, format_name, tables):
    """Permit one inserted row per table; preserve all other values and row order."""
    if (not isinstance(before, dict) or not isinstance(after, dict) or before.keys() != after.keys()
            or before.get('format') != format_name or any(
                key not in tables and json_value(before[key]) != json_value(after[key]) for key in before)):
        raise ValueError('Unrelated registry change')
    additions = []
    for table in tables:
        prior, rows = before.get(table), after.get(table)
        if (not isinstance(prior, list) or not isinstance(rows, list)
                or any(not isinstance(row, dict) or not isinstance(row.get('id'), str)
                       for row in prior + rows)):
            raise ValueError('Malformed registry table: ' + table)
        added = [row for row in rows if row['id'] == job]
        if (len(added) != 1 or any(row['id'] == job for row in prior)
                or json_value([row for row in rows if row['id'] != job]) != json_value(prior)):
            raise ValueError('Registry must add only ' + job + ' to ' + table)
        additions.append(added[0])
    return additions


def validate(plan, changes, branch, read):
    job = plan.get('puzzle_id')
    expected = package(job)
    if (plan.keys() != expected.keys() or any(
            plan[key] != expected[key] for key in expected if key not in {'purpose', 'omitted'})
            or any(not isinstance(plan[key], str) or not plan[key].strip() for key in ('purpose', 'omitted'))):
        raise ValueError('Invalid production package plan')
    if branch != product_branch(job):
        raise ValueError('Production package must match the integration branch')
    from tools.puzzle_production import puzzle_record, categories
    runtime, = registry_additions(read(RUNTIME, old=True), read(RUNTIME), job,
        'picross-runtime-registry-v9', ('entries',))
    record_path = f'content/puzzles/{job}.json'
    record = puzzle_record.decode(read(record_path, raw=True), job)
    definition = f'data/content/{job}.json'
    reveal = runtime.get('reveal')
    if (record["save_slot"] != job or record["definition"]["file"] != "game/"+definition or
            reveal not in (f"art/content/{job}.png", f"art/content/{job}.svg")):
        raise ValueError("Record or runtime does not match the new puzzle")
    catalog = categories.validate(read(categories.PATH))
    puzzle_record.validate(record, job, read("game/"+definition, raw=True), category_catalog=catalog)
    if puzzle_record.runtime_row(record) != runtime:
        raise ValueError("Record projection does not match the new runtime row")
    new_runtime = read(RUNTIME)
    if (set(new_runtime) != {"format","entries","categories"} or new_runtime["categories"] != categories.ordered(catalog)
            or [row["id"] for row in new_runtime["entries"]] != sorted({row["id"] for row in new_runtime["entries"]})):
        raise ValueError("Invalid runtime category or row order")
    additions = {record_path, 'game/'+definition, 'game/'+reveal, f'game/art/content/{job}.txt',
                 *(f'game/art/catalog/{job}-ui{scale}.png' for scale in (100,125))}
    preference = record.get('background')
    projected = runtime.get('background')
    if not isinstance(preference,dict) or not isinstance(projected,dict):
        raise ValueError('Missing background decision')
    if preference.get('status') == 'selected':
        asset = f'art/backgrounds/{job}.png'
        ref = preference.get('asset')
        if not isinstance(ref,dict) or ref.get('file') != 'game/'+asset:
            raise ValueError('Foreign background asset')
        preference = {**preference,'asset':{**ref,'file':asset}}
        additions.update({'game/'+asset,f'game/art/backgrounds/{job}.txt'})
    elif preference.get('status') not in ('standard','none') or preference.get('asset') is not None:
        raise ValueError('Invalid background decision')
    if preference != projected:
        raise ValueError('Background projection differs')
    expected_changes = dict.fromkeys(additions, ('000000', '100644', 'A'))
    expected_changes[RUNTIME] = ('100644', '100644', 'M')
    expected_changes[PLAN_PATH] = ('100644', '100644', 'M') if changes.get(PLAN_PATH, ())[:1] == ('100644',) else (
        '000000', '100644', 'A')
    if changes != expected_changes:
        extra = changes.keys() - expected_changes.keys()
        missing = expected_changes.keys() - changes.keys()
        wrong = {p for p in changes.keys() & expected_changes.keys() if changes[p] != expected_changes[p]}
        raise ValueError('Unexpected first integration diff: ' + ', '.join(sorted(extra | missing | wrong)))
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job')
    args = parser.parse_args()
    plan = package(args.job)
    branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
    if branch != product_branch(args.job):
        parser.error('Run on ' + product_branch(args.job))
    # Use an explicit binary write for identical UTF-8/LF bytes on Windows and Linux.
    path = Path(PLAN_PATH)
    prior = subprocess.run(['git', 'show', 'HEAD:' + PLAN_PATH], capture_output=True)
    raw = (json_value(plan) + '\n').encode()
    if path.is_symlink() or path.exists() and path.read_bytes().replace(b'\r\n', b'\n') not in (raw, prior.stdout):
        parser.error('Uncommitted package plan exists')
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(raw)


if __name__ == '__main__':
    main()
