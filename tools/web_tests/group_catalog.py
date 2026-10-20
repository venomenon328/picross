"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, state, point, control, wait, click, game_viewport
from browser_runtime import options, graphics


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    version = context.browser.version if context.browser else page.evaluate('navigator.userAgent')
    evidence['version'] = version
    evidence['launch_options'] = options(name)
    evidence['graphics'] = graphics(page)
    passed('export/catalog startup')
    from group_persistence import choose_sort
    initial = state(page, 'sort')['sort']
    assert initial['criterion'] == 'category' and initial['direction'] == 'asc'
    assert initial['primary'] == sorted(initial['primary'])
    choose_sort(page, 3)  # Unknown-date ties preserve the existing six slot-bound UI routes.
    evidence['catalog_geometry'] = []
    for width, height, scale in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)):
        if state(page, 'ui_scale')['ui_scale'] != scale:
            control(page, text='Einstellungen / Info'); control(page, text='UI ')
            control(page, name='nav-work')
        game_viewport(page,width,height)
        page.wait_for_timeout(200)
        labels = state(page, 'labels')['labels']
        assert all(x['unknown'] and not x['reveal'] and x['status'] == 'Neu' for x in labels)
        assert all(x['difficulty'] == 'Nicht eingestuft' for x in labels)
        assert all(x['text_fits'] and x['single_line'] and x['footer'] and x['status_kind'] == x['status'] for x in labels)
        assert all(x['size'] == labels[0]['size'] for x in labels)
        evidence['catalog_geometry'].append(dict(viewport=[width,height],ui_scale=scale,labels=labels))
        page.screenshot(path=str(output/f'{name}-ku-{width}-ui{int(scale*100)}.png'))
    first = state(page, 'labels')['labels'][0]
    for part in ('difficulty_icon','difficulty'):
        page.mouse.move(*point(page, first['centers'][part]))
        page.wait_for_timeout(900)
        assert state(page, 'visible_popups')['visible_popups'] == 0
    first = state(page, 'labels')['labels'][0]
    assert first['difficulty_tip'] == first['fallback_tip'] == '' and not first['mode_popup']
    page.screenshot(path=str(output/f'{name}-ku-no-difficulty-tooltip.png'))
    page.mouse.move(*point(page, first['mode_center']))
    wait(page, 'picrossProbe.labels[0].mode_popup')
    assert first['mode_tip'] == 'Monochromes Rätsel'
    page.screenshot(path=str(output/f'{name}-ku-mode-tooltip.png'))
    for part in ('dimensions','difficulty_icon','difficulty','mode_tip','paper','leaf','status_icon','note'):
        click(page, point(page, state(page, 'labels')['labels'][0]['centers'][part]))
        wait(page, 'picrossProbe.work')
        assert state(page, 'id')['id'] == 'T-01'
        control(page, name='nav-album')
        wait(page, 'picrossProbe.album')
    passed('KU-A single-line metadata, footer, tooltip boundaries and passive click routes')
    evidence['sorting'] = []
    canonical_ids = [slot['definition_id'] for slot in state(page, 'slots')['slots']]
    direction_labels = (
        ('Kategorie', 'Kategorienfolge', 'Umgekehrte Kategorienfolge'),
        ('Größe', 'Kleinste zuerst', 'Größte zuerst'),
        ('Schwierigkeit', 'Sehr leichte zuerst', 'Sehr schwere zuerst'),
        ('Hinzugefügt', 'Älteste zuerst', 'Neueste zuerst'),
    )
    for index, criterion in enumerate(('category', 'size', 'difficulty', 'added')):
        choose_sort(page, index)
        expected_direction = 'desc' if criterion == 'added' else 'asc'
        assert state(page, 'sort')['sort']['direction'] == expected_direction
        for direction in (expected_direction, 'asc' if expected_direction == 'desc' else 'desc'):
            current = state(page, 'sort')['sort']
            if current['direction'] != direction:
                control(page, name='catalog-direction')
                wait(page, f"picrossProbe.sort.direction === '{direction}'")
            current = state(page, 'sort')['sort']
            title, ascending, descending = direction_labels[index]
            meaning = ascending if direction == 'asc' else descending
            assert current['direction_tooltip'] == meaning
            assert current['direction_accessibility_name'] == f'Sortierrichtung ({title}): {meaning}'
            keys = current['primary']
            known = [x for x in keys if x is not None]
            assert keys == sorted(known, reverse=direction == 'desc') + [None] * (len(keys)-len(known))
            evidence['sorting'].append(current)
            chosen = current['visible_ids'][0]
            control(page, text='Blatt ' + str(canonical_ids.index(chosen)+1).zfill(2))
            wait(page, 'picrossProbe.work')
            assert state(page, 'id')['id'] == chosen
            control(page, name='nav-album'); wait(page, 'picrossProbe.album')
            returned = state(page, 'sort')['sort']
            assert returned['criterion'] == criterion and returned['direction'] == direction and returned['selected'] == chosen
            assert returned['direction_tooltip'] == meaning
            assert returned['direction_accessibility_name'] == current['direction_accessibility_name']
    page.screenshot(path=str(output/f'{name}-ku-b-sorting.png'))
    passed('KU-B four criteria, both directions, canonical ties and stable return ID')
    from at_cases import catalog
    catalog(page,name,output,evidence)
    passed('AT transparent catalog and real hover preserve white detail, holes and soft alpha')
    from hz_cases import catalog as hz_catalog
    hz_catalog(page,name,output,evidence)
    passed('HZ Tidy Hand local fallback, complete metadata, native menus and scrollable help')
    assert not errors, errors
