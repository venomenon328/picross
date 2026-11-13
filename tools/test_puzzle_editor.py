"""Small change-scoped HTTP/ownership regressions; no catalog, browser or engine replay."""
import http.client
import json
from pathlib import Path
import tempfile
import time
import unittest

from tools.puzzle_editor.server import Service, API
from tools.puzzle_production.contract import write_json


def fixture(root):
    (root/".git").mkdir(parents=True)
    write_json(root/"content/categories.json", {"format": "picross-categories-v1", "categories": []})
    write_json(root/"content/registry.json", {"format": "picross-content-registry-v4", "entries": [], "metadata": [], "backgrounds": []})
    write_json(root/"game/data/registry.json", {"format": "picross-runtime-registry-v7", "categories": [], "entries": []})
    return root


class EditorHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pe-http-")
        self.home = Path(self.temp.name)
        self.root = fixture(self.home/"checkout")
        self.service = Service(self.root, temporary=self.home)
        self.service.bind()

    def tearDown(self):
        self.service.close(); self.temp.cleanup()

    def call(self, route, body=None, *, token=True, origin=None, method=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.service.http.server_port, timeout=30)
        args = {"X-PE-Session": self.service.secret} if token else {}
        if body is not None:
            args.update({"Origin": self.service.origin, "Content-Type": "application/json"})
            if not isinstance(body, bytes): body = json.dumps(body).encode()
        if origin is not None: args["Origin"] = origin
        args.update(headers or {})
        conn.request(method or ("POST" if body is not None else "GET"), route, body, args)
        response = conn.getresponse(); raw = response.read(); status = response.status
        all_headers = dict(response.getheaders()); conn.close()
        return status, raw, all_headers

    def test_loopback_auth_origin_host_and_fixed_resources(self):
        self.assertEqual(self.service.http.server_address[0], "127.0.0.1")
        for args in ({"token": False}, {"origin": "https://evil.invalid"}, {"headers": {"Host": "localhost"}},
                     {"headers": {"Sec-Fetch-Site": "cross-site"}}):
            self.assertEqual(self.call(API+"catalog", **args)[0], 403)
        status, _, headers = self.call("/", token=False)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        for path in ("/../content/registry.json", "/%2e%2e/", "/api/pe/v1/catalog?path=x", "/tools/server.py"):
            self.assertGreaterEqual(self.call(path)[0], 400)
        self.assertEqual(self.call(API+"catalog", method="PUT")[0], 403)

    def test_strict_json_body_and_upload_bound_before_mutation(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for body in (b'{"confirmed":true,"confirmed":false}', b'{"confirmed":NaN}', b'{"confirmed":true,"path":"x"}'):
            self.assertGreaterEqual(self.call(API+"discard", body)[0], 400)
        self.assertEqual(self.call(API+"discard", b"{}", headers={"Content-Length": "999999999"})[0], 413)
        self.assertEqual(self.call(API+"discard", b"{}", headers={"Transfer-Encoding": "chunked"})[0], 400)
        self.assertEqual(self.call(API+"discard", {"confirmed": True}, origin="https://evil.invalid")[0], 403)
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}, before)

    def test_checkout_single_instance_and_reopen_after_drain(self):
        with self.assertRaisesRegex(ValueError, "bereits"):
            Service(self.root, temporary=self.home)
        work = self.service.work
        self.service.close()
        self.assertFalse(work.exists())
        self.service = Service(self.root, temporary=self.home); self.service.bind()
        self.assertEqual(self.call(API+"catalog")[0], 200)

    def test_actual_category_plan_apply_and_stale_stop(self):
        _, raw, _ = self.call(API+"catalog"); listing = json.loads(raw)
        body = {"snapshot": listing["snapshot"], "id": None,
                "metadata": [{"op": "category_create", "name": "Testgruppe"}],
                "text": None, "profile": None, "reveal": None, "background": None, "authority": None}
        status, raw, _ = self.call(API+"plan", body)
        self.assertEqual(status, 202, raw)
        for _ in range(200):
            value = json.loads(self.call(API+"status")[1])["job"]
            if value["state"] != "running": break
            time.sleep(.05)
        self.assertEqual(value["state"], "done", value)
        plan = value["result"]
        self.assertEqual(plan["kind"], "metadata")
        self.assertEqual(self.call(API+"apply", {"plan": plan["plan"], "id": "foreign"})[0], 409)
        status, raw, _ = self.call(API+"apply", {"plan": plan["plan"], "id": None})
        self.assertEqual(status, 202, raw)
        for _ in range(200):
            value = json.loads(self.call(API+"status")[1])["job"]
            if value["state"] != "running": break
            time.sleep(.05)
        self.assertEqual(value["state"], "done", value)
        self.assertEqual(json.loads(self.call(API+"catalog")[1])["categories"][0]["name"], "Testgruppe")
        self.assertEqual(self.call(API+"plan", body)[0], 409)

    def test_image_ref_rejects_changed_bytes_and_hardlinks(self):
        own = self.service.work/"test.png"; own.write_bytes(b"first")
        key = self.service.asset("test.png", root=self.service.work)
        own.write_bytes(b"foreign")
        self.assertGreaterEqual(self.call(API+"image/"+key)[0], 400)
        import os
        os.link(own, self.service.work/"alias.png")
        with self.assertRaises(ValueError): self.service.asset("test.png", root=self.service.work)

    def test_recovery_without_pending_journal_validates_and_does_not_write(self):
        from tools.puzzle_editor.worker import run
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(run(self.root, self.service.work, "recover", {})["status"], "noop")
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}, before)

    def test_bundle_inventory_rejects_missing_and_changed_program_files(self):
        from tools.puzzle_editor.bundle import verify
        from tools.puzzle_production.catalog_io import checksum
        package = self.home/"program"; package.mkdir()
        (package/"app.js").write_bytes(b"trusted program")
        write_json(package/"inventory.json", {"commit": "a"*40, "files": [{"file": "app.js", "bytes": 15, "sha256": checksum(b"trusted program")}]})
        self.assertEqual(verify(package), "a"*40)
        (package/"app.js").write_bytes(b"foreign")
        with self.assertRaises(ValueError): verify(package)

    def test_catalog_cannot_pair_old_labels_with_a_new_snapshot(self):
        from unittest.mock import patch
        from tools.puzzle_editor.server import catalog, catalog_metadata
        original = catalog_metadata.view
        def concurrent(root):
            value = original(root)
            path = root/"content/categories.json"
            path.write_bytes(path.read_bytes()+b"\n")
            return value
        with patch.object(catalog_metadata, "view", side_effect=concurrent):
            with self.assertRaisesRegex(ValueError, "Listenaufbau"): catalog(self.root)

    def test_native_status_error_keeps_the_shutdown_tick(self):
        from unittest.mock import Mock
        from tools.puzzle_editor.desktop import Window
        window = Window.__new__(Window)
        window.closing = False
        window.stop_failed = False
        window.service = Mock(stopping=False)
        window.service.status.side_effect = ValueError("concurrent source error")
        window.window = Mock(); window.status = Mock()
        window.poll()
        window.window.after.assert_called_once_with(250, window.poll)
        self.assertIn("concurrent source error", window.status.set.call_args.args[0])
        window.closing, window.drained, window.stop_error = True, True, None
        window.poll()
        window.window.destroy.assert_called_once()


if __name__ == "__main__": unittest.main()
