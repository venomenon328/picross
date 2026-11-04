"""Current geometry, save, hint and pixel verification."""
from __future__ import annotations
import gzip
import copy
import json
from pathlib import Path
import p1_preflight as toolchain
import vs2_v1_verify
import hf149_verify
import hs186_verify


def compact_geometry_reports(paths):
    """Keep every current native measurement; omit only JSON indentation."""
    for path in paths:
        report = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n",
                        encoding="utf-8", newline="\n")


def compress_geometry_report(path: Path) -> Path:
    """Retain every report byte in a deterministic, lossless delivery wrapper."""
    original = path.read_bytes()
    compressed = gzip.compress(original, mtime=0)
    if gzip.decompress(compressed) != original:
        raise toolchain.PreflightError("Geometry report compression changed bytes")
    target = path.with_suffix(path.suffix + ".gz")
    target.write_bytes(compressed)
    return target


def read_geometry_report(path: Path) -> dict:
    source = path if path.is_file() else path.with_suffix(path.suffix + ".gz")
    data = source.read_bytes()
    return json.loads(gzip.decompress(data) if source.suffix == ".gz" else data)


def capture_current(project, workspace, output, engine, render_command, environment, run_phase):
    """Current functional VS2 coverage without historical reference replay."""
    environment["VS2_PROBE_OUTPUT"] = str(output)
    environment["P1_TEST_SAVE_ROOT"] = str(workspace / "vs2-current-saves")
    try:
        for stage in ("write", "read"):
            environment["VS2_STAGE"] = stage
            run_phase("vs2-roundtrip-" + stage,
                  [engine, "--headless", "--path", str(project), "--script", "res://tests/vs2_roundtrip.gd"],
                  "VS2_ROUNDTRIP_" + stage.upper() + "_OK")
    finally:
        for key in ("VS2_STAGE", "VS2_PROBE_OUTPUT", "P1_TEST_SAVE_ROOT"):
            environment.pop(key, None)
    run_phase("vs2-gf1-tests", [engine, "--headless", "--path", str(project), "--script",
                          "res://tests/vs2_gf1_tests.gd"], "VS2_GF1_TESTS_OK")
    hf_dir = output / "hf149"
    hf_dir.mkdir()
    environment["HF149_OUTPUT"] = str(hf_dir)
    try:
        for stage in ("write", "read"):
            environment["HF149_STAGE"] = stage
            run_phase("hf149-" + stage, [engine, "--headless", "--path", str(project),
                  "--script", "res://tests/hf149_probe.gd"], "HF149_" + stage.upper() + "_OK")
        environment.pop("HF149_STAGE", None)
        run_phase("hf149-native", ["res://tests/hf149_probe.gd" if part == "res://tests/capture.gd" else part
              for part in render_command], "HF149_NATIVE_OK")
    finally:
        environment.pop("HF149_OUTPUT", None)
        environment.pop("HF149_STAGE", None)
    hf = hf149_verify.verify(hf_dir)
    renders = output / "vs2-renders"
    renders.mkdir()
    environment["VS2_CAPTURE_DIR"] = str(renders)
    try:
        run_phase("vs2-regular-matrix", ["res://tests/vs2_tests.gd" if part == "res://tests/capture.gd" else part
                  for part in render_command], "VS2_TESTS_OK")
    finally:
        environment.pop("VS2_CAPTURE_DIR", None)
    report = verify(renders)
    # Keep independent current layout mathematics from the former V1 delivery,
    # using the already running regular matrix, without its separate gallery.
    for row in report['records']:
        vs2_v1_verify.record(row['v1'])
    bad = copy.deepcopy(report['records'][0]['v1'])
    bad['row_pitch'] += 2
    try:
        vs2_v1_verify.record(bad)
    except toolchain.PreflightError:
        pass
    else:
        raise toolchain.PreflightError('Current layout oracle accepted changed row pitch')
    selected = [renders / "vs2-matrix.json", output / "vs2-write.json", output / "vs2-read.json"]
    selected += list(hf_dir.glob("*.json"))
    v2_dir = output / "v2-renders"
    v2_dir.mkdir()
    environment["VS2_V2_CAPTURE_DIR"] = str(v2_dir)
    try:
        for stage in ("write", "read"):
            environment["VS2_V2_STAGE"] = stage
            run_phase("vs2-v2-" + stage,
                  ["res://tests/vs2_v2_tests.gd" if part == "res://tests/capture.gd" else part
                   for part in render_command], "VS2_V2_" + stage.upper() + "_OK")
    finally:
        environment.pop("VS2_V2_CAPTURE_DIR", None)
        environment.pop("VS2_V2_STAGE", None)
    v2 = verify_v2(v2_dir)
    v2["plan_sha256"] = toolchain.sha256_file(Path(__file__).resolve().parents[1] / "examples/vs2/v2-plan.json")
    v2["scripts"] = {name: toolchain.sha256_file(project / "tests" / name)
                     for name in ("vs2_v2_tests.gd", "vs2_v2_cases.gd", "native_png.gd")}
    selected += list(v2_dir.glob("*.json"))
    hs_dir = output / "hs186"
    hs_dir.mkdir()
    environment["HS186_OUTPUT"] = str(hs_dir)
    try:
        run_phase("hs186-native-number-cross-pixels", ["res://tests/hs186_capture.gd" if part == "res://tests/capture.gd" else part
                                                 for part in render_command], "HS186_NATIVE_OK")
    finally:
        environment.pop("HS186_OUTPUT", None)
    hs = hs186_verify.verify(hs_dir)
    selected += list(hs_dir.glob("*.json"))
    temporary = list(hs_dir.glob("*.png"))
    hs.update(temporary_pngs=len(temporary), temporary_png_bytes=sum(p.stat().st_size for p in temporary))
    for path in temporary: path.unlink()
    hn_dir = output / "hn192"
    hn_dir.mkdir()
    environment["HN192_OUTPUT"] = str(hn_dir)
    try:
        run_phase("hn192-native-input-cursor", ["res://tests/hn192_probe.gd" if part == "res://tests/capture.gd" else part
                                          for part in render_command], "HN192_NATIVE_OK")
    finally:
        environment.pop("HN192_OUTPUT", None)
    hn = json.loads((hn_dir / "hn-native.json").read_text(encoding="utf-8"))
    from hn_evidence import verify as verify_hn
    verify_hn(hn_dir, hn)
    expected = {(width, axis) for width in (1280,)
                for axis in ("row", "column", "grid", "complete-row", "drag-row")}
    pixel_records = [r for r in hn["records"] if r["kind"] == "pixels"]
    actual = {(r["client"][0], r["file"].split("-",3)[3].removesuffix(".png"))
              for r in pixel_records}
    if (hn["failures"] or hn["checks"] < 100 or actual != expected
            or len(pixel_records) != len(expected)
            or {r["file"] for r in pixel_records} != {p.name for p in hn_dir.glob("*.png")}):
        raise toolchain.PreflightError("Missing/failed HN native routes and original pixels")
    selected += list(hn_dir.glob("*.json")) + list(hn_dir.glob("*.png"))
    # Keep full matrix telemetry without displacing mandatory native pictures
    # or increasing the shared player/evidence budget.
    packed = {p: compress_geometry_report(p) for p in
              (renders / "vs2-matrix.json",)}
    selected = [packed.get(p, p) for p in selected]
    return dict(records=len(report["records"]), failures=report["failures"],
                rendered=len(report["pictures"]), v2=v2, hf149=hf, hs186=hs, hn192=hn,
                historical_comparison="not run; CI policy #63",
                legacy_reader="separate downloaded Windows old-writer/new-reader probe"), selected


