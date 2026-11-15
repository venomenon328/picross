import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).parent/'repo'
A='docs/ai-workflows/PUZZLE_AUTHORING.md';Q='docs/PUZZLE_QUALITY.md';B='docs/PUZZLE_BACKGROUNDS.md';T='docs/REVEAL_TRANSPARENCY.md';S='docs/PUZZLE_IMAGE_STYLE.md'
def select(raw,key):
    lines=raw.splitlines(keepends=True)
    start=next(i for i,l in enumerate(lines) if re.match(rb'^#{2,4} '+re.escape(key.encode())+rb'(?:[ .]|$)',l))
    level=len(lines[start].split(b' ')[0]);end=len(lines)
    for i in range(start+1,len(lines)):
        m=re.match(rb'^(#{1,4}) ',lines[i])
        if m and len(m[1])<=level: end=i;break
    return set(range(start,end))
maps={1:{A:['1.','2.','6.1','6.2','7.'],Q:['2.','3.1'],T:['2.']},2:{A:['1.','2.','6.1','6.2','7.'],Q:['2.','3.2','H03H04']},3:{A:['1.','4.','5.2','6.1','6.2','7.'],Q:['2.','3.','4.']},4:{A:['1.','6.1','6.2','6.3','7.'],Q:['2.','9.1'],B:['3.']},5:{A:['1.','6.','7.','8.','9.']}}
out=[]
for phase,parts in maps.items():
    specs={'AGENTS.md':['production'],S:['all'],**parts}; files=[]
    for path,keys in specs.items():
        raw=(ROOT/path).read_bytes();lines=raw.splitlines(keepends=True);indices=set()
        for key in keys:
            if key=='all':indices.update(range(len(lines)))
            elif key=='production':indices.update(range(next(i for i,l in enumerate(lines) if l.startswith(b'## Entwicklungsarbeit'))))
            elif key=='H03H04':indices.update(i for i,l in enumerate(lines) if l.startswith(b'| H-03 ') or l.startswith(b'| H-04 '))
            else:indices.update(select(raw,key))
        chosen=b''.join(lines[i] for i in sorted(indices)); ranges=[]
        for i in sorted(indices):
            if ranges and i+1==ranges[-1][1]+1:ranges[-1][1]=i+1
            else:ranges.append([i+1,i+1])
        files.append({'file':path,'sections':keys,'ranges':ranges,'file_bytes_read':len(raw),'selected_bytes':len(chosen),'sha256':hashlib.sha256(chosen).hexdigest()})
    out.append({'phase':phase,'file_reads':len(files),'selected_bytes':sum(x['selected_bytes'] for x in files),'file_bytes_read':sum(x['file_bytes_read'] for x in files),'repeated_reads_within_phase':0,'truncated_local_reads':0,'files':files})
extras={}
for key in ['5.','6.','8.','8.2','8.3','8.4','8.5']:
    raw=(ROOT/Q).read_bytes();lines=raw.splitlines(keepends=True);extras['quality '+key]=sum(len(lines[i]) for i in select(raw,key))
result={'method':'UTF-8 bytes, original LF, heading range union, no token estimate; local read-only route probe, not model token telemetry','phases':out,'conditional_quality_bytes':extras}
(Path(__file__).parent/'source-map.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
