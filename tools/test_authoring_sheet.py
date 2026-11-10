"""MJ-A regressions against the real offline script; no browser or network.

The DOM is deliberately small. Image decoding is controlled here to test atomic
failure and asynchronous ordering; the one-off browser check covers real decode
and layout. ZIP contents are independently read with Python's standard library.
"""
import ast
import base64
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
from types import SimpleNamespace
import unittest
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / 'docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html'
RULEBOOKS = ('PUZZLE_AUTHORING.md', 'PUZZLE_AUTHORING_0_7_0_PREVIEW.md')


def png_chunk(kind, data):
    return (struct.pack('>I', len(data)) + kind + data +
            struct.pack('>I', zlib.crc32(kind + data)))


PNG = (b'\x89PNG\r\n\x1a\n' +
       png_chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)) +
       png_chunk(b'IDAT', zlib.compress(b'\x00\x29\x64\x4d\xff')) +
       png_chunk(b'IEND', b''))


class Form(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = {}
        self.select = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.elements[attrs['id']] = {
                'value': attrs.get('value', ''), 'tagName': tag.upper(),
                'attributes': attrs, 'options': [],
            }
        if tag == 'select':
            self.select = self.elements[attrs['id']]
        if tag == 'option' and self.select is not None:
            self.select['options'].append({'value': attrs['value']})
            if len(self.select['options']) == 1 or 'selected' in attrs:
                self.select['value'] = attrs['value']

    def handle_endtag(self, tag):
        if tag == 'select':
            self.select = None


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def producer_functions(path, names, context):
    """Execute actual pure producer functions without invoking a package build.

    Their imports would initialize unrelated production modules. Select the
    function ASTs, retaining their real bodies and using only their ordinary
    serialization/precondition helpers. No duplicate Sheet projection lives here.
    """
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in functions} != set(names):
        raise AssertionError('Missing actual producer functions: ' + str(names))
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, str(path), 'exec'), context)
    return context


def fixtures():
    """Small synthetic records made by record_for and sheet_from_record."""
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    context = producer_functions(
        ROOT / 'tools/puzzle_production/authoring_builder.py',
        {'record_for', 'sheet_from_record'},
        {'ap': SimpleNamespace(require=require),
         'io': SimpleNamespace(checksum=lambda value: hashlib.sha256(value).hexdigest()),
         'canonical_bytes': canonical,
         'digest': lambda value: hashlib.sha256(canonical(value)).hexdigest(),
         'UNSAVED': 'source: synthetic revision has not been committed'})
    reference = lambda file, digit: {'file': file, 'sha256': digit * 64, 'bytes': 42}
    stored = lambda file, digit: {
        'storage': 'package', 'root': 'background', 'ref': reference(file, digit)}
    binding = {
        'manifest': stored('work/bg01.json', 'a'), 'decision': None,
        'derivation': None, 'history': None,
    }
    options = [
        {'ID': f'bg-{index}', 'Beschreibung': f'Synthetic background {index}',
         'Datei': f'originals/bg-{index}.png', 'SHA-256': str(index) * 64,
         'Bildrevision': 'b01'}
        for index in range(1, 4)
    ]
    background = {
        'binding': binding, 'status': 'offered', 'options': options,
        'decision': None, 'ready': False, 'blockers': ['background: choice pending'],
    }
    h = {
        'puzzle_id': 'pz-synthetic-a', 'revision': 'r01', 'state': 'raster_ready',
        'repo_commit': 'd' * 40,
        'rulebook': {'version': '0.7.0', 'file': 'PICROSS_PUZZLE_AUTHORING.md',
                     'sha256': 'e' * 64},
        'inventory': {'sha256': 'f' * 64},
        'next_action': 'Review the three isolated background originals.',
        'blockers': [], 'content_blockers': [], 'reveal': None, 'motif': None,
    }
    request = {'handoff': h, 'category_id': None, 'document_revision': 5,
               'external': {}, 'reveal_options': []}
    inspection = {
        'format': 'picross-authoring-content-inspection-v1', 'technical': True,
        'editorial_approved': False, 'blockers': [], 'width': 10, 'height': 10,
        'mode': 'mono', 'used_colors': 1,
        # target_adapter.inspect supplies a nonnull bound difficulty object for
        # every technical result (its lines 351-363), unlike early phase records.
        'difficulty': {'method': 'picross-difficulty-0.1',
                       'assessment_type': 'editorial_estimate', 'level': 'L1',
                       'confidence': 'low', 'logic_hash': 'a' * 64,
                       'plausible_range': ['L1', 'L2'],
                       'rule_families': {'R1': 'Synthetic fixture, no production proof.'}},
        'effective_state': 'raster_ready', 'original_state': 'raster_ready',
        'integration_ready': False, 'background_ready': False,
    }
    directory = 'content/authoring/pz-synthetic-a/r01'
    record = context['record_for'](request, directory, b'synthetic ZIP', b'{}',
                                   inspection, background)
    sheet = context['sheet_from_record'](record, background)
    build = {'format': 'picross-authoring-build-result-v2', 'status': 'built',
             'directory': '/synthetic/repository/' + directory, 'indexed': True, 'record': record,
             'sheet': sheet, 'files': {
                 name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                 for name, raw in {'package.zip': b'synthetic ZIP',
                                   'handoff.json': b'{}',
                                   'record.json': canonical(record) + b'\n'}.items()}}
    local_request = deepcopy(request)
    local_request['handoff']['puzzle_id'] = 'pz-synthetic-local'
    local_request['handoff']['revision'] = 'r01.1'
    local_directory = 'pz-synthetic-local/r01.1'
    local_record = context['record_for'](
        local_request, local_directory, b'synthetic local ZIP', b'{}',
        inspection, background)
    local_build = {
        'format': 'picross-authoring-build-result-v2', 'status': 'built',
        'directory': '/synthetic/output/' + local_directory, 'indexed': False,
        'record': local_record, 'sheet': context['sheet_from_record'](local_record, background),
        'files': {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                  for name, raw in {'package.zip': b'synthetic local ZIP',
                                    'handoff.json': b'{}',
                                    'record.json': canonical(local_record) + b'\n'}.items()},
    }
    legacy_request = deepcopy(request)
    legacy_request['handoff']['state'] = 'content_ready'
    legacy_request['handoff']['rulebook']['version'] = '0.6.0'
    legacy_request['document_revision'] = 44
    legacy_inspection = {key: value for key, value in inspection.items()
                         if key not in ('effective_state', 'original_state',
                                        'integration_ready', 'background_ready')}
    legacy_record = context['record_for'](
        legacy_request, directory, b'synthetic old ZIP', b'{}', legacy_inspection)
    legacy_sheet = context['sheet_from_record'](legacy_record)
    final_context = producer_functions(
        ROOT / 'tools/puzzle_production/authoring_finalization.py', {'_proposed'},
        {'deepcopy': deepcopy, 'builder': SimpleNamespace(UNSAVED=context['UNSAVED']),
         'INTEGRATION': 'integration: background integration requires HP-I1b/HP-I2'})
    final_record = final_context['_proposed'](
        record, inspection, background,
        {name: None for name in ('approval.json', 'manual-authorization.json',
                                'owner-override.json', 'palette-exception.json')})
    final = {'format': 'picross-authoring-finalize-result-v1', 'status': 'updated',
             'record': final_record,
             'sheet': context['sheet_from_record'](final_record, background),
             'operation': reference(directory + '/finalization/op01/operation.json', 'c')}
    return {'record': record, 'sheet': sheet, 'build': build, 'final': final,
            'local_build': local_build,
            'legacy_record': legacy_record, 'legacy_sheet': legacy_sheet,
            'background': {'binding': binding, 'status': 'offered',
                           'options': options, 'selection': None},
            'png': base64.b64encode(PNG).decode('ascii')}


