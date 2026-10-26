"""One tiny actual solve, natural reveal, reopening and isolated reset."""
from browser_actions import open_page, control, wait, draw, state, saved
from at_cases import capture, no_spoilers, catalog


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    control(page, text='Blatt 01'); draw(page, (2,2)); saved(page)
    foreign = page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})")
    control(page, name='nav-album'); control(page, text='Blatt 03')
    # Arm only a read-only framebuffer observation. The actual gesture and
    # production clock still perform the complete 2.15-second transition.
    page.evaluate('window.picrossAtCapture = true')
    try:
        draw(page, (0,2), (4,2))
        wait(page, 'window.picrossAtFrame && picrossProbe.completed')
        frame = page.evaluate('window.picrossAtFrame')
    finally:
        page.evaluate('window.picrossAtCapture = false')
    blend = capture(page, output, f'{name}-at-blend-1920', frame['image'], opacity=frame['opacity'], frame=frame)
    wait(page, 'picrossProbe.ending && !picrossProbe.ea_active && !picrossProbe.ea_processing && picrossProbe.ea_caption_alpha === 1')
    assert state(page, 'ea_title')['ea_title'].startswith('Blatt 03')
    saved(page)
    solved = state(page, 'slots')['slots'][2]
    final = capture(page, output, f'{name}-at-final-1920', state(page, 'at_image')['at_image'])
    control(page, name='reset', tooltip='Rätsel zurücksetzen')
    control(page, text='Abbrechen', dialog=True)
    assert state(page, 'slots')['slots'][2] == solved and state(page, 'ending')['ending']
    control(page, name='nav-album'); no_spoilers(page)
    catalog(page, name, output, evidence)
    data = state(page, 'sort', 'labels')
    label = data['labels'][data['sort']['visible_ids'].index('T-04')]
    assert label['status'] == label['status_kind'] == 'Gelöst' and label['reveal'] and not label['unknown']
    control(page, text='Blatt 03')
    assert not state(page, 'ea_active')['ea_active'] and state(page, 'slots')['slots'][2] == solved
    reopen = capture(page, output, f'{name}-at-reopen-1920', state(page, 'at_image')['at_image'])
    control(page, name='reset', tooltip='Rätsel zurücksetzen')
    control(page, text='Zurücksetzen', dialog=True); saved(page)
    data = state(page, 'slots', 'work', 'ea_art', 'completed')
    assert data['work'] and not data['completed'] and not data['ea_art']
    assert data['slots'][2]['history'] == [] and set(data['slots'][2]['cells']) == {-1}
    assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})") == foreign
    evidence['at_completion'] = [dict(window=[1920,1080,1.0], final=final, reopen=reopen, blend=blend)]
    assert not errors, errors
    passed('small real completion, transparent reveal and confirmed isolated reset')