def verify_v3(directory: Path) -> dict:
    report = json.loads((directory / "v3-report.json").read_text(encoding="utf-8"))
    expected_cases = {(sheet, w, h, ui, mode, fit) for sheet in ("T-01", "T-02", "T-08")
                      for w, h, ui in vs2_v1_verify.VISUAL_CONFIGURATIONS for mode in ("G", "V") for fit in (False, True)}
    actual_cases = {(r["id"], *r["client"], r["ui"], r["mode"], r["fit"]) for r in report["records"]}
    if report["failures"] or len(report["records"]) != len(expected_cases) or actual_cases != expected_cases or report["checks"] < 1000:
        raise toolchain.PreflightError("Incomplete/failed V3 native coverage")
    for record in report["records"]:
        vs2_v1_verify.sidebar_axes(record, record["ui"])
    expected = {"v3-tight-rail.png", "v3-T01-work.png", "v3-T08-work.png", "v3-title.png", "v3-fills-five.png"}
    expected.update(['v3-sl-720-125-color-G.png', 'v3-sl-720-100-mono-V.png', 'v3-sl-900-100-color-V.png', 'v3-sl-900-125-mono-G.png', 'v3-sl-1440-125-color-V.png', 'v3-sl-720-125-recovery.png', 'v3-sidebar-detail.png'])
    metadata_path = Path(__file__).resolve().parents[1] / "game/art/book/frames.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    def serialized_geometry(value):
        # Godot JSON prints 15 significant digits. The exact source bytes remain
        # independently hash-bound; sub-nanopixel JSON rounding is not a new asset.
        if isinstance(value, float): return round(value, 9)
        if isinstance(value, list): return [serialized_geometry(v) for v in value]
        if isinstance(value, dict): return {k: serialized_geometry(v) for k,v in value.items()}
        return value
    if report.get("sidebar_metadata_sha256") != toolchain.sha256_file(metadata_path) or serialized_geometry(report.get("sidebar_assets")) != serialized_geometry(metadata) or len(report.get("frame_pixels", [])) != 3 or any(p["changed_pixels"] <= 100 for p in report["frame_pixels"]):
        raise toolchain.PreflightError("Missing/mismatched SL frame resources or actual render usage")
    if {p["file"] for p in report["pictures"]} != expected or len(report["pictures"]) != len(expected):
        raise toolchain.PreflightError("Missing V3 targeted native pictures")
    for picture in report["pictures"]:
        toolchain.verify_sha256(directory / picture["file"], picture["sha256"])
    return report


