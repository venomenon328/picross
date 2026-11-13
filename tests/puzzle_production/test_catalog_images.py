"""PE-A2 image plans and shared publication over real synthetic registrations.

Small fixed inputs exercise source binding, byte-preserving imports and rollback;
the real catalog, player profiles and production image algorithms are untouched.
"""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from tests.puzzle_production.catalog_fixtures import registered
from tools.puzzle_production import catalog_background as background, catalog_images as images
from tools.puzzle_production import catalog_io as io, catalog_metadata as metadata
from tools.puzzle_production import catalog_publication as publication, catalog_transaction as tx
from tools.puzzle_production import content_registry as registry, reveal_source as reveal
from tools.puzzle_production.contract import digest, load_json, write_json


PROVENANCE = {"author": "Synthetic fixture", "usage_basis": "Project test data",
              "source": "Fixed local geometry", "changes": "Prepared input; no conversion"}
DECISION = {"actor": "TEST ONLY", "timestamp_utc": "2026-11-12T12:00:00Z",
            "statement": "Explicit synthetic manual image selection."}
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="80"><rect x="8" y="8" width="80" height="64" fill="#369"/></svg>\n'


def png(size=(96, 80), color=(40, 90, 150, 200)):
    value = Image.new("RGBA", size, color)
    value.putpixel((0, 0), (0, 0, 0, 0))
    stream = BytesIO()
    value.save(stream, format="PNG")
    return stream.getvalue()


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def contents(root):
    return {name: row[0] for name, row in snapshot(root).items()}


def capability(root, enabled=True):
    write_json(root / background.CAPABILITY, {
        "format": background.CAPABILITY_FORMAT, "runtime_format": background.RUNTIME_FORMAT,
        "profile_id": "picross-background-png2304-v1", "enabled": enabled})


class CatalogImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="pe-a2-image-input-")
        cls.addClassCleanup(cls.shared.cleanup)
        cls.shared_root = Path(cls.shared.name)
        registered(cls.shared_root, stem="pe_images", save_slot="pe_images")
        cls.reveal_png = png()
        cls.background_png = png((2304, 576))
        cls.background_replacement = png((2304, 576), (100, 60, 30, 160))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="pe-a2-images-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.home / "checkout"
        shutil.copytree(self.shared_root / "base", self.root)
        self.original = registry.check_checkout(self.root)
        self.entry = self.original["entries"][0]
        self.identifier = self.entry["id"]
        self.sequence = 0

    def migrate(self):
        plan = images.plan_migration(self.root)
        return images.apply_migration(self.root, plan)

    def request(self, *, reveal_bytes=None, extension=".png", background_status=None,
                background_bytes=None, current_metadata=None, decision=None):
        self.sequence += 1
        directory = self.home / ("input-%d" % self.sequence)
        directory.mkdir()
        value = {"format": images.REQUEST, "id": self.identifier, "metadata": current_metadata,
                 "reveal": None, "background": None, "decision": deepcopy(decision or DECISION)}
        if reveal_bytes is not None:
            name = "reveal" + extension
            (directory / name).write_bytes(reveal_bytes)
            value["reveal"] = {"asset": background.ref(name, reveal_bytes), "provenance": deepcopy(PROVENANCE)}
        if background_status is not None:
            if background_status == "selected":
                raw = self.background_png if background_bytes is None else background_bytes
                (directory / "background.png").write_bytes(raw)
                part = {"status": background_status, "asset": background.ref("background.png", raw),
                        "provenance": deepcopy(PROVENANCE)}
            else:
                part = {"status": background_status, "asset": None, "provenance": None}
            value["background"] = part
        path = directory / "request.json"
        write_json(path, value)
        return path

    def plan(self, request):
        self.sequence += 1
        output = self.home / ("plan-%d" % self.sequence)
        value = images.plan(self.root, request, output)
        return output, value

    def edit(self, **kwargs):
        output, plan = self.plan(self.request(**kwargs))
        return images.apply(self.root, output), plan

    def test_view_and_explicit_migration_are_read_only_lossless_and_noop(self):
        before = snapshot(self.root)
        view = images.view(self.root, self.identifier)
        self.assertTrue(view["migration_required"])
        output = self.home / "migration.json"
        plan = images.plan_migration(self.root, output)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(plan["files"], [registry.RUNTIME])
        self.assertEqual(plan["new"], {**plan["old"], "format": registry.IMAGE_RUNTIME_FORMAT})
        self.assertEqual(images.apply(self.root, output)["status"], "migrated")
        after = contents(self.root)
        self.assertEqual(set(after), set(before))
        self.assertEqual({name for name in after if after[name] != before[name][0]}, {registry.RUNTIME})
        self.assertFalse(images.view(self.root, self.identifier)["migration_required"])
        unchanged = snapshot(self.root)
        self.assertEqual(images.apply(self.root, output)["status"], "noop")
        noop = images.plan_migration(self.root)
        self.assertEqual(noop["files"], [])
        self.assertEqual(images.apply_migration(self.root, noop)["status"], "noop")
        self.assertEqual(snapshot(self.root), unchanged)

    def test_detail_reuses_one_complete_snapshot_without_writing(self):
        from tools.puzzle_editor.worker import run
        before = snapshot(self.root)
        work = self.home/"detail-work"; work.mkdir()
        original = tx.capture
        with patch.object(tx, "capture_detail", wraps=tx.capture_detail) as captures, \
                patch.object(tx, "capture", side_effect=AssertionError("Detail repeated full catalog validation")):
            result = run(self.root, work, "detail", {"id": self.identifier})
        self.assertEqual(captures.call_count, 1)
        self.assertEqual(result["snapshot"], digest(tx.image_snapshot(original(self.root))))
        self.assertEqual(result["detail"]["id"], self.identifier)
        definition = load_json(self.root/"game"/self.entry["definition"])
        self.assertEqual(result["raster"]["palette"], definition["palette"])
        self.assertEqual(result["raster"]["text"], "\n".join(" ".join(map(str, row)) for row in definition["solution"])+"\n")
        self.assertEqual(snapshot(self.root), before)

    def test_migration_crash_before_with_and_after_journal_rolls_back_and_replans(self):
        before = contents(self.root)
        original_times = snapshot(self.root)
        plan = images.plan_migration(self.root)
        def before_journal(phase, name=None):
            if phase == "P0": raise InterruptedError("before first mutation")
        with patch.object(publication, "checkpoint", side_effect=before_journal), self.assertRaises(InterruptedError):
            images.apply_migration(self.root, plan)
        self.assertEqual(snapshot(self.root), original_times)
        self.assertFalse((self.root/tx.LOCK).exists())
        for boundary in ("journal-complete", "P1", "P5"):
            def crash(phase, name=None):
                if phase == boundary: raise InterruptedError("controlled migration crash")
            with self.subTest(boundary=boundary), patch.object(publication, "checkpoint", side_effect=crash), self.assertRaises(InterruptedError):
                images.apply_migration(self.root, images.plan_migration(self.root))
            self.assertTrue((self.root/tx.LOCK).exists() or publication.staging(self.root))
            def interrupted_recovery(phase, name=None):
                if phase in ("R1-runtime", "R2"): raise InterruptedError("repeated recovery interruption")
            if boundary != "journal-complete":
                with patch.object(publication, "checkpoint", side_effect=interrupted_recovery), self.assertRaises(InterruptedError):
                    registry.recover(self.root)
            self.assertEqual(registry.recover(self.root)["status"], "rolled-back")
            self.assertEqual(contents(self.root), before)
            from tools.puzzle_editor.worker import run
            work = self.home/"recover-work"; work.mkdir(exist_ok=True)
            self.assertEqual(run(self.root, work, "recover", {})["status"], "noop")
        fresh = images.plan_migration(self.root)
        self.assertEqual(images.apply_migration(self.root, fresh)["status"], "migrated")
        reached = snapshot(self.root)
        self.assertEqual(images.apply_migration(self.root, fresh)["status"], "noop")
        self.assertEqual(snapshot(self.root), reached)
        self.assertEqual(load_json(self.root/tx.RUNTIME)["format"], registry.IMAGE_RUNTIME_FORMAT)

    def test_manual_edit_requires_explicit_runtime_migration(self):
        request = self.request(reveal_bytes=SVG, extension=".svg", current_metadata={"name": "Changed"})
        before = snapshot(self.root)
        with self.assertRaisesRegex(ValueError, "[Mm]igration"):
            self.plan(request)
        self.assertEqual(snapshot(self.root), before)

    def test_combined_format_roundtrip_uses_detached_input_and_preserves_identity(self):
        self.migrate()
        before = contents(self.root)
        request = self.request(reveal_bytes=SVG, extension=".svg", background_status="standard",
                               current_metadata={"name": "Current image", "category_id": "wasserwelt"})
        untouched = snapshot(self.root)
        output, plan = self.plan(request)
        self.assertEqual(snapshot(self.root), untouched)
        self.assertEqual((output / "input/reveal.svg").read_bytes(), SVG)
        shutil.rmtree(request.parent)
        self.assertEqual(images.apply(self.root, output)["status"], "updated")
        current = registry.check_checkout(self.root)
        self.assertEqual(current["entries"], self.original["entries"])
        for name, raw in before.items():
            if name not in plan["files"]:
                self.assertEqual((self.root / name).read_bytes(), raw, name)
        historical = "game/" + self.entry["reveal"]
        active = str(Path(historical).with_suffix(".svg"))
        self.assertEqual((self.root / active).read_bytes(), SVG)
        self.assertFalse((self.root / historical).exists())
        runtime = load_json(self.root / registry.RUNTIME)["entries"][0]
        self.assertEqual(runtime["reveal"], active.removeprefix("game/"))
        self.assertEqual(runtime["name"], "Current image")
        self.assertEqual(runtime["category_id"], "wasserwelt")
        self.assertEqual(runtime["background"], {"status": "standard", "image_revision": 1, "asset": None})
        origin = load_json(self.root / reveal.path(self.identifier))["origin"]
        unchanged = snapshot(self.root)
        self.assertEqual(images.apply(self.root, output)["status"], "noop")
        self.assertEqual(snapshot(self.root), unchanged)
        self.assertEqual(self.edit(reveal_bytes=self.reveal_png)[0]["status"], "updated")
        self.assertEqual((self.root / historical).read_bytes(), self.reveal_png)
        self.assertFalse((self.root / active).exists())
        record = load_json(self.root / reveal.path(self.identifier))
        self.assertEqual(record["origin"], origin)
        self.assertEqual(record["current"]["image_revision"], 2)
        self.assertEqual(record["current"]["authority"], {"kind": "manual", "decision": DECISION, "provenance": PROVENANCE})
        unchanged = snapshot(self.root)
        later = {**DECISION, "actor": "Another synthetic tester", "timestamp_utc": "2026-11-13T12:00:00Z"}
        self.assertEqual(self.edit(reveal_bytes=self.reveal_png, decision=later)[0]["status"], "noop")
        self.assertEqual(snapshot(self.root), unchanged)

    def test_legacy_first_preferences_all_transitions_and_selected_replacement(self):
        roots = {}
        for status in ("standard", "selected", "none"):
            with self.subTest(first=status):
                self.root = roots[status] = self.home / ("first-" + status)
                shutil.copytree(self.shared_root / "base", self.root)
                self.migrate()
                capability(self.root)
                self.assertEqual(self.edit(background_status=status)[0]["status"], "updated")
                record = load_json(self.root / background.path(self.identifier))
                self.assertIsNone(record["origin"]["source"])
                self.assertEqual(record["current"]["image_revision"], 1)
                self.assertEqual(record["current"]["status"], status)
        self.root = roots["standard"]
        origin = load_json(self.root / background.path(self.identifier))["origin"]
        noops = set()
        for revision, status in enumerate(("selected", "none", "standard", "none", "selected", "standard", "selected"), 2):
            # These transitions depend on their predecessors; stop at the first
            # failure instead of reporting misleading later revision failures.
            self.assertEqual(self.edit(background_status=status)[0]["status"], "updated")
            registry.check_checkout(self.root)
            record = load_json(self.root / background.path(self.identifier))
            self.assertEqual(record["origin"], origin)
            self.assertEqual(record["current"]["status"], status)
            self.assertEqual(record["current"]["image_revision"], revision)
            self.assertEqual((self.root / background.asset_path(self.identifier)).exists(), status == "selected")
            self.assertEqual((self.root / background.notice_path(self.identifier)).exists(), status == "selected")
            if status not in noops:
                noops.add(status)
                before = snapshot(self.root)
                self.assertEqual(self.edit(background_status=status)[0]["status"], "noop")
                self.assertEqual(snapshot(self.root), before)
            if revision == 4:
                source_bytes = (self.root / background.path(self.identifier)).read_bytes()
                self.edit(current_metadata={"category_id": "wasserwelt"})
                self.assertEqual((self.root / background.path(self.identifier)).read_bytes(), source_bytes)
                runtime = load_json(self.root / registry.RUNTIME)["entries"][0]
                self.assertEqual(runtime["category_id"], "wasserwelt")
                self.assertEqual(runtime["background"], {"status": "standard", "image_revision": revision, "asset": None})
        self.edit(background_status="selected", background_bytes=self.background_replacement)
        record = load_json(self.root / background.path(self.identifier))
        self.assertEqual(record["current"]["image_revision"], 9)
        self.assertEqual((self.root / background.asset_path(self.identifier)).read_bytes(), self.background_replacement)

    def test_stale_metadata_and_inactive_reveal_absence_are_not_overwritten(self):
        self.migrate()
        request = self.request(reveal_bytes=SVG, extension=".svg")
        output, _ = self.plan(request)
        changed = metadata.plan(self.root, [{"op": "set_metadata", "id": self.identifier, "name": "Another edit"}])
        metadata.apply(self.root, changed)
        before = snapshot(self.root)
        with self.assertRaisesRegex(ValueError, "stale"):
            images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)
        output, _ = self.plan(request)
        foreign = (self.root / "game" / self.entry["reveal"]).with_suffix(".svg")
        foreign.write_bytes(b"foreign alternative must survive\n")
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)

    def test_closed_bundle_rejects_modified_bytes_extras_and_rehashed_preview(self):
        self.migrate()
        output, plan = self.plan(self.request(reveal_bytes=SVG, extension=".svg"))
        before = snapshot(self.root)
        asset = output / "input/reveal.svg"
        asset.write_bytes(SVG + b" ")
        with self.assertRaises(ValueError): images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)
        asset.write_bytes(SVG)
        for path, directory in ((output / "unbound.txt", False), (output / "unknown", True)):
            path.mkdir() if directory else path.write_bytes(b"unbound")
            with self.subTest(extra=path.name), self.assertRaises(ValueError): images.apply(self.root, output)
            self.assertEqual(snapshot(self.root), before)
            path.rmdir() if directory else path.unlink()
        forged = deepcopy(plan)
        forged["new"]["metadata"]["name"] = "Hash is not approval"
        forged["plan_hash"] = digest({key: value for key, value in forged.items() if key != "plan_hash"})
        write_json(output / "plan.json", forged)
        with self.assertRaisesRegex(ValueError, "reconstruction"):
            images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)
        write_json(output / "plan.json", plan)
        previous = next((output / "previous").iterdir())
        previous.unlink()
        with self.assertRaises((ValueError, OSError)):
            images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)

    def test_repeat_rejects_rehashed_old_previews_and_another_bound_decision(self):
        self.migrate()
        capability(self.root)
        output, plan = self.plan(self.request(reveal_bytes=SVG, extension=".svg", background_status="selected",
                                              current_metadata={"name": "Reached combined state"}))
        self.assertEqual(images.apply(self.root, output)["status"], "updated")
        self.assertEqual(images.apply(self.root, output)["status"], "noop")
        before = snapshot(self.root)
        mutations = (
            lambda value: value["old"].update(reveal={"not": "a valid historical reveal source"}),
            lambda value: value["old"].update(background={"not": "a valid historical background source"}),
            lambda value: value["old"]["metadata"].update(unbound=True),
            lambda value: value["old"]["runtime"].update(unbound=True),
            lambda value: value["old"].update(reveal=deepcopy(value["new"]["reveal"])),
        )
        for index, mutate in enumerate(mutations):
            forged = deepcopy(plan)
            mutate(forged)
            forged["plan_hash"] = digest({key: value for key, value in forged.items() if key != "plan_hash"})
            write_json(output / "plan.json", forged)
            with self.subTest(preview=index), self.assertRaises(ValueError): images.apply(self.root, output)
            self.assertEqual(snapshot(self.root), before)
        original_request = (output / "request.json").read_bytes()
        changed_request = load_json(output / "request.json")
        changed_request["decision"]["actor"] = "A different claimed original decision"
        write_json(output / "request.json", changed_request)
        forged = deepcopy(plan)
        forged["request"] = background.ref("request.json", (output / "request.json").read_bytes())
        forged["plan_hash"] = digest({key: value for key, value in forged.items() if key != "plan_hash"})
        write_json(output / "plan.json", forged)
        with self.assertRaisesRegex(ValueError, "manual decision"):
            images.apply(self.root, output)
        self.assertEqual(snapshot(self.root), before)
        (output / "request.json").write_bytes(original_request)
        write_json(output / "plan.json", plan)
        self.assertEqual(images.apply(self.root, output)["status"], "noop")
        self.assertEqual(snapshot(self.root), before)

    def test_repeat_migration_rejects_fabricated_old_runtime_and_v7_editor_sources(self):
        plan = images.plan_migration(self.root)
        self.assertEqual(images.apply_migration(self.root, plan)["status"], "migrated")
        before = snapshot(self.root)
        malformed = {"format": "not-a-runtime", "arbitrary": "never a valid previous runtime"}
        for old in (malformed, {**plan["old"], "format": "picross-runtime-registry-v6"},
                    {**plan["old"], "entries": []}):
            forged = deepcopy(plan)
            forged["old"] = old
            forged["snapshot"]["sources"][tx.RUNTIME] = io.checksum(images.encoded(old))
            forged["plan_hash"] = digest({key: value for key, value in forged.items() if key != "plan_hash"})
            with self.subTest(old=old["format"]), self.assertRaises(ValueError):
                images.apply_migration(self.root, forged)
            self.assertEqual(snapshot(self.root), before)
        self.assertEqual(images.apply_migration(self.root, plan)["status"], "noop")
        self.edit(reveal_bytes=self.reveal_png)
        forged = images.plan_migration(self.root)
        forged["old"]["format"] = registry.METADATA_RUNTIME_FORMAT
        forged["files"] = [tx.RUNTIME]
        forged["snapshot"]["sources"][tx.RUNTIME] = io.checksum(images.encoded(forged["old"]))
        forged["plan_hash"] = digest({key: value for key, value in forged.items() if key != "plan_hash"})
        before = snapshot(self.root)
        with self.assertRaisesRegex(ValueError, "Runtime v7.*editor sources"):
            images.apply_migration(self.root, forged)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(images.apply_migration(self.root, images.plan_migration(self.root))["status"], "noop")

    def test_repeated_background_transitions_keep_ref_only_notices_valid(self):
        self.migrate()
        capability(self.root)
        self.edit(background_status="selected")
        for status, raw in (("selected", self.background_replacement), ("none", None),
                            ("selected", self.background_png), ("standard", None)):
            with self.subTest(status=status):
                output, plan = self.plan(self.request(background_status=status, background_bytes=raw))
                previous_notice = plan["old"]["background"]["current"]["notice"]
                if previous_notice is not None:
                    self.assertEqual(set(previous_notice), {"file", "sha256", "bytes"})
                    self.assertIsNone(plan["old"]["background"]["origin"]["notice"])
                self.assertEqual(images.apply(self.root, output)["status"], "updated")
                if status in ("standard", "none"):
                    self.assertFalse((self.root / background.notice_path(self.identifier)).exists())
                before = snapshot(self.root)
                self.assertEqual(images.apply(self.root, output)["status"], "noop")
                self.assertEqual(snapshot(self.root), before)

    def test_pending_publication_blocks_view_plan_and_noop_apply(self):
        self.migrate()
        self.edit(reveal_bytes=SVG, extension=".svg")
        request = self.request(reveal_bytes=SVG, extension=".svg")
        output, plan = self.plan(request)
        self.assertEqual(plan["files"], [])
        lock = self.root / tx.LOCK
        lock.write_bytes(b"foreign pending publication\n")
        before = snapshot(self.root)
        for action in (lambda: images.view(self.root, self.identifier), lambda: self.plan(request),
                       lambda: images.apply(self.root, output)):
            with self.assertRaisesRegex(ValueError, "recovery required"):
                action()
            self.assertEqual(snapshot(self.root), before)

    def test_invalid_requests_and_prepared_inputs_fail_before_mutation(self):
        self.migrate()
        request = self.request(reveal_bytes=SVG, extension=".svg")
        original = load_json(request)
        before = snapshot(self.root)
        mutations = (
            lambda value: value.update(extra=True),
            lambda value: value.update(id="pz-unknown"),
            lambda value: value.update(metadata={"category_id": "not-a-category"}),
            lambda value: value.update(metadata={"definition": "replacement"}),
            lambda value: value["reveal"]["asset"].update(file="../reveal.svg"),
            lambda value: value["reveal"]["asset"].update(bytes=0),
            lambda value: value["reveal"]["provenance"].update(author="two\nlines"),
            lambda value: value["decision"].update(approval=True),
        )
        for index, mutate in enumerate(mutations):
            broken = deepcopy(original)
            mutate(broken)
            write_json(request, broken)
            with self.subTest(request=index), self.assertRaises(ValueError): self.plan(request)
            self.assertEqual(snapshot(self.root), before)
        unsafe_svg = SVG.replace(b'<rect ', b'<rect onload="run()" ')
        for raw, extension in ((unsafe_svg, ".svg"), (self.reveal_png[:50], ".png"), (png((4, 4)), ".png")):
            rejected = self.request(reveal_bytes=raw, extension=extension)
            with self.subTest(extension=extension, length=len(raw)), self.assertRaises(ValueError):
                self.plan(rejected)
            self.assertEqual(snapshot(self.root), before)
        rejected = self.request(background_status="selected", background_bytes=png((96, 80)))
        with self.assertRaisesRegex(ValueError, "2304"):
            self.plan(rejected)
        self.assertEqual(snapshot(self.root), before)
        rejected = self.request(background_status="selected")
        with self.assertRaisesRegex(ValueError, "capability"):
            self.plan(rejected)
        self.assertEqual(snapshot(self.root), before)

    def test_binary_create_remove_replace_and_combined_publication_roll_back(self):
        self.migrate()
        capability(self.root)
        self.edit(background_status="selected")
        request = self.request(reveal_bytes=SVG, extension=".svg", background_status="selected",
                               background_bytes=self.background_replacement, current_metadata={"name": "Pending name"})
        output, _ = self.plan(request)
        before = contents(self.root)
        old_reveal = "game/" + self.entry["reveal"]
        new_reveal = str(Path(old_reveal).with_suffix(".svg"))
        for target in (background.asset_path(self.identifier), old_reveal, new_reveal, tx.REGISTRY, tx.RUNTIME):
            observed = []
            def stop(phase, name=None):
                if phase in ("P3", "P4", "P5") and name == target:
                    observed.append(name)
                    raise InterruptedError("controlled image publication interruption")
            with self.subTest(target=target), patch.object(publication, "checkpoint", side_effect=stop), self.assertRaises(InterruptedError):
                images.apply(self.root, output)
            self.assertEqual(observed, [target])
            self.assertTrue((self.root / tx.LOCK).exists())
            with self.assertRaisesRegex(ValueError, "recovery required"):
                images.view(self.root, self.identifier)
            if target == new_reveal:
                journal = (self.root / tx.LOCK).read_bytes()
                def stop_recovery(phase, name=None):
                    if phase == "R1-binary": raise InterruptedError("controlled repeated rollback interruption")
                with patch.object(publication, "checkpoint", side_effect=stop_recovery), self.assertRaises(InterruptedError):
                    images.recover(self.root)
                self.assertEqual((self.root / tx.LOCK).read_bytes(), journal)
            self.assertEqual(images.recover(self.root)["status"], "rolled-back")
            self.assertEqual(contents(self.root), before)
            self.assertFalse((self.root / tx.LOCK).exists())
            registry.check_checkout(self.root)

    def test_recovery_preserves_foreign_binary_and_its_pending_journal(self):
        self.migrate()
        output, _ = self.plan(self.request(reveal_bytes=SVG, extension=".svg"))
        before = contents(self.root)
        with self.assertRaises(InterruptedError):
            images.apply(self.root, output, fail_step="crash-runtime")
        active = (self.root / "game" / self.entry["reveal"]).with_suffix(".svg")
        active.write_bytes(b"foreign replacement must remain\n")
        foreign = snapshot(self.root)
        with self.assertRaises(ValueError): images.recover(self.root)
        self.assertEqual(snapshot(self.root), foreign)
        active.write_bytes(SVG)
        self.assertEqual(images.recover(self.root)["status"], "rolled-back")
        self.assertEqual(contents(self.root), before)
        registry.check_checkout(self.root)




