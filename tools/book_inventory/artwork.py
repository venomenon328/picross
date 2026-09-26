"""BP-2 file preparation/verification only; no image generation or UI authoring.

Standard-library PNG decode, bilinear resampling, source-over montage and ZIP.
The artwork itself comes from the native image tool. See artwork/PROCESS.md.
"""
import argparse
import functools
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import zipfile
import zlib

try:
    from .production import png_pixels
except ImportError:
    from production import png_pixels

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/design/book_inventory/artwork'
PROD = ROOT / 'docs/design/book_inventory/production'
BASE = '4ef926fe033418090512d82b9aba151031534c5f'
NAMES = {'a': 'bp2-a-inventarband.png', 'b': 'bp2-b-sammlungskatalog.png'}
DETAILS = {'binding': (0, 0, 650, 220), 'paper': (600, 400, 1100, 750),
           'fold': (1450, 220, 1672, 750), 'lower-edge': (0, 800, 1672, 941)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8', newline='\n')


def png_write(path, image):
    w, h, n, pixels = image
    assert n in (3, 4) and len(pixels) == w*h*n
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)
    raw = b''.join(b'\0' + pixels[y*w*n:(y+1)*w*n] for y in range(h))
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2 if n == 3 else 6, 0, 0, 0))
    data += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def resample(image, size, box=None):
    """Bilinear sampling at pixel centres; an explicit proportional crop box."""
    w, h, n, pixels = image
    W, H = size
    x0, y0, x1, y1 = box or (0, 0, w, h)
    assert abs((x1-x0)/W - (y1-y0)/H) < 1e-9, 'non-proportional transform'
    if (W, H) == (w, h) and box is None:
        return image
    def axis(start, stop, count, limit):
        result = []
        for i in range(count):
            t = max(0, min(limit-1, start+(i+.5)*(stop-start)/count-.5))
            a = math.floor(t)
            result.append((a, min(a+1, limit-1), t-a))
        return result
    xs = axis(x0, x1, W, w)
    ys = axis(y0, y1, H, h)
    result = bytearray(W*H*n)
    for y, (ya, yb, fy) in enumerate(ys):
        for x, (xa, xb, fx) in enumerate(xs):
            a, b, c, d = ((ya*w+xa)*n, (ya*w+xb)*n, (yb*w+xa)*n, (yb*w+xb)*n)
            dest = (y*W+x)*n
            for k in range(n):
                top = pixels[a+k]*(1-fx)+pixels[b+k]*fx
                bottom = pixels[c+k]*(1-fx)+pixels[d+k]*fx
                result[dest+k] = int(top*(1-fy)+bottom*fy+.5)
    return W, H, n, bytes(result)


def montage(background, overlay):
    w, h, n, bg = background
    W, H, N, ui = overlay
    assert (w, h, n, W, H, N) == (w, h, 3, w, h, 4)
    result = bytearray(bg)
    for p in range(w*h):
        alpha = ui[p*4+3]
        if alpha:
            for k in range(3):
                result[p*3+k] = (ui[p*4+k]*alpha+bg[p*3+k]*(255-alpha)+127)//255
    return w, h, 3, bytes(result)


def crop(image, box):
    w, h, n, pixels = image
    x0, y0, x1, y1 = box
    assert 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h
    return x1-x0, y1-y0, n, b''.join(pixels[(y*w+x0)*n:(y*w+x1)*n] for y in range(y0, y1))


@functools.lru_cache(maxsize=4096)
def luminance(rgb):
    v = [c/255 for c in rgb]
    v = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in v]
    return sum(a*b for a, b in zip(v, (.2126, .7152, .0722)))


def contrast_records(background, case):
    """Conservative minimum over each actual measured normal-text rectangle.

    Declared text colour, not antialiased edge colour; miniature label has the
    unchanged opaque BP-1R card beneath it. Puzzle hints and study footer separate.
    """
    record = next(r for r in read(PROD/'render-checks.json')['records'] if r['file'] == case+'-ui')
    w, h, n, pixels = background
    ink = luminance((41, 62, 61))
    result = []
    for t in record['text_bounds']:
        if t['zone'] in ('row_hints', 'column_hints') or t['text'].startswith('BP-1R /'):
            continue
        x, y, W, H = t['box']
        vals = []
        for yy in range(max(0, math.floor(y)), min(h, math.ceil(y+H))):
            for xx in range(max(0, math.floor(x)), min(w, math.ceil(x+W))):
                p = (yy*w+xx)*n
                rgb = (255, 250, 240) if t['text'] == 'DEIN STAND' else tuple(pixels[p:p+3])
                lum = luminance(rgb)
                vals.append((max(lum, ink)+.05)/(min(lum, ink)+.05))
        result.append(dict(text=t['text'], box=t['box'], minimum=round(min(vals), 4)))
    return result


def inputs():
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
                                     '--', 'docs/design/book_inventory/production'], cwd=ROOT, text=True).splitlines()
    result = {}
    for name in paths:
        data = (ROOT/name).read_bytes()
        expected = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert data == expected, 'BP-1R input changed: '+name
        result[name] = sha(data)
    return result


