from pathlib import Path
from PIL import Image, ImageChops
import json, re
root=Path(__file__).resolve().parent
folder=root/'diagnostics-delivery'
report=json.loads((folder/'report.json').read_text())
def rectangle(text):
    x,y,w,h=map(float,re.findall(r'-?\d+(?:\.\d+)?',text))
    return int(x)-3,int(y)-3,int(x+w)+4,int(y+h)+4
base=Image.open(folder/'overlap-0-high.png').convert('RGB')
grid=rectangle(report['records'][0]['grid'])
rows=[]
for mode in range(1,4):
    other=Image.open(folder/f'overlap-{mode}-high.png').convert('RGB')
    diff=ImageChops.difference(base,other)
    outside=diff.copy()
    outside.paste((0,0,0),grid)
    rows.append(dict(mode=mode,outside_grid_bbox=outside.getbbox(),inside_grid_difference_bbox=diff.getbbox()))
trace=report['zoom_trace']
canvas={r['canvas'] for r in trace}
textures={r['texture_rid'] for r in trace}
loads={r['load_count'] for r in trace}
result=dict(outside_grid_comparisons=rows,zoom_samples=len(trace),canvas_states=len(canvas),texture_states=len(textures),load_count_states=len(loads),zoom_states=sorted({r['cell'] for r in trace}),all_ready=all(r['state']=='ready' for r in trace),failures=report['failures'])
(folder/'pixel-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
assert all(r['outside_grid_bbox'] is None for r in rows),result
assert len(canvas)==len(textures)==len(loads)==1 and result['all_ready'] and not result['failures'],result
print(json.dumps(result,indent=2))
