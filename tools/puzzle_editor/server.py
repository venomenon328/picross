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
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from tools.puzzle_production import catalog_io as io, catalog_metadata, catalog_images
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


def encoded(value): return catalog_images.encoded(value)


def pending(root):
    return io.safe(root, tx.LOCK).exists() or bool(catalog_publication.staging(root))


def catalog(root):
    value = catalog_metadata.view(root)
    runtime_raw = io.read(root, "game/data/registry.json", 8*1024*1024)
    runtime = io.json_bytes(runtime_raw, 8*1024*1024)
    raw = io.read(root, "content/registry.json", 8*1024*1024)
    require(io.json_bytes(raw, 8*1024*1024)["format"] == content_registry.METADATA_FORMAT,
            "Altformat: zuerst ausdrückliche A1-Migration über metadata_cli plan-migration/apply ausführen.")
    token = digest([io.checksum(raw), io.checksum(io.read(root, "content/categories.json", 131072)), io.checksum(runtime_raw)])
    return {**value, "format": FORMAT, "snapshot": token, "runtime_format": runtime["format"],
            "migration_required": runtime["format"] != "picross-runtime-registry-v8"}


class Service:
    def __init__(self, root, *, temporary=None):
        self.root = io.external(root)
        require(self.root.is_dir() and io.safe(self.root, ".git").exists(), "Vorhandenes Picross-Gitcheckout wählen.")
        # Validate only the cheap current indexes. Recovery is allowed even with partial data.
        pending_state = pending(self.root)
        if not pending_state: catalog(self.root)
        self.instance = Instance(self.root)
        self.directory = tempfile.TemporaryDirectory(prefix="picross-pe-", dir=temporary)
        self.work = io.external(self.directory.name)
        require(not self.work.is_relative_to(self.root) and not self.root.is_relative_to(self.work),
                "Editor-Tempablage muss außerhalb des Checkouts liegen.")
        self.secret = secrets.token_hex(32)
        self.origin, self.stopping, self.job = None, False, None
        self.lock = threading.RLock()
        self.thread, self.http, self.server_thread = None, None, None
        self.assets, self.uploads, self.plans, self.details = {}, {}, {}, {}

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
            return {"format": FORMAT, "checkout": str(self.root), "origin": self.origin,
                    "stopping": self.stopping, "recovery_required": pending(self.root), "job": job}

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

    def asset(self, path, *, root=None):
        root = self.root if root is None else root
        raw = io.read(root, path, 32*1024*1024)
        for key, row in self.assets.items():
            if row["root"] == root and row["file"] == path and row["sha256"] == io.checksum(raw): return key
        while len(self.assets) >= 32: self.assets.pop(next(iter(self.assets)))
        key = secrets.token_hex(16)
        self.assets[key] = {"root": root, "file": path, "sha256": io.checksum(raw), "bytes": len(raw)}
        return key

    def picture(self, key):
        require(HEX.fullmatch(key) and key in self.assets, "Bild ist nicht freigegeben. Detail neu laden.")
        row = self.assets[key]
        raw = io.read(row["root"], row["file"], 32*1024*1024)
        require(io.checksum(raw) == row["sha256"] and len(raw) == row["bytes"], "Bildbytes geändert. Neu laden.")
        if row["file"].endswith(".svg"):
            from tools.puzzle_production.target_adapter import validate_reveal
            validate_reveal(io.safe(row["root"], row["file"]), 1, 1)
            require(io.read(row["root"], row["file"], 32*1024*1024) == raw, "SVG während Prüfung geändert.")
        return raw, "image/svg+xml" if row["file"].endswith(".svg") else "image/png"

    def standard(self, identifier):
        view = catalog_metadata.MetadataView(self.root).document()
        require(any(row["id"] == identifier for row in view["categories"]), "Unbekannte aktuelle Kategorie.")
        assets = []
        if identifier in PILOTS:
            assets = [self.asset("game/art/drawing/margins/"+PILOTS[identifier]+"_"+side+".png") for side in ("left", "right")]
        return {"format": FORMAT, "assets": assets}

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
                command = ([sys.executable, "--worker"] if getattr(sys, "frozen", False) else
                           [sys.executable, "-I", "-m", "tools.puzzle_editor.worker"])
                # Isolated Python ignores cwd/PYTHONPATH. Insert only the installed program root.
                if not getattr(sys, "frozen", False):
                    command = [sys.executable, "-I", "-c",
                        "import sys;sys.path.insert(0,sys.argv[1]);from tools.puzzle_editor.worker import main;main(sys.argv[2])", str(CODE)]
                env = os.environ.copy()
                temp = jobdir/"temp"; temp.mkdir()
                env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp), PYTHONNOUSERSITE="1")
                with (jobdir/"operation.log").open("wb") as log:
                    process = subprocess.Popen(command+[str(jobdir/"job.json")], cwd=CODE, env=env,
                        stdout=log, stderr=log, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    while process.poll() is None:
                        time.sleep(.15)
                        with self.lock:
                            self.job["stage"] = "Fachoperation läuft: "+action
                    require(process.returncode == 0, "Fachprozess fehlgeschlagen. Erneut laden; ggf. Recovery prüfen.")
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
                    self.job.update(state="error" if error else "done", stage="Fachoperation gestoppt" if error else "Fachoperation abgeschlossen", result=result, error=error,
                                    elapsed_seconds=round(time.monotonic()-self.job["started"], 1))
                    self.thread = None
        self.thread = threading.Thread(target=execute, name="PE-writer")
        self.thread.start()
        return {"format": FORMAT, "job": jid}

    def detail(self, body):
        exact_keys(body, {"id", "snapshot"})
        listing = catalog(self.root)
        require(body["snapshot"] == listing["snapshot"], "Katalog veraltet. Neu laden.")
        require(any(e["id"] == body["id"] for e in listing["entries"]), "Unbekannte Rätsel-ID.")
        def complete(result, work):
            self.assets.clear()
            row = result["detail"]["runtime"]
            pictures = {"reveal": [self.asset("game/"+row["reveal"])], "background": []}
            bg = row["background"]
            if bg["status"] == "selected": pictures["background"] = [self.asset("game/"+bg["asset"]["file"])]
            elif bg["status"] in ("legacy", "standard") and row["category_id"] in PILOTS:
                pictures["background"] = [self.asset("game/art/drawing/margins/"+PILOTS[row["category_id"]]+"_"+side+".png") for side in ("left", "right")]
            self.details = {body["id"]: result["snapshot"]}
            result["pictures"] = pictures
            return result
        return self.start("detail", {"id": body["id"]}, complete=complete)

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
            self.uploads[key] = ref
            asset = self.asset(name, root=self.work)
            return {"upload": key, "asset": asset, "sha256": ref["sha256"], "bytes": ref["bytes"]}
        return self.start("validate_upload", {"file": name, "kind": kind}, work=self.work, complete=complete)

    def plan(self, body, migration=False):
        self.idle(); self.purge(); self.invalidate()
        if migration:
            exact_keys(body, {"snapshot"})
            require(body["snapshot"] == catalog(self.root)["snapshot"], "Katalog veraltet.")
            action, identifier, payload = "migration", None, {"catalog_snapshot": body["snapshot"]}
        else:
            exact_keys(body, {"snapshot", "id", "metadata", "text", "profile", "reveal", "background", "authority"})
            identifier = body["id"]
            if identifier is None:
                require(body["snapshot"] == catalog(self.root)["snapshot"], "Katalog veraltet.")
                require(all(body[k] is None for k in ("text", "profile", "reveal", "background", "authority")), "Kategorien separat speichern.")
                require(isinstance(body["metadata"], list) and len(body["metadata"]) == 1 and
                        body["metadata"][0].get("op") in ("category_create", "category_rename", "category_delete"), "Eine Kategorienaktion erwartet.")
                bound = None
            else:
                require(isinstance(identifier, str) and identifier in self.details and self.details[identifier] == body["snapshot"], "Detailbindung fehlt/veraltet.")
                bound = body["snapshot"]
            authority = body["authority"]
            if authority is not None:
                exact_keys(authority, {"actor", "statement", "confirmed", "provenance"})
                require(authority["confirmed"] is True, "Bewusste manuelle Bestätigung fehlt.")
            request = dict(body); request.pop("snapshot")
            uploads = {}
            selected = []
            for kind in ("reveal", "background"):
                part = body[kind]
                if part is None: continue
                exact_keys(part, {"upload", "provenance"} | ({"status"} if kind == "background" else set()))
                key = part["upload"]
                if key is None:
                    require(kind == "background" and part["status"] in ("none", "standard") and part["provenance"] is None, "Bilddatei fehlt.")
                    ref = None
                else:
                    require(key in self.uploads and self.uploads[key]["kind"] == kind, "Import fehlt/abgelaufen oder falscher Bildtyp.")
                    row = self.uploads[key]
                    raw = io.read(self.work, row["file"], 32*1024*1024)
                    require(io.checksum(raw) == row["sha256"] and len(raw) == row["bytes"], "Importbytes geändert.")
                    ref = {k: row[k] for k in ("file", "sha256", "bytes")}
                    uploads[row["file"]] = base64.b64encode(raw).decode()
                    selected.append(key)
                request[kind] = {"asset": ref, "provenance": part["provenance"], **({"status": part["status"]} if kind == "background" else {})}
            action = "plan"
            payload = {"bound_snapshot": bound, "request": request, "uploads": uploads,
                       "catalog_snapshot": body["snapshot"] if identifier is None else None,
                       "confirmed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        def complete(result, work):
            key = secrets.token_hex(16)
            hashes = {p.relative_to(work).as_posix(): io.file_hash(work, p.relative_to(work).as_posix()) for p in work.rglob("*") if p.is_file()}
            self.plans[key] = {"work": str(work), "kind": result["kind"], "id": identifier,
                               "expires": time.monotonic()+600, "hashes": hashes,
                               "uploads": [] if migration else selected}
            return {"plan": key, "id": identifier, **result, "expires_seconds": 600}
        return self.start(action, payload, complete=complete)

    def apply(self, body):
        self.idle(); self.purge()
        exact_keys(body, {"plan", "id"})
        require(body["plan"] in self.plans, "Plan fehlt/abgelaufen. Erneut prüfen.")
        row = self.plans[body["plan"]]
        require(row["id"] == body["id"], "Ziel-ID stimmt nicht mit dem Plan überein.")
        work = io.external(row["work"])
        actual = {p.relative_to(work).as_posix(): io.file_hash(work, p.relative_to(work).as_posix()) for p in work.rglob("*") if p.is_file()}
        require(actual == row["hashes"], "Planbundle geändert.")
        for key in row["uploads"]:
            require(key in self.uploads, "Import abgelaufen.")
            item = self.uploads[key]
            require(io.file_hash(self.work, item["file"]) == item["sha256"], "Importbytes geändert.")
        def complete(result, ignored):
            self.details.clear()
            return result
        return self.start("apply", {"kind": row["kind"]}, work=work, complete=complete)

    def stop(self):
        with self.lock: self.stopping = True

    def close(self):
        self.stop()
        active = self.thread
        if active: active.join()
        if self.http:
            self.http.shutdown(); self.http.server_close()
        if self.server_thread: self.server_thread.join()
        self.directory.cleanup()
        self.instance.close()


class HTTP(ThreadingHTTPServer):
    daemon_threads = False
    request_queue_size = 8

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
                s.idle()
                if upload: result = s.upload(upload[1], upload[2], raw)
                elif route == "detail": result = s.detail(body)
                elif route == "plan": result = s.plan(body)
                elif route == "migration": result = s.plan(body, migration=True)
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
