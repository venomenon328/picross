import json,os,threading,http.server,functools,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
W=Path(__file__).resolve().parent;out=W/'worker-browser';server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(out)));threading.Thread(target=server.serve_forever,daemon=True).start()
report={'purpose':'T01 actual shipped worker decodes real Godot CTEX imports in Firefox; this is not the T03 book-rendering proof','source_head':'c6c4be5bb19fecc535a9a86c5ee4fa962a2c748e','cases':[]}
try:
 with sync_playwright() as pw:
  browser=pw.firefox.launch(executable_path='C:/Users/tobia/AppData/Local/ms-playwright/firefox-1509/firefox/firefox.exe',headless=True);page=browser.new_page();page.goto('http://127.0.0.1:'+str(server.server_port))
  for key,height in [('new',768),('legacy',576),('new',768)]:
   result=page.evaluate('''async ({key,height})=>{
     const bytes=new Uint8Array(await (await fetch(key+'.ctex')).arrayBuffer());let s='';for (const b of bytes)s+=String.fromCharCode(b);
     window.probeBridge ??= picrossBackgroundLoader.create();const bridge=probeBridge;const start=bridge.start(btoa(s),2304,height);if(start)throw new Error(start);
     for(let i=0;i<200 && bridge.poll()==='pending';i++)await new Promise(r=>setTimeout(r,25));
     if(bridge.poll()!=='loaded')throw new Error(bridge.error());const data=new Uint8Array(bridge.take());const base=data.slice(0,2304*height*4);
     const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',base))).map(b=>b.toString(16).padStart(2,'0')).join('');
     return {key,width:bridge.width(),height:bridge.height(),bytes:data.length,base_rgba_sha256:hash};
   }''',{'key':key,'height':height});assert result['bytes']==(9437176 if height==768 else 7077844);report['cases'].append(result);print(result,flush=True)
  page.evaluate('probeBridge.close()');report['firefox']=browser.version;browser.close()
finally:server.shutdown();server.server_close();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