HARNESS = r"""
const fs = require('node:fs'), vm = require('node:vm');
const assert = require('node:assert/strict'), crypto = require('node:crypto');
const {File} = require('node:buffer');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const elements = {}, nodes = [], storage = new Map(), timers = new Map();
const downloads = [], objectURLs = new Map();
let timerId = 0, urlId = 0, decodeFailure = false, digestGate = null;
const plain = value => JSON.parse(JSON.stringify(value));
const clone = value => structuredClone(value);
const deferred = () => {let resolve, reject; const promise = new Promise((yes,no) => {resolve=yes;reject=no;}); return {promise,resolve,reject};};
const tick = () => new Promise(resolve => setImmediate(resolve));
function matches(el, selector) {
 if(selector.startsWith('#')) return el.id === selector.slice(1);
 if(selector.startsWith('.')) return el.className.split(/\s+/).includes(selector.slice(1));
 const attr = selector.match(/^\[([^=\]]+)(?:=["']?([^"'\]]+)["']?)?\]$/);
 if(attr) return el.hasAttribute(attr[1]) && (attr[2] === undefined || el.getAttribute(attr[1]) === attr[2]);
 return el.tagName === selector.toUpperCase();
}
class Element {
 constructor(tag='div', attrs={}) {
  this.tagName=tag.toUpperCase(); this.attributes={}; this.children=[]; this.parentNode=null;
  this.dataset={}; this.style={}; this.value=''; this.textContent=''; this.hidden=false;
  this.disabled=false; this.readOnly=false; this.open=false; this.checked=false;
  this.listeners=new Map(); this.className=''; this._options=[];
  this.classList={add:(...s)=>{this.className=[...new Set([...this.className.split(/\s+/),...s])].join(' ').trim();},
   remove:(...s)=>{this.className=this.className.split(/\s+/).filter(x=>!s.includes(x)).join(' ');},
   contains:s=>this.className.split(/\s+/).includes(s),
   toggle:(s,on)=>{const yes=on===undefined?!this.classList.contains(s):on;this.classList[yes?'add':'remove'](s);return yes;}};
  nodes.push(this); for(const [name,value] of Object.entries(attrs))this.setAttribute(name,value??'');
 }
 set id(value){if(this._id)delete elements[this._id]; this._id=value; if(value)elements[value]=this;}
 get id(){return this._id||'';}
 setAttribute(name,value){this.attributes[name]=String(value);if(name==='id')this.id=String(value);
  else if(name==='class')this.className=String(value);else if(name==='value')this.value=String(value);
  else if(name.startsWith('data-'))this.dataset[name.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=String(value);
  else if(['hidden','disabled','open','checked'].includes(name))this[name]=true;}
 getAttribute(name){if(name==='class')return this.className;if(name==='id')return this.id;
  if(name.startsWith('data-'))return this.dataset[name.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]??null;
  return Object.hasOwn(this.attributes,name)?this.attributes[name]:null;}
 hasAttribute(name){return this.getAttribute(name)!==null;}
 removeAttribute(name){delete this.attributes[name];if(['hidden','disabled','open','checked'].includes(name))this[name]=false;}
 append(...children){for(const child of children){if(typeof child==='string'){this.textContent+=child;continue;}this.children.push(child);child.parentNode=this;} }
 appendChild(child){this.append(child);return child;}
 replaceChildren(...children){for(const child of this.children)child.parentNode=null;this.children=[];this._options=[];this.append(...children);}
 remove(){if(this.parentNode)this.parentNode.children=this.parentNode.children.filter(x=>x!==this);this.parentNode=null;}
 get options(){return this.children.length?this.children.filter(x=>x.tagName==='OPTION'):this._options;}
 get selectedIndex(){return this.options.findIndex(x=>x.value===this.value);}
 set selectedIndex(index){this.value=this.options[index]?.value??'';}
 set innerHTML(value){this.replaceChildren();const stack=[this];for(const token of value.match(/<[^>]+>|[^<]+/g)||[]){
  if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}
  if(token.startsWith('<')){const match=token.match(/^<([\w-]+)([^>]*)>/);if(!match)continue;
   const attrs={};for(const a of match[2].matchAll(/([\w-]+)(?:="([^"]*)"|'([^']*)')?/g))attrs[a[1]]=a[2]??a[3]??'';
   const child=new Element(match[1],attrs);stack.at(-1).append(child);
   if(!['br','input','img','hr','meta','link'].includes(match[1])&&!token.endsWith('/>'))stack.push(child);
  }else stack.at(-1).textContent+=token;
 }}
 get innerHTML(){return this.children.map(x=>x.textContent).join('');}
 querySelectorAll(selector){const found=[];const walk=el=>{for(const child of el.children){if(matches(child,selector))found.push(child);walk(child);}};walk(this);return found;}
 querySelector(selector){return this.querySelectorAll(selector)[0]??null;}
 addEventListener(type,callback){if(!this.listeners.has(type))this.listeners.set(type,[]);this.listeners.get(type).push(callback);}
 async emit(type,extra={}){const event={target:this,currentTarget:this,preventDefault(){},...extra};for(const cb of this.listeners.get(type)||[])await cb(event);}
 click(){if(this.download&&this.href){downloads.push({name:this.download,blob:objectURLs.get(this.href)});return;}return this.emit('click');}
 focus(){document.activeElement=this;} select(){} scrollIntoView(){}
}
for(const [id,value] of Object.entries(input.elements)){
 const el=new Element(value.tagName,value.attributes);el.id=id;el.value=value.value;
 el._options=value.options.map(o=>({value:o.value}));el.textContent=value.textContent??'';
}
const body=new Element('body');
const document={getElementById:id=>elements[id]??null,documentElement:{dataset:{}},body,
 createElement:tag=>new Element(tag),querySelectorAll:selector=>nodes.filter(el=>matches(el,selector)),
 querySelector:selector=>nodes.find(el=>matches(el,selector))??null,
 addEventListener(){},execCommand:()=>true,createRange:()=>({selectNodeContents(){}})};
class Reader {
 readAsDataURL(blob){blob.arrayBuffer().then(raw=>{this.result='data:'+blob.type+';base64,'+Buffer.from(raw).toString('base64');this.onload?.();},()=>this.onerror?.());}
}
class ImageStub {
 set src(value){queueMicrotask(()=>{if(decodeFailure){this.onerror?.();return;}
  const data=Buffer.from(value.slice(value.indexOf(',')+1),'base64');
  if(data.length<24){this.onerror?.();return;}
  this.naturalWidth=data.readUInt32BE(16);this.naturalHeight=data.readUInt32BE(20);this.onload?.();});}
}
const sandbox={structuredClone,document,Blob,File,FileReader:Reader,Image:ImageStub,
 TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,DataView,Buffer,
 atob: value=>Buffer.from(value,'base64').toString('binary'),btoa:value=>Buffer.from(value,'binary').toString('base64'),
 localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,String(value)),removeItem:key=>storage.delete(key)},
 setTimeout:(callback,ms)=>{const id=++timerId;timers.set(id,{callback,ms});return id;},clearTimeout:id=>timers.delete(id),
 confirm:()=>true,navigator:{clipboard:{writeText:async()=>{}}},
 window:{matchMedia:()=>({matches:false,addEventListener(){}}),getSelection:()=>({removeAllRanges(){},addRange(){}})},
 URL:{createObjectURL:blob=>{const url='blob:synthetic-'+(++urlId);objectURLs.set(url,blob);return url;},revokeObjectURL:url=>objectURLs.delete(url)},
 crypto:{randomUUID:crypto.randomUUID,subtle:{digest:async (algorithm,bytes)=>{if(digestGate)await digestGate.promise;return crypto.webcrypto.subtle.digest(algorithm,bytes);}}},
 console:{log(){}}, fixtures:clone(input.fixtures),
};
sandbox.globalThis=sandbox;
vm.createContext(sandbox);
const run=code=>vm.runInContext(code,sandbox,{timeout:5000});
run(input.script);
const set=(id,value)=>{assert.ok(elements[id],'missing actual HTML element '+id);elements[id].value=value;};
const edit=(id,value)=>{set(id,value);run('jobChanged('+JSON.stringify(id)+')');};
const snapshot=()=>plain(run('snapshotWorkspace()'));
const pngFile=()=>new File([Buffer.from(input.fixtures.png,'base64')],'synthetic.png',{type:'image/png'});
async function importValue(value,target){sandbox.incoming=clone(value);sandbox.importTarget=target??run('activeJobId');await run('stageTransfer(incoming,importTarget)');assert.equal(run('applyTransfer()'),true);}
async function exported(){return Promise.all(downloads.map(async item=>({name:item.name,bytes:Buffer.from(await item.blob.arrayBuffer()).toString('base64')})));}
(async()=>{
 const result=await (async()=>{__SCENARIO__})();
 process.stdout.write(JSON.stringify({ok:true,result:result??null}));
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
"""


class AuthoringSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = SHEET.read_text(encoding='utf-8')
        form = Form()
        form.feed(cls.html)
        for identifier, content in re.findall(
                r'<script type="application/json" id="([^"]+)">(.*?)</script>',
                cls.html, re.S):
            form.elements[identifier]['textContent'] = content
        cls.elements = form.elements
        cls.script = re.search(r'<script>\s*(.*?)</script>', cls.html, re.S)[1]
        cls.fixture = fixtures()
        cls.node = shutil.which('node')
        if cls.node is None:
            raise AssertionError('tools authoring regression requires Node; no silent skip')

    def javascript(self, scenario):
        result = subprocess.run([self.node, '-e', HARNESS.replace('__SCENARIO__', scenario)],
                                input=json.dumps({'elements': self.elements,
                                                  'script': self.script,
                                                  'fixtures': self.fixture}),
                                capture_output=True, text=True, encoding='utf-8',
                                timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed['ok'])
        return parsed['result']

    def test_both_rulebook_snapshots_are_exact_source_bytes(self):
        embedded = [json.loads(content).encode('utf-8') for content in re.findall(
            r'<script type="application/json" id="[^"]+">(.*?)</script>', self.html, re.S)]
        for name in RULEBOOKS:
            with self.subTest(rulebook=name):
                original = (ROOT / 'docs/ai-workflows' / name).read_bytes()
                self.assertEqual(embedded.count(original), 1)

    def test_actual_step_four_default_fallback_attachment_and_saved_ref(self):
        authoring = (ROOT / 'docs/ai-workflows' / RULEBOOKS[0]).read_bytes()
        result = self.javascript(r"""
assert.equal(elements.ruleSource.value,'repo');assert.equal(elements.ruleRef.value,'main');
set('workspaceRoot','E:\\Picross-work');
edit('packagePath','content/authoring/pz-synthetic-a/r01/package.zip');
edit('revision','r01');edit('inventoryRef','a'.repeat(64));
const normal=run("prompt(CARDS.find(c=>c.id==='integrate'))");
assert.deepEqual(Array.from(normal.missing),[]);
assert.match(normal.text,/AGENTS\.md aus dem beauftragten Stand main /);
assert.match(normal.text,/Arbeite nach docs\/ai-workflows\/PUZZLE_AUTHORING\.md aus demselben Stand/);
assert.match(normal.text,/Standardauftrag 4/);
assert.equal(run("brief(CARDS.find(c=>c.id==='integrate')).rulebook.repo_ref"),'main');
set('ruleRef','');set('rulePath','');
assert.match(run('prefix()'),/Stand main /);
assert.equal(run('brief(CARDS[3]).rulebook.file'),'docs/ai-workflows/PUZZLE_AUTHORING.md');
set('ruleRef','feat/479-ri-b-verified-context');set('rulePath','docs/ai-workflows/PUZZLE_AUTHORING.md');
run('setJobDefaults()');set('ruleRef','main');run('loadSettings();createJob()');
assert.equal(elements.ruleRef.value,'feat/479-ri-b-verified-context');
assert.match(run('prompt(CARDS[3]).text'),/Stand feat\/479-ri-b-verified-context /);
set('ruleSource','attachment');
assert.equal(run('brief(CARDS[3]).rulebook.version'),'0.6.0');
assert.throws(()=>run("parseTransfer({format:'picross-background-adoption-request-v1'})"),/Eigenständige Hintergrundrevision|HP-I1b2/);
return {text:run('prompt(CARDS[3]).text'),rulebook:run('RULEBOOK'),revision:run('brief(CARDS[3]).rulebook.document_revision')};
""")
        revision = int(re.search(rb'Dokumentrevision (\d+)', authoring)[1])
        self.assertEqual(result['rulebook'].encode('utf-8'), authoring)
        self.assertEqual(result['revision'], revision)
        self.assertRegex(result['text'], rf'PICROSS_PUZZLE_AUTHORING.md .*Dokumentrevision {revision}')

    def test_real_producer_pairs_and_closed_new_contracts(self):
        self.javascript(r"""
assert.equal(run('parseTransferData(fixtures.record).needsSheet'),true);
for(const family of ['build','final'])for(const status of family==='build'?['built','reused']:['updated','reused']){
 sandbox.envelope=clone(input.fixtures[family]);sandbox.envelope.status=status;
 const result=run('parseTransferData(envelope)');assert.equal(result.family,5);
 assert.deepEqual(plain(result.record),sandbox.envelope.record);
 assert.deepEqual(plain(result.background),input.fixtures.background);
 assert.equal(result.values.puzzleId,'pz-synthetic-a');assert.equal(result.values.productionState,'raster_ready');
}
assert.equal(run('parseTransferData(fixtures.sheet).family'),5);
assert.equal(run('parseTransferData(fixtures.legacy_record).family'),4);
assert.equal(run('parseTransferData(fixtures.legacy_sheet).family'),4);
sandbox.old=clone(input.fixtures.legacy_sheet);sandbox.old.format='picross-cheatsheet-update-v1';
for(const key of ['Abschlussbild-Optionen','Raster-Optionen','Rastervariante'])delete sandbox.old[key];
assert.equal(run('parseTransferData(old).family'),4);
const mutate=[
 x=>x.sheet['Rätsel-ID']='pz-other',x=>x.sheet.Paketrevision='r02',
 x=>x.sheet.Paketpfad='content/authoring/pz-synthetic-a/r02/package.zip',
 x=>x.sheet['Inventar-SHA-256']='a'.repeat(64),x=>x.sheet.Produktionsstatus='content_ready',
 x=>x.sheet['Quellbranch / Commit']='c'.repeat(40),x=>x.sheet.PR='https://github.com/venomenon328/picross/pull/1',
 x=>x.sheet.Hintergrunddaten.manifest.ref.sha256='9'.repeat(64),
 x=>x.sheet.unexpected=true,x=>x.record.unexpected=true,x=>x.unexpected=true,
 x=>x.status='invalid_input',x=>x.record.package.bytes=-1,
];
for(const change of mutate){sandbox.bad=clone(input.fixtures.build);change(sandbox.bad);assert.throws(()=>run('parseTransferData(bad)'));}
for(const raw of ['{"format":"x","format":"y"}','{"a":1,"\\u0061":2}','{"a":{"b":1,"b":2}}','{"a":1e400}']){
 sandbox.raw=raw;assert.throws(()=>run('strictJsonParse(raw)'));
}
assert.deepEqual(plain(run('strictJsonParse(\'{"a":[1,true,null,"é"]}\')')),{a:[1,true,null,'é']});
for(const label of ['3 · Rätsel produzieren','4 · Hintergrundbereitschaft klären und Rätsel abnehmen',
 '4 · Rätsel abnehmen; finale Hintergrundintegration benötigt HP-I1/HP-I2',
 'Finale Integration nach verfügbarer HP-I1/HP-I2-Unterstützung',
 '4 · Rätsel abnehmen; finale Hintergrundintegration benötigt HP-I1b/HP-I2',
 'Finale Integration nach verfügbarer HP-I1b/HP-I2-Unterstützung']){
 sandbox.label=label;const id=run('STEP_IDS[label]');assert.ok(id,label);
 sandbox.cardId=id;assert.ok(run('CARDS.some(card=>card.id===cardId)'),label);
}
const before=snapshot();assert.equal(await run('stageTransfer(fixtures.record)'),false);
assert.deepEqual(snapshot(),before);assert.equal(run('pendingTransfer'),null);
assert.match(elements.transferPreview.textContent,/Ergänzung erforderlich/);
sandbox.companion=new File([JSON.stringify(input.fixtures.sheet)],'sheet.json',{type:'application/json'});
await run('loadCompanion(companion)');assert.equal(run('applyTransfer()'),true);
assert.deepEqual(snapshot().jobs[0].record,input.fixtures.record);
""")

    def test_background_history_intent_and_null_are_distinct(self):
        self.javascript(r"""
for(const status of [null,'legacy']){
 sandbox.bg={binding:null,status,options:[],selection:null};assert.deepEqual(plain(run('validateBackground(bg,{intent:true})')),sandbox.bg);
 sandbox.bg.selection='none';assert.throws(()=>run('validateBackground(bg,{intent:true})'));
}
sandbox.bg=clone(input.fixtures.background);sandbox.bg.selection='bg-2';
assert.equal(run('validateBackground(bg,{intent:true}).selection'),'bg-2');
assert.throws(()=>run('validateBackground(bg)'));
sandbox.bg.selection='none';assert.equal(run('validateBackground(bg,{intent:true}).status'),'offered');
sandbox.bg.selection='foreign';assert.throws(()=>run('validateBackground(bg,{intent:true})'));
for(const status of ['pending','rejected','selected','none']){
 const bg=clone(input.fixtures.background);bg.status=status;
 if(status==='pending'){bg.options=[];bg.selection=null;}
 else{bg.binding.decision={storage:'package',root:'background',ref:{file:'decisions/d01.json',sha256:'6'.repeat(64),bytes:42}};
  bg.selection=status==='selected'?'bg-1':status==='none'?'none':null;}
 sandbox.bg=bg;assert.deepEqual(plain(run('validateBackground(bg)')),bg);
}
sandbox.bg=clone(input.fixtures.background);sandbox.bg.binding.derivation={storage:'package',root:'background',ref:{file:'derived/report.json',sha256:'8'.repeat(64),bytes:42}};
assert.throws(()=>run('validateBackground(bg)'));
for(const change of [x=>x.options[0].ID='none',x=>x.options.push(clone(x.options[0])),x=>x.options[0]['SHA-256']='bad',x=>x.options[0].Datei='../escape.png',x=>x.extra=true]){
 sandbox.bg=clone(input.fixtures.background);change(sandbox.bg);assert.throws(()=>run('validateBackground(bg,{intent:true})'));
}
await importValue(input.fixtures.sheet);const stable=snapshot();
for(const change of [
 session=>session.fields.productionState='content_ready',
 session=>session.fields.productionState='editorially_approved',
 session=>session.fields.productionState='invented-ready-state',
 session=>{session.fields.puzzleId='';session.fields.packagePath='';},
]){
 sandbox.badSession=clone(stable.jobs[0].session);change(sandbox.badSession);
 await assert.rejects(run('stageTransfer(badSession)'));
 assert.deepEqual(snapshot(),stable,'session-v5 must check phase/background projection too');
}
""")


    def test_ten_jobs_roundtrip_preserves_options_attachments_and_setup(self):
        self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');set('cleanupMode','off');run("theme='dark';showTheme();saveSettings()");
