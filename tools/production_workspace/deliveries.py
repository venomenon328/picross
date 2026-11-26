"""Read the catalog identities for a single pinned main commit."""
from tools.puzzle_production import puzzle_catalog


def registered_ids(source, main):
    ids = source.puzzle_ids(main)
    puzzle_catalog.index(lambda n,limit:source.read(main,n,limit),ids)
    return frozenset(ids)
