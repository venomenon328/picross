"""Independent Decimal80 reference and finite acceptance checks, no CI hook."""
import json, math
from decimal import Decimal as D, localcontext, ROUND_HALF_EVEN
from itertools import combinations
from pathlib import Path
import measure
ROOT=Path(__file__).parent
def coordinates(rgb):
 with localcontext() as ctx:
  ctx.prec=80; ctx.rounding=ROUND_HALF_EVEN
  channels=[D(int(rgb[i:i+2],16))/D(255) for i in (1,3,5)]
  linear=[c/D('12.92') if c<=D('.04045') else ((c+D('.055'))/D('1.055'))**D('2.4') for c in channels]
  lms=[]
  for row in [('0.4122214708','0.5363325363','0.0514459929'),('0.2119034982','0.6806995451','0.1073969566'),('0.0883024619','0.2817188376','0.6299787005')]:
   value=sum((D(a)*b for a,b in zip(row,linear)),D(0))
   lms.append(value**(D(1)/D(3)))
  q=[]
  for row in [('0.2104542553','0.7936177850','-0.0040720468'),('1.9779984951','-2.4285922050','0.4505937099'),('0.0259040371','0.7827717662','-0.8086757660')]:
   value=sum((D(a)*b for a,b in zip(row,lms)),D(0))
   q.append(int((value*D(1000000)).to_integral_value(rounding=ROUND_HALF_EVEN)))
  return q
def d2(a,b): return sum((x-y)**2 for x,y in zip(a,b))
def status(value):
 return 'negative' if value<10000000000 else ('positive_warning' if value<22500000000 else 'positive')
def main():
 plan=json.loads((ROOT/'plan.json').read_text(encoding='utf-8')); cases=[]; errors=[]
 for c in plan['cases']:
  colors={p['id']:coordinates(p['srgb']) for p in c['palette']}
  for p in c['palette']:
   independent=[round(x*1_000_000) for x in measure.lab(p['srgb'])]
   assert independent==colors[p['id']],(p,independent,colors[p['id']])
  pairs=[]
  for a,b in combinations(sorted(colors),2):
   value=d2(colors[a],colors[b])
   srgb={p['id']:p['srgb'] for p in c['palette']}
   raw=measure.distance(srgb[a],srgb[b])
   raw_status='negative' if raw<10 else ('positive_warning' if raw<15 else 'positive')
   assert status(value)==raw_status,(c['id'],a,b,value,raw)
   pairs.append({'a':a,'b':b,'d2':value,'D':math.sqrt(value)/10000,'status':status(value)})
  cases.append({'id':c['id'],'coordinates':colors,'pairs':pairs,'worst':min(pairs,key=lambda x:(x['d2'],x['a'],x['b']))})
 boundary=[(0,'negative'),(9999999999,'negative'),(10000000000,'positive_warning'),(10000000001,'positive_warning'),(22499999999,'positive_warning'),(22500000000,'positive'),(22500000001,'positive')]
 for value,expected in boundary: assert status(value)==expected
 assert d2([0,0,0],[100000,0,0])==10000000000
 assert d2([0,0,0],[150000,0,0])==22500000000
 f07=next(c for c in cases if c['id']=='F07')
 assert len(f07['pairs'])==28 and f07['worst']['a']=='c01' and f07['worst']['b']=='c08'
 assert coordinates('#000000')==[0,0,0]
 data={'rule_proposal':'picross-palette-separation-1-draft1','arithmetic':'Decimal80, half-even, integer q(1e-6 Oklab), integer d2',
 'independent_binary64_coordinates':'identical quantized coordinates for every fixed input color',
 'boundary_checks':[{'d2':v,'expected':s} for v,s in boundary], 'boundary_scope':'reducer equality at Oklab-coordinate level, not claimed as sRGB color pairs',
 'cases':cases}
 (ROOT/'recalculated.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
 for c in cases: print(c['id'],c['worst'])
 print('independent coordinates, 7 boundary reductions, 2 exact coordinate equalities, black and 28 F07 pairs: PASS')
if __name__=='__main__':main()
