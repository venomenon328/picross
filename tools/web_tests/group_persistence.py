"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, control, wait, draw, state, saved

def choose_sort(page, index):
    control(page, name='catalog-sort')
    wait(page, 'picrossProbe.sort.menu.visible')
    # Real keyboard navigation avoids browser-specific mouse-motion coalescing
    # inside Godot's embedded popup, while exercising its normal focus route.
    for _ in range(5):
        focused = state(page, 'sort')['sort']['menu']['focused']
        if focused == index:
            break
        page.keyboard.press('ArrowDown')
        wait(page, f'picrossProbe.sort.menu.focused !== {focused}')
    assert state(page, 'sort')['sort']['menu']['focused'] == index
    page.keyboard.press('Enter')
    criterion = ('category', 'size', 'difficulty', 'added')[index]
    wait(page, f"picrossProbe.sort.criterion === '{criterion}'")


def preference_saved(page):
    wait(page, '!picrossStorage.preferencePending && !picrossStorage.preferenceError')


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    # Deterministic contention with a real other document. It releases only
    # after the new player's request is queued and has not touched IDBFS.
    (root/'lock-owner.html').write_text('<title>Temporary test lock owner</title>')
    owner = context.new_page(); owner.goto(url+'lock-owner.html')
    owner.evaluate('''() => { navigator.locks.request('picross-p1-userfs', () =>
      new Promise(resolve => { window.releaseLock=resolve; })); }''')
    owner.wait_for_function('!!window.releaseLock')
    context.add_init_script('''(() => {
      const open=indexedDB.open.bind(indexedDB);
      window.testIdbOpens=0;
      indexedDB.open=(...args) => { ++window.testIdbOpens; return open(...args); };
    })();''')
    def handoff(candidate):
        owner.wait_for_function('''async () =>
          (await navigator.locks.query()).pending.some(lock => lock.name==='picross-p1-userfs')''')
        candidate.wait_for_timeout(250)
        assert candidate.evaluate('testIdbOpens===0 && !picrossStorage.ready && !picrossStorage.engine')
        evidence['lock_handoff'] = owner.evaluate('navigator.locks.query()')
        owner.evaluate('releaseLock()')
    page, errors = open_page(context, url, before_start=handoff)
    owner.close()
    # A competing real document must be rejected before filesystem hydration.
    second = context.new_page(); second.goto(url)
    second.wait_for_function('document.getElementById("message").textContent.includes("anderen Tab")')
    assert not second.evaluate('window.picrossStorage.ready')
    assert not second.evaluate('!!picrossStorage.engine')
    assert second.evaluate('testIdbOpens===0')
    page.bring_to_front()

    passed('exclusive handoff and rejected second tab never hydrate early')
    choose_sort(page, 1); preference_saved(page)
    control(page, text='Blatt 01'); wait(page, 'picrossProbe.work')
    draw(page, (2,2), (5,2)); draw(page, (2,3), (4,3), button='right')
    control(page, name='undo')
    expected = state(page, 'cells', 'history', 'cursor', 'view')
    assert expected['cursor'] == 1 and len(expected['history']) == 2
    assert expected['cells'][42:46] == [1]*4 and expected['cells'][62:65] == [-1]*3
    saved(page)
    page.reload(); wait(page, 'window.picrossProbe && picrossProbe.album'); saved(page)
    assert not second.evaluate('picrossStorage.ready || !!picrossStorage.engine')
    assert second.evaluate('testIdbOpens === 0')
    second.close()
    assert state(page, 'sort')['sort']['criterion'] == 'size'
    control(page, text='Blatt 01')
    assert state(page, *expected) == expected
    evidence['reload'] = expected
    passed('acknowledged IndexedDB reload restores history, redo and preference')
    assert not errors, errors
    context.close()
    context = session.launch(1.25); page, errors = open_page(context, url)
    assert state(page, 'sort')['sort']['criterion'] == 'size'
    assert page.evaluate('devicePixelRatio') == 1.25
    control(page, text='Blatt 01')
    assert state(page, *expected) == expected
    control(page, name='redo')
    data = state(page, 'cells', 'history', 'cursor')
    assert data['cursor'] == 2 and data['history'] == expected['history']
    assert data['cells'][62:65] == [0]*3
    saved(page)
    evidence['restart'] = data
    passed('fresh browser process restores state and performs real redo')
    assert not errors, errors
    page.evaluate("""() => { window.originalTransaction = IDBDatabase.prototype.transaction;
      IDBDatabase.prototype.transaction = function(...args) {
        if(args[1]==='readwrite') throw new DOMException('test quota','QuotaExceededError');
        return originalTransaction.apply(this,args);
      }; }""")
    draw(page, (3,4)); wait(page, '!!picrossStorage.error')
    expected_retry = state(page, 'cells', 'history', 'cursor')
    control(page, name='menu'); control(page, text='Beenden')
    assert page.locator('#retry').is_visible() and not page.locator('#message').is_visible()
    page.screenshot(path=str(output/f'{name}-storage-error.png'))
    page.evaluate('IDBDatabase.prototype.transaction = window.originalTransaction')
    page.locator('#retry').click(); saved(page)
    evidence['failure_diagnostics'] = list(errors)
    assert all(error == 'Failed to save IDB file system: test quota' for error in errors), errors
    errors.clear()
    page.reload(); wait(page, 'window.picrossProbe && picrossProbe.album'); saved(page)
    control(page, text='Blatt 01')
    assert state(page, *expected_retry) == expected_retry
    evidence['retry'] = expected_retry
    assert not errors, errors
    passed('actual IndexedDB failure blocks quit and retry survives reload')
