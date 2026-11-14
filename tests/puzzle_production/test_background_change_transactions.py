"""HP-I1b2 nullable binary publication: real PNGs and isolated synthetic catalogs."""
from copy import deepcopy
import base64
import io as streams
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PIL import Image, PngImagePlugin

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tools.puzzle_production import catalog_background as bg, catalog_io as io
from tools.puzzle_production import catalog_publication as pub, catalog_transaction as tx
from tools.puzzle_production import content_registry as cr, operation_diagnostics as diagnostics
from tools.puzzle_production import registration_publication as phased
from tools.puzzle_production.contract import Aborted, InvalidInput, load_json, write_json


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def png(*, color=(90, 40, 20, 128), metadata=True, size=(2304, 576), hidden_rgb=False):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    image.putpixel((0, 0), color)
    if hidden_rgb: image.putpixel((1, 0), (1, 2, 3, 0))
    info = PngImagePlugin.PngInfo()
    if metadata: info.add(b"sRGB", b"\0")
    output = streams.BytesIO()
    image.save(output, format="PNG", pnginfo=info, compress_level=9, optimize=False)
    return output.getvalue()


class NullableBinaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first, cls.second = png(), png(color=(20, 100, 40, 255))
        cls.identifier = "pz-nullable-test"
        cls.name = bg.asset_path(cls.identifier)
        cls.registry = {"format": bg.REGISTRY_FORMAT,
                        "entries": [{"id": cls.identifier, "reveal": "art/reveals/test.png",
                                     "production": {"width": 2, "height": 2}}],
                        "backgrounds": [{"id": cls.identifier,
                                         "source": bg.ref(bg.path(cls.identifier), b"structural unit fixture")}]}

    def journal(self, old, new):
        return {"format": pub.BACKGROUND_FORMAT, "operation": "background-adoption",
                "replacements": {self.name: {"old": pub.binary(old) if old is not None else None,
                                             "new": pub.binary(new) if new is not None else None}}}

    def test_new_format_validates_actual_add_replace_delete_pngs(self):
        for old, new in ((None, self.first), (self.first, None), (self.first, self.second)):
            with self.subTest(old=old is not None, new=new is not None):
                pub.validate_replacements(self.journal(old, new), self.registry)
        journal = self.journal(None, self.first)
        journal["replacements"] = {}
        pub.validate_replacements(journal, self.registry)

    def test_nulls_equal_sides_wrong_targets_and_old_formats_are_closed(self):
        for old, new in ((None, None), (self.first, self.first)):
            with self.assertRaises(InvalidInput):
                pub.validate_replacements(self.journal(old, new), self.registry)
        for name in ("game/art/backgrounds/pz-other.png", "game/art/reveals/test.png", self.name.upper()):
            journal = self.journal(None, self.first)
            journal["replacements"][name] = journal["replacements"].pop(self.name)
            with self.subTest(name=name), self.assertRaises(InvalidInput):
                pub.validate_replacements(journal, self.registry)
        for format_ in (tx.AT_FORMATS["reveal-adoption"], tx.FORMATS["reveal-adoption"],
                        tx.BACKGROUND_FORMATS["reveal-adoption"]):
            for side in ("old", "new"):
                journal = self.journal(self.first, self.second)
                journal.update(format=format_, operation="reveal-adoption")
                pair = journal["replacements"].pop(self.name)
                pair[side] = None
                journal["replacements"]["game/art/reveals/test.png"] = pair
                with self.subTest(format=format_, side=side), self.assertRaises(InvalidInput):
                    pub.validate_replacements(journal, self.registry)

    def test_metadata_dimensions_crc_and_hash_cannot_stand_in_for_png_validation(self):
        invalid = (png(metadata=False), png(size=(20, 20)), png(color=(9, 8, 7, 0)), png(hidden_rgb=True),
                   self.first[:-1] + bytes([self.first[-1] ^ 1]), b"not a PNG")
        for raw in invalid:
            with self.subTest(size=len(raw)), self.assertRaises(InvalidInput):
                pub.validate_replacements(self.journal(None, raw), self.registry)
        journal = self.journal(None, self.first)
        journal["replacements"][self.name]["new"]["sha256"] = "a" * 64
        with self.assertRaises(InvalidInput): pub.validate_replacements(journal, self.registry)
        oversized = {"sha256": "a" * 64, "bytes": 32 * 1024 * 1024 + 1, "base64": ""}
        with self.assertRaises(InvalidInput): pub.binary_shape(oversized)

    def test_base64_padding_only_at_end_even_when_hash_and_length_match(self):
        first = b"a" * (3 * (io.CHUNK // 4) - 1)
        last = b"xyz"
        value = pub.binary(first + last)
        self.assertEqual(pub.decode_binary(value), first + last)
        # Each part is canonical alone, and joined decoded length/hash match;
        # their concatenation still is not one canonical Base64 wire value.
        value["base64"] = base64.b64encode(first).decode() + base64.b64encode(last).decode()
        with self.assertRaisesRegex(InvalidInput, "intermediate Base64 padding"):
            pub.decode_binary(value)

    def test_only_explicit_binary_wire_prefix_gets_larger_journal_limit(self):
        # The oversized text is a size-classification input, not a valid journal.
        value = {"format": pub.BACKGROUND_FORMAT, "padding": "x" * pub.NORMAL_LIMIT}
        raw = pub.journal_bytes(value)
        self.assertGreater(len(raw), pub.NORMAL_LIMIT)
        with tempfile.TemporaryDirectory(prefix="hp-i1b2-limit-") as directory:
            root = Path(directory)
            target = root / tx.LOCK
            target.parent.mkdir()
            target.write_bytes(raw)
            self.assertEqual(pub.read_journal(root), raw)
            target.write_bytes(b" " + raw)
            with self.assertRaises(InvalidInput): pub.read_journal(root)
            # PE-A2 explicitly admits the three current binary journal forms.
            # A supported version is not an unknown-format negative fixture.
            for format_ in (tx.PE_FORMATS["background-adoption"],
                            tx.IMAGE_FORMATS["background-adoption"],
                            tx.IMAGE_FORMATS["reveal-adoption"],
                            tx.IMAGE_FORMATS["editor-images"]):
                with self.subTest(format=format_):
                    current = pub.journal_bytes({**value, "format": format_})
                    self.assertGreater(len(current), pub.NORMAL_LIMIT)
                    target.write_bytes(current)
                    self.assertEqual(pub.read_journal(root), current)
                    target.write_bytes(b" " + current)
                    with self.assertRaises(InvalidInput): pub.read_journal(root)
        for format_ in (tx.BACKGROUND_FORMATS["sync"], tx.PE_FORMATS["sync"],
                        tx.IMAGE_FORMATS["sync"], "picross-background-adoption-journal-v999"):
            with self.subTest(format=format_), self.assertRaises(Aborted):
                pub.journal_bytes({**value, "format": format_})


def compact_background(root):
    """A valid small receipt fixture, never a claim of actual Git retirement."""
    registry = cr.check_checkout(root)
    entry = registry["entries"][0]
    source = bg.load(root, registry, entry)
    if not entry["production"]["test_only"]:
        raise ValueError("Only synthetic prerequisites may be compacted")
    receipt = {"format": bg.RECEIPT_FORMAT, "entry": deepcopy(entry), "integrated_commit": "a" * 40,
               "notice_sha256": io.file_hash(root, ("game/" + entry["reveal"]).rsplit(".", 1)[0] + ".txt"),
               "background": bg.receipt_binding(source, bg.index(registry)[entry["id"]])}
    package = root / entry["production"]["package"]
    shutil.rmtree(package)
    package.mkdir()
    write_json(package / "manifest.json", receipt)
    entry["production"]["package_sha256"] = io.file_hash(package, "manifest.json")
    write_json(root / tx.REGISTRY, registry)
    cr.check_checkout(root)


class BackgroundChangeTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools.puzzle_production import catalog_background_change as change
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        prerequisites = {choice: prepare(owner, choice, registered=True) for choice in ("selected", "none")}
        full_root = prerequisites["selected"].case.root / "unretired-checkout"
        shutil.copytree(prerequisites["selected"].checkout, full_root)
        for fixture in prerequisites.values(): compact_background(fixture.checkout)
        cls.examples = {}
        for key, old, new in (("replace", "selected", "selected"), ("delete", "selected", "none"),
                              ("add", "none", "selected")):
            fixture = prerequisites[old]
            home = fixture.case.root / ("transaction-" + key)
            root = home / "checkout"
            shutil.copytree(fixture.checkout, root)
            work = create_work(owner, root, home / "work", choice=new)
            _, journal, _ = change._build(root, work.request, (root / work.record_path).read_bytes(),
                                          work.payload, external_root=root)
            cls.examples[key] = (root, journal)
        work = create_work(owner, full_root, full_root.parent / "unretired-work", choice="none")
        _, journal, _ = change._build(full_root, work.request, (full_root / work.record_path).read_bytes(), work.payload)
        cls.unretired = (full_root, journal)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1b2-transactions-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.sequence = 0

    def clone(self, key):
        self.sequence += 1
        template, journal = self.examples[key]
        root = self.home / (key + "-" + str(self.sequence))
        shutil.copytree(template, root)
        return root, deepcopy(journal)

    def execute(self, root, journal, **kwargs):
        # Request/HP-W2 derivation was checked when preparing this real journal.
        # These tests exercise the common writer, not the authoring entry point.
        return tx.execute(root, journal, source_check=kwargs.pop("source_check", lambda: None), **kwargs)

    def interrupt(self, root, journal, phase, name=None):
        def stop(actual, target=None):
            if actual == phase and (name is None or target == name):
                raise InterruptedError("TEST ONLY " + phase)
        with patch.object(pub, "checkpoint", side_effect=stop), self.assertRaises(InterruptedError):
            self.execute(root, journal)

    def test_all_transitions_commit_runtime_last_and_preserve_unrelated_sources(self):
        for key in self.examples:
            with self.subTest(transition=key):
                root, journal = self.clone(key)
                before = files(root)
                image = next(iter(journal["replacements"]))
                identifier = Path(image).stem
                writes, checks = [], []
                with patch.object(pub, "checkpoint", side_effect=lambda phase, name=None:
                                  writes.append((phase, name)) if phase in ("P3", "P4", "P5") else None):
                    self.execute(root, journal, source_check=lambda: checks.append((root / tx.LOCK).exists()))
                self.assertEqual(checks, [False, True])
                self.assertFalse(phased.supports(journal))
                self.assertEqual(writes[-1], ("P5", tx.RUNTIME))
                self.assertEqual(journal["additions"], {})
                self.assertIsNone(journal["report_run"])
                allowed = {tx.REGISTRY, tx.RUNTIME, bg.path(identifier), bg.notice_path(identifier), image}
                after = files(root)
                self.assertEqual({n: value for n, value in before.items() if n not in allowed},
                                 {n: value for n, value in after.items() if n not in allowed})
                registry = cr.check_checkout(root)
                active = bg.load(root, registry, registry["entries"][0])
                self.assertEqual(bg.current(active)["image_revision"], 2)
                self.assertEqual(bg.current(active)["decision"]["outcome"], "none" if key == "delete" else "selected")
                self.assertFalse((root / tx.LOCK).exists())

    def test_every_forward_phase_and_repeated_recovery_restore_exact_old_bytes(self):
        for key in self.examples:
            for phase in ("P0", "journal-complete", "P1", "P2", "temp-prefix", "temp-complete", "P3", "P4", "P5", "P6"):
                with self.subTest(transition=key, phase=phase):
                    root, journal = self.clone(key)
                    before = {n: value[0] for n, value in files(root).items()}
                    image = next(iter(journal["replacements"]))
                    target = image if phase in ("temp-prefix", "temp-complete", "P3") and key != "delete" else None
                    self.interrupt(root, journal, phase, target)
                    if phase != "P0":
                        self.assertEqual(cr.recover(root)["status"], "rolled-back")
                    self.assertEqual(before, {n: value[0] for n, value in files(root).items()})
                    cr.check_checkout(root)
            root, journal = self.clone(key)
            before = {n: value[0] for n, value in files(root).items()}
            self.interrupt(root, journal, "P5")
            raw = (root / tx.LOCK).read_bytes()
            def stop(phase, name=None):
                if phase == "R1-binary": raise InterruptedError("TEST ONLY repeated rollback")
            with patch.object(pub, "checkpoint", side_effect=stop), self.assertRaises(InterruptedError): cr.recover(root)
            self.assertEqual((root / tx.LOCK).read_bytes(), raw)
            self.assertEqual(cr.recover(root)["status"], "rolled-back")
            self.assertEqual(before, {n: value[0] for n, value in files(root).items()})

    def test_foreign_bytes_or_missing_nonnullable_binary_preserve_pending_state(self):
        for key in self.examples:
            root, journal = self.clone(key)
            self.interrupt(root, journal, "P3")
            image = next(iter(journal["replacements"]))
            target = root / image
            own = target.read_bytes() if target.exists() else None
            for replacement in (b"FOREIGN PNG", None) if key == "replace" else (b"FOREIGN PNG",):
                if replacement is None: target.unlink()
                else: target.write_bytes(replacement)
                before = files(root)
                with self.subTest(transition=key, missing=replacement is None), self.assertRaises(InvalidInput): cr.recover(root)
                self.assertEqual(before, files(root))
                if own is None: target.unlink(missing_ok=True)
                else: target.write_bytes(own)
            raw = (root / tx.LOCK).read_bytes()
            temporary = root / pub.inventory(journal, raw)[image]
            temporary.write_bytes(b"FOREIGN TEMP")
            before = files(root)
            with self.assertRaises(InvalidInput): cr.recover(root)
            self.assertEqual(before, files(root))
            temporary.unlink()
            self.assertEqual(cr.recover(root)["status"], "rolled-back")

    def test_rollback_uses_current_v2_image_and_preserves_full_original_package(self):
        from tools.puzzle_production import catalog_background_change as change
        root, first = self.clone("replace")
        self.execute(root, first)
        work = create_work(self, root, self.home / "next-work", revision="bg-r02", choice="none")
        _, journal, _ = change._build(root, work.request, (root / work.record_path).read_bytes(), work.payload)
        before = {n: value[0] for n, value in files(root).items()}
        self.interrupt(root, journal, "P3")
        cr.recover(root)
        self.assertEqual(before, {n: value[0] for n, value in files(root).items()})
        image = next(iter(journal["replacements"]))
        self.assertEqual(load_json(root / bg.path(Path(image).stem))["current"]["image_revision"], 2)
        template, journal = self.unretired
        root = self.home / "unretired"
        shutil.copytree(template, root)
        before = {n: value[0] for n, value in files(root).items()}
        self.interrupt(root, journal, "P3")
        self.assertEqual(cr.recover(root)["status"], "rolled-back")
        self.assertEqual(before, {n: value[0] for n, value in files(root).items()})
        cr.check_checkout(root)

    def test_add_and_restore_never_replace_a_late_foreign_file(self):
        for key, recovery in (("add", False), ("delete", True)):
            root, journal = self.clone(key)
            image = next(iter(journal["replacements"]))
            if recovery: self.interrupt(root, journal, "P3")
            original = pub.rename
            def collide(source, target, *, replace):
                if target == root / image:
                    self.assertFalse(replace)
                    target.write_bytes(b"LATE FOREIGN")
                return original(source, target, replace=replace)
            with patch.object(pub, "rename", side_effect=collide), self.assertRaises((InvalidInput, OSError)):
                cr.recover(root) if recovery else self.execute(root, journal)
            self.assertEqual((root / image).read_bytes(), b"LATE FOREIGN")
            self.assertTrue((root / tx.LOCK).exists())

    def test_work_callback_and_300_second_budget_fail_before_mutation(self):
        from tools.puzzle_production import background_request as requests, catalog_background_change as change
        root, journal = self.clone("add")
        before = files(root)
        for point in (1, 2):
            calls = []
            def changed():
                calls.append(None)
                if len(calls) == point: raise InvalidInput("TEST ONLY work changed")
            with self.subTest(point=point), self.assertRaisesRegex(InvalidInput, "work changed"):
                self.execute(root, journal, source_check=changed)
            self.assertEqual(before, files(root))
        for option in ("publication_seconds", "recovery_seconds"):
            with self.assertRaisesRegex(InvalidInput, "registration"):
                self.execute(root, journal, **{option: 1800})
        class Clock:
            now = 100.0
            def __call__(self): return self.now
        clock = Clock()
        def expired_work_check(): clock.now += 301
        with patch.object(io.time, "monotonic", clock), self.assertRaises(Aborted):
            self.execute(root, journal, source_check=expired_work_check)
        self.assertEqual(before, files(root))
        record = next(row["record"] for row in load_json(root / requests.INDEX)["entries"]
                      if row["revision"] == "bg-r01")
        plan = self.home / "held-plan"
        self.assertEqual(change.plan(root, record, plan)["status"], "planned")
        def hold(phase, name=None):
            if phase == "P3": raise InterruptedError("TEST ONLY held catalog journal")
        with patch.object(pub, "checkpoint", side_effect=hold), self.assertRaises(InterruptedError):
            change.adopt(root, plan)
        self.assertTrue((root / tx.LOCK).exists())
        pending = files(root)
        bundle = files(plan)
        with self.assertRaisesRegex(InvalidInput, "recovery required"):
            change.adopt(root, plan)
        self.assertEqual(pending, files(root))
        self.assertEqual(bundle, files(plan))
        with self.assertRaisesRegex(InvalidInput, "registration"):
            cr.recover(root, recovery_seconds=1800)
        self.assertEqual(pending, files(root))
        report = diagnostics.Diagnostics("recover-registration", stderr=streams.StringIO())
        with diagnostics.observe(report): cr.recover(root)
        self.assertEqual(report.operation_class, "background-adoption-recovery")
        self.assertEqual(report.limits[-1]["recovery_seconds"], 300)

    def test_process_kill_and_rekill_recover_both_nullable_directions(self):
        code = """
import os,sys,time
from pathlib import Path
from tools.puzzle_production import catalog_publication as p, catalog_transaction as t, content_registry as c
from tools.puzzle_production.contract import load_json
root,journal,marker,phase,mode=map(Path,sys.argv[1:])
def stop(actual,name=None):
    if actual==str(phase):
        marker.write_text(str(os.getpid()))
        while True: time.sleep(.02)
p.checkpoint=stop
if str(mode)=='publish': t.execute(root,load_json(journal),source_check=lambda:None)
else: c.recover(root)
"""
        for key in ("add", "delete"):
            root, journal = self.clone(key)
            before = {n: value[0] for n, value in files(root).items()}
            saved = self.home / (key + "-journal.json")
            write_json(saved, journal)
            marker = self.home / (key + "-marker")
            for phase, mode in (("P3", "publish"), ("R1-binary", "recover")):
                marker.unlink(missing_ok=True)
                process = subprocess.Popen([sys.executable, "-c", code, str(root), str(saved), str(marker), phase, mode],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    deadline = time.monotonic() + 30
                    while not marker.exists() and process.poll() is None and time.monotonic() < deadline: time.sleep(.02)
                    if not marker.exists():
                        process.kill()
                        out, error = process.communicate(timeout=5)
                        self.fail((out + error).decode(errors="replace"))
                    process.kill()
                    process.wait(timeout=10)
                    self.assertNotEqual(process.returncode, 0)
                finally:
                    if process.poll() is None: process.kill(); process.wait(timeout=10)
                    process.stdout.close(); process.stderr.close()
                self.assertTrue((root / tx.LOCK).exists())
            self.assertEqual(cr.recover(root)["status"], "rolled-back")
            self.assertEqual(before, {n: value[0] for n, value in files(root).items()})