const personal=plain(run('settingsSnapshot()')), savedDefaults=[...storage];
const ids=[];
for(let index=0;index<10;index++){
 if(index)run('createJob()');
 const id=run('activeJobId');ids.push(id);assert.match(id,/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/);
 edit('motif','Synthetic motif '+index);
 if(index)edit('puzzleId','pz-synthetic-'+index);
 edit('productionState',['brief_ready','reveal_review','content_ready'][index%3]);
 set('repoSave',index%2?'local':'repo');await elements.repoSave.emit('change');
 set('mergeMode',index%2?'draft':'merge');await elements.mergeMode.emit('change');
 set('ruleRef','work/synthetic-'+index);await elements.ruleRef.emit('change');
 if(index===2){edit('imageRole','motif');sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);}
}
assert.equal(new Set(ids).size,10);
const before=snapshot();assert.equal(before.jobs.length,10);
assert.equal(before.jobs[0].session.fields.puzzleId,'');
assert.equal(new Set(before.jobs.map(j=>j.session.fields.productionState)).size,3);
assert.deepEqual([...storage],savedDefaults,'job options must not rewrite personal defaults');
for(let index=0;index<10;index++){
 sandbox.id=ids[index];run('switchJob(id)');
 assert.equal(elements.motif.value,'Synthetic motif '+index);
 assert.equal(elements.ruleRef.value,'work/synthetic-'+index);
 assert.equal(elements.repoSave.value,index%2?'local':'repo');
 assert.equal(run('source?.name??null'),index===2?'synthetic.png':null);
 if(index===2)assert.equal(elements.imageRole.value,'motif');
}
sandbox.id=ids[2];run('switchJob(id)');
const original=snapshot(), inactive=clone(original.jobs.filter(j=>j.job_id!==ids[2]));
sandbox.incoming=clone(original);await run('stageTransfer(incoming)');
assert.match(elements.transferPreview.textContent,/repo|local/);
assert.match(elements.transferPreview.textContent,/draft|merge/);
assert.match(elements.transferPreview.textContent,/work\/synthetic-2/);
run('discardTransfer()');assert.deepEqual(snapshot(),original);
await importValue(original);
assert.deepEqual(snapshot(),original,'collection roundtrip includes order, active job, bytes and options');
assert.deepEqual(plain(run('settingsSnapshot()')),personal);
assert.equal(elements.workspaceRoot.value,'/home/synthetic/picross');assert.equal(elements.cleanupMode.value,'off');
assert.equal(document.documentElement.dataset.theme,'dark');
run('resetJob()');const reset=snapshot();assert.equal(reset.active_job_id,ids[2]);
assert.deepEqual(reset.jobs.filter(j=>j.job_id!==ids[2]),inactive);
assert.equal(reset.jobs.find(j=>j.job_id===ids[2]).session.image,null);
run('removeJob()');assert.equal(snapshot().jobs.length,9);
assert.deepEqual(snapshot().jobs,inactive);
""")

    def test_atomic_imports_legacy_sessions_and_conflicting_collection(self):
        self.javascript(r"""
