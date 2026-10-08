"""Study trust boundary: mutations update file hashes so semantic checks must fail."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.puzzle_production import vs1
from tools.puzzle_production.contract import InvalidInput, InvalidProof, load_json, write_json
from tools.puzzle_production.images import file_hash


class StudyTests(unittest.TestCase):
    def test_e1_extension_cannot_rebind_historical_production(self):
        with tempfile.TemporaryDirectory() as tmp:
            study=Path(tmp)
            for name in ('manifest.json','plan.json','plan-vb1.json'):
                shutil.copyfile(vs1.STUDY/name,study/name)
            original=load_json(study/'plan.json')
            for attack in ('historical slot','missing E1','archive bytes'):
                active=copy.deepcopy(original)
                if attack=='historical slot': active['slots'][0]['dimensions']=[50,40]
                if attack=='missing E1': active.pop('VS-E1-R2')
                write_json(study/'plan.json',active)
                if attack=='archive bytes':
                    (study/'plan-vb1.json').write_bytes((study/'plan-vb1.json').read_bytes()+b'\n')
                with self.subTest(attack=attack),patch.object(vs1,'STUDY',study),self.assertRaises(InvalidInput):
                    vs1.verify_cases()

    def test_all_ten_reconstruct_sources_and_replay_proofs(self):
        report=vs1.verify_cases()
        self.assertEqual(len(report),10)
        self.assertTrue(all(r['certified'] and r['proof_steps'] for r in report))

    def test_definition_proof_orientation_palette_paths_and_reveal_mutations(self):
        original=load_json(vs1.STUDY/'manifest.json')
        attacks={
            'width':('definition.json',lambda d:d.update(width=31)),
            'orientation':('definition.json',lambda d:d['solution'].reverse()),
            'clue':('definition.json',lambda d:d['rows'].reverse()),
            'palette':('definition.json',lambda d:d['palette'][0].update(color='ffffff')),
            'path':('definition.json',lambda d:d['reveal'].update(image='res://art/f01.svg')),
            'truncated proof':('proof.json',lambda d:d['steps'].pop()),
            'wrong enddomains':('proof.json',lambda d:d['final_domains'][0][0].append('ink')),
        }
        with tempfile.TemporaryDirectory() as tmp:
            study=Path(tmp)/'study'; runtime=Path(tmp)/'runtime'
            study.mkdir(); runtime.mkdir()
            shutil.copyfile(vs1.STUDY/'plan.json',study/'plan.json')
            shutil.copyfile(vs1.STUDY/'plan-vb1.json',study/'plan-vb1.json')
            shutil.copytree(vs1.STUDY/'cases/vs01',study/'cases/vs01')
            shutil.copytree(vs1.RUNTIME/'cases/vs01',runtime/'cases/vs01')
            for label,(filename,mutate) in attacks.items():
                with self.subTest(label=label):
                    value=load_json(vs1.STUDY/'cases/vs01'/filename,64*1024*1024)
                    mutate(value)
                    target=study/'cases/vs01'/filename
                    write_json(target,value)
                    manifest=copy.deepcopy(original)
                    manifest['cases'][0]['files'][filename]=file_hash(target)
                    write_json(study/'manifest.json',manifest)
                    catalog=load_json(vs1.RUNTIME/'catalog.json')
                    catalog['cases'][0]['definition_sha256']=manifest['cases'][0]['files']['definition.json']
                    write_json(runtime/'catalog.json',catalog)
                    if filename=='definition.json': shutil.copyfile(target,runtime/'cases/vs01'/filename)
                    with patch.object(vs1,'STUDY',study),patch.object(vs1,'RUNTIME',runtime),self.assertRaises((InvalidInput,InvalidProof)):
                        vs1.verify_cases()
                    shutil.copyfile(vs1.STUDY/'cases/vs01'/filename,target)
            (study/'cases/vs01/proof.json').unlink()
            write_json(study/'manifest.json',original)
            shutil.copyfile(vs1.RUNTIME/'catalog.json',runtime/'catalog.json')
            with patch.object(vs1,'STUDY',study),patch.object(vs1,'RUNTIME',runtime),self.assertRaises((OSError,InvalidInput)):
                vs1.verify_cases()

    def test_manifest_cannot_certify_diagnostics_or_swap_sources(self):
        original=load_json(vs1.STUDY/'manifest.json')
        attacks=[lambda m:m['cases'][1].update(id='vs01'),
                 lambda m:m['cases'][0].update(kind='diagnostic'),
                 lambda m:m['cases'][0].update(dimensions=[40,30]),
                 lambda m:m['cases'][0].update(reveal_source=m['cases'][1]['reveal_source']),
                 lambda m:m['cases'][0].update(source={'kind':'import','bundle':'../../unbound','variant':'x'}),
                 lambda m:m.update(owner_trial='passed')]
        with tempfile.TemporaryDirectory() as tmp:
            study=Path(tmp)
            shutil.copyfile(vs1.STUDY/'plan.json',study/'plan.json')
            shutil.copyfile(vs1.STUDY/'plan-vb1.json',study/'plan-vb1.json')
            for attack in attacks:
                m=copy.deepcopy(original); attack(m); write_json(study/'manifest.json',m)
                with self.subTest(attack=attack),patch.object(vs1,'STUDY',study),self.assertRaises(InvalidInput):
                    vs1.verify_cases()

    def test_retained_repair_requires_complete_replay(self):
        with patch('tools.puzzle_production.repair.inspect_repair',return_value={'certified':False,'status':'incomplete'}),self.assertRaises(InvalidInput):
            vs1.read_source({'kind':'retained-rp6-repair','id':'F-09'})


if __name__=='__main__': unittest.main()
