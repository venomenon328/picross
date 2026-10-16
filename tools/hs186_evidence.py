"""Publish a curated native Windows original ZIP as a revision-bound GitHub gist.

Base64 is a lossless transport for binary originals, split below the Gist API's
per-file content limit. No repository branch, release, profile or save upload.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

DOWNLOAD = '''"""Download the original ZIP; standard library only, anonymous access."""
import base64, hashlib, json, sys, urllib.request, zipfile
from pathlib import Path

gist, revision, destination = sys.argv[1:]
def read(url):
    req = urllib.request.Request(url, headers={"User-Agent":"picross-HS-evidence"})
    return urllib.request.urlopen(req, timeout=120).read()
info = json.loads(read(f"https://api.github.com/gists/{gist}/{revision}"))
manifest = json.loads(read(info["files"]["manifest.json"]["raw_url"]))
parts = []
for part in manifest["parts"]:
    data = base64.b64decode(read(info["files"][part["name"]]["raw_url"]), validate=True)
    assert hashlib.sha256(data).hexdigest() == part["sha256"], part["name"]
    parts.append(data)
original = b"".join(parts)
assert len(original) == manifest["bytes"]
assert hashlib.sha256(original).hexdigest() == manifest["sha256"]
target = Path(destination)
with target.open("xb") as stream: stream.write(original)
with zipfile.ZipFile(target) as archive:
    assert set(archive.namelist()) == set(manifest["files"])
    for name, digest in manifest["files"].items():
        assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
print("Verified original Windows ZIP:", target, manifest["sha256"])
'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package(directory: Path, target: Path) -> dict:
    proof = json.loads((directory/'hs-windows-proof.json').read_text(encoding='utf-8'))
    if not proof['host'].startswith('Windows') or proof['windows_hs']['status'] != 'success':
        raise ValueError('Successful native Windows proof required')
    # Positive list: do not recurse into player profiles, saves or downloads.
    files = [directory/'hs-windows-proof.json',directory/'windows-proof.json']
    files += list((directory/'logs').glob('*.log'))
    files += list((directory/'hs186').glob('*.png')) + list((directory/'hs186').glob('*.json'))
    files += list((directory/'hf149').glob('*.png'))
    files += [directory/'hf149'/f'hf-{stage}.json' for stage in ('write','read','native','acceptance')]
    hashes = {}
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files):
            name = path.relative_to(directory).as_posix()
            data = path.read_bytes()
            hashes[name] = digest(data)
            archive.writestr(name,data)
        # Original CI report binds downloaded export and selected evidence.
        data = (directory/'technical/product-report.json').read_bytes()
        archive.writestr('ci/product-report.json',data)
        hashes['ci/product-report.json'] = digest(data)
    original = target.read_bytes()
    return dict(head=proof['head'],base=proof['base'],selection_base=proof['selection_base'],
                checkout=proof['checkout'],run=proof['run'],
                exports=proof['exports'],artifacts=proof['artifacts'],
                filename=target.name,bytes=len(original),sha256=digest(original),files=hashes)


def publish(target: Path, manifest: dict) -> dict:
    original = target.read_bytes()
    if digest(original) != manifest['sha256']: raise ValueError('Changed ZIP')
    files = {'download.py':{'content':DOWNLOAD}}
    manifest = dict(manifest,parts=[])
    for index, offset in enumerate(range(0,len(original),700000)):
        part = original[offset:offset+700000]
        name = f'windows-originals-{index:03}.zip.b64'
        files[name] = {'content':base64.b64encode(part).decode('ascii')}
        manifest['parts'].append(dict(name=name,sha256=digest(part)))
    files['manifest.json'] = {'content':json.dumps(manifest,indent=2)+'\n'}
    files['README.md'] = {'content':f'''# HS-R01/R1 B-01 / A-01: native Windows originals

PR https://github.com/venomenon328/picross/pull/187 · Issue #186 V2.
Head `{manifest['head']}`, actual merge base parent `{manifest['base']}`,
CI event/selection base `{manifest['selection_base']}`,
tested merge `{manifest['checkout']}`, CI run `{manifest['run']}`.
ZIP SHA-256 `{manifest['sha256']}` ({manifest['bytes']} bytes).
EXE/PCK and Actions artifact digests: `manifest.json` and original binding report.

The ZIP contains unchanged Windows PNGs, logs and reports, no profiles/saves.
It uses lossless base64 transport in numbered parts; these are not edited images.
Download `download.py` from this **exact gist revision** and run:

```
python download.py <gist-id> <revision> windows-originals.zip
```

Anonymous download checks every part, the complete ZIP and each original file.
Inspect `hs186/` for eight fixed 900×480 swatches (40 PNGs), and `hf149/` for
the real main-scene window/tooltip originals (1280×720/UI125, 1920×1080/UI100,
2560×1440/UI125). The binding report explicitly separates Windows from Linux CI.
Independent technical review remains open. HS-M01 was personally granted for
the unchanged appearance; no new owner test or merge permission is claimed.
'''}
    response = subprocess.run(['gh','api','gists','--method','POST','--input','-'],
                              input=json.dumps(dict(description=f'picross HS Windows originals {manifest["head"]}',
                                                    public=False,files=files)).encode(),
                              capture_output=True,check=True,timeout=300)
    info = json.loads(response.stdout)
    revision = info['history'][0]['version']
    return dict(gist=info['id'],revision=revision,url=info['html_url']+'/'+revision,
                zip_sha256=manifest['sha256'],zip_bytes=manifest['bytes'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',required=True,type=Path)
    parser.add_argument('--zip',required=True,type=Path)
    parser.add_argument('--publish',action='store_true')
    args = parser.parse_args()
    manifest = package(args.directory,args.zip)
    args.zip.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    if args.publish:
        result = publish(args.zip,manifest)
        args.zip.with_suffix('.publication.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    else:
        print(manifest['sha256'],manifest['bytes'])
