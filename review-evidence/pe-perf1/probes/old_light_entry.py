"""RAM-only low-frequency observation; original code, budgets and guards intact.

Unlike a Diagnostics observer this does not instrument each I/O tick. Get the
actual worker's CPU/I/O here, not the venv redirector process's counters.
"""
from pathlib import Path
import sys,json,time,traceback,ctypes
from tools.puzzle_editor import worker
from tools.puzzle_production import catalog_transaction as tx,catalog_publication as pub,content_registry as registry,operation_diagnostics as d
class IO(ctypes.Structure):_fields_=[(k,ctypes.c_ulonglong) for k in ('read_operations','write_operations','other_operations','read_bytes','write_bytes','other_bytes')]
k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
def counts():
    value=IO();assert k.GetProcessIoCounters(ctypes.c_void_p(k.GetCurrentProcess()),ctypes.byref(value))
    return {n:getattr(value,n) for n,_ in value._fields_}
original=worker.run
def observed(*args,**kwargs):
    start=time.perf_counter();cpu=time.process_time();io_before=counts();events=[];result={'observer':'RAM begin/end and existing phase boundaries; no per-I/O observer; no input/budget/guard changes'}
    def measured(label,fn):
        def call(*a,**kw):
            events.append({'event':label+' begin','wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu})
            try:return fn(*a,**kw)
            finally:events.append({'event':label+' end','wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu})
        return call
    for module,names in [(tx,['capture','prepare','validate_journal']),(pub,['guard']),(registry,['recover'])]:
        for name in names:setattr(module,name,measured(name,getattr(module,name)))
    boundary=pub.checkpoint;segment=d.begin_segment
    def checkpoint(phase,name=None):
        events.append({'event':'checkpoint '+phase,'target':name,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu});return boundary(phase,name)
    def begin_segment(name):
        events.append({'event':'segment '+name,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu});return segment(name)
    pub.checkpoint=checkpoint;d.begin_segment=begin_segment
    try:return original(*args,**kwargs)
    except BaseException as exc:
        result['error']=str(exc);result['traceback']=traceback.format_exc().replace(str(Path(__file__).parent),'<task>');raise
    finally:
        result.update(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,events=events)
        io_after=counts();result['actual_worker_os_io']={n:io_after[n]-v for n,v in io_before.items()}
        Path(sys.argv[2]).with_name('operation-observation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
worker.run=observed
worker.main(sys.argv[2])
