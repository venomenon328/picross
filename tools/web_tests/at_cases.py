"""AT observations from real exported players and genuine pointer input."""
import timing
import base64
import json
from PIL import Image
from browser_actions import state, point, points

POINTS={'outside':(4,4),'white':(76,76),'hole':(154,154),'soft':(16,128),'ink':(128,64)}
COLORS={1:[56,132,90],2:[174,85,52]}
MATRIX=((1920,1080,1.0),)


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


def show_card_image(page):
    # Measured text may legitimately reduce the column count. Reach the
    # earned image and its hover target through real scrolling before sampling
    # every existing alpha point; never sample an offscreen card or crop it away.
    for _ in range(20):
        label = card(page)
        x,y,w,h = state(page,'catalog_scroll')['catalog_scroll']
        rect = label['at_image']['rect']
        top = rect[1]
        bottom = max(rect[1]+rect[3],label['centers']['paper'][1]+10)
        if top >= y and bottom <= y+h:
            return
        delta = bottom-(y+h)+20 if bottom > y+h else top-y-20
        page.mouse.move(*point(page,[x+w/2,y+h/2]))
        page.mouse.wheel(0,delta)
        page.wait_for_timeout(250)
    raise AssertionError('Earned image and hover target did not become fully visible')


def capture(page, output, name, image, *, revision=1, opacity=1, frame=None):
    rect=image['rect']; samples=image['samples']; color=COLORS[revision]
    assert samples['white']==[255]*4 and samples['soft']==color+[80] and samples['ink']==color+[255]
    assert samples['hole'][3]==samples['outside'][3]==0
    path=output/(name+'.png')
    if opacity==1:
        page.screenshot(path=str(path))
        dpr=page.evaluate('devicePixelRatio')
    else:
        # Original crop of the actual WebGL framebuffer, captured by the
        # read-only export probe immediately after that frame was rendered.
        raw=base64.b64decode(frame['png'],validate=True)
        assert len(raw)<=32*1024*1024
        with timing.CURRENT.measure('image_write'):
            path.write_bytes(raw)
        dpr=1
    viewport=[page.viewport_size[k] for k in ('width','height')]
    positions=[(rect[0]+(x+.5)/256*rect[2],rect[1]+(y+.5)/256*rect[3]) for x,y in POINTS.values()]
    locations=([[position[i]-frame['bounds'][i] for i in range(2)] for position in positions]
               if frame else points(page, positions))
    rows=[]
    with Image.open(path) as raw:
        expected=frame['bounds'][2:] if frame else [v*dpr for v in viewport]
        assert all(abs(raw.size[i]-expected[i])<=1 for i in range(2)), (raw.size,expected)
        rgb=raw.convert('RGB')
        for (kind,_),location in zip(POINTS.items(),locations,strict=True):
            pixel=[int(v*dpr) for v in location]; actual=list(rgb.getpixel(tuple(pixel)))
            if opacity!=1 and kind=='ink':
                assert all(color[i]+10<actual[i]<248 for i in range(3)), (kind,actual,'not an intermediate blend')
                assert actual[1]>actual[0]+5 and actual[1]>actual[2]+3, (kind,actual,'missing green artwork')
            if opacity==1:
                if kind=='white': assert min(actual)>=246, (kind,actual)
                if kind=='ink': assert max(abs(a-b) for a,b in zip(actual,color))<=10, (kind,actual)
                if kind in ('outside','hole'): assert min(actual)>170, (kind,actual)
                if kind=='soft': assert all(color[i]+15<actual[i]<250 for i in range(3)), (kind,actual)
            rows.append(dict(kind=kind,point=pixel,actual=actual,source=samples[kind]))
    result=dict(file=path.name,rect=rect,samples=rows,revision=revision,opacity=opacity,viewport=viewport,pixel_ratio=dpr)
    if frame:result['rendered_frame']={k:v for k,v in frame.items() if k not in ('png','image')}
    return result


def catalog(page, name, output, evidence):
    # Reuse the genuinely completed tiny puzzle from C04. No second solve or
    # synthetic setter just to prepare the earned catalog/hover observation.
    rows=[]
    for spec in MATRIX:
        assert state(page,'viewport','ui_scale') == {'viewport':list(spec[:2]),'ui_scale':spec[2]}
        no_spoilers(page)
        show_card_image(page)
        label=card(page)
        # Move clear of the card, then exercise the real Godot hover route.
        page.mouse.move(3,3);page.wait_for_timeout(250)
        small=capture(page,output,f'{name}-at-card-{spec[0]}',card(page)['at_image'])
        page.mouse.move(*point(page,label['centers']['paper']));page.wait_for_timeout(600)
        assert card(page)['hovered']
        hover=capture(page,output,f'{name}-at-hover-{spec[0]}',card(page)['at_image'])
        rows.append(dict(window=list(spec),small=small,hover=hover))
    evidence['at_catalog']=rows
