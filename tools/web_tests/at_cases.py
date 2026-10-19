"""AT observations from real exported players and genuine pointer input."""
import json
from PIL import Image
from browser_actions import state, point, control, wait, draw, saved, game_viewport

POINTS={'outside':(4,4),'white':(76,76),'hole':(154,154),'soft':(16,128),'ink':(128,64)}
COLORS={1:[56,132,90],2:[174,85,52]}
MATRIX=((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25))


def fixture(root):
    manifest=json.loads((root/'build-manifest.json').read_text(encoding='utf-8'))
    return json.loads((root/'releases'/manifest['build_id']/'at-fixture.json').read_text(encoding='utf-8'))


def card(page, identifier='T-04'):
    data=state(page,'sort','labels')
    return data['labels'][data['sort']['visible_ids'].index(identifier)]


def no_spoilers(page):
    data=state(page,'sort','labels')
    for identifier,label in zip(data['sort']['visible_ids'],data['labels'],strict=True):
        if identifier in ('T-01','T-02'):
            assert not label['reveal'] and not label['at_image'], identifier


def capture(page, output, name, image, *, revision=1, opacity=1):
    rect=image['rect']; samples=image['samples']; color=COLORS[revision]
    assert samples['white']==[255]*4 and samples['soft']==color+[80] and samples['ink']==color+[255]
    assert samples['hole'][3]==samples['outside'][3]==0
    path=output/(name+'.png')
    page.screenshot(path=str(path))
    dpr=page.evaluate('devicePixelRatio')
    rows=[]
    with Image.open(path) as raw:
        rgb=raw.convert('RGB')
        for kind,(x,y) in POINTS.items():
            location=point(page,(rect[0]+(x+.5)/256*rect[2],rect[1]+(y+.5)/256*rect[3]))
            pixel=[int(v*dpr) for v in location]; actual=list(rgb.getpixel(tuple(pixel)))
            if opacity==1:
                if kind=='white': assert min(actual)>=246, (kind,actual)
                if kind=='ink': assert max(abs(a-b) for a,b in zip(actual,color))<=10, (kind,actual)
                if kind in ('outside','hole'): assert min(actual)>170, (kind,actual)
                if kind=='soft': assert all(color[i]+15<actual[i]<250 for i in range(3)), (kind,actual)
            rows.append(dict(kind=kind,point=pixel,actual=actual,source=samples[kind]))
    return dict(file=path.name,rect=rect,samples=rows,revision=revision,opacity=opacity)


def matrix(page, spec, *, catalog=False):
    width,height,scale=spec
    if state(page,'ui_scale')['ui_scale']!=scale:
        control(page,text='Einstellungen / Info') if catalog else control(page,name='menu')
        control(page,text='UI ');control(page,name='nav-work')
    game_viewport(page,width,height)
    page.wait_for_timeout(250)


def catalog(page, name, output, evidence):
    control(page,text='Blatt 01');draw(page,(2,2));saved(page)
    control(page,name='nav-album');control(page,text='Blatt 03')
    draw(page,(0,2),(4,2));wait(page,'picrossProbe.completed && !picrossProbe.ea_active');saved(page)
    control(page,name='nav-album')
    rows=[]
    for spec in MATRIX:
        matrix(page,spec,catalog=True);no_spoilers(page)
        label=card(page)
        # Move clear of the card, then exercise the real Godot hover route.
        page.mouse.move(3,3);page.wait_for_timeout(250)
        small=capture(page,output,f'{name}-at-card-{spec[0]}',card(page)['at_image'])
        page.mouse.move(*point(page,label['centers']['paper']));page.wait_for_timeout(600)
        assert card(page)['hovered']
        hover=capture(page,output,f'{name}-at-hover-{spec[0]}',card(page)['at_image'])
        rows.append(dict(window=list(spec),small=small,hover=hover))
    evidence['at_catalog']=rows


def completion(page, name, output, evidence):
    control(page,name='nav-album');control(page,text='Blatt 03')
    rows=[]
    for spec in MATRIX:
        matrix(page,spec)
        wait(page,'picrossProbe.ending && !picrossProbe.ea_active')
        final=capture(page,output,f'{name}-at-final-{spec[0]}',state(page,'at_image')['at_image'])
        original=state(page,'slots')['slots']
        control(page,name='nav-album');no_spoilers(page);control(page,text='Blatt 03')
        assert state(page,'slots')['slots']==original
        reopen=capture(page,output,f'{name}-at-reopen-{spec[0]}',state(page,'at_image')['at_image'])
        control(page,name='reset',tooltip='Rätsel zurücksetzen');control(page,text='Zurücksetzen',dialog=True)
        assert not state(page,'ea_art')['ea_art']
        draw(page,(0,2),(4,2))
        wait(page,'picrossProbe.ea_active && picrossProbe.ea_alpha > 0.15 && picrossProbe.ea_alpha < 0.85')
        observed=state(page,'at_image','ea_alpha')
        blend=capture(page,output,f'{name}-at-blend-{spec[0]}',observed['at_image'],opacity=observed['ea_alpha'])
        wait(page,'picrossProbe.completed && !picrossProbe.ea_active');saved(page)
        rows.append(dict(window=list(spec),final=final,reopen=reopen,blend=blend))
    evidence['at_completion']=rows
