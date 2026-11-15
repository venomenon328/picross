from pathlib import Path
import json,re,time,hashlib,statistics,subprocess,sys,platform
ROOT=Path(__file__).resolve().parent; REPO=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'repo'
BASE='a559e8b38be7e658ff1d3d2aa667380657c89f4d'
A='docs/ai-workflows/PUZZLE_AUTHORING.md';Q='docs/PUZZLE_QUALITY.md';S='docs/PUZZLE_IMAGE_STYLE.md';AT='docs/REVEAL_TRANSPARENCY.md';HG='docs/PUZZLE_BACKGROUNDS.md'
def section(text,num):
 m=re.search(r'^#{2,4} '+re.escape(num)+r'(?:\. | )',text,re.M)
 assert m,num
 level=len(m.group(0).split(' ')[0]);end=re.search(r'^#{1,'+str(level)+r'} ',text[m.end():],re.M)
 return text[m.start():m.end()+end.start() if end else len(text)]
def agent(text):return text[:text.index('## Entwicklungsarbeit')]
def route(root,phase,new):
 scope={'AGENTS.md':['production'],S:['full'],A:['full'] if new else ['1','6.1','6.2','7']}
 if new:scope[A.replace('.md',f'_STEP_{phase[0]}.md')]=['full']
 elif phase[0] in '12':scope[A].append('2')
 elif phase[0]=='3':scope[A].extend(['4','5.2'])
 elif phase[0]=='4':scope[A].append('6.3')
 else:scope[A]=['1','6','7','8','9']
 if phase[0]=='1':scope.update({Q:['2','3.1'],AT:['2']})
 if phase[0]=='2':scope[Q]=['2','3.2','H-03','H-04']
 if phase[0]=='3':scope[Q]=['2','3','4']+(['8.4','8.5'] if new else ['8']) if phase=='3color' else ['2','3','4']
 if phase[0]=='4':scope.update({Q:['2','9.1'],HG:['3']})
 result=[];combined=[]
 for path,sections in scope.items():
  raw=(root/path).read_bytes();text=raw.decode('utf-8').replace('\r\n','\n')
  pieces=[]
  for sec in sections:
   if sec=='full':part=text
   elif sec=='production':part=agent(text)
   elif sec.startswith('H-'):part=next(line+'\n' for line in text.splitlines() if line.startswith('| '+sec))
   else:part=section(text,sec)
   if not new and phase=='5' and path==A and sec=='9':part=part.rstrip()+'\n'
   pieces.append(part)
  selected=''.join(pieces).encode('utf-8');combined.append(selected)
  result.append({'file':path,'sections':sections,'file_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'selected_utf8_lf_bytes':len(selected)})
 return {'sources':result,'calls':len(scope),'bytes':sum(x['selected_utf8_lf_bytes'] for x in result),'whole_file_bytes':sum(x['file_bytes'] for x in result),'routine_historical_reads':0,'truncated_responses':0,'unplanned_repeats':0},b''.join(combined)
def setup():
 paths=['AGENTS.md',A,S,Q,AT,HG]
 original={p:subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+p]).decode('utf-8') for p in paths}
 before=ROOT/'probe-before';after=ROOT/'probe-after'
 for p,txt in original.items():
  f=before/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(txt.encode('utf-8'))
 paths=list(original)+[A.replace('.md',f'_STEP_{n}.md') for n in range(1,6)]
 for p in paths:
  f=after/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((REPO/p).read_bytes())
 return before,after
if __name__=='__main__':
 setup_at=time.perf_counter_ns();before,after=setup();setup_ns=time.perf_counter_ns()-setup_at;phases=['1','2','3mono','3color','4','5'];result={'basis':BASE,'setup_ns':setup_ns,'source_head':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'environment':{'python':sys.version,'platform':platform.platform(),'filesystem':'NTFS (Get-Volume E verified)'},'channel':'Python pathlib.read_bytes + exact heading/row selection; local NTFS; UTF-8/LF output','setup':'Git source retrieval and copies outside timing, equal path depths; one warm-up per complete route, no persistent result cache. Section 9 excludes its delimiter blank line, as in PW-PERF-A.','phases':{}}
 for phase in phases:
  b,_=route(before,phase,False);a,_=route(after,phase,True)
  result['phases'][phase]={'before':b,'after':a}
  print(phase,b['bytes'],a['bytes'],b['calls'],a['calls'])
 # Predetermined paired protocol, all samples retained, not best-of reruns.
 for phase in phases:route(before,phase,False);route(after,phase,True)
 samples={'before':[],'after':[]}
 phase_samples={name:{phase:[] for phase in phases} for name in samples}
 for i in range(101):
  for name,root,new in ([('before',before,False),('after',after,True)] if i%2==0 else [('after',after,True),('before',before,False)]):
   start=time.perf_counter_ns()
   for phase in phases:
    at=time.perf_counter_ns();route(root,phase,new);phase_samples[name][phase].append(time.perf_counter_ns()-at)
   samples[name].append(time.perf_counter_ns()-start)
 result['samples_ns']=samples
 result['phase_samples_ns']=phase_samples
 for phase in phases:
  result['phases'][phase]['timing']={name:{'total_ns':sum(phase_samples[name][phase]),'median_ns':statistics.median(phase_samples[name][phase])} for name in samples}
 result['timing']={name:{'total_ns':sum(v),'median_ns':statistics.median(v)} for name,v in samples.items()}
 (ROOT/'source-map.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(result['timing'])
