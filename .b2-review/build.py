from pathlib import Path
import os, platform, sys, subprocess, zipfile, shutil
runner = Path(__file__).resolve().parent.parent
repo = runner / 'repo'
sys.path[:0] = [str(repo),str(repo/'tools')]
import p1_preflight as tc
import background_import
from product_fixtures import copy_regression_game
host=platform.system()
build=runner/'integration-build'
game=build/'game'
out=build/'export'
out.mkdir(parents=True)
shutil.copytree(repo/'game',game,ignore=shutil.ignore_patterns('.godot'))
background_import.prepare_import(game,background_import.source_inventory(repo))
cache=Path(os.environ['RUNNER_TEMP'])/'p1-toolchain-cache'
cache.mkdir(exist_ok=True)
editor=tc.EDITORS[host]
meta=tc.request_json(tc.RELEASE_API)
urls=tc.official_asset_urls(meta,(editor,tc.TEMPLATES))
for asset in (editor,tc.TEMPLATES):
    tc.download_asset(urls[asset.name],cache/asset.name,asset.sha256,1200)
engine=tc.extract_editor(cache/editor.name,build/'engine',host)
templates=tc.template_directory(build,host)
templates.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(cache/tc.TEMPLATES.name) as z:
    for name in ('web_nothreads_debug.zip','version.txt','windows_debug_x86_64.exe','windows_debug_x86_64_console.exe'):
        (templates/name).write_bytes(z.read('templates/'+name))
port = 18221 if host=='Windows' else 18211
with (game/'project.godot').open('a',encoding='utf8') as f:
    f.write(f'\n[picross]\nsync/api_base="http://127.0.0.1:{port}"\nsync/loopback_test=true\n[autoload]\nB2Observer="*res://book/b2_observer.gd"\n')
shutil.copyfile(Path(__file__).with_name('observer.gd'),game/'book/b2_observer.gd')
env=tc.isolated_environment(build,host)
env.pop('GITHUB_TOKEN',None)
preset,entry=('P1 Windows x86_64','picross.exe') if host=='Windows' else ('P1 Web','index.html')
for args in (['--import'],['--export-debug',preset,str(out/entry)]):
    with (build/'engine.log').open('wb') as log:
        subprocess.run([str(engine),'--headless','--path',str(game),*args],env=env,stdout=log,stderr=log,check=True)
    assert b'SCRIPT ERROR:' not in (build/'engine.log').read_bytes()
if host!='Windows':
    shutil.copyfile(game/'web/storage.js',out/'storage.js')
    html=out/entry
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    html.write_text(html.read_text().replace('./releases/@@BUILD@@/','./').replace('@@BUILD@@',head).replace('@@SHORT@@',head[:8]),encoding='utf8')
