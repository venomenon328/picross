"""Disposable loopback OpenSSH reference; never reads a user's deployment config."""
from __future__ import annotations
import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deploy_web
import web_bundle
from serve import serve, Handler


def check_failure(action):
    try:
        action()
    except (ValueError, RuntimeError):
        return
    raise AssertionError('Expected failure did not occur')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    first=web_bundle.validate(args.build.resolve())
    report={'source_commit':first['source_commit'],'build_id':first['build_id'],
            'environment':'isolated loopback POSIX/OpenSSH', 'scenarios':[], 'status':'running'}
    def passed(label):
        report['scenarios'].append(label); print('SSH PASS',label,flush=True)
    with tempfile.TemporaryDirectory(prefix='picross-ssh-') as temporary:
        work=Path(temporary); root=work/'site'/'picross-web'; root.mkdir(parents=True)
        (root/'.picross-web').write_text('picross-web-v1\n')
        for name in ('client','host'):
            subprocess.run(['ssh-keygen','-q','-t','ed25519','-N','','-f',str(work/name)],check=True,capture_output=True)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        sshd=work/'sshd_config'
        sshd.write_text(f'''ListenAddress 127.0.0.1
Port {port}
HostKey {work}/host
PidFile {work}/pid
AuthorizedKeysFile {work}/client.pub
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM no
StrictModes yes
AllowUsers {getpass.getuser()}
Subsystem sftp internal-sftp
''')
        subprocess.run(['sudo','mkdir','-p','/run/sshd'],check=True)
        log=(work/'sshd.log').open('w')
        process=subprocess.Popen(['sudo','/usr/sbin/sshd','-D','-e','-f',str(sshd)],stdout=log,stderr=log)
        pub=(work/'host.pub').read_text().split()
        (work/'known_hosts').write_text(f'[127.0.0.1]:{port} {pub[0]} {pub[1]}\n')
        client=work/'ssh_config'
        client.write_text(f'Host 127.0.0.1\n IdentityFile {work}/client\n IdentitiesOnly yes\n UserKnownHostsFile {work}/known_hosts\n')
        server,url=serve(root)
        cfg=dict(host='127.0.0.1',user=getpass.getuser(),port=port,root=str(root),url=url,ssh_config=str(client))
        remote=deploy_web.Remote(cfg)
        try:
            for attempt in range(30):
                try: remote.preflight(); break
                except RuntimeError:
                    if attempt==29: raise
                    time.sleep(.2)
            before={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            deploy_web.deploy(cfg,args.build.resolve(),dry_run=True)
            assert before=={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            passed('dry run has no file mutations')
            deploy_web.deploy(cfg,args.build.resolve())
            assert remote.current()==first['build_id']
            passed('real SFTP transfer, verified staging, atomic activation and HTTP resources')
            deploy_web.deploy(cfg,args.build.resolve())
            passed('repeat identical update preserves immutable bytes')
            remote.acquire()
            try: check_failure(lambda:deploy_web.deploy(cfg,args.build.resolve()))
            finally: remote.release()
            assert remote.current()==first['build_id']
            passed('concurrent deployment rejected under real remote lock')
            incomplete=work/'incomplete'; shutil.copytree(args.build,incomplete)
            missing=next(p for p in incomplete.rglob('*.wasm')); missing.unlink()
            check_failure(lambda:deploy_web.deploy(cfg,incomplete))
            remote.acquire()
            try: check_failure(lambda:remote.upload(incomplete,first))
            finally: remote.release()
            assert remote.current()==first['build_id']
            passed('incomplete bundle and actual interrupted SFTP upload leave current intact')
            # A second version is the same verified export under a different immutable URL.
            second_dir=work/'second'; shutil.copytree(args.build,second_dir)
            old=first['build_id']; new=old[:-14]+'20990101000000'
            (second_dir/'releases'/old).rename(second_dir/'releases'/new)
            for entry in (second_dir/'index.html',second_dir/'releases'/new/'entry.html'):
                entry.write_text(entry.read_text().replace(old,new),encoding='utf-8')
            second={**first,'build_id':new,'files':web_bundle.inventory(second_dir)}
            (second_dir/'build-manifest.json').write_text(json.dumps(second)+'\n')
            web_bundle.validate(second_dir)
            old_html=urlopen(url).read()
            remote.acquire()
            try:
                remote.upload(second_dir,second)
                (root/('.entry-'+remote.token)).mkdir() # Actual mv failure, not a mocked SSH command.
                check_failure(lambda:remote.activate(new))
            finally: remote.release()
            assert remote.current()==old
            passed('real activation failure preserves previous entry')
            deploy_web.deploy(cfg,second_dir)
            assert old.encode() in old_html and remote.current()==new
            for name,entry in first['files'].items():
                if name.startswith('releases/'):
                    import hashlib
                    assert hashlib.sha256(urlopen(url+deploy_web.quote(name)).read()).hexdigest()==entry['sha256']
            passed('staggered old-entry resource fetches survive activation without mixed versions')
            deploy_web.deploy(cfg,None,rollback=old)
            assert remote.current()==old
            passed('scripted rollback restores retained version')
            previous_mime=Handler.extensions_map['.wasm']; Handler.extensions_map['.wasm']='text/plain'
            try: check_failure(lambda:deploy_web.deploy(cfg,second_dir))
            finally: Handler.extensions_map['.wasm']=previous_mime
            assert remote.current()==old
            passed('failed HTTP completion check reports failure and restores previous entry')
            bad={**cfg,'root':str(work)}
            config_file=work/'invalid.json'; config_file.write_text(json.dumps(bad))
            check_failure(lambda:deploy_web.config(config_file))
            (root/'.picross-web').rename(root/'.marker-held')
            check_failure(remote.preflight)
            (root/'.marker-held').rename(root/'.picross-web')
            passed('broad target and missing ownership marker rejected')
            # Same entry and resources also work below a URL prefix.
            parent_server,parent_url=serve(work)
            try: deploy_web.check_http(parent_url+'site/picross-web/',first)
            finally: parent_server.shutdown()
            passed('site root and subpath MIME/cache/integrity checks')
            report['status']='passed'
        finally:
            server.shutdown()
            if process.poll() is None:
                pidfile=work/'pid'
                if pidfile.exists(): subprocess.run(['sudo','kill',pidfile.read_text().strip()],check=False)
                process.wait(timeout=10)
            log.close()
            (args.output/'ssh-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
