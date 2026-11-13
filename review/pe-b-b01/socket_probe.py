"""One-time real Windows B01 proof. Never prints or stores session secrets."""
import ctypes
from contextlib import closing
import hashlib
import http.client
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys

HOME = Path(__file__).resolve().parent
REPO = HOME / "repo"
sys.path.insert(0, str(REPO))
from tools.test_puzzle_editor import fixture
from tools.puzzle_editor.server import Service, API

ATTACK = '''import json,socket,sys,os
with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,int(sys.argv[2]))
    try:
        s.bind(('127.0.0.1',int(sys.argv[1])));s.listen()
        print(json.dumps({'pid':os.getpid(),'bound':True,'reuse':int(sys.argv[2])}))
    except OSError as e:
        print(json.dumps({'pid':os.getpid(),'bound':False,'reuse':int(sys.argv[2]),'winerror':e.winerror}))
'''

def contender(port, reuse):
    result = subprocess.run([sys.executable, "-I", "-c", ATTACK, str(port), str(reuse)],
                            capture_output=True, text=True, check=True, timeout=10,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    return json.loads(result.stdout)

def request(service):
    with closing(http.client.HTTPConnection("127.0.0.1", service.http.server_port, timeout=5)) as conn:
        conn.request("GET", API+"status", headers={"X-PE-Session": service.secret})
        response = conn.getresponse()
        assert response.status == 200
        body = json.loads(response.read())
        assert body["checkout"] == str(service.root) and body["origin"] == service.origin
        assert not body["stopping"]
    return {"status": 200, "correct_checkout_and_origin": True}

def inventory(root):
    return {p.relative_to(root).as_posix(): [hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns]
            for p in root.rglob("*") if p.is_file()}

def main():
    assert os.name == "nt" and not ctypes.windll.shell32.IsUserAnAdmin()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    root = HOME / "socket-target"
    if not root.exists(): fixture(root)
    before = inventory(root)
    report = {"head": head, "platform": platform.platform(), "windows": list(sys.getwindowsversion()),
              "standard_user": True, "host_pid": os.getpid(), "later_contenders": [], "prior_occupants": []}
    service = Service(root, temporary=HOME/"temp")
    try:
        service.bind()
        assert service.http.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 0
        assert service.http.socket.getsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE) == 1
        report["socket_options"] = {"SO_REUSEADDR": 0, "SO_EXCLUSIVEADDRUSE": 1}
        report["port"] = service.http.server_port
        report["before"] = request(service)
        for reuse in (0, 1):
            result = contender(service.http.server_port, reuse)
            assert not result["bound"] and result["pid"] != os.getpid()
            assert result["winerror"] in (10013, 10048)
            result["original_session"] = [request(service) for _ in range(5)]
            report["later_contenders"].append(result)
        work = service.work
    finally:
        service.close()
    assert not work.exists()
    for reuse in (0, 1):
        with socket.socket() as foreign:
            foreign.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse)
            foreign.bind(("127.0.0.1", 0)); foreign.listen()
            port = foreign.getsockname()[1]
            candidate = Service(root, temporary=HOME/"temp")
            try:
                try:
                    candidate.bind(port)
                except OSError as exc:
                    assert exc.winerror in (10013, 10048)
                    row = {"foreign_reuse": reuse, "occupied_port": port, "rejected_winerror": exc.winerror}
                else:
                    raise AssertionError("Existing foreign listener must be rejected")
                # Explicit API choice; the separate native T03 verifies the user's Yes dialog.
                candidate.bind(0)
                assert candidate.http.server_port != port
                row.update(alternative_port=candidate.http.server_port, session=request(candidate), foreign_preserved=True)
                assert foreign.getsockname() == ("127.0.0.1", port)
                report["prior_occupants"].append(row)
            finally:
                candidate.close()
    assert inventory(root) == before
    report.update(passed=True, checkout_bytes_and_mtimes_unchanged=True, temp_removed=True)
    (HOME/"socket-report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report), flush=True)

if __name__ == "__main__": main()