def validate_retouch(source, qualified):
    assert source[:3] == qualified[:3] == (1672, 941, 3)
    a, b = source[3], qualified[3]
    stride = 1672*3
    assert a[:820*stride] == b[:820*stride]
    for y in range(820, 941):
        alpha = min(1, (y-819)/60)
        for x in range(stride):
            expected = int(a[y*stride+x]*(1-alpha)+a[(y-24)*stride+x]*alpha)
            assert abs(expected-b[y*stride+x]) <= 1, 'unexpected A retouch'


def process(build=False):
    """Build or independently decode and compare every delivered pixel."""
    cases = read(PROD/'layout.json')['cases']
    cache = {}
    def decode(path):
        if path not in cache:
            cache[path] = png_pixels(path.read_bytes())
        return cache[path]
    def deliver(name, expected):
        path = OUT/name
        if build:
            png_write(path, expected)
        else:
            assert decode(path) == expected, 'pixel mismatch: '+name
    native_a = decode(OUT/'originals/a-qualified.png')
    validate_retouch(decode(OUT/'originals/a-generator.png'), native_a)
    contrasts = {}
    for key, name in NAMES.items():
        native = native_a if key == 'a' else decode(OUT/'originals/b-generator.png')
        assert native[:3] == (1672, 941, 3)
        master = resample(native, (2560, 1440), (0, .25, 1672, 940.75))
        deliver(name, master)
        backgrounds = {}
        for g in cases:
            W, H = g['viewport']
            tr = g['background']
            assert tr['offset_px'] == [0, 0] and tr['crop_px'] == [0, 0, 2560, 1440]
            assert [W, H] == [2560*tr['uniform_scale'], 1440*tr['uniform_scale']]
            if W not in backgrounds:
                backgrounds[W] = resample(master, (W, H))
            bg = backgrounds[W]
            ui = decode(PROD/'png'/f'{g["name"]}-ui.png')
            composed = montage(bg, ui)
            deliver(f'checks/{key}-{g["name"]}.png', composed)
            contrasts[key+'-'+g['name']] = contrast_records(bg, g['name'])
            # 1:1 screen-pixel detail: clue/grid junction and separate status zone.
            gx, gy = g['rects']['grid'][:2]
            sx, sy, sw, sh = g['rects']['status']
            deliver(f'checks/{key}-{g["name"]}-numbers.png', crop(composed, (gx-70, gy-70, gx+250, gy+170)))
            deliver(f'checks/{key}-{g["name"]}-status.png', crop(composed, (sx-8, sy-8, sx+sw+8, sy+sh+8)))
        deliver(f'checks/{key}-background-1080.png', backgrounds[1920])
        for detail, box in DETAILS.items():
            deliver(f'checks/{key}-native-{detail}.png', crop(native, box))
    assert all(t['minimum'] >= 4.5 for values in contrasts.values() for t in values), 'normal text contrast below 4.5'
    if build:
        write_json(OUT/'checks/contrast.json', contrasts)
    else:
        assert read(OUT/'checks/contrast.json') == contrasts
    return contrasts


def package_files():
    return sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'bp2-review.zip')


def metadata():
    result = {}
    for p in package_files():
        if p.name == 'manifest.json':
            continue
        data = p.read_bytes()
        item = dict(sha256=sha(data), bytes=len(data))
        if p.suffix == '.png':
            w, h, n, pixels = png_pixels(data)
            item.update(width=w, height=h, format='PNG', channels=n, opaque=n == 3 or min(pixels[3::4]) == 255)
        result[p.relative_to(OUT).as_posix()] = item
    return result


def pack():
    with zipfile.ZipFile(OUT/'bp2-review.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in package_files():
            info = zipfile.ZipInfo(p.relative_to(OUT).as_posix(), (2026, 9, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, p.read_bytes())


def verify():
    m = read(OUT/'manifest.json')
    assert m['input_commit'] == BASE and m['inputs'] == inputs()
    assert m['files'] == metadata(), 'file list/hash/dimensions mismatch'
    assert m['native_to_master'] == dict(source=[1672, 941], crop=[0, .25, 1672, 940.75], target=[2560, 1440], sampler='bilinear pixel centres', scale=2560/1672)
    process()
    expected = {p.relative_to(OUT).as_posix(): p.read_bytes() for p in package_files()}
    with zipfile.ZipFile(OUT/'bp2-review.zip') as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
        assert set(archive.namelist()) == set(expected)
        assert all(archive.read(n) == b for n, b in expected.items())
    print('BP-2: native/output mapping, opaque PNGs, unchanged BP-1R inputs, 10 exact UI montages, native/screen details, local text contrast and ZIP OK')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'pack', 'verify'])
    command = parser.parse_args().command
    if command == 'build':
        process(True)
        m = dict(schema=1, package='BP-2 / B2-01..B2-05', input_commit=BASE,
                 inputs=inputs(), provenance=read(OUT/'generation.json'),
                 native_to_master=dict(source=[1672, 941], crop=[0, .25, 1672, 940.75],
                 target=[2560, 1440], sampler='bilinear pixel centres', scale=2560/1672), files=metadata())
        write_json(OUT/'manifest.json', m)
        pack()
    elif command == 'pack':
        m = read(OUT/'manifest.json'); m['files'] = metadata(); write_json(OUT/'manifest.json', m); pack()
    else:
        verify()
