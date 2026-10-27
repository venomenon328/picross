"""Small immutable synthetic prerequisites, not cached test/verification results."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

from tools.puzzle_production import content_registry as registry
from tools.puzzle_production.authoring_package import file_hash
from tools.puzzle_production.contract import write_json
from tools.puzzle_production.integrated_content import FORMAT


_registered = {}


def registered(home, *, stem, save_slot, revision=1):
    """Copy identical full/compact synthetic prerequisites into a private root.

    Only the template's input bytes and checked rating input are shared. Every
    caller, including the first, receives a deep copy and its own directory.
    All real registration, transaction and source checks still execute in tests.
    """
    if type(revision) is not int:
        raise ValueError('Synthetic fixture revision must be an integer')
    key = (stem, save_slot, revision)
    if key not in _registered:
        from tools.puzzle_production.target_adapter import export
        from tools.puzzle_production.za1_fixtures import FIXTURES, approve, isolated_checkout, difficulty_for_export
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = isolated_checkout(root/'base')
            approval = root/'approval.json'; approve(FIXTURES/'direct-mono', approval)
            exported = root/'export'
            export(FIXTURES/'direct-mono', exported, name='TEST ONLY', revision=revision,
                   stem=stem, save_slot=save_slot, approval_path=approval,
                   category_id='voegel', categories_path=base/'content/categories.json')
            checked = difficulty_for_export(exported)
            registry.registration(exported, base, apply=True, difficulty=checked)
            shutil.copytree(base, root/'full-base')
            compact(base, [checked['current_source']['id']])
            # Immutable bytes, never a shared mutable test root. Deleting the
            # builder here keeps its teardown inside the measured class setup.
            directories = tuple(p.relative_to(root) for p in sorted(root.rglob('*')) if p.is_dir())
            files = tuple((p.relative_to(root), p.read_bytes(), p.stat().st_mode & 0o777)
                          for p in sorted(root.rglob('*')) if p.is_file())
            _registered[key] = (directories, files, json.dumps(checked))
    directories, files, checked = _registered[key]
    home.mkdir(parents=True, exist_ok=True)
    for name in directories: (home/name).mkdir(exist_ok=True)
    for name, raw, mode in files:
        (home/name).write_bytes(raw)
        (home/name).chmod(mode)
    return json.loads(checked)


def compact(root, identifiers):
    """Keep a real registered source's exact compact historical binding.

    Tests of full production retain their full inputs. Metadata/foreign-neighbour
    assertions need only a valid registered receipt, definition, image and notice.
    """
    value = registry.check_checkout(root)
    for entry in value['entries']:
        if entry['id'] not in identifiers:
            continue
        if entry['production']['test_only'] is not True:
            raise ValueError('Only synthetic test prerequisites may be compacted')
        package = root / entry['production']['package']
        if not package.resolve().is_relative_to((root / 'content/packages').resolve()):
            raise ValueError('Fixture package escaped its temporary checkout')
        receipt = {'format': FORMAT, 'entry': deepcopy(entry), 'integrated_commit': 'a' * 40,
                   'notice_sha256': file_hash((root / 'game' / entry['reveal']).with_suffix('.txt'))}
        shutil.rmtree(package)
        package.mkdir()
        write_json(package / 'manifest.json', receipt)
        entry['production']['package_sha256'] = file_hash(package / 'manifest.json')
    write_json(root / registry.REGISTRY, value)
    registry.check_checkout(root)
