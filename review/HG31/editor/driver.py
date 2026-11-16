import sys,os,json,subprocess
from pathlib import Path
R=Path.cwd();W=R.parent;sys.path[:0]=[str(R),str(R/'tools')]
from tools.puzzle_editor.server import Service
from playwright.sync_api import sync_playwright
root=W/'editor-throughput';subprocess.run(['git','init','--quiet',str(root)],check=True);out=W/'editor-composition-final';out.mkdir(exist_ok=True);service=Service(root,temporary=W/'temp',state=W/'editor-settings');service.bind()
report={'source_head':'c6c4be5bb19fecc535a9a86c5ee4fa962a2c748e','cases':[]}
try:
 with sync_playwright() as pw:
  b=pw.firefox.launch(executable_path='C:/Users/tobia/AppData/Local/ms-playwright/firefox-1509/firefox/firefox.exe',headless=True)
  page=b.new_page(viewport={'width':1920,'height':1080});page.goto(service.url());page.locator('#row-pz-hg31-editor').click();page.locator('#form').wait_for(state='visible')
  for width,height,path in [(1920,1080,W/'ri-throughput/game/art/backgrounds/pz-hg31-new.png'),(1280,720,W/'ri-throughput/game/art/backgrounds/pz-hg31-new.png'),(1920,1080,W/'ri-throughput/game/art/backgrounds/pz-hg31-legacy.png')]:
   page.set_viewport_size({'width':width,'height':height});page.locator('#background-file').set_input_files(str(path));page.locator('#composition-background img').wait_for(state='visible');page.wait_for_timeout(250)
   page.locator('#composition').scroll_into_view_if_needed();page.wait_for_timeout(100);info=page.locator('#composition-background img').evaluate('(im)=>({width:im.naturalWidth,height:im.naturalHeight,rect:{x:im.getBoundingClientRect().x,y:im.getBoundingClientRect().y,width:im.getBoundingClientRect().width,height:im.getBoundingClientRect().height},opacity:getComputedStyle(im).opacity,box:im.parentElement.getBoundingClientRect().toJSON()})');assert abs(info['rect']['width']/info['rect']['height']-info['width']/info['height'])<.001
   name=f'editor-{width}x{height}-{info["height"]}.png';page.locator('#composition').screenshot(path=str(out/name));report['cases'].append({'capture':name,'viewport':[width,height],'image':info});print(name,info,flush=True)
  report['firefox']=b.version;b.close()
finally:
 service.close();(out/'protocol.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
