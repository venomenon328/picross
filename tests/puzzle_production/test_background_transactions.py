"""HP-I1b1 source boundaries on real synthetic v6 exports and filesystem writes."""
from copy import deepcopy
import hashlib
import io as streams
import json
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tools.puzzle_production import authoring_package as ap, catalog_background as bg
from tools.puzzle_production import catalog_io as io, catalog_publication as pub, catalog_transaction as tx
from tools.puzzle_production import content_registry as cr, operation_diagnostics as diagnostic
from tools.puzzle_production import registration_publication as phased, registration_verification as verification
from tools.puzzle_production import target_adapter as adapter
from tools.puzzle_production.contract import Aborted, InvalidInput, write_json
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, difficulty_for_export, isolated_checkout


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def capability(root, enabled):
    write_json(root / bg.CAPABILITY, {"format": bg.CAPABILITY_FORMAT, "runtime_format": bg.RUNTIME_FORMAT,
        "profile_id": "picross-background-png2304-v1", "enabled": enabled})


class BackgroundTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.examples = {}
        for choice in ("selected", "none"):
            f = prepare(owner, choice)
            f.checked = difficulty_for_export(f.export)
            def capture(root, journal, additions, **kwargs):
                f.journal = deepcopy(journal)
                stage = kwargs["_verification"].stage
                f.additions = {n: f.export / p.relative_to(stage) for n, p in additions.items()}
            with patch.object(tx, "execute", side_effect=capture):
                cr.registration(f.export, f.checkout, apply=True, difficulty=f.checked)
            cls.examples[choice] = f

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1b1-transaction-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.clone("selected", "checkout")

    def clone(self, choice, name):
        root = self.home / name
        shutil.copytree(self.examples[choice].checkout, root)
        return root

    def execute(self, choice="selected", **kwargs):
        f = self.examples[choice]
        return pub.execute(self.root, deepcopy(f.journal), f.additions, **kwargs)

    def test_selected_none_sources_and_phased_publication(self):
        for choice in ("selected", "none"):
            with self.subTest(choice=choice):
                self.root = self.clone(choice, choice)
                f = self.examples[choice]
                j = f.journal
                self.assertEqual(j["format"], tx.BACKGROUND_FORMATS["registration"])
                self.assertEqual(set(j), {"format", "operation", "old", "new", "retained", "additions", "report_run", "replacements"})
                self.assertEqual(j["replacements"], {})
                identifier = f.manifest["definition_id"]
                for name in (bg.path(identifier), bg.notice_path(identifier), bg.CAPABILITY):
                    self.assertIn(name, j["old"])
                    self.assertIn(name, j["new"])
                self.assertEqual(j["old"][bg.CAPABILITY], j["new"][bg.CAPABILITY])
                self.assertIsNone(j["old"][bg.path(identifier)])
                self.assertEqual(bg.asset_path(identifier) in j["additions"], choice == "selected")
                boundaries = []
                with patch.object(pub, "checkpoint", side_effect=lambda phase, name=None: boundaries.append(phase) if phase.startswith("G") else None):
                    self.execute(choice)
                self.assertEqual(boundaries, ["G0", "G2", "G5a", "G5b", "G6"])
                registry = cr.check_checkout(self.root, replay=True)
                runtime = json.loads((self.root / tx.RUNTIME).read_bytes())
                self.assertEqual(registry["format"], bg.REGISTRY_FORMAT)
                self.assertEqual(runtime["entries"][0]["background"]["status"], choice)
                captured = tx.capture(self.root)
                self.assertIn(bg.path(identifier), captured["texts"])
                self.assertIn(bg.notice_path(identifier), captured["texts"])
                self.assertEqual(bg.asset_path(identifier) in captured["retained"], choice == "selected")
                self.assertEqual(set(captured["namespaces"]), {"reveals", "difficulty", "added", "packages", "backgrounds", "background_assets"})
                self.assertFalse((self.root / tx.LOCK).exists())

    def test_capability_change_at_every_global_boundary_preserves_state(self):
        for boundary in ("G0", "G2", "G5a", "G5b", "G6"):
            with self.subTest(boundary=boundary):
                self.root = self.clone("selected", boundary)
                observed = []
                def change(phase, name=None):
                    if phase == boundary:
                        capability(self.root, False)
                        observed.append(files(self.root))
                with patch.object(pub, "checkpoint", side_effect=change), self.assertRaises(InvalidInput):
                    self.execute()
                self.assertEqual(len(observed), 1)
                self.assertEqual(files(self.root), observed[0])
                self.assertEqual((self.root / tx.LOCK).exists(), boundary != "G0")

    def test_none_and_foreign_background_namespace_cannot_hide_unbound_bytes(self):
        f = self.examples["none"]
        identifier = f.manifest["definition_id"]
        for name in (bg.asset_path(identifier), bg.notice_path(identifier), bg.PATH + "/pz-foreign.json"):
            with self.subTest(name=name):
                self.root = self.clone("none", "namespace-" + str(len(list(self.home.iterdir()))))
                target = self.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"FOREIGN")
                before = files(self.root)
                with self.assertRaises(InvalidInput): self.execute("none")
                self.assertEqual(files(self.root), before)
                self.assertFalse((self.root / tx.LOCK).exists())

    def test_package_source_and_runtime_interruptions_have_repeatable_rollback(self):
        identifier = self.examples["selected"].manifest["definition_id"]
        for failure in ("crash-package", "crash-" + bg.path(identifier), "crash-runtime"):
            with self.subTest(failure=failure):
                self.root = self.clone("selected", "crash-" + str(len(list(self.home.iterdir()))))
                before = {n: row[0] for n, row in files(self.root).items()}
                with self.assertRaises(InterruptedError): self.execute(fail_step=failure)
                raw = (self.root / tx.LOCK).read_bytes()
                def stop(phase, name=None):
                    if phase == "R1-addition": raise InterruptedError("controlled recovery interruption")
                with patch.object(pub, "checkpoint", side_effect=stop), self.assertRaises(InterruptedError):
                    cr.recover(self.root)
                self.assertEqual((self.root / tx.LOCK).read_bytes(), raw)
                boundaries = []
                with patch.object(pub, "checkpoint", side_effect=lambda phase, name=None: boundaries.append(phase) if phase.startswith("GR") else None), \
                        patch.object(verification._Verification, "written", side_effect=AssertionError("No proof context in recovery")):
                    self.assertEqual(cr.recover(self.root)["status"], "rolled-back")
                self.assertEqual(boundaries, ["GR0", "GR2"])
                self.assertEqual({n: row[0] for n, row in files(self.root).items()}, before)

    def test_new_staging_recovery_binds_capability_and_keeps_foreign_bytes(self):
        def stop(phase, name=None):
            if phase == "journal-complete": raise InterruptedError("complete staging before lock")
        with patch.object(pub, "checkpoint", side_effect=stop), self.assertRaises(InterruptedError): self.execute()
        self.assertFalse((self.root / tx.LOCK).exists())
        self.assertEqual(len(pub.staging(self.root)), 1)
        capability(self.root, False)
        before = files(self.root)
        with self.assertRaises(InvalidInput): cr.recover(self.root)
        self.assertEqual(files(self.root), before)
        capability(self.root, True)
        self.assertEqual(cr.recover(self.root)["status"], "rolled-back")
        self.assertFalse(pub.staging(self.root))

    def test_existing_background_png_is_a_retained_authority(self):
        self.execute()
        snapshot = tx.capture(self.root)
        journal = tx.prepare(self.root, snapshot, {}, operation="sync")
        identifier = self.examples["selected"].manifest["definition_id"]
        name = bg.asset_path(identifier)
        self.assertEqual(journal["retained"][name], snapshot["retained"][name])
        (self.root / name).write_bytes(b"FOREIGN")
        before = files(self.root)
        with self.assertRaises(InvalidInput): pub.execute(self.root, journal)
        self.assertEqual(files(self.root), before)

    def test_ri_b_binds_background_addition_and_exact_zip_limit_through_writer(self):
        f = self.examples["selected"]
        package = json.loads(f.journal["new"][tx.REGISTRY])["entries"][0]["production"]["package"]
        # A canonical empty transport root is valid both before/after Git or
        # file publication. It must not become a false RI-B/C conflict.
        external = self.root / package / "external"
        external.mkdir(parents=True)
        read, write = io.read, pub.write
        zip_reads, zip_writes = [], []
        def bounded(root, name, limit, **kwargs):
            if name == "input/package.zip" or name.endswith("/input/package.zip") or name == "package.zip" and Path(root).name == "input":
                zip_reads.append(limit)
                self.assertEqual(limit, ap.MAX_ZIP)
            return read(root, name, limit, **kwargs)
        def publish(root, name, *args, **kwargs):
            if name.endswith("/input/package.zip"):
                zip_writes.append(kwargs["limit"])
                self.assertEqual(kwargs["limit"], ap.MAX_ZIP)
            return write(root, name, *args, **kwargs)
        d = diagnostic.Diagnostics("register", stderr=streams.StringIO())
        with patch.object(io, "read", side_effect=bounded), patch.object(pub, "write", side_effect=publish), diagnostic.observe(d):
            self.assertEqual(cr.registration(f.export, self.root, apply=True, difficulty=f.checked)["status"], "registered")
        self.assertTrue(zip_reads)
        self.assertEqual(zip_writes, [ap.MAX_ZIP])
        self.assertEqual(d.counters["full_candidate_proof_checks"], 2)
        self.assertEqual(d.counters["verified_package_reuses"], 2)
        self.assertEqual(d.counters["catalog_boundaries"], 5)
        self.assertFalse(verification._active)
        self.assertEqual(list(external.iterdir()), [])

    def test_historical_v6_journal_accepts_only_inactive_false_capability(self):
        base = isolated_checkout(self.home / "legacy")
        capability(base, False)
        approval = self.home / "legacy-approval.json"
        approve(FIXTURES / "direct-color", approval)
        exported = self.home / "legacy-export"
        adapter.export(FIXTURES / "direct-color", exported, name="TEST ONLY", revision=1, stem="legacy", save_slot="legacy",
                       approval_path=approval, category_id="voegel", categories_path=base / "content/categories.json")
        captured = {}
        def capture(root, journal, additions, **kwargs):
            stage = kwargs["_verification"].stage
            captured["additions"] = {n: exported / p.relative_to(stage) for n, p in additions.items()}
            changes = {n: raw.encode() if raw is not None else None for n, raw in journal["new"].items() if raw != journal["old"][n]}
            captured["journal"] = tx.prepare(root, tx.capture(root), changes, operation="registration",
                                             additions=captured["additions"], generation="sd2")
        with patch.object(tx, "execute", side_effect=capture):
            cr.registration(exported, base, apply=True, difficulty=difficulty_for_export(exported))
        self.assertEqual(captured["journal"]["format"], tx.FORMATS["registration"])
        self.assertNotIn(bg.CAPABILITY, captured["journal"]["old"])
        for mutation in ("false", "missing", "true", "foreign-source"):
            with self.subTest(mutation=mutation):
                root = self.home / ("legacy-" + mutation)
                shutil.copytree(base, root)
                with self.assertRaises(InterruptedError):
                    pub.execute(root, deepcopy(captured["journal"]), captured["additions"], fail_step="crash-index")
                if mutation == "missing": (root / bg.CAPABILITY).unlink()
                elif mutation == "true": capability(root, True)
                elif mutation == "foreign-source":
                    target = root / bg.PATH / "pz-foreign.json"
                    target.parent.mkdir(parents=True)
                    target.write_bytes(b"FOREIGN")
                before = files(root)
                if mutation in ("true", "foreign-source"):
                    with self.assertRaises(InvalidInput): cr.recover(root)
                    self.assertEqual(files(root), before)
                else:
                    self.assertEqual(cr.recover(root)["status"], "rolled-back")
                    self.assertEqual(cr.check_checkout(root)["entries"], [])


