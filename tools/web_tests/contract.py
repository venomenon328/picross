"""Versioned browser coverage inventory; imported by selection, runners and gate."""
CORE_GROUPS = ('regular', 'catalog', 'input', 'completion', 'persistence')
# Export compatibility is a separately requested, bounded profile, never in all.
GROUPS = (*CORE_GROUPS, 'export')
BROWSERS = ('chromium',)
BROWSER_SCOPES = ('none', *GROUPS, 'short', 'all')


def browser_request(scope):
    """Canonical opt-in, independent of every changed path and general scope."""
    if scope not in BROWSER_SCOPES:
        raise ValueError('Unknown explicit browser scope')
    return None if scope == 'none' else {'browser': 'chromium', 'scope': scope}


def requested_groups(request):
    if request is None:
        return []
    scope = request.get('scope') if isinstance(request, dict) else None
    if scope == 'none' or request != browser_request(scope):
        raise ValueError('Invalid canonical browser request')
    return list(CORE_GROUPS) if scope in ('short', 'all') else ['regular'] + ([] if scope == 'regular' else [scope])


def required_builds(groups):
    if not groups or len(set(groups)) != len(groups) or any(g not in GROUPS for g in groups):
        raise ValueError('Expected nonempty unique browser groups')
    names = ['web-player'] if 'regular' in groups else []
    if any(g != 'regular' for g in groups):
        names.append('web-test')
    if 'export' in groups:
        names.append('web-test-update')
    return tuple(names)


def original_request(event, payload):
    """Only the original dispatch inputs can authorize browser work."""
    inputs = (payload.get('inputs') or {}) if event == 'workflow_dispatch' else {}
    return browser_request(inputs.get('browser_scope', 'none'))


def validate_request(plan, event, payload):
    if plan.get('browser_request') != original_request(event, payload):
        raise ValueError('Browser request differs from original event inputs')
    if event != 'workflow_dispatch' and plan.get('browser_request') is not None:
        raise ValueError('Browser request requires workflow_dispatch')
    if event == 'workflow_dispatch' and plan.get('requested_scope') != (payload.get('inputs') or {}).get('scope', 'auto'):
        raise ValueError('General scope differs from original dispatch inputs')

SCENARIOS = (
    {'id': 'regular-start', 'group': 'regular', 'label': 'uninstrumented startup, WebGL2, offline and no errors', 'browsers': ['chromium'], 'images': ['regular-catalog.png']},
    {'id': 'C01', 'group': 'catalog', 'label': 'current catalog, sorting and paper controls', 'browsers': ['chromium'], 'images': ['catalog.png', 'category.png', 'sort.png', 'view.png']},
    {'id': 'C02', 'group': 'input', 'label': 'real elastic edit, atomic undo, redo and cancellation', 'browsers': ['chromium'], 'images': ['input.png']},
    {'id': 'C03', 'group': 'input', 'label': 'resize and live DPI preserve fit and hit geometry', 'browsers': ['chromium'], 'images': []},
    {'id': 'C04', 'group': 'completion', 'label': 'small real completion, transparent reveal and confirmed isolated reset', 'browsers': ['chromium'], 'images': ['at-final-1920.png', 'at-reopen-1920.png', 'at-blend-1920.png', 'at-card-1920.png', 'at-hover-1920.png']},
    {'id': 'C05', 'group': 'persistence', 'label': 'exclusive handoff and rejected second tab never hydrate early', 'browsers': ['chromium'], 'images': []},
    {'id': 'C06', 'group': 'persistence', 'label': 'acknowledged IndexedDB reload restores history, redo and preference', 'browsers': ['chromium'], 'images': []},
    {'id': 'C07', 'group': 'persistence', 'label': 'fresh browser process restores state and performs real redo', 'browsers': ['chromium'], 'images': []},
    {'id': 'C08', 'group': 'persistence', 'label': 'actual IndexedDB failure blocks quit and retry survives reload', 'browsers': ['chromium'], 'images': ['storage-error.png']},
    {'id': 'E01', 'group': 'export', 'label': 'two genuine image exports preserve begun and solved saves', 'browsers': ['chromium'], 'images': ['at-before-update.png', 'at-after-update.png', 'at-restart-update.png']},
)


def require_browser(browser):
    if browser not in BROWSERS:
        raise ValueError('Unsupported CI browser; expected chromium')


def expected(browser, groups):
    require_browser(browser)
    return [row for row in SCENARIOS if browser in row['browsers'] and row['group'] in groups]


def coverage(groups):
    return {browser: {group: [s['id'] for s in expected(browser, [group])]
                      for group in groups} for browser in BROWSERS} if groups else {}
