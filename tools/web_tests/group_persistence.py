"""Independent real-browser group; see the versioned scenario inventory."""
import json
import shutil
import tempfile
from browser_actions import open_page, control, wait, draw, state, saved
from browser_runtime import launch

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
    passed('delayed exclusive lock handoff waits before IndexedDB hydration')
    choose_sort(page, 1)
    control(page, name='catalog-direction')
    wait(page, "picrossProbe.sort.direction === 'desc'")
    preference_saved(page)
    preference = state(page, 'sort')['sort']
    pref_bytes = page.evaluate("picrossStorage.fs.readFile(picrossProbe.sort.path,{encoding:'utf8'})")
    control(page, text='Blatt 01')
    wait(page, 'picrossProbe.work')
    draw(page, (2,2), (8,2), retract=(5,2))
    data = state(page, 'cells', 'cursor')
    assert data['cells'][42:46] == [1]*4 and data['cells'][46] == -1 and data['cursor'] == 1
    draw(page, (2,3), (4,3), button='right')
    assert state(page, 'cells')['cells'][62:65] == [0]*3
    control(page, name='undo')
    assert state(page, 'cursor')['cursor'] == 1 and len(state(page, 'history')['history']) == 2
    expected = state(page, 'cells', 'history', 'cursor', 'view')
    saved(page)
    # Real input establishes durable history/redo for this group.
    # A competing real document must be rejected before filesystem hydration.
    second = context.new_page(); second.goto(url)
    second.wait_for_function('document.getElementById("message").textContent.includes("anderen Tab")')
    assert not second.evaluate('window.picrossStorage.ready')
    assert not second.evaluate('!!picrossStorage.engine')
    assert second.evaluate('testIdbOpens===0')
    page.bring_to_front()
    passed('second writer blocked')
    page.reload(); wait(page, 'window.picrossProbe && picrossProbe.album'); saved(page)
    assert state(page, 'sort')['sort']['criterion'] == 'size' and state(page, 'sort')['sort']['direction'] == 'desc'
    # The rejected request must be gone, not start later when the owner reloads.
    assert not second.evaluate('picrossStorage.ready || !!picrossStorage.engine')
    assert second.evaluate('testIdbOpens===0')
    assert second.locator('#message').inner_text().startswith('Start fehlgeschlagen:')
    second.close()
    control(page, text='Blatt 01')
    for key in expected: assert state(page, key)[key] == expected[key], key
    passed('reload restores cells, complete history/redo and view')
    assert not errors, errors
    context.close()
    context = session.launch(1.25); page, errors = open_page(context, url)
    assert state(page, 'sort')['sort']['criterion'] == 'size' and state(page, 'sort')['sort']['direction'] == 'desc'
    assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.sort.path,{encoding:'utf8'})") == pref_bytes
    assert page.evaluate('devicePixelRatio') == 1.25
    control(page, text='Blatt 01')
    for key in expected: assert state(page, key)[key] == expected[key], key
    control(page, name='redo'); assert state(page, 'cursor')['cursor'] == 2
    saved(page)
    passed('real browser process restart at DPI125 restores history and redo works')
    expected_update = state(page, 'cells', 'history', 'cursor', 'view')
    identity = state(page, 'root')['root']
    from at_cases import fixture, capture, no_spoilers
    first_fixture,second_fixture=fixture(root),fixture(update)
    assert first_fixture['image_revision']==1 and second_fixture['image_revision']==2
    assert first_fixture['definitions']==second_fixture['definitions'] and first_fixture['registry_sha256']==second_fixture['registry_sha256']
    assert first_fixture['image_sha256']!=second_fixture['image_sha256']
    control(page,name='nav-album');control(page,text='Blatt 03')
    draw(page,(0,2),(4,2));wait(page,'picrossProbe.completed && !picrossProbe.ea_active');saved(page)
    at_slots=state(page,'slots')['slots']
    at_before=capture(page,output,f'{name}-at-before-update',state(page,'at_image')['at_image'])
    # Install a second genuine export at the same entry; keep old resources.
    for release in (update/'releases').iterdir():
        shutil.copytree(release, root/'releases'/release.name, dirs_exist_ok=True)
    shutil.copyfile(update/'index.html',root/'next.html')
    (root/'next.html').replace(root/'index.html')
    page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
    assert state(page,'slots')['slots']==at_slots
    no_spoilers(page);control(page,text='Blatt 03')
    at_after=capture(page,output,f'{name}-at-after-update',state(page,'at_image')['at_image'],revision=2)
    assert state(page,'ending')['ending'] and not state(page,'ea_active')['ea_active']
    assert not errors,errors
    context.close();context=session.launch(1.25);page,errors=open_page(context,url)
    assert state(page,'slots')['slots']==at_slots and state(page,'root')['root']==identity
    no_spoilers(page);control(page,text='Blatt 03')
    at_restart=capture(page,output,f'{name}-at-restart-update',state(page,'at_image')['at_image'],revision=2)
    evidence['at_update']=dict(first=first_fixture,second=second_fixture,before=at_before,after=at_after,restart=at_restart,
                               slots_before=at_slots,slots_after=state(page,'slots')['slots'],root=identity)
    control(page,name='nav-album')
    passed('AT two genuine image exports retain begun and solved saves across reload and browser restart')
    assert state(page, 'sort')['sort']['criterion'] == 'size' and state(page, 'sort')['sort']['direction'] == 'desc'
    # Preference failure has its own channel; no puzzle-save acknowledgement.
    assert not errors, errors
    page.evaluate('''() => { window.originalPreferenceTransaction = IDBDatabase.prototype.transaction;
      IDBDatabase.prototype.transaction = function(...args) { if(args[1]==='readwrite') throw new DOMException('preference quota','QuotaExceededError'); return originalPreferenceTransaction.apply(this,args); }; }''')
    choose_sort(page, 3)
    wait(page, '!!picrossStorage.preferenceError')
    assert not page.evaluate('!!picrossStorage.error')
    page.screenshot(path=str(output/f'{name}-ku-b-preference-error.png'))
    page.evaluate('() => { IDBDatabase.prototype.transaction = window.originalPreferenceTransaction; }')
    control(page, text='Erneut versuchen'); preference_saved(page)
    # Godot's own autosync may hit the same deliberately failing transaction.
    # Bind only this exact injected diagnostic; all unrelated errors still fail.
    evidence['preference_failure_diagnostics'] = list(errors)
    assert all(error == 'Failed to save IDB file system: preference quota' for error in errors), errors
    errors.clear()
    choose_sort(page, 0); choose_sort(page, 2); choose_sort(page, 1)
    control(page, name='catalog-direction'); preference_saved(page)
    page.reload(); wait(page,'window.picrossProbe && picrossProbe.album')
    assert state(page, 'sort')['sort']['criterion'] == 'size' and state(page, 'sort')['sort']['direction'] == 'desc'
    passed('KU-B preference reload, process restart, compatible export, isolated failure and latest-change retry')
    assert page.locator('body').get_attribute('data-build') == json.loads((update/'build-manifest.json').read_text())['build_id']
    control(page,text='Blatt 01')
    assert state(page, 'root')['root'] == identity
    for key in expected_update: assert state(page, key)[key] == expected_update[key], key
    passed('second genuine compatible export retains IndexedDB identity and progress')
    control(page,name='nav-album'); control(page,text='Blatt 05')
    for index in range(8):
        control(page,name=f'color-{index+1}')
        draw(page,(index,2))
    wait(page,'picrossProbe.ending && picrossProbe.completed'); saved(page)
    control(page,name='nav-album'); control(page,text='Blatt 06')
    control(page,name='color-8'); draw(page,(2,2)); saved(page)
    assert not errors, errors
    # Real IDB transaction boundary throws quota failure, then an actual retry commits.
    page.evaluate('''() => { window.originalTransaction = IDBDatabase.prototype.transaction;
      IDBDatabase.prototype.transaction = function(...args) { if(args[1]==='readwrite') throw new DOMException('test quota','QuotaExceededError'); return originalTransaction.apply(this,args); }; }''')
    draw(page,(3,2)); wait(page,'!!picrossStorage.error')
    control(page,name='menu'); control(page,text='Beenden')
    page.wait_for_timeout(500)
    assert page.locator('#retry').is_visible() and not page.locator('#message').is_visible()
    page.evaluate('() => { IDBDatabase.prototype.transaction = window.originalTransaction; }')
    page.locator('#retry').click(); saved(page)
    passed('actual IndexedDB write failure is visible; own quit stays open; retry commits')
    # End a document without beforeunload while a real transaction fails.
    control(page,name='nav-work')
    durable = state(page, 'cells')['cells']
    page.evaluate('''() => { IDBDatabase.prototype.transaction = function(...args) { if(args[1]==='readwrite') throw new DOMException('blocked','QuotaExceededError'); return originalTransaction.apply(this,args); }; }''')
    draw(page,(4,2)); wait(page,'!!picrossStorage.error')
    page.close(run_before_unload=False)
    page, errors = open_page(context,url)
    control(page,text='Blatt 06')
    assert state(page, 'cells')['cells'] == durable
    passed('abrupt tab close loses unacknowledged edit but retains last acknowledged state')
    # Corrupt only a test slot primary, persist it, and load real recovery after reload.
    control(page,name='nav-album'); control(page,text='Blatt 01')
    draw(page,(8,8)); saved(page)
    page.evaluate('''() => { picrossStorage.fs.writeFile(picrossProbe.root+'/t01.json','broken'); picrossStorage.changed(); }''')
    saved(page); page.reload(); wait(page,'window.picrossProbe && picrossProbe.album')
    assert state(page, 'slot_status')['slot_status'][0] == 'recovered'
    passed('corrupt primary reload uses valid backup without silent overwrite')
    assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})") == 'broken'
    control(page,text='Backup übernehmen'); control(page,text='Übernehmen',dialog=True)
    saved(page)
    assert state(page, 'slot_status')['slot_status'][0] == 'loaded'
    passed('explicit backup confirmation repairs primary through existing validation')
    # Both copies become incompatible; startup must leave their bytes intact.
    page.evaluate('''() => { for (const suffix of ['.json','.bak']) {
      const path=picrossProbe.root+'/t01'+suffix;
      const data=JSON.parse(picrossStorage.fs.readFile(path,{encoding:'utf8'}));
      data.definition_revision+=1; picrossStorage.fs.writeFile(path,JSON.stringify(data));
    } picrossStorage.changed(); }''')
    saved(page)
    incompatible = page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})")
    page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
    assert state(page, 'slot_status')['slot_status'][0] == 'error'
    assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})") == incompatible
    passed('incompatible revisions rejected without migration or overwrite')
    # Reset is exercised via the real confirmation dialog and preserves other slots.
    other = state(page, 'slots')['slots'][4]
    control(page,name='reset-T-01',tooltip='Rätsel zurücksetzen')
    control(page,text='Zurücksetzen',dialog=True)
    saved(page)
    assert state(page, 'slots')['slots'][0]['history'] == [] and state(page, 'slots')['slots'][4] == other
    passed('confirmed reset and slot isolation')
    # Same origin under a path prefix still runs the real export and shares saves.
    nested = root/'nested'
    if not nested.exists(): shutil.copytree(update,nested)
    page.goto(url+'nested/'); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
    assert state(page, 'slots')['slots'][4] == other
    control(page,text='Blatt 06')
    context.set_offline(True)
    before = state(page, 'cells')['cells']; draw(page,(7,7)); assert state(page, 'cells')['cells'] != before
    control(page,name='undo'); assert state(page, 'cells')['cells'] == before
    saved(page); context.set_offline(False)
    passed('real subpath startup, stable saves and offline-after-load input')
    assert not errors, errors
    control(page,name='nav-album')
    control(page,text='Beenden'); page.wait_for_function('document.getElementById("message").textContent.includes("Spiel beendet")')
    assert not page.evaluate('picrossStorage.pending')
    assert page.evaluate('picrossStorage.exitCode') == 0
    # This pinned-engine diagnostic occurs only during engine teardown,
    # including in the uninstrumented player. Keep it visible in evidence;
    # gameplay/navigation errors above and all new restart errors still fail.
    exit_errors = list(errors)
    known_exit = ['ERROR: Pages in use exist at exit in PagedAllocator: N16WorkerThreadPool5GroupE',
                  '   at: ~PagedAllocator (./core/templates/paged_allocator.h:170)']
    evidence['exit_diagnostics'] = exit_errors
    assert exit_errors in ([], known_exit), exit_errors
    page.reload()
    wait(page,'window.picrossProbe && picrossProbe.album && picrossStorage.ready && document.getElementById("message").hidden')
    saved(page)
    assert state(page, 'slots')['slots'][4] == other
    assert errors == exit_errors, errors
    passed('own quit acknowledges durable sync, exits zero and reload restores saved state')
    context.close()
    with tempfile.TemporaryDirectory(prefix='picross-blocked-',ignore_cleanup_errors=True) as blocked_profile:
        blocked = launch(pw, name, blocked_profile)
        try:
            blocked.add_init_script("indexedDB.open = () => { throw new DOMException('blocked by test policy','SecurityError'); };")
            denied = blocked.pages[0]; denied.goto(url)
            try:
                denied.wait_for_function('document.getElementById("message").textContent.includes("Browserspeicher nicht verfügbar")',timeout=60000)
            except Exception:
                denied.screenshot(path=str(output/f'{name}-blocked-failure.png'))
                evidence['blocked_failure_message'] = denied.locator('#message').inner_text()
                raise
            assert not denied.evaluate('picrossStorage.ready')
            passed('blocked IndexedDB startup displays failure before gameplay')
        finally: blocked.close()