edit('motif','unexported briefing');const first=run('activeJobId');
set('mergeMode','draft');await elements.mergeMode.emit('change');
set('ruleRef','work/retained');await elements.ruleRef.emit('change');
const options=clone(snapshot().jobs[0].options);
await importValue(input.fixtures.legacy_sheet);
assert.equal(run('activeJobId'),first);assert.equal(elements.puzzleId.value,'pz-synthetic-a');
assert.deepEqual(snapshot().jobs[0].options,options);
const withID=snapshot();
sandbox.bad=clone(input.fixtures.legacy_sheet);sandbox.bad['Rätsel-ID']='pz-other';
sandbox.bad.Paketpfad='content/authoring/pz-other/r01/package.zip';
await assert.rejects(run('stageTransfer(bad)'),/ID|Produktion|Job/);assert.deepEqual(snapshot(),withID);
await assert.rejects(run("stageTransfer(fixtures.legacy_sheet,'new')"),/ID|Produktion|Job/);
assert.deepEqual(snapshot(),withID);
sandbox.next=clone(input.fixtures.legacy_sheet);sandbox.next.Paketrevision='r02';
sandbox.next.Paketpfad='content/authoring/pz-synthetic-a/r02/package.zip';
await run('stageTransfer(next)');assert.match(elements.transferPreview.textContent,/r02/);
assert.deepEqual(snapshot(),withID,'staging itself must not alter the job');
assert.equal(run('applyTransfer()'),true);assert.equal(elements.revision.value,'r02');
run('createJob()');edit('motif','unrelated job');const stable=snapshot();
const cases=[
 x=>x.unexpected=true,x=>x.format='picross-cheatsheet-workspace-v2',
 x=>x.jobs[1].job_id=x.jobs[0].job_id,
 x=>x.jobs[1].session.fields.puzzleId=x.jobs[0].session.fields.puzzleId,
 x=>x.active_job_id='not-present',x=>x.jobs[0].options.workspaceRoot='/foreign/root',
 x=>x.jobs[0].options.mergeMode='silently-authorized',
 x=>x.jobs[0].session.fields.extra='unknown',
 x=>x.jobs[0].session.image={name:'bad.png',dataUrl:'data:image/png;base64,AAAA'},
];
for(const change of cases){
 sandbox.bad=clone(stable);change(sandbox.bad);
 await assert.rejects(run('stageTransfer(bad)'));
 assert.deepEqual(snapshot(),stable,'bad collection may not partly replace jobs');
}
sandbox.badJSON=new File(['{"format":"picross-cheatsheet-workspace-v1","format":"other"}'],'duplicate.json',{type:'application/json'});
assert.equal(await run('loadImportFile(badJSON)'),false);
assert.match(elements.transferPreview.textContent,/Doppelter JSON-Schlüssel/);
assert.deepEqual(snapshot(),stable,'file import must use the duplicate-aware parser too');
// All structural checks precede any decode: an invalid later job rejects with
// the live decoder deliberately held; it must never start that costly work.
sandbox.bad=clone(stable);sandbox.bad.jobs[0].session.image={name:'valid.png',dataUrl:'data:image/png;base64,'+input.fixtures.png};
sandbox.bad.jobs[1].job_id=sandbox.bad.jobs[0].job_id;
let decodes=0;const originalImage=sandbox.Image;
sandbox.Image=class {set src(_){decodes++;}};
await assert.rejects(run('validateWorkspace(bad)'));assert.equal(decodes,0);sandbox.Image=originalImage;
const blank=clone(stable.jobs[1].session);
for(const generation of [1,2,3,4]){
 const old=clone(blank);old.format='picross-cheatsheet-session-v'+generation;
 if(generation<3)delete old.choices;
 if(generation<4){delete old.fields.colorPolicy;delete old.fields.repoRef;}
 sandbox.old=old;const before=snapshot();
 await run('stageTransfer(old)');run('discardTransfer()');assert.deepEqual(snapshot(),before);
 await importValue(old);const loaded=snapshot().jobs.find(j=>j.job_id===run('activeJobId'));
 assert.equal(loaded.session.format,'picross-cheatsheet-session-v4');
 assert.deepEqual(loaded.options,before.jobs.find(j=>j.job_id===before.active_job_id).options);
 assert.ok(!Object.hasOwn(loaded.session,'background'));
}
const empty={format:'picross-cheatsheet-workspace-v1',active_job_id:null,jobs:[]};
await importValue(empty);assert.deepEqual(snapshot(),empty);
run('createJob()');assert.equal(snapshot().jobs.length,1);
""")

    def test_invalid_decode_and_stale_import_preview_are_atomic(self):
        self.javascript(r"""
