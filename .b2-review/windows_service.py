from pathlib import Path
import os,sys,subprocess,time,secrets,urllib.request
class WindowsProject:
    def __init__(self,name,image,password):
        base=Path(os.environ['RUNNER_TEMP'])
        self.pg=base/name
        self.repo=Path(__file__).resolve().parent.parent/'repo/server/save_sync'
        self.binaries=next(iter(sorted(Path(os.environ['ProgramFiles']).glob('PostgreSQL/*/bin/initdb.exe'),reverse=True))).parent
        self.env=dict(os.environ,PGHOST='127.0.0.1',PGPORT='15432',PGUSER='picross',PGDATABASE='postgres',PGPASSWORD=password)
        self.port=18333
        self.proc=None
        self.started=False
    def up(self,*_):
        passwd=self.pg.with_suffix('.password')
        passwd.write_text(self.env['PGPASSWORD'],encoding='ascii')
        try:
            subprocess.run([str(self.binaries/'initdb.exe'),'-D',str(self.pg),'-U','picross','--encoding=UTF8','--no-locale','--auth=scram-sha-256','--pwfile='+str(passwd)],env=self.env,check=True,stdout=subprocess.DEVNULL)
        finally: passwd.unlink(missing_ok=True)
        subprocess.run([str(self.binaries/'pg_ctl.exe'),'-D',str(self.pg),'-l',str(self.pg/'db.log'),'-o','-h 127.0.0.1 -p 15432','-w','start'],check=True,env=self.env)
        self.started=True
        self.admin('migrate')
        self.proc=subprocess.Popen([sys.executable,'-m','uvicorn','sync.api:app','--host','127.0.0.1','--port',str(self.port),'--no-access-log'],cwd=self.repo,env=self.env)
        for i in range(60):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{self.port}/health/ready'):return
            except OSError:time.sleep(1)
        raise RuntimeError('Isolated API not ready')
    def admin(self,*args):
        return subprocess.check_output([sys.executable,'-m','sync.admin',*args],cwd=self.repo,env=self.env,text=True).strip()
    def down(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=20)
        if self.started:subprocess.run([str(self.binaries/'pg_ctl.exe'),'-D',str(self.pg),'-m','fast','stop'],env=self.env,check=True)
