"""Current geometry, save, hint and pixel verification."""
from __future__ import annotations
import gzip
import copy
import json
from pathlib import Path
import p1_preflight as toolchain
import vs2_v1_verify

# Independent of the native producer's table. D02 accepts the omitted combinations.
MATRIX_CASES = tuple(
    (name.startswith('VS'), name, w, h, ui, mode)
    for w, h, ui, cases in (
        (1280, 720, 1.25, {'T-01':'G', 'T-02':'GV', 'T-06':'GV', 'VS06':'V', 'VS09':'G'}),
        (1920, 1080, 1.0, {'T-01':'G', 'T-06':'G', 'VS04':'GV', 'VS08':'GV', 'VS09':'GV'}),
        (2560, 1440, 1.25, {'T-02':'GV', 'VS07':'V'}),
    ) for name, modes in cases.items() for mode in modes)


def compact_frames(stage):
    """Exact selected native frames: name -> (client width, height, UI, fixture)."""
    if stage == 'layout':
        return {'album': (1920,1080,1.0,'T-06'),
                '1280x720-ui125-f6-independent-slots': (1280,720,1.25,'T-06'),
                '1920x1080-ui100-f2': (1920,1080,1.0,'T-02')}
    if stage in ('cells-f1', 'cells-f2'):
        fixture = int(stage[-1])
        return {f'separation-f{fixture}-{step}-{suffix}': (1920,1080,1.0,f'T-{fixture:02d}')
                for step in (12,16,18,24,72)
                for suffix in ['confirmed'] + [f'preview-color{c}' for c in
                    (range(1,5) if fixture == 2 and step == 24 else (1,))]}
    if stage == 'axis':
        frames = {name: (1920,1080,1.0,'T-06') for name in
                  ('t06-grid-focus','gesture-counter-8','t06-full-clues-in-work-tooltip','t06-overview')}
        frames.update({name: (1920,1080,1.0,fixture)
                       for label, fixture in (('g1-t02','T-02'),('g1-t04','T-06'))
                       for name in (label+'-old-arm','g1-counter-1-'+label,'g1-counter-4-'+label)})
        frames.update({f'zr-{w}-ui{round(ui*100)}-z{zoom}-{i}': (w,h,ui,'T-01')
                       for w,h,ui in vs2_v1_verify.VISUAL_CONFIGURATIONS
                       for zoom in ((12,72) if w == 1280 else (72,))
                       for i in (range(11) if zoom == 12 else (0,7,10))})
        return frames
    if stage == 'h1':
        frames = {f'h1-vs2-{w}x{h}-ui{round(ui*100)}-{mode}-{state}': (w,h,ui,'T-01')
                  for w,h,ui,mode in ((1280,720,1.25,'G'),(1920,1080,1.0,'V'),(2560,1440,1.25,'V'))
                  for state in ('off','on')}
        frames.update({f'f{i}-{state}': (2560,1440,1.25,f'T-{i:02d}')
                       for i in (1,2) for state in ('reveal','earned-album')})
        return frames
    raise toolchain.PreflightError('Unknown compact render stage: '+stage)


def verify_compact_stage(stage, report):
    """Validate original native evidence, never accept a count-only success."""
    expected = compact_frames(stage)
    frames = report['frames']
    counts = {'layout':0, 'cells-f1':27, 'cells-f2':76, 'axis':117, 'h1':180}
    def require(ok):
        if not ok:
            raise toolchain.PreflightError('Incomplete/inconsistent compact render stage: '+stage)
    require(report['failed'] is False and report['compact'] is True
            and not report['failure'] and report['failure_captures'] == []
            and report['captures'] == [] and report['retained_count'] == 0
            and report['rendered_count'] == len(frames) == len(expected)
            and {f['name'] for f in frames} == set(expected)
            and report['pixel_checks'] == counts[stage])
    by_name = {f['name']:f for f in frames}
    for f in frames:
        w,h,ui,fixture = expected[f['name']]
        require(f['logical_surface'] == [w,h] and f['ui_scale'] == ui and f['fixture'] == fixture
                and f['retained'] is False and f['crop'] is False and 0 < f['cell_pitch'] <= 72)
        if stage.startswith('cells-'):
            require(f['cell_pitch'] == int(f['name'].split('-')[2]))
        if f['name'].startswith('h1-') and f['name'].endswith('-on'):
            pair = f['h1_pair']
            require(pair['off_frame'] == f['name'][:-2]+'off' and pair['searches_on_toggle'] == 0
                    and pair['marked_tokens']['row'] > 0 and pair['marked_tokens']['column'] > 0
                    and len(pair['colors']) > 0)
    samples = report['zr_samples']
    require(len(samples) == len([n for n in expected if n.startswith('zr-')])
            and {s['name'] for s in samples} == {n for n in expected if n.startswith('zr-')})
    for s in samples:
        f = by_name[s['name']]
        w,h,ui,_ = expected[s['name']]
        x,y,rw,rh = s['rect']
        require(s['requested_zoom'] == int(s['name'].split('-')[3][1:])
                and s['actual_cell'] == f['cell_pitch'] and s['ui'] == ui
                and s['font_size'] == round(24*ui) and s['length'] > 1
                and x >= 0 and y >= 0 and rw > 0 and rh > 0 and x+rw <= w and y+rh <= h
                and 3 <= s['changed_pixels'] < rw*rh*.8)


def compact_summary(reports):
    return dict(stages=len(reports), pixel_checks=sum(r['pixel_checks'] for r in reports),
                rendered_count=sum(r['rendered_count'] for r in reports),
                retained_count=sum(r['retained_count'] for r in reports),
                captures=[c for r in reports for c in r['captures']], compact=True)


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
    import hf149_verify
    import hs186_verify
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
    expected = set(MATRIX_CASES)
    actual = {(r["corpus"],r["id"],*r["client"],r["ui_scale"],r["mode"]) for r in report["records"]}
    if report["failures"] or actual != expected or len(report["records"]) != len(expected):
        raise toolchain.PreflightError("Incomplete/failed VS2 regular matrix")
    for record in report["records"]:
        invalid = record['client'][0] == 1280 and record['mode'] == 'V' and record['id'] in ('T-06','VS06')
        if record['layout_valid'] is not (not invalid):
            raise toolchain.PreflightError('VS2 selected valid/blocked geometry changed')
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