edit('motif','A');const a=run('activeJobId');run('createJob()');edit('motif','B');
const b=run('activeJobId');sandbox.a=a;run('switchJob(a)');
sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
const before=snapshot(), imageBefore=plain(run('source'));
let invalid=clone(before.jobs.find(j=>j.job_id===a).session);
invalid.image={name:'new.png',dataUrl:'data:image/png;base64,'+input.fixtures.png};
sandbox.incoming=invalid;decodeFailure=true;
await assert.rejects(run('stageTransfer(incoming)'));decodeFailure=false;
assert.deepEqual(snapshot(),before);assert.deepEqual(plain(run('source')),imageBefore);
await run('stageTransfer(fixtures.legacy_sheet)');
sandbox.b=b;run('switchJob(b)');run('switchJob(a)');
assert.equal(run('applyTransfer()'),false);assert.deepEqual(snapshot(),before);
await run('stageTransfer(fixtures.legacy_sheet)');
edit('motif','A changed after preview');const changed=snapshot();
assert.equal(run('applyTransfer()'),false);assert.deepEqual(snapshot(),changed);
await run('stageTransfer(fixtures.legacy_sheet)');run('resetJob()');
const reset=snapshot();assert.equal(run('applyTransfer()'),false);assert.deepEqual(snapshot(),reset);
await run('stageTransfer(fixtures.legacy_sheet)');run('removeJob()');
const removed=snapshot();assert.equal(run('applyTransfer()'),false);assert.deepEqual(snapshot(),removed);
""")

    def test_actual_zip_inventory_bytes_and_versioned_rulebooks(self):
        result = self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');
edit('puzzleId','pz-zip-old');edit('motif','Old job only');set('ruleSource','attachment');run('optionChanged()');
edit('imageRole','motif');sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
await run("exportPackage(CARDS.find(c=>c.id==='start'))");
await importValue(input.fixtures.sheet,'new');
set('ruleSource','attachment');run('optionChanged()');
set('rulePath','docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md');run('optionChanged()');
edit('motif','New background job only');
await run("exportPackage(CARDS.find(c=>c.id==='start'))");
assert.equal(downloads.length,2);
return exported();
""")
        self.assertEqual(len(result), 2)
        for index, item in enumerate(result):
            with self.subTest(generation=index):
                raw = base64.b64decode(item['bytes'])
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))
                    inventory = json.loads(archive.read('dateien.json'))
                    self.assertEqual(inventory['format'], 'picross-request-files-v1')
                    entries = {row['file']: row for row in inventory['files']}
                    self.assertEqual(set(entries), set(archive.namelist()) - {'dateien.json'})
                    for name, binding in entries.items():
                        original = archive.read(name)
                        self.assertEqual(len(original), binding['bytes'])
                        self.assertEqual(hashlib.sha256(original).hexdigest(), binding['sha256'])
                    request = json.loads(archive.read('brief.json'))
                    self.assertEqual(request['format'], 'picross-authoring-request-v' + str(3 + index))
                    self.assertEqual(request['requested_step'], 'start')
                    self.assertEqual(request['prompt_file'], 'auftrag.md')
                    self.assertEqual(request['rulebook']['version'], ('0.6.0', '0.7.0')[index])
                    self.assertEqual(archive.read('PICROSS_PUZZLE_AUTHORING.md'),
                                     (ROOT / 'docs/ai-workflows' / RULEBOOKS[index]).read_bytes())
                    if index == 0:
                        self.assertEqual(request['fields']['puzzleId'], 'pz-zip-old')
                        self.assertEqual(archive.read('motif/abstracted.png'), PNG)
                        self.assertEqual(request['input_image']['role'], 'motif')
                        self.assertNotIn('background', request)
                    else:
                        self.assertEqual(request['fields']['puzzleId'], 'pz-synthetic-a')
                        self.assertEqual(request['background'], self.fixture['background'])
                        self.assertEqual(request['input_image'], None)
                        self.assertNotIn(b'Old job only', archive.read('auftrag.md'))
                self.assertIn(('pz-zip-old', 'pz-synthetic-a')[index], item['name'])

    def test_background_choice_record_retention_and_rule_conflict(self):
        self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');
await importValue(input.fixtures.build);const a=run('activeJobId');sandbox.a=a;
assert.deepEqual(snapshot().jobs[0].record,input.fixtures.record);
assert.match(elements.jobBlockers.textContent,/background: choice pending/);
assert.match(elements.jobBlockers.textContent,/nicht frisch geprüft/);
assert.equal(run("choiceBlock(CARDS.find(c=>c.id==='integrate'))").length>0,true);
edit('imageRole','reveal');sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
const image=plain(run('source')), oldBinding=clone(input.fixtures.background.binding);
run("chooseBackground('bg-2')");
assert.deepEqual(plain(run('source')),image,'background intent must not clear the independent role attachment');
assert.deepEqual(plain(run('background.binding')),oldBinding);
assert.equal(run('background.status'),'offered');assert.equal(run('background.selection'),'bg-2');
assert.deepEqual(snapshot().jobs[0].record,input.fixtures.record,'intent does not forge or rewrite historical source record');
assert.equal(run("choiceBlock(CARDS.find(c=>c.id==='integrate'))"),'');
const text=run("prompt(CARDS.find(c=>c.id==='integrate')).text");
assert.match(text,/bg-2/);assert.match(text,new RegExp('2'.repeat(64)));
assert.match(text,/Endabnahme/);assert.match(text,/keine zweite gleichlautende Bildbestätigung/);
run('createJob()');const b=run('activeJobId');run('switchJob(a)');
assert.equal(run('background.selection'),'bg-2');assert.deepEqual(plain(run('source')),image);
edit('inventoryRef','9'.repeat(64));assert.equal(snapshot().jobs.find(j=>j.job_id===a).record,null);
const afterEdit=snapshot();sandbox.incoming=afterEdit;await run('validateWorkspace(incoming)');
// A newly imported material revision has its own open intent; no implicit
// transfer of the previous selection or proof into the changed manifest.
const changed=clone(input.fixtures.sheet);changed.Paketrevision='r02';
changed.Paketpfad='content/authoring/pz-synthetic-a/r02/package.zip';
changed.Hintergrunddaten.manifest.ref.sha256='7'.repeat(64);
await importValue(changed);assert.equal(run('background.selection'),null);
assert.equal(run('background.status'),'offered');
// A declaration reference may already represent a valid administrative
// carried_from continuation. The Sheet preserves it; it cannot re-read its bytes.
const carried=clone(changed);carried.Hintergrundstatus='selected';carried.Hintergrundauswahl='bg-1';
carried.Hintergrunddaten.decision={storage:'external',root:'content/authoring/pz-synthetic-a/r02/background',ref:{file:'decisions/d02-carried.json',sha256:'8'.repeat(64),bytes:85}};
carried.Hintergrunddaten.history={commit:'b'.repeat(40),storage:'directory',path:'content/authoring/pz-synthetic-a/r01',root:'background'};
await importValue(carried);
assert.deepEqual(snapshot().jobs.find(j=>j.job_id===a).session.background.binding,carried.Hintergrunddaten);
assert.equal(run("choiceBlock(CARDS.find(c=>c.id==='integrate'))"),'');
run('switchJob('+JSON.stringify(b)+')');run('switchJob(a)');
assert.equal(run('background.selection'),'bg-1');
const pending=clone(changed);pending.Hintergrundstatus='pending';pending['Hintergrund-Optionen']=[];
await importValue(pending);run("chooseBackground('none')");
const early=run("prompt(CARDS.find(c=>c.id==='background-decide')).text");
assert.match(early,/verzichte.*drei Kandidaten/);
assert.equal(run('background.status'),'pending');assert.equal(run('background.binding.decision'),null);
// Import preserves job options. An old input must surface the remaining 0.7
// rule path, and no ZIP may escape until the user makes the compatible choice.
await importValue(input.fixtures.legacy_sheet);
assert.equal(snapshot().jobs.find(j=>j.job_id===a).session.format,'picross-cheatsheet-session-v4');
assert.equal(elements.rulePath.value,'docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md');
assert.ok(run("settingsBlock(CARDS.find(c=>c.id==='start'))"));
assert.match(elements.ruleCollision.textContent,/0\.6/);
await run("exportPackage(CARDS.find(c=>c.id==='start'))");assert.equal(downloads.length,0);
run('useCompatibleRule()');assert.equal(run("settingsBlock(CARDS.find(c=>c.id==='start'))"),'');
assert.equal(elements.rulePath.value,'docs/ai-workflows/PUZZLE_AUTHORING.md');
""")

    def test_raster_selection_moves_its_matching_package_binding(self):
        self.javascript(r"""
