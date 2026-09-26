"""Offline evidence checks, discovered by the repository's existing unittest job."""
import hashlib
from html.parser import HTMLParser
import json
import os
import struct
import subprocess
import unittest
import xml.etree.ElementTree as ET
import zlib

from design_study import generate as g

NS={'s':'http://www.w3.org/2000/svg'}


class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.paths=[]

    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src'): self.paths.append(v)


def png_size(path):
    """Read every chunk, check CRC and inflate pixels without a third-party codec."""
    b=path.read_bytes()
    if b[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('PNG signature')
    offset=8; compressed=bytearray(); size=None; ended=False
    while offset<len(b):
        n=struct.unpack('>I',b[offset:offset+4])[0]
        chunk=b[offset+4:offset+8]; payload=b[offset+8:offset+8+n]
        crc=struct.unpack('>I',b[offset+8+n:offset+12+n])[0]
        if zlib.crc32(chunk+payload)!=crc: raise ValueError('PNG CRC')
        if chunk==b'IHDR':
            w,h,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',payload)
            if depth!=8 or color not in (2,6) or interlace: raise ValueError('Unsupported PNG layout')
            size=(w,h); channels=3 if color==2 else 4
        if chunk==b'IDAT': compressed.extend(payload)
        if chunk==b'IEND': ended=True
        offset+=12+n
    if not ended or not size: raise ValueError('Truncated PNG')
    if len(zlib.decompress(compressed))!=h*(1+w*channels): raise ValueError('PNG scanlines')
    return list(size)


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((g.OUT/'manifest.json').read_text(encoding='utf-8'))

    def test_complete_deliverables_and_decodable_renders(self):
        expected={'comparison','sizes','icons','typography','layouts'}
        expected.update(f'{s}-{suffix}' for s in ('s1','s2','s3') for suffix in ('u1-f02-1920','detail','background'))
        expected.add('s1-u2-f02-1920')
        expected.update(f's1-{u}-{f}-{w}' for u in ('u1','u2') for f,w in [('f01',2560),('f03',1920),('f02',1280)])
        self.assertEqual({r['name'] for r in self.manifest['records']},expected)
        for r in self.manifest['records']:
            with self.subTest(r=r['name']):
                svg=g.OUT/'svg'/f'{r["name"]}.svg'; png=g.OUT/'png'/f'{r["name"]}.png'
                root=ET.parse(svg).getroot()
                self.assertEqual([int(root.get('width')),int(root.get('height'))],r['dimensions'])
                self.assertEqual(png_size(png),r['dimensions'])
                for path,key in [(svg,'svg_sha256'),(png,'png_sha256')]:
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),r[key])
                self.assertEqual(r['outer_text_overflow'],[])
                self.assertTrue(all(f['status']=='loaded' for f in r['fonts_loaded']))

    def test_demo_transcription_and_undone_action(self):
        d=g.data('f02'); cells=d['cells']
        self.assertEqual(cells[41:79],[4]*38)
        self.assertEqual(cells[:13],[0]*13)
        self.assertEqual(sum(v==2 for v in cells),36)
        self.assertEqual(sum(v==3 for v in cells),20)
        self.assertEqual(sum(v==1 for v in cells),18)
        self.assertEqual(sum(v==0 for v in cells),22)
        self.assertEqual(cells[82:85],[-1]*3)  # final demonstration stroke was undone
        self.assertEqual(d['rows'][1],[{'length':38,'color':4}])
        self.assertNotIn('solution',d); self.assertNotIn('reveal',d)

    def test_original_fixtures_and_exported_public_data(self):
        for key in ('f01','f02','f03'):
            d=g.data(key)
            exported=json.loads((g.OUT/'sources'/f'{key}-public-demo.json').read_text())
            self.assertEqual(d,exported)
            original=subprocess.check_output(['git','show',f'{g.BASE}:prototypes/p1/data/{key}.json'],cwd=g.ROOT)
            self.assertEqual(hashlib.sha256(original).hexdigest(),d['fixture_sha256'])
        source=(g.OUT/'sources/demo.gd.txt').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),self.manifest['demo_source_sha256'])

    def test_comparison_identity_and_rendered_cells_clues(self):
        main=[r for r in self.manifest['records'] if r.get('fixture')=='f02' and r['dimensions']==[1920,1080]]
        self.assertEqual(len(main),4)
        self.assertEqual(len({r['data_sha256'] for r in main}),1)
        self.assertEqual(len({json.dumps(r['geometry'],sort_keys=True) for r in main if r['layout']=='u1'}),1)
        for r in self.manifest['records']:
            if 'geometry' not in r: continue
            d=g.data(r['fixture']); colors={p['id']:p['color'] for p in d['palette']}
            self.assertEqual(r['data_sha256'],g.digest(d))
            self.assertEqual(r['palette'],d['palette'])
            root=ET.parse(g.OUT/'svg'/f'{r["name"]}.svg').getroot()
            geom=r['geometry']; ox,oy=geom['origin']; _,_,gw,gh=geom['grid']; cell=geom['cell']
            for group,region in [('grid',(ox,oy,gw//cell,gh//cell)),('miniature',(0,0,d['width'],d['height']))]:
                element=root.find(f'.//s:g[@id="{group}"]',NS)
                actual={}
                for el in element.iter():
                    if el.get('data-cell'):
                        x,y,v=map(int,el.get('data-cell').split(',')); actual[x,y]=v
                        if v>0: self.assertEqual(el.get('fill'),colors[v])
                rx,ry,rw,rh=map(int,region)
                expected={(x,y):d['cells'][y*d['width']+x] for y in range(ry,ry+rh) for x in range(rx,rx+rw) if d['cells'][y*d['width']+x]>=0}
                self.assertEqual(actual,expected)
            for el in root.findall('.//s:text[@data-clue]',NS):
                axis,line,idx=el.get('data-clue').split(','); idx=int(idx)
                if idx>=0:
                    token=d[axis][int(line)][idx]
                    self.assertEqual(el.text,str(token['length']))
                    self.assertEqual(el.get('fill'),colors[token['color']])
                else: self.assertIn(el.text,('…','–'))

    def test_clue_windows_and_size_layouts(self):
        seq=g.data('f03')['rows'][50]
        result=g.tokens(seq,7)
        self.assertEqual(result[0],(-1,None))
        self.assertEqual([i for i,_ in result[1:]],list(range(len(seq)-6,len(seq))))
        self.assertEqual(g.tokens(seq[:3],7),list(enumerate(seq[:3])))
        for r in self.manifest['records']:
            if 'geometry' not in r: continue
            geom=r['geometry']; x,y,w,h=geom['grid']; sw,sh=r['dimensions']
            self.assertLessEqual(x+w,sw); self.assertLessEqual(y+h,sh)
            self.assertGreater(r['visible_background_percent'],20)
            self.assertEqual({a['action'] for a in r['actions']},set(g.ICONS)-{'album'})
            for a in r['actions']:
                ax,ay,aw,ah=a['rect']
                self.assertGreaterEqual(ax,0); self.assertGreaterEqual(ay,0)
                self.assertLessEqual(ax+aw,sw); self.assertLessEqual(ay+ah,sh)
                self.assertFalse(ax<x+w and ax+aw>x and ay<y+h and ay+ah>y)
            if sw==1280:
                self.assertEqual(geom['ui'],1.25); self.assertEqual(geom['cell'],22)
            if r['fixture']=='f01': self.assertEqual(geom['cell'],24)

    def test_offline_gallery_and_sources(self):
        parser=References(); parser.feed((g.OUT/'index.html').read_text(encoding='utf-8'))
        self.assertGreater(len(parser.paths),50)
        for path in parser.paths:
            self.assertNotIn('://',path)
            resolved=(g.OUT/path).resolve()
            self.assertTrue(resolved.is_relative_to(g.OUT)); self.assertTrue(resolved.is_file(),path)
        for r in self.manifest['records']:
            root=ET.parse(g.OUT/'svg'/f'{r["name"]}.svg').getroot()
            for el in root.iter():
                for k,v in el.attrib.items():
                    if k.endswith('href'): self.assertTrue(v.startswith(('data:','#')),v[:80])
        for f in json.loads((g.OUT/'sources/fonts.json').read_text()):
            self.assertEqual(hashlib.sha256((g.OUT/f['file']).read_bytes()).hexdigest(),f['sha256'])

    def test_diff_scope(self):
        # Delivery gate for this PR only, not a ban on subsequent product work.
        branch=os.environ.get('GITHUB_HEAD_REF') or subprocess.check_output(
            ['git','rev-parse','--abbrev-ref','HEAD'],cwd=g.ROOT,text=True).strip()
        if branch!='chore/26-art-direction':
            self.skipTest('Issue-26 scope gate applies only to its delivery branch')
        # Includes committed and staged scope; unrelated untracked files are not claimed.
        paths=subprocess.check_output(['git','diff','--name-only',g.BASE],cwd=g.ROOT,text=True).splitlines()
        self.assertTrue(all(p.startswith(('docs/design/z1_1/','tools/design_study/')) for p in paths),paths)

    def test_ui_contrast(self):
        for style in g.STYLES.values():
            self.assertGreaterEqual(contrast(g.INK,style['paper']),4.5)
            self.assertGreaterEqual(contrast(style['accent'],style['paper']),4.5)
            self.assertGreaterEqual(contrast(g.PAPER,style['accent']),4.5)
        self.assertGreaterEqual(contrast(g.INK,'#ddd9bd'),4.5)


def contrast(a,b):
    def lum(c):
        rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)]
        lin=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(v*k for v,k in zip(lin,(.2126,.7152,.0722)))
    x,y=sorted((lum(a),lum(b)))
    return (y+.05)/(x+.05)


if __name__=='__main__': unittest.main()
