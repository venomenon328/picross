"""Public immutable Raw HTTP retrieval, no preview conversion or login."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zlib
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
def fetch(commit,path):
 with urlopen('https://raw.githubusercontent.com/venomenon328/picross/'+commit+'/'+path,timeout=60) as response:
  return response.read()
def verify_png(data,size):
 assert data[:8]==b'\x89PNG\r\n\x1a\n'
 offset=8;idat=[];dimensions=None;channels=None
 while offset<len(data):
  length=struct.unpack('>I',data[offset:offset+4])[0];kind=data[offset+4:offset+8]
  payload=data[offset+8:offset+8+length];crc=struct.unpack('>I',data[offset+8+length:offset+12+length])[0]
  assert zlib.crc32(kind+payload)&0xffffffff==crc
  if kind==b'IHDR':
   w,h,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',payload)
   assert depth==8 and color in (2,6) and compression==filtering==interlace==0
   dimensions=[w,h];channels=3 if color==2 else 4
  if kind==b'IDAT':idat.append(payload)
  offset+=length+12
  if kind==b'IEND':break
 assert offset==len(data) and dimensions==size
 decoded=zlib.decompress(b''.join(idat));stride=1+size[0]*channels
 assert len(decoded)==stride*size[1] and all(decoded[y*stride]<=4 for y in range(size[1]))
def main():
 commit=sys.argv[1];target=Path(sys.argv[2]);target.mkdir(parents=True,exist_ok=False)
 assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
 raw=fetch(commit,'review-evidence/pa-v01/manifest.json');manifest=json.loads(raw)
 (target/'manifest.json').write_bytes(raw)
 def one(item):
  data=fetch(commit,item['file'])
  assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],item['file']
  verify_png(data,item['image_size'])
  (target/Path(item['file']).name).write_bytes(data)
  return item['file']
 with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(one,manifest['originals']))
 report={'source_commit':commit,'product_head':manifest['product_head'],'method':'public raw.githubusercontent.com immutable commit; urllib binary HTTP; SHA256/bytes/PNG CRC/IHDR/full IDAT verified',
 'count':len(files),'bytes':manifest['original_bytes'],'files':files,'account_scope':'no authentication; repository public; no independent personal sighting claimed','visual_opening':'separate image viewer required',
 'failed_alternative':'Windows gh api Accept raw+json returned transform: short source buffer for PNGs. No successful binary access claimed for that path.'}
 (target/'access.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('download verified:',len(files),'original PNGs,',manifest['original_bytes'],'bytes')
if __name__=='__main__':main()
