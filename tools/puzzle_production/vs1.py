"""Bounded VS-1 corpus production; retained sources keep their original contracts."""
from __future__ import annotations

import argparse
import copy
import platform
import shutil
import tempfile
import time
from pathlib import Path

from .contract import Budget, digest, load_json, write_json, validate_logic
from .images import file_hash, import_image, inspect_candidate, versions, logic_from_matrix, raster_image
from .verifier import verify
from .repair import require

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "examples/vs1"
RUNTIME = ROOT / "prototypes/p1/full_view_study"
FORMATS = [(30,30),(40,30),(30,40),(40,40),(50,30)]


def read_source(source: dict) -> tuple[dict, list, dict]:
    """No trusted result flags: reconstruct imports or replay the entire retained repair."""
    if source["kind"] == "import":
        c, proof, checked = inspect_candidate(ROOT / source["bundle"], source["variant"], Budget(30, 100_000))
        require(checked["certified"] and checked["status"] == "solved", "Incomplete import proof")
        return c["design"], c["matrix"], proof
    require(source["kind"] == "retained-rp6-repair" and source["id"] == "F-09", "Unsupported source kind")
    from .rp5 import unpack_archive
    from .repair import inspect_repair
    locked = next(e for e in load_json(ROOT / "examples/rp6/plan.json")["selection"] if e["definition_id"] == "F-09")
    with tempfile.TemporaryDirectory(prefix="vs1-replay-") as tmp:
        folder = Path(tmp) / "repair"
        unpack_archive(ROOT / "examples/rp5/baseline.zip", load_json(ROOT / "examples/rp5/archive.json"), folder)
        bundle = folder / locked["repair_bundle"]
        checked = inspect_repair(bundle, ROOT / locked["reference_bundle"], Budget(60, 1_000_000))
        require(checked["certified"] and checked["status"] == "found", "Incomplete repair replay")
        raw = load_json(bundle / "repair.json")
        require(raw["id"] == locked["repair_id"] and digest(raw["matrix"]) == locked["matrix_hash"], "Repair identity differs")
        return load_json(ROOT / locked["reference_bundle"] / "design.json"), raw["matrix"], load_json(bundle / "final-proof.json", 64*1024*1024)


def definition(id: str, design: dict, matrix: list, suffix: str, name: str) -> dict:
    wire = logic_from_matrix(matrix, design)
    mapping = {"empty": 0, **{c: i+1 for i,c in enumerate(wire["colors"])}}
    adapt = lambda lines: [[{"length": c["length"], "color": mapping[c["color"]]} for c in line] for line in lines]
    return {"schema":2, "id":id.upper(), "revision":1, "width":design["width"], "height":design["height"],
            "palette":[{"id":mapping[c["id"]],"color":c["rgb"].lstrip("#"),"symbol":chr(64+mapping[c["id"]])} for c in design["palette"]],
            "solution":[[mapping[c] for c in row] for row in matrix], "rows":adapt(wire["row_clues"]), "columns":adapt(wire["column_clues"]),
            "reveal":{"version":1,"definition_id":id.upper(),"name":name,"image":f"res://full_view_study/cases/{id}/reveal{suffix}"}}


def distribution(lines):
    from collections import Counter
    return {"max":max(map(len,lines)), "counts":{str(k):v for k,v in sorted(Counter(map(len,lines)).items())},
            "largest_number":max((c["length"] for line in lines for c in line),default=0)}


