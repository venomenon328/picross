from pathlib import Path
import os,sys,subprocess,json,time
root=Path.cwd();base=root.parent
sys.path[:0]=[str(root),str(root/'tools')]
import book_lifecycle
from native_results import validate_book_lifecycle
from p1_evidence import source_identity
actual_popen=subprocess.Popen
def hidden_popen(*args,**kwargs):
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
 kwargs.setdefault('startupinfo',startup)
 return actual_popen(*args,**kwargs)
subprocess.Popen=hidden_popen
began=time.monotonic()
report=book_lifecycle.run_lifecycle(base/'cache',base/'lifecycle-final2')
validate_book_lifecycle(dict(book_lifecycle=report),base/'lifecycle-final2',source_identity(root),'Windows')
print('LIFECYCLE_PASS seconds',round(time.monotonic()-began,3),flush=True)
