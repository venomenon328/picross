"""Small synthetic PE-A3 regressions; no real catalog or player profiles."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.catalog_fixtures import registered
from tests.puzzle_production.test_catalog_images import PROVENANCE, DECISION, SVG, snapshot
from tools.puzzle_production import catalog_raster as raster, editor_raster as wire
from tools.puzzle_production import catalog_images as images, content_registry as registry
from tools.puzzle_production import catalog_transaction as tx
from tools.puzzle_production.contract import write_json, load_json


class RasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="pe-a3-input-")
        cls.addClassCleanup(cls.shared.cleanup)
        cls.shared_root = Path(cls.shared.name)
        registered(cls.shared_root,stem="pe_raster",save_slot="pe_raster")
        images.apply_migration(cls.shared_root/"base",images.plan_migration(cls.shared_root/"base"))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="pe-a3-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.home/"checkout"
        shutil.copytree(self.shared_root/"base",self.root)
        self.entry = registry.check_checkout(self.root)["entries"][0]
        self.identifier = self.entry["id"]
        self.input = self.home/"input"
        self.input.mkdir()

    def request(self,text=None,**changes):
        if text is None: text = raster.view(self.root,self.identifier)["text"]
        value = {"format":wire.REQUEST,"id":self.identifier,"text":text,"metadata":None,"reveal":None,
                 "background":None,"decision":deepcopy(DECISION),"provenance":deepcopy(PROVENANCE),"profile":"line"}
        value.update(changes)
        write_json(self.input/"request.json",value)
        return self.input/"request.json"

    def test_text_errors_positions_and_clues(self):
        palette = [{"id":1},{"id":2}]
        self.assertEqual(wire.parse("01\t2\r\n0  1\r\n",palette),[[1,2],[0,1]])
        self.assertEqual(wire.parse("0"*5000+"1",palette),[[1]])
        self.assertEqual(wire.clues([1,1,2,0,2]),[{"length":2,"color":1},{"length":1,"color":2},{"length":1,"color":2}])
        for text,position in (("1 2\n1","2, Spalte 2"),("1\n\n1","2, Spalte 1"),("1 -1","1, Spalte 2"),
                              ("1 3","1, Spalte 2"),("1 1.0","1, Spalte 2"),("1 +1","1, Spalte 2")):
            with self.subTest(text=text),self.assertRaisesRegex(ValueError,position): wire.parse(text,palette)

    def test_logical_noop_is_byte_mtime_identical_and_never_analyzes(self):
        before = snapshot(self.root)
        text = raster.view(self.root,self.identifier)["text"].replace(" ","\t").replace("\n","\r\n")
        with patch.object(raster.analysis,"analyze_single",side_effect=AssertionError("unnecessary analysis")):
            value = raster.plan(self.root,self.request(text),self.home/"bundle")
            self.assertIsNone(value["quality"])
            self.assertEqual(value["files"],[])
            self.assertEqual(raster.apply(self.root,self.home/"bundle")["status"],"noop")
        self.assertEqual(before,snapshot(self.root))
        original_guard = raster._bundle_guard
        def concurrent_writer(*args):
            original_guard(*args)
            (self.root/tx.LOCK).write_bytes(b"foreign writer")
        with patch.object(raster,"_bundle_guard",side_effect=concurrent_writer),self.assertRaises(ValueError):
            raster.apply(self.root,self.home/"bundle")
        self.assertEqual((self.root/tx.LOCK).read_bytes(),b"foreign writer")
        (self.root/tx.LOCK).unlink()
        self.assertEqual(before,snapshot(self.root))

    def test_checked_dimension_change_and_combined_metadata_image(self):
        previous = snapshot(self.root)
        (self.input/"reveal.svg").write_bytes(SVG)
        from tools.puzzle_production.catalog_background import ref
        request = self.request("1 1 1\n1 1 1\n",metadata={"name":"Aktuelles Motiv"},
            reveal={"asset":ref("reveal.svg",SVG),"provenance":deepcopy(PROVENANCE)})
        value = raster.plan(self.root,request,self.home/"bundle")
        self.assertEqual(previous,snapshot(self.root))
        self.assertEqual(value["new"]["definition"]["revision"],value["old"]["definition"]["revision"]+1)
        self.assertEqual(raster.apply(self.root,self.home/"bundle")["status"],"applied")
        current = registry.check_checkout(self.root,replay=True)
        self.assertEqual(current["metadata"][0]["name"],"Aktuelles Motiv")
        self.assertEqual((self.root/"game/art/content/pe_raster.svg").read_bytes(),SVG)
        for path,(raw,_) in previous.items():
            if path.startswith(self.entry["production"]["package"]+"/"): self.assertEqual((self.root/path).read_bytes(),raw)
        self.assertFalse((self.root/tx.LOCK).exists())
        applied = snapshot(self.root)
        self.assertEqual(raster.apply(self.root,self.home/"bundle")["status"],"noop")
        self.assertEqual(applied,snapshot(self.root))

    def test_raster_preserves_manual_images_and_historical_registration(self):
        from tools.puzzle_production.catalog_background import ref
        (self.input/"reveal.svg").write_bytes(SVG)
        raster.plan(self.root,self.request("1 1\n1 1\n",reveal={"asset":ref("reveal.svg",SVG),"provenance":deepcopy(PROVENANCE)},
            background={"status":"standard","asset":None,"provenance":None}),self.home/"first")
        raster.apply(self.root,self.home/"first")
        old_reveal = load_json(self.root/"content/reveals"/(self.identifier+".json"))
        old_background = load_json(self.root/"content/backgrounds"/(self.identifier+".json"))
        raster.plan(self.root,self.request("1 1 1\n1 1 1\n"),self.home/"second")
        raster.apply(self.root,self.home/"second")
        registry.check_checkout(self.root,replay=True)
        for name,previous in (("reveals",old_reveal),("backgrounds",old_background)):
            current = load_json(self.root/"content"/name/(self.identifier+".json"))
            self.assertEqual(current["origin"],previous["origin"])
            self.assertEqual(current["current"],previous["current"])
        before = snapshot(self.root)
        self.assertEqual(registry.registration(self.shared_root/"export",self.root,apply=True)["status"],"no-op")
        self.assertEqual(before,snapshot(self.root))

    def test_stale_and_unprovable_edit_do_not_mutate_checkout(self):
        before = snapshot(self.root)
        with self.assertRaisesRegex(ValueError,"stalled"):
            raster.plan(self.root,self.request("1 0\n0 1\n"),self.home/"blocked")
        self.assertEqual(before,snapshot(self.root))
        raster.plan(self.root,self.request("1 1\n1 1\n"),self.home/"bundle")
        (self.root/"content/categories.json").write_bytes((self.root/"content/categories.json").read_bytes()+b"\n")
        changed = snapshot(self.root)
        with self.assertRaises(ValueError): raster.apply(self.root,self.home/"bundle")
        self.assertEqual(changed,snapshot(self.root))

    def test_interrupted_definition_publication_rolls_back(self):
        before = {name:row[0] for name,row in snapshot(self.root).items()}
        raster.plan(self.root,self.request("1 1\n1 1\n"),self.home/"bundle")
        with self.assertRaises(InterruptedError):
            raster.apply(self.root,self.home/"bundle",fail_step="crash-game/"+self.entry["definition"])
        self.assertTrue((self.root/tx.LOCK).exists())
        registry.recover(self.root)
        registry.check_checkout(self.root)
        self.assertEqual(before,{name:row[0] for name,row in snapshot(self.root).items()})
        prefix = self.root/"content/packages"/self.identifier/"editor-2"
        foreign = prefix/"foreign.txt"
        foreign.write_bytes(b"foreign")
        occupied = snapshot(self.root)
        with self.assertRaisesRegex(ValueError,"foreign"):
            raster.apply(self.root,self.home/"bundle")
        self.assertEqual(occupied,snapshot(self.root))
        foreign.unlink()
        self.assertEqual(raster.apply(self.root,self.home/"bundle")["status"],"applied")
        registry.check_checkout(self.root,replay=True)

    def test_verified_manual_retirement_keeps_live_proof_and_sync(self):
        from tools.puzzle_production import integrated_content
        raster.plan(self.root,self.request("1 1\n1 1\n"),self.home/"bundle")
        raster.apply(self.root,self.home/"bundle")
        write_json(self.root/integrated_content.INDEX,{"format":"picross-authoring-index-v1","entries":[]})
        def git(*args):
            return subprocess.check_output(["git",*args],cwd=self.root,stderr=subprocess.PIPE).decode().strip()
        git("init","-q")
        git("add",".")
        git("-c","user.name=Test","-c","user.email=test@example.invalid","commit","-qm","synthetic integrated editor source")
        commit = git("rev-parse","HEAD")
        git("update-ref","refs/remotes/origin/main",commit)
        before = {name:row for name,row in snapshot(self.root).items() if not name.startswith(".git/")}
        self.assertEqual(integrated_content.retire(self.root,[self.identifier],commit)["status"],"no-op")
        registry.sync_runtime(self.root)
        registry.check_checkout(self.root,replay=True)
        self.assertEqual(before,{name:row for name,row in snapshot(self.root).items() if not name.startswith(".git/")})
