"""HP-I1b2 compact source and narrowly authorized retained-context authority."""
from copy import deepcopy
import unittest

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tests.puzzle_production.background_fixtures import file_ref, put_json
from tools.puzzle_production import background_package as package, background_request as requests
from tools.puzzle_production import catalog_background as bg, content_registry as registry
from tools.puzzle_production.contract import InvalidInput, load_json


class BackgroundSourceTests(unittest.TestCase):
    def changed(self, choice="selected"):
        fixture = prepare(self, registered=True)
        work = create_work(self, fixture.checkout, fixture.case.root, choice=choice)
        catalog = load_json(fixture.checkout / registry.REGISTRY)
        entry = catalog["entries"][0]
        original = bg.load(fixture.checkout, catalog, entry)
        request, raw, _ = requests.read(fixture.checkout, work.record_path)
        graph = package.validate_change(fixture.checkout, request, original, entry)
        source = bg.build_change(original, entry, request, bg.ref(work.record_path, raw), graph,
                                 bg.notice_bytes(entry["id"], graph["candidate"]))
        return fixture, work, catalog, entry, original, graph, source

    def test_real_selected_and_none_work_keep_initial_receipt_and_project_current(self):
        for choice in ("selected", "none"):
            with self.subTest(choice=choice):
                fixture, work, catalog, entry, original, graph, source = self.changed(choice)
                original_ref = bg.index(catalog)[entry["id"]]
                self.assertEqual(bg.initial(source), original)
                self.assertEqual(bg.initial_ref(source), original_ref)
                self.assertEqual(bg.current(source)["image_revision"], 2)
                self.assertEqual(bg.current(source)["decision"]["outcome"], choice)
                self.assertEqual(bg.effective(source)["identity"], original["identity"])
                new_ref = bg.ref(bg.path(entry["id"]), bg.encoded(source))
                self.assertNotEqual(new_ref, original_ref)
                self.assertEqual(bg.receipt_binding(source, new_ref), bg.receipt_binding(original, original_ref))
                self.assertEqual(bg.load(fixture.checkout, catalog, entry), original)
                projected_catalog = deepcopy(catalog)
                projected_catalog["backgrounds"][0]["source"] = new_ref
                projection = bg.projection(projected_catalog, {bg.path(entry["id"]): bg.encoded(source)})[entry["id"]]
                self.assertEqual(projection["status"], choice)
                self.assertEqual(projection["image_revision"], 2)
                if choice == "none":
                    self.assertIsNone(projection["asset"])
                    self.assertIsNone(graph["asset_bytes"])
                else:
                    self.assertEqual(projection["asset"]["sha256"], bg.ref("image", graph["asset_bytes"])["sha256"])
                expected_files = {requests.directory(work.request) + "/" + row["file"] for row in work.request["files"]}
                authorization = requests.directory(work.request) + "/" + work.request["authorization"]["evidence"]["file"]
                self.assertEqual(graph["used_files"] | {authorization}, expected_files)

    def test_compact_v2_rejects_forged_origin_target_current_and_authority_shapes(self):
        _, _, _, entry, _, _, source = self.changed()
        cases = []
        def changed(*keys, value):
            result = deepcopy(source)
            target = result
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value
            cases.append(result)
        changed("extra", value=None)
        changed("initial", "format", value=bg.CHANGE_FORMAT)
        changed("initial", "origin", "approval", "actor", value="Forged original actor")
        changed("current", "image_revision", value=True)
        changed("current", "image_revision", value=3)
        changed("current", "adoption", "target", "source", "sha256", value="0" * 64)
        changed("current", "adoption", "target", "origin_sha256", value="0" * 64)
        changed("current", "adoption", "target", "image_revision", value=0)
        changed("current", "adoption", "background", "manifest", "root", value="content/authoring/foreign/r01")
        changed("current", "adoption", "background", "decision", "storage", value="package")
        changed("current", "adoption", "request", "file", value="content/authoring/foreign/r01/record.json")
        changed("current", "adoption", "authorization", "timestamp_utc", value="yesterday")
        changed("current", "decision", "actor", value="Forged current actor")
        changed("current", "decision", "statement", value="Forged current selection")
        changed("current", "decision", "evidence", "sha256", value="0" * 64)
        changed("current", "derivation", "request_sha256", value="0" * 64)
        changed("current", "provenance", "rights_status", value="unresolved")
        changed("current", "review", "Q-HG01", "result", value="Warnung")
        changed("current", "notice", "sha256", value="0" * 64)
        for altered in cases:
            with self.subTest(altered=altered), self.assertRaises((InvalidInput, ValueError)):
                bg.validate(altered, entry)

    def test_rehashed_foreign_context_cannot_replace_retained_real_authority(self):
        fixture = prepare(self, registered=True)
        work = create_work(self, fixture.checkout, fixture.case.root)
        catalog = load_json(fixture.checkout / registry.REGISTRY)
        entry = catalog["entries"][0]
        original = bg.load(fixture.checkout, catalog, entry)
        request = deepcopy(work.request)
        base = fixture.checkout / requests.directory(request)
        manifest = load_json(base / "work/bg01.json")
        # All modified file refs are real and consistent. It remains the wrong
        # authority even though an ordinary evidence reader can hash it.
        manifest["context"]["reveal_approval"] = put_json(base, "context/active-source.json",
                                                          original["origin"]["approval"])
        manifest_ref = put_json(base, "work/bg01.json", manifest)
        decision = load_json(base / "decisions/d01.json")
        decision["manifest"] = manifest_ref
        decision_ref = put_json(base, "decisions/d01.json", decision)
        request["background"]["manifest"]["ref"] = manifest_ref
        request["background"]["decision"]["ref"] = decision_ref
        request["files"] = [file_ref(base, p.relative_to(base).as_posix())
                            for p in sorted(base.rglob("*")) if p.is_file() and p.name != "record.json"]
        with self.assertRaisesRegex(InvalidInput, "context authority is not the current source bytes"):
            package.validate_change(fixture.checkout, request, original, entry)


if __name__ == "__main__":
    unittest.main()
