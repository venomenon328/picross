"""Committed deliveries require the complete pinned ID namespace and selected original bytes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from tests.puzzle_production import current_fixtures as fixture
from tools.production_workspace.sources import GitSource
from tools.puzzle_production import catalog_integration, current_delivery, puzzle_record


class CurrentCompletionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        work = Path(temp.name)
        self.root = fixture.checkout(work / "repo")
        self.key = "pz-current"
        source = fixture.make(work / "input", identifier=self.key, background="selected")
        catalog_integration.integrate(source,self.root,apply=True)
        self.git("init","-q","-b","main")
        self.original = self.commit()
        self.source = GitSource(self.root)

    def git(self,*args):
        return subprocess.check_output(["git","-C",str(self.root),*args], stderr=subprocess.PIPE,text=True).strip()

    def commit(self):
        self.git("add",".")
        self.git("-c","user.name=Synthetic","-c","user.email=test@example.invalid","commit","-qm","Synthetic catalog")
        return self.git("rev-parse","HEAD")

    def test_pinned_delivery_rejects_missing_record_and_preserves_original(self):
        expected = current_delivery.from_source(self.source,self.original,self.key)
        (self.root / puzzle_record.path(self.key)).unlink()
        with self.assertRaisesRegex(ValueError,"inventory"):
            current_delivery.from_source(self.source,self.commit(),self.key)
        self.assertEqual(current_delivery.from_source(self.source,self.original,self.key),expected)

    def test_rights_change_and_foreign_record_are_visible_at_own_commit(self):
        before = current_delivery.from_source(self.source,self.original,self.key)
        notice = "game/art/backgrounds/"+self.key+".txt"
        (self.root / notice).write_bytes(b"New synthetic notice.\n")
        after = current_delivery.from_source(self.source,self.commit(),self.key)
        self.assertNotEqual(before["files"][notice],after["files"][notice])
        (self.root / puzzle_record.path("pz-foreign")).write_bytes(b"{}")
        with self.assertRaisesRegex(ValueError,"inventory"):
            current_delivery.from_source(self.source,self.commit(),self.key)
