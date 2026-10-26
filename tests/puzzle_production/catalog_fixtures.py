"""Small immutable synthetic prerequisites, not cached test/verification results."""
from copy import deepcopy
import shutil

from tools.puzzle_production import content_registry as registry
from tools.puzzle_production.authoring_package import file_hash
from tools.puzzle_production.contract import write_json
from tools.puzzle_production.integrated_content import FORMAT


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
