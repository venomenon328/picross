"""Explicit image-export compatibility profile: two real technical exports."""
import json
import shutil
from browser_actions import open_page, control, wait, draw, state, saved


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    control(page, text='Blatt 01'); draw(page, (2,2)); saved(page)
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

    assert page.locator('body').get_attribute('data-build') == json.loads((update/'build-manifest.json').read_text())['build_id']
    assert not errors, errors
    passed('two genuine image exports preserve begun and solved saves')
