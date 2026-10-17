"""SD-B-T01: frozen independent inputs and exact arithmetic counterexamples.

No sampling, parameter fitting, catalog reading or production snapshots in tests.
"""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.analysis import analyze
from tools.puzzle_production.analysis_contract import AnalysisBudget, analysis_input, result_data
from tools.puzzle_production.analysis_io import analyze_file, check_bundle
from tools.puzzle_production.analysis_verifier import verify_trace
from tools.puzzle_production.contract import Budget, InvalidInput, InvalidProof, digest, load_json, validate_logic, write_json
from tools.puzzle_production.difficulty_rating import (METHOD_ID, frozen_method, logical_level,
    profile, rating_result, size_effect)
from tools.puzzle_production.solver import solve
from test_paired import wire

ROOT = Path(__file__).resolve().parents[2] / "tools" / "puzzle_production"
REFERENCES = load_json(ROOT / "difficulty_references_0_3.json")["references"]
BY_ID = {r["id"]: r for r in REFERENCES}


def features(family, demand, *, fluent=False, local=False):
    return {"highest_family": f"R{family}", "demand": [demand.numerator, demand.denominator],
            "fluent_r1": fluent, "localized_combination": local}


def wave(family=2, offer=(1, 4), open_cells=4, cardinalities=((2, 1),)):
    # Explicit arithmetic input, NOT a certified trace or a puzzle reference.
    return {"family": f"R{family}", "productive_fraction": list(offer),
            "open_cells_before": open_cells, "domain_cardinalities": list(cardinalities),
            "removed_values": sum(a-b for a, b in cardinalities)}


def metrics(waves, area=100, colors=1):
    return {"waves": waves, "workload": {"cells": area, "colors": colors}}


class ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = frozen_method()["configuration"]

    def test_level_boundaries_exactly_below_equal_above(self):
        for family in (2, 3):
            for demand, extra in ((Fraction(749,1000),0), (Fraction(3,4),1), (Fraction(751,1000),1)):
                self.assertEqual(logical_level(features(family,demand), self.config), family+1+extra)
        self.assertEqual(logical_level(features(0,Fraction(1)),self.config),1)
        self.assertEqual(logical_level(features(1,Fraction(1)),self.config),2)
        self.assertEqual(logical_level(features(1,Fraction(1),fluent=True),self.config),1)
        self.assertEqual(logical_level(features(2,Fraction(0),local=True),self.config),2)

    def test_fluent_r1_offer_and_gain_are_inclusive_alternatives(self):
        for numerator, expected in ((499,False),(500,True),(501,True)):
            p=profile(metrics([wave(1,(numerator,1000),1000)]),self.config)
            self.assertEqual(p["fluent_r1"],expected)
        for changed, expected in ((499,False),(500,True),(501,True)):
            p=profile(metrics([wave(1,(1,100),1000,[(2,1)]*changed)],10000),self.config)
            self.assertEqual(p["fluent_r1"],expected)
        self.assertEqual(profile(metrics([wave(1)]*1000,10000),self.config)["demand"],[0,1])

    def test_local_combination_information_offer_gain_boundaries(self):
        for removed, expected in ((124,True),(125,True),(126,False)):
            p=profile(metrics([wave(2,(1,1),removed,[(2,1)]*removed)],1000),self.config)
            self.assertEqual(p["localized_combination"],expected)
        for numerator, expected in ((499,False),(500,True),(501,True)):
            p=profile(metrics([wave(2,(numerator,1000),1)],100),self.config)
            self.assertEqual(p["localized_combination"],expected)
        for changed, expected in ((499,False),(500,True),(501,True)):
            p=profile(metrics([wave(2,(1,1),1000,[(2,1)]*changed)],10000),self.config)
            self.assertEqual(p["localized_combination"],expected)

    def test_narrow_offer_gain_phase_duration_and_saturation(self):
        for numerator, expected in ((249,1),(250,1),(251,0)):
            p=profile(metrics([wave(2,(numerator,1000),4)]),self.config)
            self.assertEqual(p["bottleneck_waves"],expected)
        for changed, expected in ((249,1),(250,1),(251,0)):
            p=profile(metrics([wave(2,(1,4),1000,[(2,1)]*changed)],10000),self.config)
            self.assertEqual(p["bottleneck_waves"],expected)
        narrow=wave(2,(1,10),10)
        for count in (3,4,5):
            p=profile(metrics([narrow]*count),self.config)
            self.assertEqual(Fraction(*p["recurrence_bonus"]),Fraction(min(count,4),16))
            self.assertEqual(p["longest_bottleneck"],count)
        p=profile(metrics([narrow,narrow,wave(0),narrow]),self.config)
        self.assertEqual((p["bottleneck_waves"],p["bottleneck_phases"],p["longest_bottleneck"]),(3,2,2))
        self.assertEqual(p["recurrence_bonus"],[5,32])
        self.assertEqual(profile(metrics([narrow]*5),self.config)["demand"],[1,1])

    def test_local_peak_survives_easy_prefix_and_cleanup_does_not_inflate(self):
        hard=[wave(3,(1,9),14),wave(2,(1,9),13)]
        p=profile(metrics(hard,1000),self.config)
        longer=profile(metrics([wave(0,(1,1),1)]*500+hard+[wave(0,(1,100),1)]*200,1000),self.config)
        for key in ("peak_strain","demand","bottleneck_waves","longest_bottleneck"):
            self.assertEqual(p[key],longer[key])
        self.assertEqual(longer["cleanup_suffix_waves"],200)
        self.assertEqual(logical_level(longer,self.config),5)
        for broad in (wave(3,(1,1),100),wave(3,(1,100),1)):
            p=profile(metrics([broad]),self.config)
            self.assertEqual(p["peak_strain"],[0,1])
            self.assertEqual(p["bottleneck_waves"],0)
            self.assertEqual(logical_level(p,self.config),4)

    def test_partial_information_is_fractional_and_color_count_is_not_a_weight(self):
        p=profile(metrics([wave(2,(1,2),4,[(3,2),(3,1)])],4,2),self.config)
        self.assertEqual(p["peak_strain"],[5,16])  # gain=(1/2+1)/4=3/8
        self.assertEqual(p["strong_information_fraction"],[3,8])
        for colors in (1,2,8):
            p=profile(metrics([wave(2,(1,1),8,[(colors+1,1)]*8)],64,colors),self.config)
            self.assertEqual(p["strong_information_fraction"],[1,8])
            self.assertTrue(p["localized_combination"])
        empty=profile(metrics([]),self.config)
        self.assertEqual(empty["demand"],[0,1])
        self.assertEqual(empty["bottleneck_phases"],0)

    def test_size_breakpoints_and_gates(self):
        p=features(1,Fraction(0))
        for area, pressure in ((99,Fraction(0)),(100,Fraction(0)),(101,Fraction(1,6400)),
                               (1699,Fraction(1599,6400)),(1700,Fraction(1,4)),(1701,Fraction(1,4))):
            self.assertEqual(Fraction(*size_effect(area,2,p,self.config)[0]),pressure)
        for area, expected in ((899,0),(900,1),(901,1)):
            self.assertEqual(size_effect(area,2,p,self.config)[1],expected)
        for family, base in ((2,3),(3,4)):
            for demand, expected in ((Fraction(499,1000),0),(Fraction(1,2),1),(Fraction(501,1000),1)):
                self.assertEqual(size_effect(2500,base,features(family,demand),self.config)[1],expected)
            # At 900 cells z=1/8; exact combined boundary B=5/8.
            for demand, expected in ((Fraction(624,1000),0),(Fraction(5,8),1),(Fraction(626,1000),1)):
                self.assertEqual(size_effect(900,base,features(family,demand),self.config)[1],expected)
        for area in (1,100,900,1700,2500,10000):
            self.assertEqual(size_effect(area,1,None,self.config)[1],0)
            self.assertEqual(size_effect(area,5,None,self.config)[1],0)
            self.assertEqual(size_effect(area,4,features(2,Fraction(1)),self.config)[1],0)
            for family in range(4):
                for n in range(101):
                    p=features(family,Fraction(n,100))
                    base=logical_level(p,self.config)
                    adjustment=size_effect(area,base,p,self.config)[1]
                    self.assertIn(adjustment,(0,1))
                    self.assertLessEqual(base+adjustment,5)


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.method=frozen_method()

    def test_all_preselected_references_and_bound_identities(self):
        levels=set()
        evidence=load_json(ROOT/"difficulty_calibration_0_3.json")
        evidence_by_id={r["id"]:r for r in evidence["results"]}
        self.assertEqual(evidence["references_hash"],self.method["references"]["hash"])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for ref in REFERENCES:
                with self.subTest(ref=ref["id"]):
                    p=validate_logic(ref["logic"])
                    self.assertEqual(p.logic_hash,ref["logic_hash"])
                    self.assertEqual(digest(analysis_input(p)),ref["analysis_hash"])
                    source=root/(ref["id"]+".json");write_json(source,p.to_wire())
                    kwargs={}
                    if ref["r4_evidence_required"]:
                        baseline=root/(ref["id"]+"-base.json");pair=root/(ref["id"]+"-pair.json")
                        write_json(baseline,solve(p))
                        write_json(pair,solve(p,profile="paired-lines-mono" if p.format.endswith("v1") else "paired-lines-color"))
                        kwargs={"proof_path":pair,"baseline_path":baseline}
                    output=root/ref["id"]
                    report=analyze_file(source,output,method=METHOD_ID,**kwargs)
                    checked=check_bundle(source,output,method=METHOD_ID)
                    rating=load_json(output/"rating.json")["result"]
                    self.assertTrue(checked["rating_verified"])
                    self.assertEqual(rating["level"],ref["expected_level"])
                    expected=evidence_by_id[ref["id"]]
                    self.assertEqual(report["result"]["trace_hash"],expected["trace_hash"])
                    self.assertEqual(digest(report["result"]["metrics"]),expected["metrics_hash"])
                    self.assertEqual(rating,expected["rating_result"])
                    self.assertIsNone(report["result"]["method"])
                    self.assertIsNone(report["result"]["level"])
                    if rating["level"] is not None:
                        levels.add(rating["level"])
                        self.assertEqual(rating["confidence"],"medium")
                    if ref["id"]=="late-general-line":
                        self.assertTrue(report["result"]["line_analysis_complete"])
                        self.assertFalse(rating["r4_required"])
        self.assertEqual(levels,{1,2,3,4,5})

    def test_rotation_reflection_transposition_and_color_renaming(self):
        for id in ("fluid-r1","local-combination","sustained-combination","repeated-narrow","late-general-line","color-combination"):
            p=validate_logic(BY_ID[id]["logic"]);t=analyze(p);verify_trace(p,t)
            reference=rating_result(result_data(p,t),self.method)
            names=("empty",*p.colors)
            matrix=[[names[d.bit_length()-1] for d in row] for row in t["final_domains"]]
            variants=[matrix[::-1],[r[::-1] for r in matrix],list(map(list,zip(*matrix))),
                      list(map(list,zip(*matrix[::-1])))]
            rename={name:f"z{len(p.colors)-i}" for i,name in enumerate(p.colors)}
            variants.append([[rename.get(v,v) for v in row] for row in matrix])
            for index,cells in enumerate(variants):
                colors=tuple(rename.values()) if index==4 else p.colors
                q=validate_logic(wire(cells,colors));trace=analyze(q);verify_trace(q,trace)
                result=rating_result(result_data(q,trace),self.method)
                result.pop("workload");expected=deepcopy(reference);expected.pop("workload")
                self.assertEqual(result,expected,(id,index))

    def test_other_entries_and_operating_time_do_not_change_single_value(self):
        def evaluate(ids):
            result={}
            for id in ids:
                p=validate_logic(BY_ID[id]["logic"]);t=analyze(p);verify_trace(p,t)
                result[id]=rating_result(result_data(p,t),self.method)
            return result
        alone=evaluate(["late-general-line"])
        for ids in (["fluid-r1","late-general-line","color-combination"],
                    ["color-combination","late-general-line"],["late-general-line","fluid-r1"]):
            self.assertEqual(evaluate(ids)["late-general-line"],alone["late-general-line"])
        # No catalog input/API, method configuration is a fixed standalone object.
        self.assertNotIn("catalog",json.dumps(self.method))


