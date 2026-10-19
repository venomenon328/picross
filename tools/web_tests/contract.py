"""Versioned browser coverage inventory; imported by selection, runners and gate."""
GROUPS = ('regular', 'catalog', 'input', 'completion', 'persistence')
BROWSERS = ('chromium',)
SCENARIOS = (
    {'id':'AT-W01-C','group':'catalog','label':'AT transparent catalog and real hover preserve white detail, holes and soft alpha','browsers':['chromium'],'images':[f'at-{kind}-{w}.png' for kind in ('card','hover') for w in (1280,1920,2560)]},
    {'id':'AT-W01-E','group':'completion','label':'AT transparent transition, final image and reopening preserve earned saves','browsers':['chromium'],'images':[f'at-{kind}-{w}.png' for kind in ('final','reopen','blend') for w in (1280,1920,2560)]},
    {'id':'AT-W01-P','group':'persistence','label':'AT two genuine image exports retain begun and solved saves across reload and browser restart','browsers':['chromium'],'images':[f'at-{kind}-update.png' for kind in ('before','after','restart')]},
    {'id': 'KU-B01', 'group': 'catalog', 'label': 'KU-B four criteria, both directions, canonical ties and stable return ID', 'browsers': ['chromium'], 'images': ['ku-b-sorting.png']},
    {'id': 'KU-B02', 'group': 'persistence', 'label': 'KU-B preference reload, process restart, compatible export, isolated failure and latest-change retry', 'browsers': ['chromium'], 'images': ['ku-b-preference-error.png']},
    {'id': 'regular-start', 'group': 'regular', 'label': 'uninstrumented startup, WebGL2, offline and no errors', 'browsers': ['chromium'], 'images': ['regular-catalog.png']},
    {'id': 'B01', 'group': 'persistence', 'label': 'delayed exclusive lock handoff waits before IndexedDB hydration', 'browsers': ['chromium'], 'images': []},
    {'id': 'B02', 'group': 'catalog', 'label': 'export/catalog startup', 'browsers': ['chromium'], 'images': []},
    {'id': 'B03', 'group': 'catalog', 'label': 'KU-A single-line metadata, footer, tooltip boundaries and passive click routes', 'browsers': ['chromium'], 'images': ['ku-no-difficulty-tooltip.png', 'ku-mode-tooltip.png', 'ku-1280-ui125.png', 'ku-1920-ui100.png', 'ku-2560-ui125.png']},
    {'id': 'B04', 'group': 'input', 'label': 'left/right elastic stroke, atomic undo and redo branch', 'browsers': ['chromium'], 'images': ['mono.png']},
    {'id': 'B05', 'group': 'input', 'label': 'Escape/opposite-button/focus cancellation without phantom commit', 'browsers': ['chromium'], 'images': []},
    {'id': 'B06', 'group': 'persistence', 'label': 'second writer blocked', 'browsers': ['chromium'], 'images': []},
    {'id': 'B07', 'group': 'persistence', 'label': 'reload restores cells, complete history/redo and view', 'browsers': ['chromium'], 'images': []},
    {'id': 'B08', 'group': 'persistence', 'label': 'real browser process restart at DPI125 restores history and redo works', 'browsers': ['chromium'], 'images': []},
    {'id': 'B09', 'group': 'persistence', 'label': 'second genuine compatible export retains IndexedDB identity and progress', 'browsers': ['chromium'], 'images': []},
    {'id': 'B10', 'group': 'input', 'label': 'UI125, 720p/1080p, wheel zoom, fullscreen fit and hit geometry', 'browsers': ['chromium'], 'images': []},
    {'id': 'B11', 'group': 'input', 'label': 'live DPI change to 150 percent preserves hit geometry', 'browsers': ['chromium'], 'images': []},
    {'id': 'B12', 'group': 'input', 'label': 'left mouse moves long row/column clue windows and preserves cells', 'browsers': ['chromium'], 'images': ['colour-row-clues.png', 'colour-column-clues.png']},
    {'id': 'B13', 'group': 'completion', 'label': 'EA completion, late caption, neutral heading, cancel, durable browser reload, origin-bound reset and repeated animation', 'browsers': ['chromium'], 'images': ['ku-solved-footer.png']},
    {'id': 'B14', 'group': 'completion', 'label': 'mono and eight-colour completion through real mouse events', 'browsers': ['chromium'], 'images': []},
    {'id': 'B15', 'group': 'input', 'label': '50x30 rectangle, colour ID 8 and full-grid fit', 'browsers': ['chromium'], 'images': []},
    {'id': 'B16', 'group': 'persistence', 'label': 'actual IndexedDB write failure is visible; own quit stays open; retry commits', 'browsers': ['chromium'], 'images': []},
    {'id': 'B17', 'group': 'persistence', 'label': 'abrupt tab close loses unacknowledged edit but retains last acknowledged state', 'browsers': ['chromium'], 'images': []},
    {'id': 'B18', 'group': 'persistence', 'label': 'corrupt primary reload uses valid backup without silent overwrite', 'browsers': ['chromium'], 'images': []},
    {'id': 'B19', 'group': 'persistence', 'label': 'explicit backup confirmation repairs primary through existing validation', 'browsers': ['chromium'], 'images': []},
    {'id': 'B20', 'group': 'persistence', 'label': 'incompatible revisions rejected without migration or overwrite', 'browsers': ['chromium'], 'images': []},
    {'id': 'B21', 'group': 'persistence', 'label': 'confirmed reset and slot isolation', 'browsers': ['chromium'], 'images': []},
    {'id': 'B22', 'group': 'persistence', 'label': 'real subpath startup, stable saves and offline-after-load input', 'browsers': ['chromium'], 'images': []},
    {'id': 'B23', 'group': 'persistence', 'label': 'own quit acknowledges durable sync, exits zero and reload restores saved state', 'browsers': ['chromium'], 'images': []},
    {'id': 'B24', 'group': 'persistence', 'label': 'blocked IndexedDB startup displays failure before gameplay', 'browsers': ['chromium'], 'images': []},
)


