"""One-off P-A comparison; never a production validator or CI test."""
import json, math, sys
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).parent
M1=((.4122214708,.5363325363,.0514459929),(.2119034982,.6806995451,.1073969566),(.0883024619,.2817188376,.6299787005))
M2=((.2104542553,.7936177850,-.0040720468),(1.9779984951,-2.4285922050,.4505937099),(.0259040371,.7827717662,-.8086757660))
def linear(s):
 c=[int(s[i:i+2],16)/255 for i in (1,3,5)]
 return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
def lab(s):
 rgb=linear(s)
 lms=[sum(a*b for a,b in zip(row,rgb))**(1/3) for row in M1]
 return [sum(a*b for a,b in zip(row,lms)) for row in M2]
def luminance(s): return sum(a*b for a,b in zip((.2126,.7152,.0722),linear(s)))
def distance(a,b): return 100*math.dist(lab(a),lab(b))
def contrast(a,b):
 x,y=sorted((luminance(a),luminance(b)))
 return (y+.05)/(x+.05)
def pair(a,b):
 return {'a':a['id'],'b':b['id'],'srgb':[a['srgb'],b['srgb']], 'distance':distance(a['srgb'],b['srgb']),
 'contrast':contrast(a['srgb'],b['srgb']),'delta_Y':abs(luminance(a['srgb'])-luminance(b['srgb']))}
def main():
 include_held='--held' in sys.argv
 plan=json.loads((ROOT/'plan.json').read_text(encoding='utf-8'))
 results=[]
 for case in plan['cases']:
  if case['held_out'] and not include_held: continue
  pairs=[pair(a,b) for a,b in combinations(case['palette'],2)]
  results.append({'id':case['id'],'pairs':pairs,
    'background_diagnostics':[{'id':a['id'],'paper_surrogate':'#faf6ec','contrast':contrast(a['srgb'],'#faf6ec'),'line_surrogate':'#343f42','line_contrast':contrast(a['srgb'],'#343f42')} for a in case['palette']]})
 name='measurement-all.json' if include_held else 'measurement-development.json'
 (ROOT/name).write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8',newline='\n')
 for case in results:
  worst=min(case['pairs'],key=lambda p:p['distance'])
  print(case['id'], 'worst',worst['a'],worst['b'],f"D={worst['distance']:.9f} C={worst['contrast']:.9f}")
  if case['id']=='F08':
   for p in case['pairs']: print(' ',p['a'],p['b'],f"D={p['distance']:.9f}")
if __name__=='__main__': main()
