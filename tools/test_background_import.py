"""Cheap source/copy/profile boundaries; real decoding needs Godot/PCK evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch

import background_import as background
from product_background_fixtures import IDS, png


class BackgroundImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.png, cls.rgba = png("a")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i2-import-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source/game"
        (self.source / "data").mkdir(parents=True)
        (self.source / "art/backgrounds").mkdir(parents=True)
        asset = f"art/backgrounds/{IDS['a']}.png"
        notice = f"art/backgrounds/{IDS['a']}.txt"
        (self.source / asset).write_bytes(self.png)
        (self.source / notice).write_bytes(b"TEST ONLY generated neutral contours.\n")
        def ref(name):
            raw = (self.source / name).read_bytes()
            return dict(file=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        row = dict(id=IDS["a"], image_revision=1, asset=ref(asset), notice=ref(notice))
        runtime = dict(format="picross-runtime-registry-v6", entries=[dict(id=IDS["a"],
            background=dict(status="selected", image_revision=1, asset=row["asset"]))])
        raw = (json.dumps(runtime) + "\n").encode()
        (self.source / "data/registry.json").write_bytes(raw)
        self.inventory = dict(format=background.FORMAT, source_game=str(self.source),
                              registry_sha256=hashlib.sha256(raw).hexdigest(), assets=[row])
        self.project = self.root / "disposable"
        shutil.copytree(self.source, self.project)

    def header_only_import(self, image_format=5):
        """Only a fake transport/header; never counted as image decoding evidence."""
        for row in self.inventory["assets"]:
            path = self.project / background.remap_path(row["asset"]["file"]).removeprefix("res://")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"GST2" + struct.pack("<8I", 1, 2304, 576, 1 << 23, 0xffffffff, 0, 0, 0)
                             + struct.pack("<IHHII", 2, 2304, 576, 11, image_format) + (struct.pack("<I", 1) + b"x")*12)

    def test_direct_png_header_allowlist_and_source_format_binding(self):
        # Header counterexamples only; these deliberately do not prove PNG
        # decoding, tRNS/Adam7 pixel correctness or the real PCK import path.
        signature = b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR"
        for color, depths in ((0, (1, 2, 4, 8)), (2, (8,)), (3, (1, 2, 4, 8)), (4, (8,)), (6, (8,))):
            for depth in depths:
                for interlace in (0, 1):
                    raw = signature + struct.pack(">IIBBBBB", 2304, 576, depth, color, 0, 0, interlace) + b"\0"*4
                    with self.subTest(color=color, depth=depth, interlace=interlace):
                        self.assertEqual(background._png_image_format(raw, "header-only.png"), 1 if color in (0, 4) else 5)
                        if (depth, color, interlace) == (8, 6, 0):
                            self.assertEqual(background._png_image_format(raw, "header-only.png", prepared=False), 5)
                        else:
                            with self.assertRaisesRegex(ValueError, "Historical HP-W2"):
                                background._png_image_format(raw, "header-only.png", prepared=False)
        for values in ((2303, 576, 8, 6, 0, 0, 0), (2304, 575, 8, 6, 0, 0, 0),
                       (2304, 576, 16, 6, 0, 0, 0), (2304, 576, 4, 4, 0, 0, 0),
                       (2304, 576, 4, 2, 0, 0, 0), (2304, 576, 8, 1, 0, 0, 0),
                       (2304, 576, 8, 5, 0, 0, 0), (2304, 576, 8, 6, 1, 0, 0),
                       (2304, 576, 8, 6, 0, 1, 0), (2304, 576, 8, 6, 0, 0, 2)):
            raw = signature + struct.pack(">IIBBBBB", *values) + b"\0"*4
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, "supported PNG2304"):
                background._png_image_format(raw, "header-only.png")

    def test_imported_format_must_match_the_bound_png_color_type(self):
        background.prepare_import(self.project, self.inventory)
        self.header_only_import(image_format=1)
        with self.assertRaisesRegex(ValueError, "source-format/mipmap"):
            background.verify_import(self.project, self.inventory)
        self.header_only_import(image_format=5)
        self.assertEqual(background.verify_import(self.project, self.inventory)["source_bytes"], len(self.png))

    def test_source_and_wrong_copy_are_never_import_destinations(self):
        before = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        for project in (self.source, self.source.parent, self.source / "nested"):
            with self.subTest(project=project), self.assertRaisesRegex(ValueError, "isolated"):
                background.prepare_import(project, self.inventory)
        with self.assertRaisesRegex(ValueError, "bound source inventory"):
            background.prepare_import(self.project)
        self.assertEqual(before, {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file()})

    def test_player_restore_checks_isolation_before_removing_fixture_files(self):
        from product_fixtures import restore_player_catalog
        fixture = self.source / "data/fixtures/keep.json"
        fixture.parent.mkdir()
        fixture.write_text("source data must remain untouched")
        with self.assertRaisesRegex(ValueError, "isolated"):
            restore_player_catalog(self.source.parent, self.source)
        self.assertEqual(fixture.read_text(), "source data must remain untouched")

    def test_actual_sources_and_notices_are_checked_before_writing_sidecars(self):
        for key in ("asset", "notice"):
            path = self.project / self.inventory["assets"][0][key]["file"]
            original = path.read_bytes()
            for replacement in (None, original + b"changed"):
                with self.subTest(key=key, replacement=replacement is None):
                    if replacement is None: path.unlink()
                    else: path.write_bytes(replacement)
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        background.prepare_import(self.project, self.inventory)
                    self.assertFalse(list((self.project / "art/backgrounds").glob("*.import")))
                    path.write_bytes(original)
        stray = self.project / "art/backgrounds/unbound.png.import"
        stray.write_text("unbound sidecar")
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            background.prepare_import(self.project, self.inventory)

    def test_profile_is_common_and_remaps_are_checked_after_engine(self):
        background.prepare_import(self.project, self.inventory)
        self.header_only_import()
        report = background.verify_import(self.project, self.inventory)
        self.assertEqual(report["source_bytes"], len(self.png))
        self.assertEqual(report["imported_bytes"], 112)
        sidecar = self.project / (self.inventory["assets"][0]["asset"]["file"] + ".import")
        original = sidecar.read_text()
        self.assertIn("process/fix_alpha_border=false", original)
        for before, after in (("mipmaps/generate=true", "mipmaps/generate=false"),
                              ("compress/mode=0", "compress/mode=1"),
                              ('type="CompressedTexture2D"', 'type="ImageTexture"')):
            sidecar.write_text(original.replace(before, after))
            with self.subTest(change=after), self.assertRaisesRegex(ValueError, "profile/remap"):
                background.verify_import(self.project, self.inventory)
        sidecar.write_text(original)
        row = self.inventory["assets"][0]
        (self.project / row["notice"]["file"]).write_text("changed after import")
        with self.assertRaisesRegex(ValueError, "size/hash"):
            background.verify_import(self.project, self.inventory)

    def test_true_import_setting_cannot_hide_missing_actual_mip_payloads(self):
        background.prepare_import(self.project, self.inventory)
        self.header_only_import()
        path = self.project / background.remap_path(self.inventory["assets"][0]["asset"]["file"]).removeprefix("res://")
        path.write_bytes(path.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError, "mipmap blocks"):
            background.verify_import(self.project, self.inventory)

    def test_restore_removes_synthetic_files_and_only_their_matching_import_cache(self):
        background.prepare_import(self.project, self.inventory)
        self.header_only_import()
        stale = "art/backgrounds/pz-hp-i2-old.png"
        (self.project / stale).write_bytes(self.png)
        (self.project / (stale + ".import")).write_text("old technical sidecar")
        remap = background.remap_path(stale).removeprefix("res://")
        (self.project / remap).write_bytes(b"old imported texture")
        (self.project / remap).with_suffix(".md5").write_bytes(b"old import digest")
        unrelated = self.project / (".godot/imported/pz-hp-i2-old.png-" + "f"*32 + ".ctex")
        unrelated.write_bytes(b"same basename from another namespace")
        for _ in range(2):
            background.restore_sources(self.source.parent, self.project, self.inventory)
            self.assertEqual({p.name for p in (self.project / "art/backgrounds").iterdir()},
                             {IDS["a"] + ".png", IDS["a"] + ".txt"})
            self.assertEqual(list((self.project / ".godot/imported").iterdir()), [unrelated])
        self.assertFalse(list((self.source / "art/backgrounds").glob("*.import")))

    def test_empty_legacy_source_inventory_stays_standard_library_and_rejects_strays(self):
        source_root = self.root / "legacy"
        (source_root / "game/data").mkdir(parents=True)
        (source_root / "content").mkdir()
        (source_root / "content/registry.json").write_text(json.dumps(dict(format="picross-content-registry-v2", entries=[])))
        (source_root / "game/data/registry.json").write_text(json.dumps(dict(format="picross-runtime-registry-v5", categories=[], entries=[])))
        self.assertEqual(background.source_inventory(source_root)["assets"], [])
        stray = source_root / "game/art/backgrounds/pz-unbound.png.import"
        stray.parent.mkdir(parents=True)
        stray.write_text("engine import must not write into this namespace")
        with self.assertRaisesRegex(ValueError, "Unknown/noncanonical"):
            background.source_inventory(source_root)

    def test_metadata_inventory_requires_v7_or_v8_and_keeps_legacy_capability_optional(self):
        source_root = self.root / "metadata"
        (source_root / "game/data").mkdir(parents=True)
        (source_root / "content").mkdir()
        (source_root / "content/registry.json").write_text(json.dumps(dict(
            format="picross-content-registry-v4", entries=[], metadata=[], backgrounds=[])))
        runtime_path = source_root / "game/data/registry.json"
        runtime = dict(format="picross-runtime-registry-v7", categories=[], entries=[])
        runtime_path.write_text(json.dumps(runtime))
        self.assertEqual(background.source_inventory(source_root)["assets"], [])
        runtime_path.write_text(json.dumps({**runtime, "format": "picross-runtime-registry-v8"}))
        self.assertEqual(background.source_inventory(source_root)["assets"], [])
        capability = dict(format="picross-runtime-background-capability-v1",
                          runtime_format="picross-runtime-registry-v6",
                          profile_id="picross-background-png2304-v1", enabled=False)
        capability_path = source_root / "game/data/background-capability.json"
        capability_path.write_text(json.dumps(capability))
        self.assertEqual(background.source_inventory(source_root)["assets"], [])
        runtime_path.write_text(json.dumps({**runtime, "format": "picross-runtime-registry-v6"}))
        with self.assertRaisesRegex(ValueError, "generation differs"):
            background.source_inventory(source_root)
        runtime_path.write_text(json.dumps(runtime))
        capability_path.write_text(json.dumps({**capability, "enabled": "false"}))
        with self.assertRaisesRegex(ValueError, "Invalid background capability"):
            background.source_inventory(source_root)

    def test_fixed_patterns_have_distinct_source_and_pixel_identity(self):
        second, rgba = png("b")
        self.assertNotEqual(hashlib.sha256(second).digest(), hashlib.sha256(self.png).digest())
        self.assertNotEqual(hashlib.sha256(rgba).digest(), hashlib.sha256(self.rgba).digest())
        self.assertEqual(len(rgba), 2304*576*4)
        self.assertEqual(set(rgba[3::4]), {0, 96, 175, 205})

    def test_both_presets_ship_notices_and_only_web_ships_worker(self):
        import configparser
        config = configparser.ConfigParser(interpolation=None)
        root = Path(__file__).resolve().parents[1]
        config.read(root / "game/export_presets.cfg")
        for section in ("preset.0", "preset.1"):
            self.assertIn("art/backgrounds/*.txt", config[section]["include_filter"])
        self.assertNotIn("web/background_loader.js", config["preset.0"]["include_filter"])
        self.assertIn("web/background_loader.js", config["preset.1"]["include_filter"])
        self.assertNotIn("web/*", config["preset.1"]["exclude_filter"])
        self.assertEqual(config["preset.1.options"]["variant/thread_support"], "false")