const sheet=clone(input.fixtures.sheet), fields=run('Object.keys(RASTER_FIELDS)');
const option=(id,revision)=>({
 ID:id,Beschreibung:'Synthetic raster '+id,Rasterdatei:'rasters/'+id+'.png',Kandidat:'candidate-'+id,Schwierigkeit:'L2',
 Paketrevision:revision,Paketpfad:'content/authoring/pz-synthetic-a/'+revision+'/package.zip',
 'Inventar-SHA-256':(id==='a'?'a':'b').repeat(64),'Quellbranch / Commit':'work/synthetic',PR:null,
 Rasterbreite:10,Rasterhöhe:10,Rätselmodus:'Monochrom','Verwendete Farben':1,
 Abschlussbild:'reveal/selected.png',Motivvorlage:'motif/abstracted.png',Parameterkorridor:'Synthetic approved corridor',
 Hintergrunddaten:clone(sheet.Hintergrunddaten),Produktionsstatus:'raster_ready'
});
sheet['Raster-Optionen']=[option('a','r01'),option('b','r02')];sheet.Rastervariante='a';
const ref=sheet['Raster-Optionen'][1].Hintergrunddaten.manifest.ref;
sheet['Raster-Optionen'][1].Hintergrunddaten.manifest.ref={bytes:ref.bytes,sha256:ref.sha256,file:ref.file};
for(const key of fields)sheet[key]=sheet['Raster-Optionen'][0][key];
await importValue(sheet);run("chooseBackground('bg-3')");
const oldBinding=plain(run('background.binding'));
assert.equal(run("chooseVariant('raster','b')"),true);
assert.equal(elements.revision.value,'r02');
assert.equal(elements.packagePath.value,'content/authoring/pz-synthetic-a/r02/package.zip');
assert.equal(elements.inventoryRef.value,'b'.repeat(64));
assert.deepEqual(plain(run('background.binding')),oldBinding);assert.equal(run('background.selection'),'bg-3');
const saved=snapshot();sandbox.incoming=saved;await run('validateWorkspace(incoming)');
await importValue(saved);assert.deepEqual(snapshot(),saved);
""")

    def test_actual_local_producer_session_and_zip_roundtrip(self):
        result = self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');
await importValue(input.fixtures.local_build);
assert.equal(elements.packagePath.value,'pz-synthetic-local/r01.1/package.zip');
assert.equal(elements.revision.value,'r01.1');
edit('imageRole','source');sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
set('repoSave','local');await elements.repoSave.emit('change');
set('mergeMode','draft');await elements.mergeMode.emit('change');
run('saveSession()');assert.equal(downloads.length,1);
const saved=JSON.parse(await downloads[0].blob.text());
assert.equal(saved.format,'picross-cheatsheet-session-v5');
run('resetJob()');await importValue(saved);
const current=snapshot().jobs.find(j=>j.job_id===run('activeJobId'));
assert.deepEqual(current.session,saved,'actual downloaded single session must roundtrip');
run('saveWorkspace()');assert.equal(downloads.length,2);
const collection=JSON.parse(await downloads[1].blob.text());
await importValue(collection);assert.deepEqual(snapshot(),collection);
await run("exportPackage(CARDS.find(c=>c.id==='start'))");
assert.equal(downloads.length,3);return exported();
""")
        session = json.loads(base64.b64decode(result[0]['bytes']))
        collection = json.loads(base64.b64decode(result[1]['bytes']))
        self.assertEqual(collection['jobs'][0]['session'], session)
        self.assertEqual(session['fields']['packagePath'], 'pz-synthetic-local/r01.1/package.zip')
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(result[2]['bytes']))) as archive:
            self.assertIsNone(archive.testzip())
            request = json.loads(archive.read('brief.json'))
            self.assertEqual(request['format'], 'picross-authoring-request-v4')
            self.assertEqual(request['fields']['packagePath'], session['fields']['packagePath'])
            self.assertEqual(request['fields']['revision'], 'r01.1')
            self.assertEqual(request['fields']['inventoryRef'], self.fixture['local_build']['record']['inventory_sha256'])
            self.assertEqual(request['background'], self.fixture['background'])
            self.assertEqual(archive.read('source/reference.png'), PNG)
            inventory = json.loads(archive.read('dateien.json'))
            self.assertEqual(set(archive.namelist()) - {'dateien.json'},
                             {entry['file'] for entry in inventory['files']})
            for entry in inventory['files']:
                raw = archive.read(entry['file'])
                self.assertEqual(entry['bytes'], len(raw))
                self.assertEqual(entry['sha256'], hashlib.sha256(raw).hexdigest())

    def test_image_commit_and_settings_changes_cancel_other_pending_work(self):
        self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');edit('motif','Stable job');
const importGate=deferred();sandbox.importFile={size:100,text:()=>importGate.promise};
const importing=run('loadImportFile(importFile)');
sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
const afterImage=snapshot();importGate.resolve(JSON.stringify(input.fixtures.legacy_sheet));
assert.equal(await importing,false);assert.deepEqual(snapshot(),afterImage);
assert.equal(run('pendingTransfer'),null);
// A separately committed image invalidates an already captured export. Only
// the export's first digest waits; the newer image is checked and committed.
const originalDigest=sandbox.crypto.subtle.digest, exportGate=deferred();let calls=0;
sandbox.crypto.subtle.digest=async (...args)=>{if(++calls===1)await exportGate.promise;return originalDigest(...args);};
const exporting=run("exportPackage(CARDS.find(c=>c.id==='start'))");await tick();
assert.equal(await run('acceptImage(imageFile)'),true);const exportStable=snapshot();
exportGate.resolve();assert.equal(await exporting,false);sandbox.crypto.subtle.digest=originalDigest;
assert.equal(downloads.length,0);assert.deepEqual(snapshot(),exportStable);
// A deferred personal-settings file is tied to its initiating visit too.
const setup=plain(run('settingsSnapshot()')), settingsGate=deferred(), a=run('activeJobId');
const changedSetup=clone(setup);changedSetup.settings.workspaceRoot='/home/synthetic/replacement';
changedSetup.settings.cleanupMode='off';changedSetup.theme='dark';
sandbox.settingsFile={size:200,text:()=>settingsGate.promise};
const loading=run('importSettingsFile(settingsFile)');
run('createJob()');run('switchJob('+JSON.stringify(a)+')');
const afterVisit=snapshot(), status=elements.settingsStatus.textContent;
settingsGate.resolve(JSON.stringify(changedSetup));assert.equal(await loading,false);
assert.deepEqual(plain(run('settingsSnapshot()')),setup);assert.deepEqual(snapshot(),afterVisit);
assert.equal(elements.settingsStatus.textContent,status);
// A real global Change listener releases busy state and invalidates image I/O.
const imageGate=deferred();sandbox.lateImage={name:'late.png',size:Buffer.from(input.fixtures.png,'base64').length,arrayBuffer:()=>imageGate.promise};
const imaging=run('acceptImage(lateImage)');assert.equal(run('busy'),true);
set('cleanupMode','off');await elements.cleanupMode.emit('change');
assert.equal(run('busy'),false);assert.equal(elements.saveSession.disabled,false);
const afterOption=snapshot(), error=elements.imageError.textContent, original=Buffer.from(input.fixtures.png,'base64');
imageGate.resolve(original.buffer.slice(original.byteOffset,original.byteOffset+original.length));
assert.equal(await imaging,false);assert.deepEqual(snapshot(),afterOption);assert.equal(elements.imageError.textContent,error);
// Direct manual IDs cannot bypass the collection's uniqueness rule.
edit('puzzleId','pz-one');run('createJob()');const beforeDuplicate=snapshot();
edit('puzzleId','pz-one');assert.equal(elements.puzzleId.value,'');
assert.deepEqual(snapshot(),beforeDuplicate);
""")

    def test_discard_cancels_inflight_decode_and_companion_reads(self):
        self.javascript(r"""