def verify_v2(directory: Path) -> dict:
    reports = {stage: json.loads((directory / ("v2-" + stage + ".json")).read_text(encoding="utf-8"))
               for stage in ("write", "read")}
    for stage, report in reports.items():
        if report["failures"] or report["checks"] < (100 if stage == "write" else 8):
            raise toolchain.PreflightError("Incomplete/failed V2 " + stage)
    if len(reports["write"]["scenarios"]) != 19 or len(set(reports["write"]["scenarios"])) != 19 or reports["read"]["scenarios"] != ["fresh process redo restores X"]:
        raise toolchain.PreflightError("Incomplete V2 transition coverage")
    return reports


def verify_records(report: dict) -> None:
    expected = {(corpus,index,w,h,ui,mode) for corpus,indices in ((False,(0,1,3,5,7,8)),(True,range(10))) for index in indices for w,h,ui in vs2_v1_verify.VISUAL_CONFIGURATIONS for mode in ("G","V")}
    actual = {(r["corpus"], int(r["id"].replace("T-","").replace("VS",""))-1,*r["client"],r["ui_scale"],r["mode"]) for r in report["records"]}
    if report["failures"] or actual != expected or len(report["records"]) != len(expected):
        raise toolchain.PreflightError("Incomplete/failed VS2 regular matrix")
    for record in report["records"]:
        if record["layout_valid"] and not record["grid_fit"]:
            raise toolchain.PreflightError("VS2 frame does not fit")
        if record["mode"] == "V" and record["hidden_tokens"]:
            raise toolchain.PreflightError("VS2 V hides hints")
        if record["status"] == "geometric_fit_owner_open" and (record["clipped_glyphs"] or record["glyph_collisions"] or record["cell_pitch"] < 16):
            raise toolchain.PreflightError("VS2 false positive legibility status")


def verify(renders: Path) -> dict:
    report = read_geometry_report(renders / "vs2-matrix.json")
    verify_records(report)
    expected = {"album", "options"}
    expected.update(f"regular-T-{i:02d}-G-ui100" for i in (1,6))
    expected.update(f"corpus-VS{i:02d}-{mode}-ui100" for i in (4,8,9) for mode in ("G","V"))
    expected.update(f"rectangular-VS{i:02d}-reveal" for i in (1,3,5,7,9))
    if len(report["pictures"]) != len(expected) or {r["case"] for r in report["pictures"]} != expected:
        raise toolchain.PreflightError("Incomplete native frame assertions")
    for picture in report["pictures"]:
        if any(edge["minimum_ink_pixels"] < 1 for edge in picture.get("frame_pixels",{}).values()):
            raise toolchain.PreflightError("VS2 rendered frame edge missing")
        if picture["case"].startswith(("regular-","corpus-")) and set(picture.get("frame_pixels",{})) != {"top","bottom","left","right"}:
            raise toolchain.PreflightError("VS2 rendered frame evidence incomplete")
    return report
