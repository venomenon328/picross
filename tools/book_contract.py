"""Shared B-B resource and lifecycle evidence inventory (no puzzle catalog)."""
RUNTIME = tuple('game/book/'+name for name in (
    'main.gd', 'content.gd', 'binding.gd', 'catalog.gd', 'information.gd',
    'information_routes.gd', 'surface.gd', 'page.gdshader', 'material.gdshader',
    'fold.gdshaderinc', 'paper.png', 'paper.png.import', 'paper.json',
    'leather.png', 'leather.png.import', 'leather.json',
    'table.png', 'table.png.import', 'table.json'))
SOURCES = (*RUNTIME, 'game/tests/book_integration.gd', 'game/tests/book-save-v1.json',
           'game/main.tscn', 'game/ui/main.gd', 'tools/book_contract.py')
INTEGRATION_ASSERTIONS = {
    'regular root and real SaveStore', 'regular registry starts catalog',
    'unchanged preference identity', 'opening reaches bound work',
    'opening/capture creates no save', 'actual filesystem failure reported',
    'failed flush blocks return before preparation',
    'failed flush blocks information before preparation',
    'failed quit stays usable with retry',
    'failed navigation preserves pending state and primary bytes',
    'visible retry commits real slot', 'capture and return do not rewrite save',
    'cancelled opening restores source binding', 'stale callback cannot revive capture',
    'wrong session ID invalidates pending capture',
    'invalid save blocks only its slot', 'unrelated valid slot still opens',
    'switching leaves unrelated bytes unchanged',
    'options survive without transient camera save',
    'frozen schema1 history redo and view load exactly',
    'frozen tool color zoom and clue anchors survive activation',
    'passive opening preserves frozen save bytes',
    'backup-only load stays write blocked', 'backup-only write requires confirmation',
    'backup-only quit preserves bytes and exposes recovery',
    'confirmed recovery remains ID bound',
    'null session context', 'empty and invalid catalogs distinct',
    'null session settings reachable', 'null session help reachable',
    'null session catalog return', 'null session returns without retained resources',
    'null session native close invalidates preparation',
}