edit('motif','Unchanged while preview is discarded');
const initial=snapshot(), originalImage=sandbox.Image;
for(const wholeWorkspace of [false,true]){
 const release=deferred(), entered=deferred();
 sandbox.Image=class extends originalImage {
  set src(value){entered.resolve();release.promise.then(()=>{super.src=value;});}
 };
 const session=clone(initial.jobs[0].session);
 session.image={name:'incoming.png',dataUrl:'data:image/png;base64,'+input.fixtures.png};
 const incoming=wholeWorkspace?clone(initial):session;
 if(wholeWorkspace)incoming.jobs[0].session=session;
 sandbox.incoming=incoming;const staging=run('stageTransfer(incoming)');
 await entered.promise;run('discardTransfer()');
 const preview=elements.transferPreview.textContent;
 assert.equal(run('pendingTransfer'),null);assert.equal(elements.applyTransfer.disabled,true);
 release.resolve();assert.equal(await staging,false);
 assert.deepEqual(snapshot(),initial);assert.equal(run('pendingTransfer'),null);
 assert.equal(elements.applyTransfer.disabled,true);assert.equal(elements.transferPreview.textContent,preview);
}
sandbox.Image=originalImage;
await run('stageTransfer(fixtures.record)');
assert.ok(run('pendingRecord'));assert.equal(run('pendingTransfer'),null);
const release=deferred();sandbox.companionFile={size:200,text:()=>release.promise};
const reading=run('loadCompanion(companionFile)');
run('discardTransfer()');const preview=elements.transferPreview.textContent;
release.resolve(JSON.stringify(input.fixtures.sheet));await reading;
assert.equal(run('pendingRecord'),null);assert.equal(run('pendingTransfer'),null);
assert.equal(elements.applyTransfer.disabled,true);assert.equal(elements.transferPreview.textContent,preview);
assert.deepEqual(snapshot(),initial);assert.equal(run('applyTransfer()'),false);
""")

    def test_export_rechecks_image_bytes_and_cached_metadata(self):
        self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');edit('motif','Image validation before export');
sandbox.imageFile=pngFile();assert.equal(await run('acceptImage(imageFile)'),true);
const original=plain(run('source'));sandbox.originalSource=original;
const mutations=[
 image=>image.sha256='0'.repeat(64),image=>image.bytes++,
 image=>image.width++,image=>image.height++,image=>image.type='image/jpeg',
 image=>image.dataUrl='data:image/png;base64,AAAA',
];
for(const change of mutations){
 sandbox.corruptSource=clone(original);change(sandbox.corruptSource);
 run('source=structuredClone(corruptSource)');
 const before=snapshot();
 assert.equal(await run("exportPackage(CARDS.find(c=>c.id==='start'))"),false);
 assert.equal(downloads.length,0,'stale image metadata must not become a request ZIP');
 assert.deepEqual(snapshot(),before);
}
run('source=structuredClone(originalSource)');
assert.equal(await run("exportPackage(CARDS.find(c=>c.id==='start'))"),true);
assert.equal(downloads.length,1,'the unchanged validated image still exports');
""")

    def test_late_image_import_export_and_clipboard_completions(self):
        self.javascript(r"""
set('workspaceRoot','/home/synthetic/picross');edit('motif','A');
const a=run('activeJobId');run('createJob()');edit('motif','B');const b=run('activeJobId');
sandbox.a=a;sandbox.b=b;run('switchJob(a)');
for(const action of ['visit','reset','revision','remove']){
 if(!snapshot().jobs.some(j=>j.job_id===a)){run('createJob()');sandbox.a=run('activeJobId');}
 else run('switchJob(a)');
 const gate=deferred();sandbox.delayedFile={name:'late.png',size:PNG_SIZE(),arrayBuffer:()=>gate.promise};
 const work=run('acceptImage(delayedFile)');
 if(action==='visit'){run('switchJob(b)');run('switchJob(a)');}
 if(action==='reset')run('resetJob()');
 if(action==='revision')edit('revision','new-revision');
 if(action==='remove')run('removeJob()');
 const stable=snapshot(), live=elements.live.textContent;
 const original=Buffer.from(input.fixtures.png,'base64');
 gate.resolve(original.buffer.slice(original.byteOffset,original.byteOffset+original.length));
 await work;
 assert.deepEqual(snapshot(),stable,action+' must invalidate image callback');
 assert.equal(elements.live.textContent,live,'no stale success or finally status');
}
function PNG_SIZE(){return Buffer.from(input.fixtures.png,'base64').length;}
// File.text can finish after A -> B -> A without becoming current again.
sandbox.a=run('activeJobId');const fileGate=deferred();
sandbox.lateJSON={size:100,text:()=>fileGate.promise};const importing=run('loadImportFile(lateJSON)');
run('createJob()');run('switchJob(a)');const afterVisit=snapshot();
fileGate.resolve(JSON.stringify(input.fixtures.legacy_sheet));await importing;
assert.equal(run('pendingTransfer'),null);assert.deepEqual(snapshot(),afterVisit);
// Digest completion cannot combine a job's bytes with another job's name/options.
edit('motif','Export A');edit('puzzleId','pz-export-a');
digestGate=deferred();const exporting=run("exportPackage(CARDS.find(c=>c.id==='start'))");
await tick();run('createJob()');edit('puzzleId','pz-export-b');edit('motif','Export B');
const exportStable=snapshot(), exportLive=elements.live.textContent;digestGate.resolve();await exporting;digestGate=null;
assert.equal(downloads.length,0);assert.deepEqual(snapshot(),exportStable);assert.equal(elements.live.textContent,exportLive);
const clipboard=deferred();sandbox.navigator.clipboard.writeText=()=>clipboard.promise;
const button=document.querySelector('[data-copy="start"]'), prior=button.textContent;
sandbox.button=button;const copying=run("copyCard(CARDS.find(c=>c.id==='start'),button)");
run('createJob()');const copyLive=elements.live.textContent;clipboard.resolve();await copying;
assert.equal(button.textContent,prior);assert.equal(elements.live.textContent,copyLive);
""")