def require_browser(browser):
    if browser not in BROWSERS:
        raise ValueError('Unsupported CI browser; expected chromium')


def expected(browser, groups):
    require_browser(browser)
    return [row for row in SCENARIOS if browser in row['browsers'] and row['group'] in groups]


def select_groups(web_reasons):
    """Exact audited leaf dependencies; anything else conservatively selects all.

    Catalog controls are also exercised by completion/reset and recovery. Input
    actions feed completion and persistence. Save/session/main/export are shared.
    """
    selected = {'regular'} if web_reasons else set()
    for reason in web_reasons:
        if reason in {'explicit scope: browser-'+g for g in GROUPS[1:]}:
            selected.add(reason.removeprefix('explicit scope: browser-'))
        elif reason in {'tools/web_tests/group_'+g+'.py' for g in GROUPS[1:]}:
            selected.add(reason.removeprefix('tools/web_tests/group_').removesuffix('.py'))
        elif reason in {'game/ui/catalog_ink.gd', 'game/ui/catalog_tip.gd',
                      'game/model/catalog_difficulty.gd'}:
            selected.update(('catalog',))
        elif reason in {'game/ui/catalog.gd', 'game/ui/catalog_card.gd'}:
            selected.update(('catalog', 'completion', 'persistence'))
        elif reason in {'game/ui/completion.gd'}:
            selected.update(('completion',))
        elif reason in {'game/ui/gesture_counter.gd', 'game/ui/clue_overlay.gd',
                        'game/ui/clue_layout.gd'}:
            selected.update(('input',))
        elif reason in {'game/model/gesture.gd', 'game/ui/full_view_board.gd',
                        'game/ui/board.gd', 'game/ui/grid_view.gd'}:
            selected.update(('input', 'completion', 'persistence'))
        else:
            selected.update(GROUPS)
    return [group for group in GROUPS if group in selected]


def coverage(groups):
    return {browser: {group: [s['id'] for s in expected(browser, [group])]
                      for group in groups} for browser in BROWSERS} if groups else {}
