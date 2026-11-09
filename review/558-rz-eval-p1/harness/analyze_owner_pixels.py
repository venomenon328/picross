from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import json,re
r=Path(__file__).parent;folder=r/'owner-diagnostics';report=json.loads((folder/'report.json').read_text())
record=report['records'][0]
def rects(value):
 numbers=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',value)))
 return [(int(x)-3,int(y)-3,int(x+w)+4,int(y+h)+4) for x,y,w,h in zip(numbers[0::4],numbers[1::4],numbers[2::4],numbers[3::4])]
regions=rects(record['grid'])+rects(record['clues'])
base=Image.open(folder/'overlap-0-high.png').convert('RGB');rows=[]
for mode in range(1,4):
 diff=ImageChops.difference(base,Image.open(folder/f'overlap-{mode}-high.png').convert('RGB'))
 outside=diff.copy()
 for rect in regions:outside.paste((0,0,0),rect)
 rows.append(dict(mode=mode,outside_grid_and_clues_bbox=outside.getbbox(),difference_bbox=diff.getbbox()))
trace=report['zoom_trace']
result=dict(comparisons=rows,zoom_samples=len(trace),canvas_states=len({x['canvas'] for x in trace}),texture_states=len({x['texture_rid'] for x in trace}),load_count_states=len({x['load_count'] for x in trace}),all_ready=all(x['state']=='ready' for x in trace),failures=report['failures'])
assert all(x['outside_grid_and_clues_bbox'] is None for x in rows),result
assert result['canvas_states']==result['texture_states']==result['load_count_states']==1 and result['all_ready'] and not result['failures']
(folder/'pixel-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
