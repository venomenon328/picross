"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, control, wait, draw, state, saved, game_viewport


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch(1.25)
    page, errors = open_page(context, url)
    control(page, text='Blatt 01')
    control(page, name='menu'); control(page, text='UI ')
    control(page, name='nav-work')
    draw(page, (2,2))
    saved(page)
    game_viewport(page,1920,1080)
    control(page,name='nav-album'); control(page,text='Blatt 03')
    draw(page,(0,2),(4,2)); wait(page,'picrossProbe.ending && picrossProbe.completed')
    wait(page,'!picrossProbe.ea_active && !picrossProbe.ea_processing && picrossProbe.ea_caption_alpha===1')
    assert state(page, 'ea_title')['ea_title'].startswith('Blatt 03') and state(page, 'ea_art')['ea_art']
    saved(page)
    completed_slot = state(page, 'slots')['slots'][2]
    control(page,name='reset',tooltip='Rätsel zurücksetzen')
    control(page,text='Abbrechen',dialog=True)
    assert state(page, 'ending')['ending'] and state(page, 'slots')['slots'][2] == completed_slot
    page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
    control(page,text='Blatt 03')
    assert state(page, 'ending')['ending'] and not state(page, 'ea_active')['ea_active'] and not state(page, 'ea_processing')['ea_processing']
    assert state(page, 'slots')['slots'][2] == completed_slot
    foreign_slot = state(page, 'slots')['slots'][0]
    control(page,name='reset',tooltip='Rätsel zurücksetzen')
    control(page,text='Zurücksetzen',dialog=True); saved(page)
    assert state(page, 'work')['work'] and not state(page, 'completed')['completed'] and not state(page, 'ea_art')['ea_art']
    assert state(page, 'slots')['slots'][2]['history'] == [] and state(page, 'slots')['slots'][0] == foreign_slot
    draw(page,(0,2),(4,2)); wait(page,'picrossProbe.ending && picrossProbe.completed')
    assert state(page, 'ea_active')['ea_active']
    passed('EA completion, late caption, neutral heading, cancel, durable browser reload, origin-bound reset and repeated animation')
    control(page,name='nav-album')
    control(page,text='Blatt 05')
    for index in range(8):
        control(page,name=f'color-{index+1}')
        draw(page,(index,2))
    wait(page,'picrossProbe.ending && picrossProbe.completed'); saved(page)
    passed('mono and eight-colour completion through real mouse events')
    assert not errors, errors