def build_cases():
    """Curated selection after all 26 imports; no new candidate search."""
    from PIL import Image
    plan = load_json(STUDY / "plan.json")
    selection = {"vs01":(1,"area-128","Pilz"), "vs02":(2,"area-128","Pagode"),
                 "vs03":(1,"area-176","Lokomotive"), "vs04":(1,"area-128","Katzengesicht"),
                 "vs05":(1,"area-176","Lokomotive · transponiert"), "vs06":(1,"area-128","Katzengesicht · transponiert"),
                 "vs07":(0,"area-128","Teekanne"), "vs08":(0,"area-128","Eule"),
                 "vs09":(1,"area-176","Lokomotive"), "vs10":(1,"area-128","Katzengesicht")}
    judgments = {"vs01":"Breite Kappe, schmaler mittiger Stiel; sehr einfache Silhouette und kurze Hinweise, keine Schwierigkeitseinstufung.",
      "vs02":"Drei gestaffelte Dächer, zentrale Pfeiler, Treppe und Grün bleiben bei 30×30 erkennbar; kleine Details abstrahiert.",
      "vs03":"Lokomotive seitlich mit Schlot, Kabine und Rädern; hohe Leerflächen durch contain offen ausgewiesen.",
      "vs04":"Beide Augen, Stirnzeichnung, Nase und helle Schnauze im schrägen Katzengesicht; hohe echte Farbhinweislast.",
      "vs05":"Kontrolliertes Transponat von VS03: gleiche Lokomotive seitlich gedreht/gespiegelt; kein neuer natürlicher Hochkantentwurf.",
      "vs06":"Kontrolliertes Transponat von VS04: Katze in unnatürlicher Orientierung; nur Achsenvergleich, kein Katalogmotiv.",
      "vs07":"Kannenrumpf, Tülle, offener Henkel und Deckelknauf; vorhandene verfeinerte Kanne passt zur Silhouette.",
      "vs08":"Frontale Eule mit Augen, Flügeln, Füßen und Ast; RP5-Endmatrix unverändert, lange Hinweise auf beiden Achsen.",
      "vs09":"Breites Format erhält Lokomotive mit drei sichtbaren Rädern und Kabine; erhebliche seitliche Leerränder.",
      "vs10":"Breites Katzenporträt mit Augen, Nase, heller Schnauze und differenzierten Farbflächen; stärkere Hinweislast als die geprüfte Kaffeetasse."}
    manifest={"format":"picross-vs1-manifest-v1","plan_sha256":file_hash(STUDY/'plan.json'),
              "base_commit":plan['base_commit'],"cases":[],"missing_slots":[],"owner_trial":"open","product_decision":"open"}
    require(not (STUDY/'cases').exists(), 'Do not overwrite selected cases')
    for slot in plan['slots']:
        id=slot['id']; rev,variant,name=selection[id]
        if rev:
            attempt=slot['attempts'][rev-1]
            source={"kind":"import","bundle":f"examples/vs1/imports/{id}-r{rev}","variant":variant}
            reveal=ROOT/attempt['reveal']; transpose=attempt['transpose']
        else:
            source={"kind":"import","bundle":slot['retained'],"variant":variant} if id=='vs07' else {"kind":"retained-rp6-repair","id":"F-09"}
            reveal=ROOT/slot['reveal']; transpose=False
        design,matrix,proof=read_source(source)
        require([design['width'],design['height']]==slot['dimensions'], 'Orientation differs')
        case=STUDY/'cases'/id; case.mkdir(parents=True)
        wire=logic_from_matrix(matrix,design)
        write_json(case/'logic.json',wire); write_json(case/'proof.json',proof)
        asset=case/('reveal'+reveal.suffix)
        if transpose:
            with Image.open(reveal) as im: im.transpose(Image.Transpose.TRANSPOSE).save(asset)
        else: shutil.copyfile(reveal,asset)
        data=definition(id,design,matrix,reveal.suffix,name)
        write_json(case/'definition.json',data)
        raster_image(matrix,design).save(case/'raster.png')
        source_size=(design['crop'][2]-design['crop'][0],design['crop'][3]-design['crop'][1])
        w,h=slot['dimensions']; sw,sh=source_size
        fitted=[w,max(1,sh*w//sw)] if w*sh<=h*sw else [max(1,sw*h//sh),h]
        entry={"id":id,"revision":1,"dimensions":[w,h],"mode":slot['mode'],"kind":"playable","certified":True,
               "source":source,"source_design":design,"matrix_hash":digest(matrix),"logic_hash":digest(wire),
               "reveal_source":reveal.relative_to(ROOT).as_posix(),"reveal_source_sha256":file_hash(reveal),"transpose_reveal":transpose,
               "motif_review":{"actor":"implementing_agent","date":"2026-10-08","judgment":judgments[id],"final_catalog_acceptance":False},
               "reveal_quality":"existing refinement" if id in ['vs01','vs02','vs07','vs08'] else "simplified study resource; existing source illustration",
               "hint_load":{"row":distribution(wire['row_clues']),"column":distribution(wire['column_clues'])},
               "contain":{"motif_frame_cells":fitted,"free_columns":w-fitted[0],"free_rows":h-fitted[1]},
               "files":{p.name:file_hash(p) for p in sorted(case.iterdir())}}
        entry['motif_review'].update(matrix_hash=entry['matrix_hash'],reveal_sha256=file_hash(asset))
        manifest['cases'].append(entry)
        target=RUNTIME/'cases'/id; target.mkdir(parents=True)
        for p in [case/'definition.json',asset]: shutil.copyfile(p,target/p.name)
    write_json(STUDY/'manifest.json',manifest)
    write_json(RUNTIME/'catalog.json',{"revision":1,"cases":[{"id":e['id'],"definition_sha256":e['files']['definition.json'],"kind":e['kind'],"certified":e['certified']} for e in manifest['cases']]})
    return manifest


def verify_cases():
    from PIL import Image, ImageChops
    manifest=load_json(STUDY/'manifest.json'); plan=load_json(STUDY/'plan.json')
    require(manifest['format']=='picross-vs1-manifest-v1' and manifest['plan_sha256']==file_hash(STUDY/'plan.json'), 'Plan binding differs')
    require([e['id'] for e in manifest['cases']]==[s['id'] for s in plan['slots']], 'Missing, duplicate or reordered IDs')
    require(manifest['missing_slots']==[] and manifest['owner_trial']=='open' and manifest['product_decision']=='open', 'Unperformed acceptance or missing slot')
    catalog=load_json(RUNTIME/'catalog.json')
    require(catalog=={'revision':1,'cases':[{'id':e['id'],'definition_sha256':e['files']['definition.json'],'kind':'playable','certified':True} for e in manifest['cases']]}, 'Runtime catalog binding differs')
    report=[]
    for e,slot in zip(manifest['cases'],plan['slots']):
        require(e['dimensions']==slot['dimensions'] and e['mode']==slot['mode'] and e['kind']=='playable' and e['certified'] is True,'Incorrect slot certification')
        if slot['attempts']:
            candidates=[a for a in slot['attempts'] if e['source'].get('bundle')==f"examples/vs1/imports/{slot['id']}-r{a['revision']}"]
            require(len(candidates)==1 and e['source'].get('kind')=='import','Unbound source')
            attempt=candidates[0]
            require(e['source']['variant'] in [v['id'] for v in attempt['design']['variants']], 'Unbound variant')
            require(e['reveal_source']==attempt['reveal'] and e['transpose_reveal']==attempt['transpose'],'Unbound reveal/orientation')
        else:
            expected_source={'kind':'import','bundle':slot['retained'],'variant':'area-128'} if slot['id']=='vs07' else {'kind':'retained-rp6-repair','id':'F-09'}
            require(e['source']==expected_source and e['reveal_source']==slot['reveal'] and e['transpose_reveal'] is False,'Unbound retained source')
        design,matrix,original_proof=read_source(e['source'])
        if slot['attempts']:
            require(design==attempt['design'] and file_hash(ROOT/attempt['source'])==attempt['source_sha256'],'Bound design/source changed')
            imported=ROOT/e['source']['bundle']/'original.png'
            if attempt['transpose']:
                with Image.open(ROOT/attempt['source']) as a,Image.open(imported) as b:
                    expected=a.transpose(Image.Transpose.TRANSPOSE)
                    require(b.size==expected.size and ImageChops.difference(expected,b).getbbox() is None,'Wrong transposed source')
            else:
                require(file_hash(imported)==attempt['source_sha256'],'Unbound source pixels')
        require(design==e['source_design'] and digest(matrix)==e['matrix_hash'], 'Source/matrix changed')
        folder=STUDY/'cases'/e['id']
        required={'definition.json','logic.json','proof.json','raster.png','reveal'+Path(e['reveal_source']).suffix}
        require(set(e['files'])==required, 'Missing/unsafe case file')
        for name,sha in e['files'].items():
            require(not (folder/name).is_symlink() and file_hash(folder/name)==sha, 'Case file changed')
        wire=logic_from_matrix(matrix,design)
        require(wire==load_json(folder/'logic.json') and digest(wire)==e['logic_hash'], 'Clues changed')
        proof=load_json(folder/'proof.json',64*1024*1024)
        checked=verify(validate_logic(wire),proof,Budget(30,100_000))
        require(checked['certified'] and proof['final_domains']==[[[v] for v in row] for row in matrix] and proof==original_proof,'Incomplete or wrong proof')
        asset=folder/next(n for n in required if n.startswith('reveal'))
        require(e['motif_review']['matrix_hash']==digest(matrix) and e['motif_review']['reveal_sha256']==file_hash(asset) and e['motif_review']['final_catalog_acceptance'] is False,'Motif judgment binding differs')
        require(file_hash(ROOT/e['reveal_source'])==e['reveal_source_sha256'], 'Reveal source changed')
        if e['transpose_reveal']:
            with Image.open(ROOT/e['reveal_source']) as a,Image.open(asset) as b:
                expected=a.transpose(Image.Transpose.TRANSPOSE)
                require(b.size==expected.size and ImageChops.difference(expected,b).getbbox() is None,'Wrong oriented reveal')
        else: require(file_hash(asset)==e['reveal_source_sha256'],'Swapped reveal')
        data=load_json(folder/'definition.json')
        expected=definition(e['id'],design,matrix,asset.suffix,data['reveal']['name'])
        require(data==expected and [data['width'],data['height']]==e['dimensions'],'Definition/paths/palette/orientation changed')
        for p in [folder/'definition.json',asset]:
            require(file_hash(RUNTIME/'cases'/e['id']/p.name)==file_hash(p),'Runtime export differs')
        require(e['hint_load']=={'row':distribution(wire['row_clues']),'column':distribution(wire['column_clues'])},'Hint measurements differ')
        report.append({'id':e['id'],'certified':True,'proof_steps':len(proof['steps'])})
    return report


def produce() -> dict:
    from PIL import Image
    plan = load_json(STUDY / "plan.json")
    output = STUDY / "imports"
    require(not output.exists(), "Production is single-use; do not overwrite attempts")
    output.mkdir()
    report = {"format": "picross-vs1-production-v1", "plan_sha256": file_hash(STUDY / "plan.json"),
              "host": platform.platform(), "versions": versions(), "human_minutes": None,
              "ai_calls": 0, "repairs": [], "attempts": [], "new_candidates": 0}
    write_json(STUDY / "production.json", report)
    for slot in plan["slots"]:
        for attempt in slot["attempts"]:
            stem = f'{slot["id"]}-r{attempt["revision"]}'
            d = output / (stem + "-design.json")
            write_json(d, attempt["design"])
            source = ROOT / attempt["source"]
            require(file_hash(source) == attempt["source_sha256"], "Bound source changed")
            if attempt["transpose"]:
                target = output / (stem + "-transposed.png")
                with Image.open(source) as im:
                    im.transpose(Image.Transpose.TRANSPOSE).save(target)
                source = target
            started = time.monotonic()
            row = {"slot": slot["id"], "revision": attempt["revision"], "name": attempt["name"],
                   "bundle": f"examples/vs1/imports/{stem}", "status": "started", "variants": []}
            report["attempts"].append(row)
            report["new_candidates"] += len(attempt["design"]["variants"])
            require(report["new_candidates"] <= 40, "Candidate budget exceeded")
            write_json(STUDY / "production.json", report)
            try:
                import_image(source, d, ROOT / row["bundle"], seconds=30, max_lines=100_000)
                for variant in attempt["design"]["variants"]:
                    result = load_json(ROOT / row["bundle"] / f'{variant["id"]}-result.json')
                    row["variants"].append({"variant": variant["id"], "result": result})
                row["status"] = "produced"
            except Exception as exc:
                row.update(status="technical_error", error=str(exc))
                raise
            finally:
                row["seconds"] = time.monotonic() - started
                write_json(STUDY / "production.json", report)
            print(stem, [(r["variant"], r["result"].get("status"), r["result"].get("certified")) for r in row["variants"]], flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["produce","build","verify"])
    args = parser.parse_args()
    if args.command == "produce":
        produce()
    elif args.command == "build":
        build_cases()
    else:
        print(verify_cases())


if __name__ == "__main__":
    main()
