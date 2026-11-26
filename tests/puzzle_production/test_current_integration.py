"""RI-ONE current input, bounded publication and recovery contracts."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.current_fixtures import put, checkout, make, approve, json_file, fingerprints
from tools.puzzle_production import catalog_integration as core, current_content as content
from tools.puzzle_production import current_registration as transaction, integration_input, catalog_io
from tools.puzzle_production import editor_change
from tools.puzzle_production.contract import InvalidInput


def registration_batch(source, current, repo, *, record=None):
    from tools.puzzle_production import batch_io
    evidence = put(source, "order.txt", b"Synthetic batch integration order.\n")
    authorization = json_file(source, "order.json", {"format":"picross-integration-order-v1",
        "operation":"register", "puzzle_id":"pz-current", "revision":"r01", "actor":"Synthetic test",
        "timestamp_utc":"2026-11-16T00:00:00Z", "statement":"Integrate this synthetic selection.",
        "evidence":evidence, "test_only":True})
    inputs = {"current":{"directory":current.relative_to(source).as_posix(), "files":batch_io.inventory(current)}}
    if record is not None:
        inputs["pw_record"] = content.ref(record.relative_to(source).as_posix(), record.read_bytes())
    return {"format":"picross-integration-batch-plan-v2","batch_id":"current-test","revision":1,
            "previous_plan_sha256":None,"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip(),
            "jobs":[{"job_id":"first","puzzle_id":"pz-current","revision":"r01","operation":"register",
                     "authorization":authorization,"inputs":inputs,"parameters":{},
                     "budgets":{"export_seconds":300,"plan_seconds":300,"reconcile_seconds":300,
                                "publication_seconds":1800,"recovery_seconds":1800},
                     "max_attempts":dict.fromkeys(("export","plan","apply","reconcile"),3)}]}


class CurrentIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name)
        self.root=checkout(self.work/"checkout")

    def test_modes_backgrounds_and_byte_mtime_noop(self):
        for mode,status in (("mono","standard"),("color","none"),("color","selected")):
            with self.subTest(mode=mode,background=status):
                root=checkout(self.work/(mode+"-"+status))
                source=make(self.work/("input-"+mode+"-"+status),mode=mode,background=status,
                            colors=2 if mode == "color" else 1)
                before=fingerprints(root)
                plan = core.integrate(source,root)
                self.assertEqual(plan["status"], "planned")
                self.assertEqual(len(plan["changes"]), 9 if status == "selected" else 7)
                self.assertEqual(fingerprints(root),before)
                self.assertEqual(core.integrate(source,root,apply=True)["status"],"registered")
                before=fingerprints(root)
                self.assertEqual(core.integrate(source,root,apply=True)["status"],"no-op")
                self.assertEqual(fingerprints(root),before)
                entry=json.loads((root/"content/puzzles/pz-current.json").read_bytes())
                self.assertEqual(entry["mode"],mode)
                self.assertNotIn("production",entry)
                self.assertFalse((root/"content/packages").exists())

    def test_versioned_review_cannot_use_legacy_criterion_booleans(self):
        source = make(self.work/'old-review')
        manifest = json.loads((source/'manifest.json').read_bytes())
        manifest['format'] = integration_input.FINDING_FORMAT
        approve(source,manifest)
        json_file(source,'manifest.json',manifest)
        before = fingerprints(self.root)
        with self.assertRaises(InvalidInput):
            core.integrate(source,self.root,apply=True)
        self.assertEqual(fingerprints(self.root),before)

    def test_current_input_needs_no_producer_or_rulebook(self):
        source=make(self.work/"input")
        value=integration_input.Input(source)
        self.assertEqual(set(value.checked),{"format","method","production_mode","current_source","logic_binding",
                                            "rating","compact_analysis","rating_revision","record_hash"})
        self.assertNotIn("tool",value.checked)
        with patch("tools.puzzle_production.solver.solve",side_effect=AssertionError("Integrator must verify, not solve")):
            core.integrate(source,self.root,apply=True)

    def test_invalid_definition_proof_and_decision_rejected_without_writes(self):
        source=make(self.work/"input")
        original=json.loads((source/"manifest.json").read_bytes())
        for kind in ("definition","proof","approval"):
            with self.subTest(kind=kind):
                value=deepcopy(original)
                if kind=="approval":
                    value["approval"]["selection_sha256"]="0"*64
                else:
                    filename=value[kind]["file"]
                    old=(source/filename).read_bytes()
                    altered=json.loads(old)
                    if kind=="definition":altered["rows"][0][0]["length"]=2
                    else:altered["final_domains"][0][0]=["c1"]
                    value[kind]=json_file(source,filename,altered)
                    approve(source,value)
                json_file(source,"manifest.json",value)
                before=fingerprints(self.root)
                with self.assertRaises((InvalidInput,ValueError)):
                    core.integrate(source,self.root,apply=True)
                self.assertEqual(fingerprints(self.root),before)
                if kind!="approval":(source/filename).write_bytes(old)
        json_file(source,"manifest.json",original)

    def test_occupied_id_and_slot_are_conflicts(self):
        source=make(self.work/"first")
        core.integrate(source,self.root,apply=True)
        other=make(self.work/"second",identifier="pz-other")
        value=json.loads((other/"manifest.json").read_bytes())
        value["entry"]["save_slot"]="pz-current";approve(other,value)
        before=fingerprints(self.root)
        with self.assertRaisesRegex(InvalidInput,"Occupied current save_slot"):
            core.integrate(other,self.root,apply=True)
        self.assertEqual(fingerprints(self.root),before)
        value=json.loads((source/"manifest.json").read_bytes())
        value["entry"]["visible"]=False;approve(source,value)
        with self.assertRaisesRegex(InvalidInput,"Occupied ID"):
            core.integrate(source,self.root,apply=True)
        self.assertEqual(fingerprints(self.root),before)

    def test_interrupted_current_write_and_repeated_recovery(self):
        source=make(self.work/"input")
        before=fingerprints(self.root)
        with self.assertRaises(RuntimeError):
            core.integrate(source,self.root,apply=True,fail_step=4)
        self.assertTrue((self.root/transaction.LOCK).exists())
        self.assertEqual(transaction.recover(self.root)["status"],"rolled-back")
        # Rollback restores data; timestamps of restored shared files may change.
        self.assertEqual({k:v[0] for k,v in fingerprints(self.root).items()},{k:v[0] for k,v in before.items()})
        stable=fingerprints(self.root)
        self.assertEqual(transaction.recover(self.root)["status"],"no-op")
        self.assertEqual(fingerprints(self.root),stable)
        self.assertEqual(core.integrate(source,self.root,apply=True)["status"],"registered")

    def test_recovery_preserves_foreign_data(self):
        source=make(self.work/"input")
        with self.assertRaises(RuntimeError):
            core.integrate(source,self.root,apply=True,fail_step=4)
        changed=self.root/"content/puzzles/pz-current.json"
        changed.write_bytes(b'{"foreign":true}\n')
        before=fingerprints(self.root)
        with self.assertRaisesRegex(InvalidInput,"Foreign"):
            transaction.recover(self.root)
        self.assertEqual(fingerprints(self.root),before)

    def test_no_foreign_archive_reads_during_plan_write_repeat_or_batch_result(self):
        source=make(self.work/"input")
        trap=self.root/"content/packages/pz-unrelated/r01/input/package.zip"
        trap.parent.mkdir(parents=True);trap.write_bytes(b"unrelated archive")
        original=catalog_io.read
        def guarded(root,name,*args,**kwargs):
            if "content/packages/" in name:raise AssertionError("Foreign archive read: "+name)
            return original(root,name,*args,**kwargs)
        with patch.object(catalog_io,"read",side_effect=guarded):
            core.integrate(source,self.root)
            core.integrate(source,self.root,apply=True)
            core.integrate(source,self.root)
            from tools.puzzle_production.integration_batch_operations import reached
            self.assertEqual(reached(self.root,"pz-current")["entry"]["id"],"pz-current")

    def test_cli_and_export_use_current_input(self):
        source=make(self.work/"input")
        output=self.work/"export"
        integration_input.export(source,output)
        result=subprocess.run([sys.executable,"-m","tools.puzzle_production.target_adapter","register",
                               "--input",str(output),"--checkout",str(self.root)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"],"registered")
        self.assertEqual(core.integrate(source,self.root)["status"],"no-op")

    def test_editor_listing_detail_metadata_and_raster_use_current_sources(self):
        source=make(self.work/"input")
        core.integrate(source,self.root,apply=True)
        self.assertEqual(len(editor_change.listing(self.root)["entries"]),1)
        self.assertFalse(editor_change.detail(self.root,"pz-current")["source_migration_required"])
        request={"id":"pz-current","metadata":{"name":"Renamed","category_id":"test"},
                 "text":None,"profile":None,"reveal":None,"background":None}
        plan=editor_change.plan(self.root,request)
        self.assertEqual(editor_change.apply(self.root,plan)["status"],"updated")
        self.assertEqual(editor_change.detail(self.root,"pz-current")["detail"]["metadata"]["name"],"Renamed")
        request.update(metadata=None,text="1 1 1\n1 1 1\n1 1 1",profile="line")
        plan=editor_change.plan(self.root,request,work=self.work/"raster-work")
        self.assertEqual(editor_change.apply(self.root,plan)["status"],"updated")
        self.assertEqual(editor_change.detail(self.root,"pz-current")["raster"]["revision"],2)
        self.assertFalse((self.root/"content/packages").exists())

    def test_actual_batch_run_and_resume_only_current_selected_data(self):
        from tools.puzzle_production import integration_batch_runner as runner, batch_io
        repo=Path(__file__).resolve().parents[2]
        source=self.work/"sources";make(source/"current")
        plan=registration_batch(source,source/"current",repo)
        path=self.work/"batch.json";path.write_bytes(content.encoded(plan))
        work=self.work/"batch-work"
        original=catalog_io.read
        def guarded(root,name,*args,**kwargs):
            if "content/packages/" in name:raise AssertionError("Unrelated archive read")
            return original(root,name,*args,**kwargs)
        with patch.object(catalog_io,"read",side_effect=guarded):
            result=runner.run(path,source,repo,self.root,work)
            self.assertEqual(result["status"],"completed",{"jobs":result.get("jobs"),"errors":[a.get("result",{}).get("error") for a in result.get("attempts",[])]})
            before={n:v for n,v in fingerprints(self.root).items() if not n.startswith(".picross-")}
            result=runner.resume(path,source,repo,self.root,work)
            self.assertEqual(result["status"],"completed",{"jobs":result.get("jobs"),"errors":[a.get("result",{}).get("error") for a in result.get("attempts",[])]})
            self.assertEqual(before,{n:v for n,v in fingerprints(self.root).items() if not n.startswith(".picross-")})

    def test_visual_rights_and_path_failures_cannot_be_reapproved(self):
        source=make(self.work/"input")
        original=json.loads((source/"manifest.json").read_bytes())
        for kind in ("visual", "rights", "path", "reserved-slot"):
            value=deepcopy(original)
            if kind=="visual":
                review=json.loads((source/"review.json").read_bytes())
                review["criteria"]["Q-R04"].update(result="failed",accepted=False)
                value["quality"]["review"]=json_file(source,"failed-review.json",review)
            elif kind=="rights": value["reveal"]["rights"]["author"]="Invented author absent from notice"
            elif kind=="path": value["proof"]["file"]="../proof.json"
            else: value["entry"]["save_slot"]="CON"
            approve(source,value)
            before=fingerprints(self.root)
            with self.assertRaises(InvalidInput): core.integrate(source,self.root,apply=True)
            self.assertEqual(fingerprints(self.root),before)

    def test_profile_and_runtime_interruptions_are_recoverable(self):
        source = make(self.work/"profile-input")
        before = {n: v[0] for n, v in fingerprints(self.root).items()}
        for path in ("game/art/catalog/pz-current-ui100.png", "content/puzzles/pz-current.json", content.RUNTIME):
            def interrupt(phase, name=None):
                if phase == "after-write" and name == path:
                    raise RuntimeError("synthetic interruption")
            with patch.object(transaction, "checkpoint", side_effect=interrupt), self.assertRaises(RuntimeError):
                core.integrate(source, self.root, apply=True)
            self.assertEqual(transaction.recover(self.root)["status"], "rolled-back")
            self.assertEqual(transaction.recover(self.root)["status"], "no-op")
            self.assertEqual(before, {n: v[0] for n, v in fingerprints(self.root).items()})

    def test_runtime_last_and_controlled_abort_rolls_back_with_own_budget(self):
        from tools.puzzle_production.contract import Aborted
        source=make(self.work/"input")
        before={k:v[0] for k,v in fingerprints(self.root).items()}
        writes=[]
        def abort(where,name=None):
            if where=="after-write":
                writes.append(name)
                if len(writes)==2: raise Aborted("synthetic bounded interruption")
        with patch.object(transaction,"boundary",side_effect=abort):
            with self.assertRaises(Aborted):core.integrate(source,self.root,apply=True)
        self.assertEqual({k:v[0] for k,v in fingerprints(self.root).items()},before)
        self.assertFalse(transaction.pending(self.root))
        writes=[]
        with patch.object(transaction,"boundary",side_effect=lambda where,name=None:writes.append(name) if where=="after-write" else None):
            core.integrate(source,self.root,apply=True)
        self.assertEqual(writes[-1],content.RUNTIME)

    def test_concurrent_source_and_unknown_journal_preserve_foreign_bytes(self):
        source=make(self.work/"input")
        before={k:v[0] for k,v in fingerprints(self.root).items()}
        changed=False
        def mutate(where,name=None):
            nonlocal changed
            if where=="after-write" and not changed:
                changed=True;(source/"approval.txt").write_text("Foreign decision",encoding="utf-8")
        with patch.object(transaction,"boundary",side_effect=mutate):
            with self.assertRaises(InvalidInput):core.integrate(source,self.root,apply=True)
        self.assertEqual({k:v[0] for k,v in fingerprints(self.root).items()},before)
        self.assertEqual((source/"approval.txt").read_text(),"Foreign decision")
        put(self.root,transaction.LOCK,b'{"format":"picross-registration-journal-v6"}\n')
        before=fingerprints(self.root)
        with self.assertRaises(InvalidInput):transaction.recover(self.root)
        self.assertEqual(fingerprints(self.root),before)



    def test_hg31_new_profile_first_integration_and_capability_boundary(self):
        from io import BytesIO
        from PIL import Image, PngImagePlugin
        source=make(self.work/'hg31-input',background='selected')
        value=json.loads((source/'manifest.json').read_bytes())
        image=Image.new('RGBA',(2304,768),(0,0,0,0));image.putpixel((100,700),(60,60,60,128))
        stream=BytesIO();info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\0');image.save(stream,format='PNG',pnginfo=info)
        raw=stream.getvalue();value['background']['image']['asset']=put(source,'background.png',raw);approve(source,value)
        before=fingerprints(self.root)
        with self.assertRaisesRegex(ValueError,'capability'): core.integrate(source,self.root,apply=True)
        self.assertEqual(fingerprints(self.root),before)
        json_file(self.root,'game/data/background-capability.json',{'format':'picross-runtime-background-capability-v2',
            'runtime_format':'picross-runtime-registry-v8','profile_ids':['picross-background-png2304-v1','picross-background-png2304x768-v1'],'enabled':True})
        self.assertEqual(core.integrate(source,self.root)['status'],'planned')
        self.assertEqual(core.integrate(source,self.root,apply=True)['status'],'registered')
        self.assertEqual((self.root/'game/art/backgrounds/pz-current.png').read_bytes(),raw)
        before=fingerprints(self.root)
        self.assertEqual(core.integrate(source,self.root,apply=True)['status'],'no-op')
        self.assertEqual(fingerprints(self.root),before)
