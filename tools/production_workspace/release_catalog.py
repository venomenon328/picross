"""Catalog limits shared by work publishers and both signed application publishers."""
import json
import time

LOCK_BRANCH = 'work-prod-control/catalog'
PAGE_SIZE = 100
PAGE_LIMIT = 4
PAGE_BYTES = 4 * 1024**2
# A signed application release has five delivery files, manifest and signature.
SIGNED_ASSETS = 7
ENTRY_ALLOWANCE = 16 * 1024


def catalog(request):
    rows = []
    started = time.monotonic()
    for page in range(1, PAGE_LIMIT + 1):
        batch = request(f'releases?per_page={PAGE_SIZE}&page={page}')
        if not isinstance(batch, list) or len(batch) > PAGE_SIZE:
            raise ValueError('Invalid release catalog')
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            return rows, time.monotonic() - started
    raise ValueError('App catalog has no terminating page')


def capacity(rows, elapsed, tag, additions, *, reserved_apps):
    existing = next((row for row in rows if row['tag_name'] == tag), None)
    new = int(existing is None)
    if len(rows) + new + reserved_apps >= PAGE_LIMIT * PAGE_SIZE:
        raise ValueError('App catalog requires a terminating page')
    if elapsed >= 45:
        raise ValueError('Insufficient margin in the installed 60-second metadata budget')
    if len((existing or {}).get('assets', [])) + additions > 1000:
        raise ValueError('GitHub release asset limit')
    # Bound even a reordered page including both generations and future apps.
    sizes = sorted((len(json.dumps(row, ensure_ascii=True).encode()) for row in rows), reverse=True)
    growth = new + additions + reserved_apps * (1 + SIGNED_ASSETS)
    if sum(sizes[:PAGE_SIZE]) + 1024 + ENTRY_ALLOWANCE * growth >= PAGE_BYTES:
        raise ValueError('Insufficient installed-client metadata page capacity')
