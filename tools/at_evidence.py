"""Independent AT pixel/composition gate, using only the standard library."""
import json
import hashlib
import struct
import zlib

MATRIX = [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]
SAMPLES = {'outside': (0,0,0,0), 'white': (255,255,255,255),
           'hole': (0,0,0,0), 'soft': (56,132,90,80), 'ink': (56,132,90,255)}


def require(value, message):
    if not value: raise ValueError('AT evidence: '+message)


def png(path):
    raw=path.read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n' and len(raw)<=32*1024*1024,'invalid PNG')
    offset=8; data=bytearray(); header=None
    while offset<len(raw):
        length=struct.unpack('>I',raw[offset:offset+4])[0]
        kind=raw[offset+4:offset+8]; block=raw[offset+8:offset+8+length]
        require(len(block)==length and zlib.crc32(kind+block)==struct.unpack('>I',raw[offset+8+length:offset+12+length])[0],'PNG CRC')
        if kind==b'IHDR': header=struct.unpack('>IIBBBBB',block)
        if kind==b'IDAT': data.extend(block)
        offset+=length+12
        if kind==b'IEND': break
    require(header is not None,'missing PNG header')
    width,height,depth,color,compression,filtering,interlace=header
    require(0<width<=4096 and 0<height<=4096 and depth==8 and color in (2,6) and (compression,filtering,interlace)==(0,0,0),'PNG layout')
    channels=3 if color==2 else 4; stride=width*channels
    decoder=zlib.decompressobj(); decoded=decoder.decompress(bytes(data),(stride+1)*height+1)
    require(len(decoded)==(stride+1)*height and decoder.eof and not decoder.unused_data,'PNG payload size')
    rows=[]; previous=bytearray(stride)
    for y in range(height):
        mode=decoded[y*(stride+1)]; row=bytearray(decoded[y*(stride+1)+1:(y+1)*(stride+1)])
        require(mode<=4,'PNG filter')
        for i in range(stride):
            left=row[i-channels] if i>=channels else 0; above=previous[i]; corner=previous[i-channels] if i>=channels else 0
            if mode==4:
                p=left+above-corner; distances=(abs(p-left),abs(p-above),abs(p-corner))
                predictor=(left,above,corner)[distances.index(min(distances))]
            else: predictor=(0,left,above,(left+above)//2)[mode]
            row[i]=(row[i]+predictor)&255
        rows.append(row); previous=row
    return (width,height),lambda x,y: tuple(rows[y][x*channels:x*channels+3])


def native(directory, report, kinds):
    fixture=json.loads((directory/'at-fixture.json').read_text(encoding='utf-8'))
    require(fixture['test_only'] is True and fixture['image_revision']==1,'fixture identity')
    require({k:tuple(v['rgba']) for k,v in fixture['samples'].items()}==SAMPLES,'independent fixture samples')
    rows=report['at_measurements']
    require([r['window'] for r in rows]==MATRIX,'mandatory native matrix')
    for row in rows:
        for kind in kinds:
            item=row[kind]; w=row['window'][0]
            name='catalog' if kind=='small' else kind
            require(item['file']==f'at-{name}-{w}.png' and item['background_file']==f'at-{name}-{w}-paper.png','original image names')
            size,pixel=png(directory/item['file']); back_size,paper=png(directory/item['background_file'])
            bounds=item['bounds']; require(list(size)==bounds[2:] and size==back_size,'original crop geometry')
            require(item['framebuffer']==row['window'][:2],'actual framebuffer')
            require([s['kind'] for s in item['samples']]==list(SAMPLES),'complete pixel samples')
            for sample in item['samples']:
                source=SAMPLES[sample['kind']]; actual_source=sample['source']
                require(abs(actual_source[3]-source[3]/255)<.001 and (source[3]==0 or all(abs(actual_source[i]-source[i]/255)<.001 for i in range(3))),'imported RGBA')
                opacity=.5 if kind=='blend' else 1
                require(sample['opacity']==opacity,'actual reveal phase')
                x,y=(sample['point'][i]-bounds[i] for i in (0,1))
                require(0<=x<size[0] and 0<=y<size[1],'sample within original crop')
                actual=pixel(x,y); background=paper(x,y); alpha=source[3]/255*opacity
                require(all(abs(actual[i]/255-sample['actual'][i])<.005 and abs(background[i]/255-sample['background'][i])<.005 for i in range(3)),'JSON differs from original pixels')
                require(max(abs(actual[i]/255-(background[i]/255*(1-alpha)+source[i]/255*alpha)) for i in range(3))<=.035,'original alpha composition')
    return len(rows)*len(kinds)*len(SAMPLES)


def browser(directory, report, builds):
    group=report['group']
    def check_image(item, revision=1, blend=False):
        require(item['file'].startswith('chromium-at-') and '/' not in item['file'] and '\\' not in item['file'],'browser original name')
        size,pixel=png(directory/item['file'])
        viewport=item['viewport'];ratio=item['pixel_ratio']
        require(type(ratio) in (int,float) and 0<ratio<=4 and len(viewport)==2 and
                all(type(v) is int and v>0 for v in viewport),'browser screenshot geometry')
        if blend:
            frame=item['rendered_frame'];bounds=frame['bounds'];surface=frame['framebuffer']
            require(frame['definition_id']=='T-04' and type(frame['key']) is str and frame['key'].isdigit() and
                    frame['opacity']==item['opacity'] and .3<=item['opacity']<=.7,'actual rendered transition binding')
            require(len(bounds)==4 and all(type(v) is int for v in bounds) and len(surface)==2 and
                    all(type(v) is int and v>0 for v in surface) and
                    all(0<=bounds[i] and bounds[i+2]>0 and bounds[i]+bounds[i+2]<=surface[i] for i in range(2)),
                    'rendered framebuffer crop')
            require(list(size)==bounds[2:] and ratio==1,'browser device pixel geometry')
        else:
            require(all(abs(size[i]-viewport[i]*ratio)<=1 for i in range(2)),'browser device pixel geometry')
        require(item['revision']==revision and (0<item['opacity']<1 if blend else item['opacity']==1),'browser image phase/revision')
        require([s['kind'] for s in item['samples']]==list(SAMPLES),'browser pixel inventory')
        color=(56,132,90) if revision==1 else (174,85,52)
        for sample in item['samples']:
            x,y=sample['point'];require(0<=x<size[0] and 0<=y<size[1],'browser pixel outside screenshot')
            actual=pixel(x,y);kind=sample['kind'];source=sample['source']
            require(list(actual)==sample['actual'],'browser pixels differ from original')
            expected=(255,255,255,255) if kind=='white' else (*color,80 if kind=='soft' else 255)
            require(source[3]==0 if kind in ('outside','hole') else tuple(source)==expected,'browser imported source')
            if blend and kind=='ink':
                require(all(color[i]+10<actual[i]<248 for i in range(3)), 'original browser frame is not an intermediate blend')
                require(actual[1]>actual[0]+5 and actual[1]>actual[2]+3, 'original browser blend has no green artwork')
            if not blend:
                if kind=='white': require(min(actual)>=246,'lost opaque white detail')
                elif kind=='ink': require(max(abs(a-b) for a,b in zip(actual,color))<=10,'wrong export image')
                elif kind in ('outside','hole'): require(min(actual)>170,'opaque exterior/hole')
                else: require(all(color[i]+15<actual[i]<250 for i in range(3)),'lost soft alpha')
    if group in ('catalog','completion'):
        rows=report['at_'+group];require([r['window'] for r in rows]==MATRIX,'browser AT matrix')
        for row in rows:
            if group=='completion':require(row['blend']['rendered_frame']['framebuffer']==row['window'][:2], 'actual browser framebuffer matrix')
            for kind in (('small','hover') if group=='catalog' else ('final','reopen','blend')):
                check_image(row[kind],blend=kind=='blend')
    elif group=='persistence':
        value=report['at_update'];first=value['first'];second=value['second']
        require(first['image_revision']==1 and second['image_revision']==2 and first['image_sha256']!=second['image_sha256'],'two distinct synthetic image revisions')
        require(first['definitions']==second['definitions'] and first['registry_sha256']==second['registry_sha256'],'image-only export identity')
        require(value['slots_before']==value['slots_after'],'save migration/change during image update')
        slots={s['definition_id']:s for s in value['slots_before']}
        require(slots['T-01']['history'] and slots['T-01']['completed'] is False and slots['T-04']['completed'] is True,'begun and solved export cases')
        for key,binding in (('web-test',first),('web-test-update',second)):
            manifest=builds[key]['manifest']
            raw=(json.dumps(binding,sort_keys=True)+'\n').encode()
            expected=manifest['files']['releases/'+manifest['build_id']+'/at-fixture.json']
            require(expected=={'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'fixture is not bound to delivered export')
        check_image(value['before']);check_image(value['after'],2);check_image(value['restart'],2)
