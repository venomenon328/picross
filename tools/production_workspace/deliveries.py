"""Read the catalog identities for a single pinned main commit."""
from tools.puzzle_production import catalog_io, categories, current_content
from .sources import JSON_LIMIT


def registered_ids(source, main):
    limit = 8 * JSON_LIMIT
    registry = catalog_io.json_bytes(source.read(main, current_content.REGISTRY, limit), limit)
    catalog = catalog_io.json_bytes(source.read(main, categories.PATH, categories.MAX_BYTES),
                                    categories.MAX_BYTES)
    current_content.validate(registry, catalog)
    return frozenset(row['id'] for row in registry['entries'])
