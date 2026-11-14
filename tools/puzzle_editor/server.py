"""Bounded loopback session and asynchronous calls to the shared writers."""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import base64
import hmac
import json
import os
import re
import secrets
import socket
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from tools.puzzle_production import catalog_io as io, editor_change
from tools.puzzle_production import catalog_transaction as tx, content_registry
from tools.puzzle_production import catalog_publication
from tools.puzzle_production.contract import digest, exact_keys
from tools.puzzle_production.authoring_package import require
from .instance import Instance

API = "/api/pe/v1/"
FORMAT = "picross-pe-api-v1"
UI = Path(__file__).parent/"ui"
CODE = Path(__file__).resolve().parents[2]
HEX = re.compile(r"[0-9a-f]{32}")
PILOTS = {"wasserwelt": "water", "landschaften-natur": "nature"}


def encoded(value): return editor_change.encoded(value)


def pending(root):
    from tools.puzzle_production.editor_change import pending as check
    return check(root)


def catalog(root):
    from tools.puzzle_production.editor_change import listing
    return listing(root)


class Service:
    def __init__(self, root, *, temporary=None, state=None):
        self.root = io.external(root)
        from .settings import Settings
        self.settings = Settings(state)
        require(not self.settings.directory.is_relative_to(self.root), "Programmeinstellungen müssen außerhalb des Checkouts liegen.")
        require(self.root.is_dir() and io.safe(self.root, ".git").exists(), "Vorhandenes Picross-Gitcheckout wählen.")
        # Validate only the cheap current indexes. Recovery is allowed even with partial data.
        pending_state = pending(self.root)
        if not pending_state: catalog(self.root)
        temp_base = io.external(temporary if temporary is not None else tempfile.gettempdir())
        require(not temp_base.is_relative_to(self.root),
                "Editor-Tempablage muss außerhalb des Checkouts liegen.")
        self.instance = Instance(self.root)
        try:
            self.directory = tempfile.TemporaryDirectory(prefix="picross-pe-", dir=temp_base)
        except BaseException:
            self.instance.close(); raise
        self.work = io.external(self.directory.name)
        require(not self.work.is_relative_to(self.root) and not self.root.is_relative_to(self.work),
                "Editor-Tempablage muss außerhalb des Checkouts liegen.")
        self.secret = secrets.token_hex(32)
        self.origin, self.stopping, self.job = None, False, None
        self.lock = threading.RLock()
        self.thread, self.http, self.server_thread = None, None, None
        self.assets, self.uploads, self.plans, self.details = {}, {}, {}, {}
        self.worker = None; self.worker_log = None

    def bind(self, port=0):
        self.http = HTTP(("127.0.0.1", port), Handler)
        self.http.service = self
        self.origin = "http://127.0.0.1:"+str(self.http.server_port)
        self.server_thread = threading.Thread(target=self.http.serve_forever, name="PE-http")
        self.server_thread.start()
        return self.origin

    def url(self): return self.origin+"/#"+self.secret

    def status(self):
        with self.lock:
            if not self.thread or not self.thread.is_alive(): self.purge()
            job = dict(self.job) if self.job else None
            if job:
                job.pop("started", None)
                if job["state"] == "running": job["elapsed_seconds"] = round(time.monotonic()-self.job["started"], 1)
            running = bool(self.thread and self.thread.is_alive())
            return {"format": FORMAT, "checkout": str(self.root), "origin": self.origin,
                    "stopping": self.stopping, "recovery_required": False if running else pending(self.root), "job": job}

    def idle(self):
        require(not self.stopping, "Editor wird beendet.")
        require(not self.thread or not self.thread.is_alive(), "Fachprüfung läuft. Danach erneut versuchen.")

    def purge(self):
        now = time.monotonic()
        for key, row in list(self.uploads.items()):
            if row["expires"] < now:
                io.safe(self.work, row["file"]).unlink(missing_ok=True)
                self.uploads.pop(key)
        for key, row in list(self.plans.items()):
            if row["expires"] < now:
                self.remove_plan(key)

    def remove_plan(self, key):
        row = self.plans.pop(key)
        path = io.external(row["work"])
        require(path.is_relative_to(self.work), "Ungültige eigene Planablage.")
        require(path.name == "work" and re.fullmatch(r"job-[0-9a-f]{32}", path.parent.name) and path.parent.parent == self.work,
                "Ungültige eigene Planwurzel.")
        path = path.parent
        # Verify all components before deleting only our own plan workspace.
        for child in path.rglob("*"): io.safe(path, child.relative_to(path).as_posix())
        shutil.rmtree(path)

    def invalidate(self):
        for key in list(self.plans): self.remove_plan(key)

    def asset(self, path, *, root=None, expected=None, validated=False):
        root = self.root if root is None else root
        for key, row in self.assets.items():
            if row["root"] == root and row["file"] == path and row["sha256"] == expected: return key
        while len(self.assets) >= 32: self.assets.pop(next(iter(self.assets)))
        key = secrets.token_hex(16)
        self.assets[key] = {"root": root, "file": path, "sha256": expected, "validated": validated}
        return key

    def picture(self, key):
        require(HEX.fullmatch(key) and key in self.assets, "Bild ist nicht freigegeben. Detail neu laden.")
        row = self.assets[key]
        raw = io.read(row["root"], row["file"], 32*1024*1024)
        require(row["sha256"] is None or io.checksum(raw) == row["sha256"], "Bildbytes geändert. Neu laden.")
        if row["file"].endswith(".svg") and not row["validated"]:
            from tools.puzzle_production.editor_image_input import validate_reveal
            validate_reveal(raw, ".svg")
            row["validated"] = row["sha256"] is not None
        return raw, "image/svg+xml" if row["file"].endswith(".svg") else "image/png"

    def standard(self, identifier):
        assets = []
        if identifier in PILOTS:
            assets = [self.asset("game/art/drawing/margins/"+PILOTS[identifier]+"_"+side+".png", root=CODE) for side in ("left", "right")]
        return {"format": FORMAT, "assets": assets}

    def start_worker(self):
        if self.worker is not None:
            require(self.worker.poll() is None, "Fachprozess beendet. Editor neu starten; ggf. Recovery prüfen.")
            return
        command = [sys.executable, "--session"] if getattr(sys, "frozen", False) else [sys.executable, "-I", "-c",
            "import sys;sys.path.insert(0,sys.argv[1]);from tools.puzzle_editor.worker import loop;loop(sys.argv[2])", str(CODE)]
        env = os.environ.copy()
        temp = self.work/"session-temp"; temp.mkdir()
        env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp), PYTHONNOUSERSITE="1")
        self.worker_log = (self.work/"worker.log").open("wb")
        self.worker = subprocess.Popen(command+[str(self.work)], cwd=CODE, env=env,
            stdin=subprocess.PIPE, stdout=self.worker_log, stderr=self.worker_log,
            text=True, encoding="utf-8", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def start(self, action, body, *, work=None, complete=None):
        self.idle()
        jid = secrets.token_hex(16)
        jobdir = self.work/("job-"+jid)
        jobdir.mkdir()
        work = jobdir/"work" if work is None else work
        work.mkdir(exist_ok=True)
        payload = {"root": str(self.root), "work": str(work), "action": action, "body": body}
        (jobdir/"job.json").write_bytes(encoded(payload))
        self.job = {"id": jid, "operation": action, "state": "running", "stage": "Fachoperation gestartet: "+action,
                    "started": time.monotonic(), "result": None, "error": None}

        def execute():
            result, error = None, None
            try:
                self.start_worker()
                self.worker.stdin.write(str(jobdir/"job.json")+"\n"); self.worker.stdin.flush()
                while not (jobdir/"result.json").exists():
                    require(self.worker.poll() is None, "Fachprozess fehlgeschlagen. Neu starten; ggf. Recovery prüfen.")
                    time.sleep(.025)
                    with self.lock:
                        try:
                            progress = io.read(jobdir, "progress.json", 4096, missing=True)
                            if progress is not None:
                                progress = io.json_bytes(progress, 4096)
                                exact_keys(progress, {"stage", "elapsed_seconds"})
                                require(isinstance(progress["stage"], str) and len(progress["stage"]) <= 512, "Ungültige Fachprozessphase")
                                self.job["stage"] = progress["stage"]
                        except Exception:
                            pass
                value = io.json_bytes(io.read(jobdir, "result.json", 48*1024*1024), 48*1024*1024)
                require(not value["error"], value["error"] or "Fachprüfung fehlgeschlagen.")
                result = value["result"]
                with self.lock:
                    if complete is not None: result = complete(result, work)
            except Exception as exc:
                error = str(exc)[:2048]
            finally:
                if action == "validate_upload" and not any(row["file"] == body["file"] for row in self.uploads.values()):
                    io.safe(self.work, body["file"]).unlink(missing_ok=True)
                # Keep only the current plan; all other per-operation work ends here.
                keep = any(Path(row["work"]).is_relative_to(jobdir) for row in self.plans.values())
                if not keep:
                    for child in jobdir.rglob("*"): io.safe(jobdir, child.relative_to(jobdir).as_posix())
                    shutil.rmtree(jobdir)
                with self.lock:
                    self.job.update(state="error" if error else "done", stage="Fachoperation fehlgeschlagen" if error else "Readback / Fachoperation abgeschlossen", result=result, error=error,
                                    elapsed_seconds=round(time.monotonic()-self.job["started"], 1))
                    self.thread = None
        self.thread = threading.Thread(target=execute, name="PE-writer")
        self.thread.start()
        return {"format": FORMAT, "job": jid}

    def detail(self, body):
        exact_keys(body, {"id", "snapshot"})
        def complete(result, work):
            self.assets.clear()
            row = result["detail"]["runtime"]
            bound = result.pop("_resources")
            name = "game/"+row["reveal"]
            pictures = {"reveal": [self.asset(name, expected=bound[name])], "background": []}
            bg = row["background"]
            if bg["status"] == "selected":
                name = "game/"+bg["asset"]["file"]
                pictures["background"] = [self.asset(name, expected=bound[name])]
            elif bg["status"] in ("legacy", "standard") and row["category_id"] in PILOTS:
                pictures["background"] = self.standard(row["category_id"])["assets"]
            pictures["paper"] = self.asset("game/book/paper.png", root=CODE)
            self.details = {body["id"]: {"snapshot": result["snapshot"], "definition_sha256": result["definition_sha256"]}}
            result["pictures"] = pictures
            return result
        return self.start("detail", body, complete=complete)

    def upload(self, kind, suffix, raw):
        self.idle(); self.purge(); self.invalidate()
        for prior, row in list(self.uploads.items()):
            if row["kind"] == kind:
                io.safe(self.work, row["file"]).unlink(missing_ok=True)
                self.uploads.pop(prior)
        require(len(self.uploads) < 2, "Höchstens zwei Importe. Verwerfen oder neu starten.")
        require(kind in ("reveal", "background") and suffix in ("png", "svg") and
                (kind != "background" or suffix == "png"), "Ungültiger Bildimport.")
        key = secrets.token_hex(16)
        name = "upload-"+key+"."+suffix
        with io.safe(self.work, name).open("xb") as stream: stream.write(raw)
        ref = {"file": name, "sha256": io.checksum(raw), "bytes": len(raw), "kind": kind,
               "expires": time.monotonic()+900}
        def complete(result, work):
            ref["checked"] = result
            self.uploads[key] = ref
            asset = self.asset(name, root=self.work, expected=ref["sha256"], validated=True)
            return {"upload": key, "asset": asset, "sha256": ref["sha256"], "bytes": ref["bytes"]}
        return self.start("validate_upload", {"file": name, "kind": kind}, work=self.work, complete=complete)

    def plan(self, body):
        self.idle(); self.purge(); self.invalidate()
        exact_keys(body, {"snapshot", "id", "metadata", "text", "profile", "reveal", "background"})
        identifier = body["id"]
        if identifier is None:
            require(all(body[k] is None for k in ("text", "profile", "reveal", "background")), "Kategorien separat speichern.")
            require(isinstance(body["metadata"], list) and len(body["metadata"]) == 1 and
                    body["metadata"][0].get("op") in ("category_create", "category_rename", "category_delete"), "Eine Kategorienaktion erwartet.")
            bound = None
        else:
            require(isinstance(identifier, str) and identifier in self.details and self.details[identifier]["snapshot"] == body["snapshot"], "Detailbindung fehlt/veraltet.")
            bound = body["snapshot"]
        request = dict(body); request.pop("snapshot")
        uploads = {}
        selected = []
        for kind in ("reveal", "background"):
            part = body[kind]
            if part is None: continue
            exact_keys(part, {"upload"} | ({"status"} if kind == "background" else set()))
            key = part["upload"]
            if key is None:
                require(kind == "background" and part["status"] in ("none", "standard", "selected"), "Bilddatei fehlt.")
                ref = None
            else:
                require(key in self.uploads and self.uploads[key]["kind"] == kind, "Import fehlt/abgelaufen oder falscher Bildtyp.")
                row = self.uploads[key]
                uploads[key] = {"file": row["file"], "sha256": row["sha256"]}
                selected.append(key)
        action = "plan"
        payload = {"request": request, "uploads": uploads, "catalog_snapshot": body["snapshot"],
                   "definition_sha256": self.details[identifier]["definition_sha256"] if identifier else None}
        def complete(result, work):
            key = secrets.token_hex(16)
            plan_hash = result["plan_hash"]
            self.plans[key] = {"work": str(work), "kind": result["kind"], "id": identifier,
                               "expires": time.monotonic()+600, "plan_hash": plan_hash,
                               "uploads": selected}
            return {"plan": key, "id": identifier, **result, "expires_seconds": 600}
        return self.start(action, payload, complete=complete)

    def apply(self, body):
        self.idle(); self.purge()
        exact_keys(body, {"plan", "id"})
        require(body["plan"] in self.plans, "Plan fehlt/abgelaufen. Erneut prüfen.")
        row = self.plans[body["plan"]]
        require(row["id"] == body["id"], "Ziel-ID stimmt nicht mit dem Plan überein.")
        work = io.external(row["work"])
        def complete(result, ignored):
            for identifier, previous in self.details.items():
                previous["snapshot"] = result["catalog"]["snapshot"]
                if identifier == row["id"] and result.get("definition_sha256"):
                    previous["definition_sha256"] = result["definition_sha256"]
            return result
        return self.start("apply", {"kind": row["kind"], "plan_hash": row["plan_hash"]}, work=work, complete=complete)

    def stop(self):
        with self.lock: self.stopping = True

    def close(self):
        self.stop()
        active = self.thread
        if active: active.join()
        if self.worker is not None:
            if self.worker.poll() is None:
                self.worker.stdin.write("stop\n"); self.worker.stdin.flush()
                self.worker.stdin.close(); self.worker.wait()
            self.worker = None
        if self.worker_log: self.worker_log.close(); self.worker_log = None
        if self.http:
            self.http.shutdown(); self.http.server_close()
        if self.server_thread: self.server_thread.join()
        self.directory.cleanup()
        self.instance.close()


class HTTP(ThreadingHTTPServer):
    daemon_threads = False
    request_queue_size = 8

    def server_bind(self):
        if os.name == "nt":
            # Windows SO_REUSEADDR permits a second listener on our live port.
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def __init__(self, *args):
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(*args)

    def process_request(self, request, address):
        if not self.slots.acquire(False):
            request.close(); return
        try: super().process_request(request, address)
        except Exception:
            self.slots.release(); raise

    def process_request_thread(self, *args):
        try: super().process_request_thread(*args)
        finally: self.slots.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Never log session headers/fragment.
    def setup(self):
        super().setup(); self.connection.settimeout(15)

    def reply(self, status, value, mime="application/json; charset=utf-8"):
        raw = encoded(value) if isinstance(value, dict) else value
        self.send_response(status)
        for key, content in {"Content-Type": mime, "Content-Length": str(len(raw)), "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "Connection": "close",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"}.items():
            self.send_header(key, content)
        self.end_headers(); self.wfile.write(raw)

    def handle_route(self):
        status = 400
        try:
            s = self.server.service
            for key in ("Host", "Origin", "Sec-Fetch-Site", "X-PE-Session", "Content-Length", "Content-Type"):
                require(len(self.headers.get_all(key, [])) <= 1, "Doppelter HTTP-Header.")
            status = 403
            require(self.headers.get("Host") == s.origin.removeprefix("http://"), "Fremder Host.")
            require(self.headers.get("Origin") in (None, s.origin), "Fremder Ursprung.")
            require(self.headers.get("Sec-Fetch-Site") in (None, "none", "same-origin"), "Fremder Browserzugriff.")
            status = 400
            require(re.fullmatch(r"/[a-zA-Z0-9/._-]*", self.path) and ".." not in self.path, "Ungültige Route.")
            require(not self.headers.get_all("Transfer-Encoding"), "Transfer-Encoding ist nicht erlaubt.")
            if self.command == "GET": require(self.headers.get("Content-Length", "0") == "0", "GET hat keinen Body.")
            static = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
            if self.command == "GET" and self.path in static:
                name, mime = static[self.path]; return self.reply(200, (UI/name).read_bytes(), mime)
            status = 403
            require(hmac.compare_digest(self.headers.get("X-PE-Session", "").encode(), s.secret.encode()), "Sitzung fehlt. Im Starter Browser öffnen.")
            status = 404
            require(self.path.startswith(API), "Unbekannte Route.")
            route = self.path[len(API):]
            if self.command == "GET":
                if route == "status": return self.reply(200, s.status())
                if route == "settings": return self.reply(200, {"theme": s.settings.read()["theme"]})
                if route == "catalog": return self.reply(200, catalog(s.root))
                if re.fullmatch(r"standard/[a-z][a-z0-9-]{0,63}", route):
                    with s.lock:
                        s.idle(); return self.reply(200, s.standard(route.split("/")[1]))
                if re.fullmatch(r"image/[0-9a-f]{32}", route):
                    raw, mime = s.picture(route.split("/")[1]); return self.reply(200, raw, mime)
                raise ValueError("Unbekannte Leseroute.")
            status = 403
            require(self.command == "POST" and self.headers.get("Origin") == s.origin, "POST verlangt den eigenen Ursprung.")
            status = 400
            length = self.headers.get("Content-Length", "")
            require(re.fullmatch(r"[0-9]{1,9}", length), "Exakte Content-Length erforderlich.")
            upload = re.fullmatch(r"upload/(reveal|background)/(png|svg)", route)
            size = int(length)
            status = 413
            require(0 < size <= (32*1024*1024 if upload else 256*1024), "Anfrage überschreitet Bytegrenze.")
            status = 400
            expected = ("image/png" if upload[2] == "png" else "image/svg+xml") if upload else "application/json"
            require(self.headers.get("Content-Type") == expected, "Unpassender Content-Type.")
            raw = self.rfile.read(size)
            require(len(raw) == size, "Unvollständige Anfrage.")
            body = None if upload else io.json_bytes(raw, 256*1024)
            status = 409
            with s.lock:
                if route == "stop":
                    exact_keys(body, {"confirmed"}); require(body["confirmed"] is True, "Bestätigung fehlt.")
                    s.stop(); return self.reply(200, {"format": FORMAT, "stopping": True})
                if route == "settings":
                    exact_keys(body, {"theme"})
                    return self.reply(200, {"theme": s.settings.update(**body)["theme"]})
                s.idle()
                if upload: result = s.upload(upload[1], upload[2], raw)
                elif route == "detail": result = s.detail(body)
                elif route == "plan": result = s.plan(body)
                elif route == "apply": result = s.apply(body)
                elif route == "recover":
                    exact_keys(body, {"confirmed"}); require(body["confirmed"] is True, "Bestätigung fehlt.")
                    s.invalidate(); result = s.start("recover", {})
                elif route == "discard":
                    exact_keys(body, {"confirmed"}); require(body["confirmed"] is True, "Bestätigung fehlt.")
                    s.invalidate()
                    for row in s.uploads.values(): io.safe(s.work, row["file"]).unlink(missing_ok=True)
                    s.uploads.clear(); s.assets.clear()
                    return self.reply(200, {"format": FORMAT, "discarded": True})
                else:
                    status = 404; raise ValueError("Unbekannte Schreibroutine.")
            return self.reply(202, result)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError): pass
        except Exception as exc:
            try: self.reply(status, {"format": "picross-pe-error-v1", "error": str(exc)[:2048]})
            except OSError: pass

    do_GET = handle_route
    do_POST = handle_route
    do_PUT = handle_route
    do_DELETE = handle_route
    do_OPTIONS = handle_route