class OriginalZipLimitTests(unittest.TestCase):
    def test_only_exact_declared_original_gets_128_mib_inventory_allowance(self):
        # This is an I/O-policy unit case, never a certified production fixture.
        # The sparse oversized byte file is temporary and is not passed to ZA-1.
        with tempfile.TemporaryDirectory(prefix="hp-i1b1-size-") as directory:
            root = Path(directory)
            original = root / "input/package.zip"
            original.parent.mkdir()
            size = ap.MAX_FILE + 1
            with original.open("wb") as stream: stream.truncate(size)
            checksum = hashlib.sha256()
            with original.open("rb") as stream:
                for block in iter(lambda: stream.read(io.CHUNK), b""): checksum.update(block)
            write_json(root / "manifest.json", {"format": "picross-target-export-v6",
                "input": {"original_package": {"file": "input/package.zip", "bytes": size, "sha256": checksum.hexdigest()},
                          "external_root": "external", "discarded_files": []},
                "files": {"input/package.zip": checksum.hexdigest()}})
            with self.assertRaises(Aborted): io.file_hash(root, "input/package.zip")
            with self.assertRaises(InvalidInput): ap.file_table(root, time.monotonic() + 300)
            self.assertEqual(io.export_limit(root, "input/package.zip"), ap.MAX_ZIP)
            self.assertEqual(verification.inventory(root)[1]["input/package.zip"], checksum.hexdigest())
            original.rename(root / "input/other.zip")
            self.assertEqual(io.export_limit(root, "input/other.zip"), ap.MAX_FILE)
            with self.assertRaises(Aborted): io.read(root, "input/other.zip", io.export_limit(root, "input/other.zip"))
            with self.assertRaises(InvalidInput): verification.inventory(root)


if __name__ == "__main__":
    unittest.main()
