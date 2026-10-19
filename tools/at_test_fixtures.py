"""Tiny fabricated gate inputs only; these never count as native/browser evidence."""
import hashlib
import json
import struct
import zlib
from at_evidence import MATRIX,SAMPLES


def fixture(revision):
    return dict(format='picross-at-fixture-v1',test_only=True,image_revision=revision,
                image_sha256=str(revision)*64,definitions={'T-01':{'revision':1},'T-04':{'revision':1}},registry_sha256='a'*64)


def png(path,pixels):
    def chunk(kind,raw):return struct.pack('>I',len(raw))+kind+raw+struct.pack('>I',zlib.crc32(kind+raw))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',len(pixels),1,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(b'\0'+bytes(c for p in pixels for c in p)))+chunk(b'IEND',b''))


def browser_row(directory,row):
    def image(name,revision=1,blend=False):
        color=(56,132,90) if revision==1 else (174,85,52)
        rows=[];pixels=[]
        for i,(kind,source) in enumerate(SAMPLES.items()):
            if kind in ('soft','ink'):source=(*color,source[3])
            actual=tuple(round(240*(1-source[3]/255)+source[c]*source[3]/255) for c in range(3))
            rows.append(dict(kind=kind,source=list(source),point=[i,0],actual=list(actual)));pixels.append(actual)
        png(directory/name,pixels)
        return dict(file=name,rect=[0,0,5,1],revision=revision,opacity=.5 if blend else 1,samples=rows)
    group=row['group']
    if group in ('catalog','completion'):
        rows=[]
        for window in MATRIX:
            values={}
            for kind in (('small','hover') if group=='catalog' else ('final','reopen','blend')):
                name='card' if kind=='small' else kind
                values[kind]=image(f'chromium-at-{name}-{window[0]}.png',blend=kind=='blend')
            rows.append(dict(window=window,**values))
        row['at_'+group]=rows
    elif group=='persistence':
        slots=[dict(definition_id='T-01',history=[{}],completed=False),dict(definition_id='T-04',history=[{}],completed=True)]
        row['at_update']=dict(first=fixture(1),second=fixture(2),slots_before=slots,slots_after=slots,
            before=image('chromium-at-before-update.png'),after=image('chromium-at-after-update.png',2),restart=image('chromium-at-restart-update.png',2))


def fixture_record(revision):
    raw=(json.dumps(fixture(revision),sort_keys=True)+'\n').encode()
    return {'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