class BindingTests(unittest.TestCase):
    def test_rated_cli_legacy_checker_and_missing_rating(self):
        source=Path(__file__).parent/"fixtures"/"sd-runtime.json"
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/"out"
            args=[sys.executable,"-m","tools.puzzle_production"]
            run=subprocess.run([*args,"analyze-difficulty","--input",str(source),"--input-kind","runtime",
                                "--output-dir",str(output),"--method",METHOD_ID],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertEqual(json.loads(run.stdout)["level"],1)
            check=subprocess.run([*args,"check-analysis","--input",str(source),"--bundle",str(output),
                                  "--method",METHOD_ID],capture_output=True,text=True,timeout=30)
            self.assertEqual(check.returncode,0,check.stdout+check.stderr)
            self.assertTrue(json.loads(check.stdout)["rating_verified"])
            analyze_file(source,Path(temp)/"repeat",kind="runtime",method=METHOD_ID)
            self.assertEqual((output/"rating.json").read_bytes(),(Path(temp)/"repeat"/"rating.json").read_bytes())
            legacy=check_bundle(source,output)
            self.assertNotIn("rating_verified",legacy)
            (output/"rating.json").unlink()
            with self.assertRaises(InvalidProof):check_bundle(source,output,method=METHOD_ID)

    def test_rehashed_binding_and_result_manipulations_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"input.json";write_json(source,BY_ID["sustained-combination"]["logic"])
            output=root/"out";analyze_file(source,output,method=METHOD_ID)
            rating=load_json(output/"rating.json")
            changes=[lambda r:r["result"].update(level=5),lambda r:r["result"].update(level=True),
                     lambda r:r["result"].update(confidence="high"),lambda r:r["result"].update(size_adjustment=2),
                     lambda r:r["source"].update(sha256="0"*64),lambda r:r.update(analysis_result_hash="0"*64),
                     lambda r:r["method"].update(id="unknown"),lambda r:r["method"].update(rules="sd-rules-2"),
                     lambda r:r["method"]["references"].update(hash="0"*64),
                     lambda r:r["method"]["configuration"].update(severe_demand=[1,2]),
                     lambda r:r["result"]["profile"].update(demand=[1,1]),lambda r:r.update(extra=True),
                     lambda r:r.pop("source")]
            for change in changes:
                bad=deepcopy(rating);change(bad);bad["method_hash"]=digest(bad["method"])
                bad.pop("rating_hash");bad["rating_hash"]=digest(bad)
                write_json(output/"rating.json",bad)
                with self.assertRaises(InvalidProof):check_bundle(source,output,method=METHOD_ID)
            write_json(output/"rating.json",rating)
            report=load_json(output/"report.json")
            report["operation"]["elapsed_seconds"]+=100
            write_json(output/"report.json",report)
            self.assertEqual(check_bundle(source,output,method=METHOD_ID)["rating_hash"],rating["rating_hash"])

    def test_custom_parameters_remain_uncalibrated_and_unknown_methods_fail(self):
        config={"aggregation":{"format":"sd-aggregation-1","min_family":2,
            "max_productive_fraction":[1,4],"cleanup_remaining_cells":4}}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"input.json";write_json(source,BY_ID["fluid-r1"]["logic"])
            for method in (METHOD_ID,"picross-difficulty-0.4"):
                with self.assertRaises(InvalidInput):analyze_file(source,root/method,config=config,method=method)
                self.assertFalse((root/method).exists())
            analyze_file(source,root/"raw",config=config)
            self.assertTrue(check_bundle(source,root/"raw")["report_verified"])
            with self.assertRaises(InvalidInput):check_bundle(source,root/"raw",method=METHOD_ID)

    def test_incomplete_statuses_and_r4_necessity_are_not_fallback_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"input.json";write_json(source,BY_ID["required-pair"]["logic"])
            p=validate_logic(BY_ID["required-pair"]["logic"])
            pair=root/"pair.json";base=root/"base.json"
            write_json(pair,solve(p,profile="paired-lines-mono"));write_json(base,solve(p,Budget(max_lines=0)))
            report=analyze_file(source,root/"unproven",method=METHOD_ID,proof_path=pair,baseline_path=base)
            self.assertTrue(report["result"]["deduction_complete"])
            rating=load_json(root/"unproven"/"rating.json")["result"]
            self.assertEqual(rating["reason"],"r4_necessity_unproven")
            self.assertIsNone(rating["level"])
            check_bundle(source,root/"unproven",method=METHOD_ID)
            analyze_file(source,root/"aborted",method=METHOD_ID,budget=AnalysisBudget(max_lines=0))
            rating=load_json(root/"aborted"/"rating.json")["result"]
            self.assertEqual(rating["reason"],"analysis_aborted")
            self.assertIsNone(rating["confidence"])
            self.assertEqual(load_json(root/"aborted"/"report.json")["result"]["metrics"]["simple_fraction_determined"],[0,0])
            bad=deepcopy(BY_ID["fluid-r1"]["logic"]);bad["row_clues"]=[[] for _ in bad["row_clues"]]
            write_json(source,bad);analyze_file(source,root/"contradiction",method=METHOD_ID)
            self.assertEqual(load_json(root/"contradiction"/"rating.json")["result"]["reason"],"line_contradiction")
            # A false or missing R4 file cannot be rescued by a forged rating.
            write_json(source,p.to_wire());write_json(base,solve(p))
            analyze_file(source,root/"pair",method=METHOD_ID,proof_path=pair,baseline_path=base)
            (root/"pair"/"r4-baseline.json").unlink()
            with self.assertRaises(OSError):check_bundle(source,root/"pair",method=METHOD_ID)
            write_json(base,solve(p));bad=load_json(pair);bad["logic_hash"]="0"*64;write_json(pair,bad)
            with self.assertRaises(InvalidProof):analyze_file(source,root/"bad",method=METHOD_ID,proof_path=pair,baseline_path=base)

    def test_changed_frozen_sources_configuration_or_references_fail_closed(self):
        method=frozen_method()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            names=["difficulty_method_0_3.json","difficulty_references_0_3.json",
                   "difficulty_calibration_0_3.json",*method["implementation"]]
            for name in names:(root/name).write_bytes((ROOT/name).read_bytes())
            with patch("tools.puzzle_production.difficulty_rating._ROOT",root):
                for name in ("difficulty_method_0_3.json","difficulty_references_0_3.json",
                             "difficulty_calibration_0_3.json","difficulty_rating.py"):
                    original=(root/name).read_bytes()
                    if name.endswith("json"):
                        data=load_json(root/name);data["unknown"]=True;write_json(root/name,data)
                    else:(root/name).write_bytes(original+b"# changed\n")
                    with self.assertRaises(InvalidInput):frozen_method()
                    (root/name).write_bytes(original)
                self.assertEqual(frozen_method(),method)

    def test_verification_abort_or_invalid_input_never_writes_a_rating(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"input.json"
            write_json(source,BY_ID["fluid-r1"]["logic"])
            from tools.puzzle_production.contract import Aborted
            with self.assertRaises(Aborted):
                analyze_file(source,root/"verify-abort",method=METHOD_ID,
                             verify_budget=AnalysisBudget(max_lines=0))
            self.assertFalse((root/"verify-abort"/"rating.json").exists())
            write_json(source,{"width":True})
            with self.assertRaises(InvalidInput):analyze_file(source,root/"invalid",method=METHOD_ID)
            self.assertFalse((root/"invalid"/"rating.json").exists())


if __name__=="__main__":unittest.main()