class CatalogValidationScopeTests(unittest.TestCase):
    def test_json_reuse_is_exact_bounded_detached_and_ends_with_operation(self):
        raw = b'{"nested":[1,2]}\n'
        with io.budget():
            first = io.json_bytes(raw, 100)
            first["nested"].append(3)
            self.assertEqual(io.json_bytes(raw, 100), {"nested": [1, 2]})
            with self.assertRaisesRegex(RuntimeError, "byte limit"):
                io.json_bytes(raw, 1)
            with self.assertRaises(ValueError):
                io.json_bytes(b'{"a":1,"a":2}', 100)
            self.assertEqual(io.json_bytes(b'{"nested":[4]}', 100), {"nested": [4]})
            context = io._operation_data.get()
            with io.budget(): self.assertIs(io._operation_data.get(), context)
        self.assertIsNone(io._operation_data.get())
        with io.budget(): self.assertIsNot(io._operation_data.get(), context)

    def test_method_reuse_reopens_all_bound_inputs_and_detects_equal_mtime_change(self):
        from tools.puzzle_production import catalog_method, sd2_rating_freeze as frozen
        import json
        import os
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            method = json.loads((frozen._ROOT/"sd2_method_0_4.json").read_bytes())
            names = {"sd2_method_0_4.json", *method["artifacts"], *method["implementation"]}
            for name in names: (root/name).write_bytes((frozen._ROOT/name).read_bytes())
            with patch.object(frozen, "_ROOT", root), io.budget():
                expected = catalog_method.method_hash(catalog_method.NEW)
                actual_read = io.read
                reads = []
                def observed(root, name, *args, **kwargs):
                    reads.append(name)
                    return actual_read(root, name, *args, **kwargs)
                with patch.object(io, "read", side_effect=observed):
                    self.assertEqual(catalog_method.method_hash(catalog_method.NEW), expected)
                self.assertEqual(set(reads), names)
                target = root/next(iter(method["implementation"]))
                info = target.stat(); raw = target.read_bytes()
                target.write_bytes(bytes([raw[0] ^ 1])+raw[1:])
                os.utime(target, ns=(info.st_atime_ns, info.st_mtime_ns))
                with self.assertRaisesRegex(ValueError, "Changed frozen"):
                    catalog_method.method_hash(catalog_method.NEW)
                self.assertEqual(target.read_bytes(), bytes([raw[0] ^ 1])+raw[1:])
            self.assertIsNone(io._operation_data.get())
            target.write_bytes(raw)
            with patch.object(frozen, "_ROOT", root), io.budget():
                with self.assertRaisesRegex(ValueError, "Changed frozen"):
                    with catalog_method._read_batch():
                        catalog_method.method_hash(catalog_method.NEW)
                        target.write_bytes(bytes([raw[0] ^ 1])+raw[1:])
                        # Reuse inside a reader cannot publish a result before
                        # the mandatory end binding rejects the changed bytes.
                        catalog_method.method_hash(catalog_method.NEW)
                self.assertIsNone(catalog_method._batch.get())


if __name__ == "__main__":
    unittest.main()
