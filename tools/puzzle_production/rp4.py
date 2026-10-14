"""Import-result integrity helper retained by the generic synthetic regression."""
from pathlib import Path
from .contract import Budget, InvalidInput, load_json
from .images import file_hash, inspect_candidate

def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidInput(message)


def local(root: Path, name: str) -> Path:
    require(isinstance(name, str) and '\\' not in name, 'Invalid local path')
    p = root / name
    require(not Path(name).is_absolute() and '..' not in Path(name).parts and
            not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), 'Unsafe local path')
    require(p.is_file(), f'Missing file: {name}')
    return p


def inspect_trial(root: Path, bundle: Path, trial: dict, record: dict, policy: dict) -> list[dict]:
    require(record['status'] == 'produced', 'Incomplete import: inspect its recorded error')
    manifest = load_json(bundle / 'manifest.json')
    require(record['manifest_sha256'] == file_hash(bundle / 'manifest.json'), 'Baseline manifest changed')
    require(manifest['design'] == trial['design'], 'Bundle has wrong paired parameters')
    require(file_hash(bundle / manifest['original']) == file_hash(local(root, trial['input'])), 'Wrong source for trial')
    require(manifest['limits']['seconds_per_solver_or_verifier'] == policy['solver_seconds'] and
            manifest['limits']['max_lines'] == policy['max_lines'], 'Unequal original budgets')
    require(record['candidates'] == manifest['candidates'], 'Original report differs from bundle')
    variants = trial['design']['variants']
    require([c['variant'] for c in manifest['candidates']] == [v['id'] for v in variants], 'Dropped/reordered candidate')
    rows = []
    for v, entry in zip(variants, manifest['candidates']):
        c, proof, fresh = inspect_candidate(bundle, v['id'], Budget(policy['verifier_seconds'], policy['max_lines']))
        original = load_json(bundle / f"{v['id']}-result.json")
        require(entry['id'] == c['id'] and entry['technical'] == original, 'Candidate/status binding mismatch')
        require(type(original['certified']) is bool and type(original['proof_verified']) is bool, 'Invalid result flags')
        if original['proof_verified']:
            require(all(original[k] == fresh[k] for k in ('status', 'certified', 'proof_verified', 'logic_hash', 'profile_hash')),
                    'Claimed original verification differs from proof replay')
        else:
            require(original['status'] == 'aborted' and original['certified'] is False and
                    bool(original.get('reason')), 'Unverified original must be explicit aborted result')
        rows.append({'trial': trial['id'], 'variant': v['id'], 'candidate_id': c['id'],
                     'logic_hash': c['logic_hash'], 'original': original, 'fresh': fresh,
                     'logically_accepted': original['certified'] and fresh['certified'],
                     'filled_cells': sum(value != 'empty' for row in c['matrix'] for value in row),
                     'proof_steps': len(proof['steps']),
                     'unresolved_cells': sum(len(d) != 1 for row in proof['final_domains'] for d in row)})
    return rows
