"""Small fixed PE-A2 source tests; no real catalog, image generation or solver replay."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image

from tools.puzzle_production import catalog_background as bg, catalog_io as io
from tools.puzzle_production import content_registry as registry, reveal_source as at
from tools.puzzle_production import editor_image_source as images
from tools.puzzle_production.contract import canonical_bytes, digest, InvalidInput, load_json, write_json
from tests.puzzle_production.catalog_fixtures import registered


PROVENANCE = {"author": "Synthetic fixture", "usage_basis": "Project test data",
              "source": "Fixed local geometry", "changes": "Prepared image, no conversion"}
DECISION = {"actor": "TEST ONLY", "timestamp_utc": "2026-11-12T12:00:00Z",
            "statement": "Explicit synthetic manual image selection."}
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect x="8" y="8" width="64" height="64" fill="#369"/></svg>\n'


def png(size=(80, 80), color=(50, 120, 160, 255)):
    value = Image.new("RGBA", size, color)
    value.putpixel((0, 0), (0, 0, 0, 0))
    stream = BytesIO()
    value.save(stream, format="PNG")
    return stream.getvalue()


def rehash(value):
    value["record_hash"] = digest({key: item for key, item in value.items() if key != "record_hash"})
    return value


class EditorImageSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory()
        cls.home = Path(cls.shared.name)
        registered(cls.home, stem="pe_source", save_slot="pe_source")

    @classmethod
    def tearDownClass(cls):
        cls.shared.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "checkout"
        shutil.copytree(self.home / "base", self.root)
        self.catalog = load_json(self.root / "content/categories.json")
        self.registry = load_json(self.root / registry.REGISTRY)
        self.entry = self.registry["entries"][0]

    def publish_reveal(self, source, raw):
        write_json(self.root / at.path(self.entry["id"]), source)
        selected = source["current"]["asset"]["file"]
        for name in images.reveal_candidates(self.entry) - {selected}:
            (self.root / name).unlink(missing_ok=True)
        (self.root / selected).write_bytes(raw)
        (self.root / at.identity(self.entry)["notice"]).write_bytes(source["current"]["notice"]["text"].encode("utf-8"))

    def publish_background(self, source, raw=None, notice=None):
        write_json(self.root / bg.path(self.entry["id"]), source)
        self.registry["backgrounds"] = [{"id": self.entry["id"], "source": bg.ref(bg.path(self.entry["id"]), bg.encoded(source))}]
        write_json(self.root / registry.REGISTRY, self.registry)
        for name, data in ((bg.asset_path(self.entry["id"]), raw), (bg.notice_path(self.entry["id"]), notice)):
            path = self.root / name
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)

    def approval(self, source, raw, notice):
        return {"format": at.APPROVAL, "id": self.entry["id"],
            "image_revision": source["current"]["image_revision"] + 1,
            "definition_sha256": source["binding"]["entry"]["production"]["definition_sha256"],
            "previous_reveal_sha256": source["current"]["asset"]["sha256"],
            "reveal_sha256": io.checksum(raw), "notice_sha256": notice["sha256"],
            **DECISION, "checks": dict.fromkeys(("reveal_approved", "motif_raster_consistent", "final_editorial_approved"), True),
            "test_only": True}

    def test_format_switch_preserves_receipt_definition_origin_and_true_noop(self):
        definition = (self.root / "game" / self.entry["definition"]).read_bytes()
        receipt = (self.root / self.entry["production"]["package"] / "manifest.json").read_bytes()
        asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
        source = images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, DECISION)
        self.assertEqual(source["format"], images.REVEAL_FORMAT)
        self.assertIsNone(source["origin"]["source"])
        self.assertEqual(source["current"]["image_revision"], 1)
        self.assertFalse((self.root / at.path(self.entry["id"])).exists())
        self.publish_reveal(source, SVG)
        resolved = at.resolve(self.root, self.entry, self.catalog)
        self.assertEqual(resolved["effective_reveal_ref"], asset)
        self.assertEqual(resolved["effective_reveal"], asset["file"].removeprefix("game/"))
        later = {**DECISION, "actor": "Another tester", "timestamp_utc": "2026-11-13T12:00:00Z"}
        self.assertEqual(images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, later), source)
        self.assertEqual((self.root / "game" / self.entry["definition"]).read_bytes(), definition)
        self.assertEqual((self.root / self.entry["production"]["package"] / "manifest.json").read_bytes(), receipt)
        (self.root / "game" / self.entry["reveal"]).write_bytes(png())
        with self.assertRaisesRegex(InvalidInput, "Inactive reveal"):
            at.resolve(self.root, self.entry, self.catalog)

    def test_closed_sources_reject_rehashed_wrong_bindings_and_manual_claims(self):
        asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
        source = images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, DECISION)
        mutations = [lambda v: v.update(extra=True),
            lambda v: v["origin"].update(source=deepcopy(source)),
            lambda v: v["current"]["asset"].update(file="game/art/content/foreign.svg"),
            lambda v: v["binding"]["identity"]["definition"].update(sha256="0" * 64),
            lambda v: v["current"]["authority"]["decision"].update(timestamp_utc="2026-02-30T12:00:00Z"),
            lambda v: v["current"]["authority"]["provenance"].update(author="Forged author"),
            lambda v: v["current"].update(image_revision=True),
            lambda v: v["current"]["authority"].update(approval={}),
            lambda v: v["binding"]["entry"].update(save_slot="foreign")]
        for mutate in mutations:
            altered = deepcopy(source)
            mutate(altered)
            with self.subTest(mutate=mutate), self.assertRaises(InvalidInput):
                images.validate(rehash(altered), self.catalog)

    def test_legacy_background_all_transitions_keep_actual_production_receipt(self):
        write_json(self.root / bg.CAPABILITY, {"format": bg.CAPABILITY_FORMAT, "runtime_format": bg.RUNTIME_FORMAT,
                                             "profile_id": "picross-background-png2304-v1", "enabled": True})
        raw = png((2304, 576))
        receipt_path = self.root / self.entry["production"]["package"] / "manifest.json"
        receipt = receipt_path.read_bytes()
        original = None
        previous_revision = 0
        for status in ("selected", "standard", "none", "selected", "none", "standard", "selected"):
            with self.subTest(status=status, previous_revision=previous_revision):
                asset = bg.ref(bg.asset_path(self.entry["id"]), raw) if status == "selected" else None
                provenance = PROVENANCE if status == "selected" else None
                old_notice_path = self.root / bg.notice_path(self.entry["id"])
                prefix = old_notice_path.read_bytes() if old_notice_path.exists() else b""
                source = images.manual_background(self.root, self.registry, self.entry, status, asset, provenance, DECISION)
                self.assertEqual(source["current"]["image_revision"], previous_revision + 1)
                if original is None:
                    original = deepcopy(source["origin"])
                self.assertEqual(source["origin"], original)
                self.assertIsNone(bg.initial(source))
                notice = images.manual_notice(prefix, PROVENANCE, DECISION) if status == "selected" else None
                self.publish_background(source, raw if status == "selected" else None, notice)
                self.assertEqual(bg.load(self.root, self.registry, self.entry), source)
                self.assertEqual(bg.projection(self.registry, {bg.path(self.entry["id"]): bg.encoded(source)})[self.entry["id"]]["status"], status)
                self.assertEqual(images.manual_background(self.root, self.registry, self.entry, status, asset, provenance,
                                                         {**DECISION, "actor": "Repeat"}), source)
                self.assertEqual(receipt_path.read_bytes(), receipt)
                previous_revision += 1

    def test_explicit_standard_needs_no_enabled_capability_and_broken_capability_is_error(self):
        source = images.manual_background(self.root, self.registry, self.entry, "standard", None, None, DECISION)
        self.publish_background(source)
        self.assertEqual(source["current"]["image_revision"], 1)
        self.assertEqual(bg.load(self.root, self.registry, self.entry), source)
        write_json(self.root / bg.CAPABILITY, {"enabled": False})
        with self.assertRaises(InvalidInput):
            bg.load(self.root, self.registry, self.entry)

    def test_manual_then_real_at_then_raster_rebind_retains_adoption_definition(self):
        asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
        manual = images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, DECISION)
        image = png(color=(150, 20, 80, 255))
        next_asset = bg.ref("game/" + self.entry["reveal"], image)
        declaration = self.approval(manual, image, manual["current"]["notice"])
        adopted = images.adopt_reveal(manual, next_asset, manual["current"]["notice"], PROVENANCE, declaration, self.catalog)
        current_entry = deepcopy(adopted["binding"]["entry"])
        definition = load_json(self.root / "game" / current_entry["definition"])
        definition["revision"] += 1
        raw = canonical_bytes(definition) + b"\n"
        current_entry["production"].update(revision="r99", package="content/packages/" + self.entry["id"] + "/r99",
                                            package_sha256="a" * 64, definition_sha256=io.checksum(raw))
        rebound = images.rebind(adopted, current_entry, bg.ref("game/" + current_entry["definition"], raw), definition["revision"], self.catalog)
        self.assertEqual(rebound["current"], adopted["current"])
        self.assertEqual(rebound["origin"], manual["origin"])
        self.assertEqual(rebound["record_revision"], 3)
        self.assertEqual(rebound["current"]["image_revision"], 2)
        self.assertNotEqual(rebound["binding"], rebound["current"]["authority"]["binding"])
        altered = deepcopy(rebound)
        altered["current"]["authority"]["approval"]["definition_sha256"] = io.checksum(raw)
        with self.assertRaisesRegex(InvalidInput, "definition_sha256"):
            images.validate(rehash(altered), self.catalog)

    def test_notice_is_exact_bounded_and_does_not_invent_a_time(self):
        raw = images.manual_notice(b"Original attribution\n", PROVENANCE, DECISION)
        self.assertTrue(raw.startswith(b"Original attribution\n\nManuelle Bildpflege (PE-A2)\n"))
        self.assertTrue(raw.endswith(b"statement: Explicit synthetic manual image selection.\n"))
        self.assertIn(b"timestamp_utc: 2026-11-12T12:00:00Z\n", raw)
        for prefix, provenance in ((b"x" * 65535 + b"\n", PROVENANCE), (b"", {**PROVENANCE, "source": "two\nlines"})):
            with self.assertRaises(InvalidInput):
                images.manual_notice(prefix, provenance, DECISION)

    def test_productive_promotion_preserves_real_hp_source_and_old_adoption(self):
        from tests.puzzle_production.background_catalog_fixtures import prepare
        from tests.puzzle_production.background_change_fixtures import create_work
        from tools.puzzle_production import background_package, background_request
        for changed in (False, True):
            with self.subTest(previous_adoption=changed):
                fixture = prepare(self, registered=True)
                self.root = fixture.checkout
                self.catalog = load_json(self.root / "content/categories.json")
                self.registry = load_json(self.root / registry.REGISTRY)
                self.entry = self.registry["entries"][0]
                if changed:
                    work = create_work(self, self.root, fixture.case.root)
                    old = bg.load(self.root, self.registry, self.entry)
                    request, request_raw, _ = background_request.read(self.root, work.record_path)
                    graph = background_package.validate_change(self.root, request, old, self.entry)
                    notice = bg.notice_bytes(self.entry["id"], graph["candidate"])
                    change = bg.build_change(old, self.entry, request, bg.ref(work.record_path, request_raw), graph, notice)
                    self.publish_background(change, graph["asset_bytes"], notice)
                old = bg.load(self.root, self.registry, self.entry)
                old_raw = (self.root / bg.asset_path(self.entry["id"])).read_bytes()
                old_notice = (self.root / bg.notice_path(self.entry["id"])).read_bytes()
                asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
                reveal = images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, DECISION)
                self.publish_reveal(reveal, SVG)
                binding = images.make_binding(self.root, self.entry)
                promoted = images.promote_background(self.root, self.registry, self.entry, binding["entry"],
                                                     binding["identity"]["definition"], binding["identity"]["runtime_revision"])
                self.assertEqual(promoted["origin"]["source"], old)
                self.assertEqual(promoted["current"]["image_revision"], bg.current(old)["image_revision"])
                self.assertEqual(promoted["current"]["authority"]["adoption"], bg.current(old).get("adoption"))
                self.assertEqual(promoted["current"]["authority"]["kind"], "production")
                self.publish_background(promoted, old_raw, old_notice)
                self.assertEqual(bg.load(self.root, self.registry, self.entry), promoted)
                self.assertEqual(at.resolve(self.root, self.entry, self.catalog)["effective_reveal_ref"], asset)
                self.assertEqual(bg.initial(promoted), bg.initial(old))
                altered = deepcopy(promoted)
                altered["current"]["authority"]["provenance"]["author"] = "Invented replacement author"
                with self.assertRaises(InvalidInput):
                    images.validate(rehash(altered), self.catalog)

    def test_old_background_at_prefix_remains_real_after_manual_format_switch(self):
        from tests.puzzle_production.background_catalog_fixtures import prepare
        from tools.puzzle_production import background_rebind
        fixture = prepare(self, registered=True)
        self.root = fixture.checkout
        self.catalog = load_json(self.root / "content/categories.json")
        self.registry = load_json(self.root / registry.REGISTRY)
        self.entry = self.registry["entries"][0]
        original_bg = bg.load(self.root, self.registry, self.entry)
        bg_raw = (self.root / bg.asset_path(self.entry["id"])).read_bytes()
        bg_notice = (self.root / bg.notice_path(self.entry["id"])).read_bytes()
        definition = (self.root / "game" / self.entry["definition"]).read_bytes()
        notice = (self.root / at.identity(self.entry)["notice"]).read_bytes()
        image = png(color=(90, 80, 70, 255))
        approval = {"format": at.APPROVAL, "id": self.entry["id"], "image_revision": 1,
            "definition_sha256": self.entry["production"]["definition_sha256"],
            "previous_reveal_sha256": self.entry["production"]["reveal_sha256"],
            "reveal_sha256": io.checksum(image), "notice_sha256": io.checksum(notice), **DECISION,
            "checks": dict.fromkeys(("reveal_approved", "motif_raster_consistent", "final_editorial_approved"), True), "test_only": True}
        record = at.revise(self.root, self.entry, self.catalog, io.checksum(image), approval, PROVENANCE)
        actual_binding = background_rebind.binding(self.root, original_bg, self.entry, definition, image, notice, record)
        rebound = background_rebind.append(original_bg, self.entry, actual_binding, "reveal-adoption")
        write_json(self.root / at.path(self.entry["id"]), record)
        (self.root / "game" / self.entry["reveal"]).write_bytes(image)
        self.publish_background(rebound, bg_raw, bg_notice)
        bg.load(self.root, self.registry, self.entry)
        asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
        manual = images.manual_reveal(self.root, self.entry, self.catalog, asset,
                                      {**PROVENANCE, "changes": "Prepared SVG replacement"}, DECISION)
        self.publish_reveal(manual, SVG)
        self.assertEqual(manual["origin"]["source"], record)
        self.assertEqual(bg.load(self.root, self.registry, self.entry), rebound)
        self.assertEqual(at.resolve(self.root, self.entry, self.catalog)["effective_reveal_ref"], asset)
        binding = images.make_binding(self.root, self.entry)
        promoted = images.promote_background(self.root, self.registry, self.entry, binding["entry"],
                                             binding["identity"]["definition"], binding["identity"]["runtime_revision"])
        self.publish_background(promoted, bg_raw, bg_notice)
        self.assertEqual(bg.load(self.root, self.registry, self.entry), promoted)
        self.assertEqual(promoted["origin"]["source"], rebound)
        self.assertEqual(promoted["current"]["image_revision"], 1)

    def test_productive_svg_retirement_and_batch_bind_the_actual_active_file(self):
        from tools.puzzle_production import integration_batch_operations as batch, reveal_retirement
        asset = bg.ref(str(Path("game/" + self.entry["reveal"]).with_suffix(".svg")), SVG)
        manual = images.manual_reveal(self.root, self.entry, self.catalog, asset, PROVENANCE, DECISION)
        self.publish_reveal(manual, SVG)
        raw = SVG.replace(b"#369", b"#963")
        notice = at.make_notice(manual["current"]["notice"]["text"].encode() + b"Actual synthetic AT production approval\n")
        approval = self.approval(manual, raw, notice)
        adopted = images.adopt_reveal(manual, bg.ref(asset["file"], raw), notice, PROVENANCE, approval, self.catalog)
        self.publish_reveal(adopted, raw)
        write_json(self.root / registry.RUNTIME, registry.projection(self.registry, self.catalog, self.root, version=8))
        registry.check_checkout(self.root)
        reached = batch.reached(self.root, self.entry["id"])
        files = {ref["file"]: ref for ref in reached["files"]}
        self.assertEqual(files[asset["file"]], adopted["current"]["asset"])
        self.assertNotIn("game/" + self.entry["reveal"], files)

        revision = "at-editor-r01"
        directory = reveal_retirement.selection(self.entry["id"], revision)
        source_name = at.path(self.entry["id"])
        approval_name = directory + "/approval.json"
        write_json(self.root / approval_name, approval)
        write_json(self.root / directory / "record.json", {
            "format": "picross-authoring-record-v1", "puzzle_id": self.entry["id"], "revision": revision,
            "state": "registered", "blockers": [],
            "integration": {"operation": "catalog_reveal adopt", "image_revision": adopted["current"]["image_revision"],
                            "active_record": source_name, "active_record_sha256": io.file_hash(self.root, source_name)},
            "final_editorial_approval": {"file": approval_name, "sha256": io.file_hash(self.root, approval_name)}})
        write_json(self.root / reveal_retirement.INDEX, {"format": "picross-authoring-index-v1", "entries": [
            {"puzzle_id": self.entry["id"], "revision": revision, "record": directory + "/record.json"}]})

        def git(*args):
            return subprocess.run(["git", "-c", "user.name=PE-A2 synthetic test", "-c",
                "user.email=pe-a2@example.invalid", "-c", "commit.gpgsign=false", *args], cwd=self.root,
                check=True, capture_output=True, text=True, timeout=20).stdout.strip()

        git("init", "--quiet")
        git("add", ".")
        git("commit", "--quiet", "--message", "Synthetic productive SVG adoption")
        commit = git("rev-parse", "HEAD")
        git("update-ref", "refs/remotes/origin/main", commit)
        source_raw = (self.root / source_name).read_bytes()
        self.assertEqual(reveal_retirement.retire(self.root, [(self.entry["id"], revision)], commit)["status"],
                         "reveal_production_retired")
        self.assertEqual((self.root / source_name).read_bytes(), source_raw)
        self.assertEqual((self.root / asset["file"]).read_bytes(), raw)
        self.assertEqual(reveal_retirement.retire(self.root, [(self.entry["id"], revision)], commit)["status"], "no-op")
        registry.check_checkout(self.root)


if __name__ == "__main__":
    unittest.main()
