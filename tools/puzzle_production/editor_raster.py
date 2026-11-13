"""Closed manual raster inputs and packages, distinct from authoring exports."""
from copy import deepcopy
from pathlib import Path
import re

from .authoring_package import require, relative, sha
from .contract import canonical_bytes, digest, exact_keys, integer, Budget, load_json
from . import catalog_io as io, catalog_rating as rating, catalog_background as bg
from . import editor_image_source as images, reveal_source as reveal

REQUEST = "picross-editor-raster-request-v1"
PACKAGE = "picross-editor-raster-package-v1"
REQUEST_LIMIT = 256 * 1024
PACKAGE_LIMIT = 1024 * 1024


def encoded(value):
    return canonical_bytes(value) + b"\n"


def parse(text, palette):
    require(isinstance(text, str) and len(text.encode("utf-8")) <= 65536, "Rastertext exceeds 64 KiB")
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "": lines.pop()
    require(lines, "Zeile 1, Spalte 1: Raster fehlt")
    allowed = {0, *(row["id"] for row in palette)}
    matrix = []
    for y, line in enumerate(lines, 1):
        require(y <= 50, f"Zeile {y}, Spalte 1: höchstens 50 Rasterzeilen")
        tokens = line.split()
        require(tokens, f"Zeile {y}, Spalte 1: leere Rasterzeile")
        row = []
        for x, token in enumerate(tokens, 1):
            location = f"Zeile {y}, Spalte {x}: "
            require(x <= 50, location + "höchstens 50 Zellen je Zeile")
            require(re.fullmatch(r"[0-9]+", token), location + "nichtnegative Ganzzahl erwartet")
            normalized = token.lstrip("0") or "0"
            require(len(normalized) == 1, location + "unbekannte Palette-ID")
            value = int(normalized)
            require(value in allowed, location + "unbekannte Palette-ID")
            row.append(value)
        if matrix:
            require(len(row) == len(matrix[0]), f"Zeile {y}, Spalte {min(len(row),len(matrix[0]))+1}: abweichende Zeilenbreite")
        matrix.append(row)
    return matrix


def clues(line):
    result, previous = [], 0
    for color in line:
        if color:
            if color == previous: result[-1]["length"] += 1
            else: result.append({"length": 1, "color": color})
        previous = color
    return result


def definition(previous, matrix):
    value = deepcopy(previous)
    value.update(width=len(matrix[0]), height=len(matrix), solution=matrix,
                 rows=[clues(row) for row in matrix], columns=[clues(row) for row in zip(*matrix)])
    if (previous["width"], previous["height"], previous["solution"]) != (value["width"], value["height"], matrix):
        value["revision"] = integer(previous["revision"]+1, 1, 1000000, "new runtime revision")
    rating.definition(encoded(value))
    return value


def request(value):
    exact_keys(value, {"format", "id", "text", "metadata", "reveal", "background", "decision", "provenance", "profile"})
    require(value["format"] == REQUEST, "Unsupported raster request")
    rating.identity(value["id"])
    images.decision(value["decision"])
    reveal.provenance(value["provenance"])
    require(value["profile"] in ("line", "paired"), "Unsupported deduction profile")
    require(isinstance(value["text"], str) and len(value["text"].encode()) <= 65536, "Rastertext exceeds 64 KiB")
    # Reuse the exact A2 request validator, including metadata and input refs.
    if any(value[key] is not None for key in ("metadata", "reveal", "background")):
        from .catalog_images import validate_request, REQUEST as IMAGE_REQUEST
        validate_request({"format": IMAGE_REQUEST, **{key: value[key] for key in ("id", "metadata", "reveal", "background", "decision")}})
    require(len(encoded(value)) <= REQUEST_LIMIT, "Raster request exceeds 256 KiB")
    return value


def identity(entry, raw):
    value = io.json_bytes(raw, 2*1024*1024)
    return {"key": entry["key"], "save_slot": entry["save_slot"],
            "definition": bg.ref("game/"+entry["definition"], raw), "runtime_revision": value["revision"]}


def quality(value, raw):
    exact_keys(value, {"method", "checked", "proof", "baseline"})
    from .catalog_method import method_hash
    method_hash(value["method"])
    rating.validate(value["checked"], active=False, definition_bytes=raw)
    require(rating.method(value["checked"]) == value["method"] and
            value["checked"]["rating"]["result"]["status"] == "rated", "Raster requires complete current rating")
    bg._ref(value["proof"], name="proof.json", limit=64*1024*1024)
    if value["baseline"] is not None: bg._ref(value["baseline"], name="baseline.json", limit=64*1024*1024)
    return value


def check_end(definition, proof):
    expected = [[["empty" if value == 0 else "c"+str(value)] for value in row] for row in definition["solution"]]
    require(proof.get("status") == "solved" and proof.get("final_domains") == expected,
            "Independently checked proof end differs from selected matrix")


def validate(value, raw=None):
    exact_keys(value, {"format", "id", "revision", "previous", "origin", "definition", "reveal_sha256", "notice_sha256",
                       "quality", "decision", "provenance", "files", "package_hash"})
    require(value["format"] == PACKAGE and len(encoded(value)) <= PACKAGE_LIMIT, "Invalid raster package format/size")
    rating.identity(value["id"])
    images.decision(value["decision"])
    reveal.provenance(value["provenance"])
    for key in ("previous", "origin"): images.validate_binding(value[key], value["id"])
    old = value["previous"]
    require(old["identity"]["runtime_revision"] < 1000000 and
            value["revision"] == "editor-"+str(old["identity"]["runtime_revision"]+1), "Invalid editor package revision")
    bg._ref(value["definition"], name="definition.json", limit=2*1024*1024)
    sha(value["notice_sha256"])
    sha(value["reveal_sha256"])
    require(isinstance(value["files"], dict), "Invalid raster inventory")
    for name, checksum in value["files"].items():
        relative(name); sha(checksum)
        require(name in ("definition.json", "previous-definition.json", "request.json", "proof.json", "baseline.json") or name.startswith("analysis/"),
                "Foreign raster package file")
    required = {"definition.json", "previous-definition.json", "request.json", "proof.json"} | ({"baseline.json"} if value["quality"]["baseline"] is not None else set())
    require(required <= set(value["files"]), "Incomplete raster package")
    require(value["files"]["definition.json"] == value["definition"]["sha256"], "Raster definition ref differs")
    require(value["files"]["previous-definition.json"] == old["identity"]["definition"]["sha256"], "Raster predecessor definition ref differs")
    require(sha(value["package_hash"]) == digest({k: v for k, v in value.items() if k != "package_hash"}), "Raster package hash differs")
    if raw is not None:
        require(bg.ref("definition.json", raw) == value["definition"], "Raster definition bytes differ")
        quality(value["quality"], raw)
        current = rating.definition(raw)[0]
        require(current["id"] == value["id"] and current["revision"] == old["identity"]["runtime_revision"]+1,
                "Raster package definition identity/revision differs")
    return value


def inventory(directory):
    """Safe, exact file/parent inventory; no supplied paths are opened first."""
    result, directories = {}, set()
    for candidate in directory.rglob("*"):
        name = candidate.relative_to(directory).as_posix()
        path = io.safe(directory, name)
        if path.is_file(): result[name] = path
        else: directories.add(name)
    require(len(result) <= 64, "Raster package has too many files")
    parents = {p.as_posix() for name in result for p in Path(name).parents if p.as_posix() != "."}
    require(directories <= parents, "Raster package contains foreign empty directories")
    return result


def verify(directory, *, replay=False):
    actual = inventory(directory)
    manifest_raw = io.read(directory, "manifest.json", PACKAGE_LIMIT)
    value = validate(io.json_bytes(manifest_raw, PACKAGE_LIMIT), io.read(directory, "definition.json", 2*1024*1024))
    require(manifest_raw == encoded(value) and set(actual) == set(value["files"]) | {"manifest.json"}, "Raster inventory differs")
    for name, checksum in value["files"].items():
        require(io.file_hash(directory, name, 64*1024*1024) == checksum, "Raster package file changed: "+name)
    req = request(io.json_bytes(io.read(directory, "request.json", REQUEST_LIMIT), REQUEST_LIMIT))
    current = rating.definition(io.read(directory, "definition.json", 2*1024*1024))[0]
    previous_raw = io.read(directory,"previous-definition.json",2*1024*1024)
    previous = rating.definition(previous_raw)[0]
    require(identity(value["previous"]["entry"],previous_raw) == value["previous"]["identity"] and
            previous["id"] == current["id"] and previous["palette"] == current["palette"] and
            previous["reveal"] == current["reveal"] and
            definition(previous,parse(req["text"],previous["palette"])) == current and
            current["revision"] == previous["revision"]+1,"Raster predecessor logic/palette/revision differs")
    require(req["id"] == value["id"] and req["decision"] == value["decision"] and req["provenance"] == value["provenance"] and
            parse(req["text"], current["palette"]) == current["solution"], "Raster request/definition/decision differs")
    q = value["quality"]
    from .catalog_method import NEW
    analysis_files = {"input.json","logic.json","trace.json","report.json"}
    if q["baseline"] is not None: analysis_files |= {"r4-proof.json","r4-baseline.json"}
    if q["method"] == NEW:
        expected_analysis = {"analysis/catalog-context.json","analysis/rating/rating.json","analysis/rating/report.md"}
        expected_analysis |= {"analysis/rating/analysis/"+name for name in analysis_files}
    else:
        expected_analysis = {"analysis/catalog-context.json","analysis/rating.json"} | {"analysis/"+name for name in analysis_files}
    expected = {"definition.json","previous-definition.json","request.json","proof.json"} | expected_analysis
    if q["baseline"] is not None: expected.add("baseline.json")
    require(set(value["files"]) == expected,"Raster package contains foreign/missing analysis files")
    for key in ("proof", "baseline"):
        if q[key] is not None: bg._bound(q[key], io.read(directory, q[key]["file"], 64*1024*1024), limit=64*1024*1024)
    require((req["profile"] == "paired") == (q["baseline"] is not None), "Raster profile/baseline differs")
    if replay:
        from .verifier import verify as verify_proof
        puzzle = rating.definition(encoded(current))[1]
        proof = load_json(directory/"proof.json", puzzle.proof_byte_limit)
        from .contract import selected_profile
        expected_profile = selected_profile(puzzle,"paired-lines-color") if q["baseline"] is not None else puzzle.profile
        require(proof.get("profile") == expected_profile,"Raster proof profile differs from selected request")
        checked = verify_proof(puzzle, proof, Budget())
        require(checked["certified"] and proof["status"] == "solved", "Raster proof is incomplete")
        check_end(current, proof)
        if q["baseline"] is not None:
            baseline = load_json(directory/"baseline.json", puzzle.proof_byte_limit)
            verify_proof(puzzle, baseline, Budget())
            require(baseline["profile"] == puzzle.profile, "Raster baseline profile differs")
        checked_rating = rating.import_bundle(directory/"definition.json", directory/"analysis")
        require(checked_rating == q["checked"], "Raster rating differs from independently checked bundle")
    return value


def package(root, entry, manifest, *, replay=False, seen=None):
    """Validate real predecessor packages, without embedding recursive wrappers."""
    original = deepcopy(entry)
    files, frames = set(), []
    seen = set() if seen is None else seen
    while manifest.get("format") == PACKAGE:
        entry, manifest, own_files = _package_link(root, entry, manifest, replay=replay, seen=seen)
        frames.append(own_files[0])
        files.update(own_files[1])
        replay = False
    _, notice, _, previous_files = reveal.package(root,entry,historical=True)
    require(all(frame["notice_sha256"] == notice for frame in frames), "Raster package changes historical notice")
    require(frames[-1]["origin"] == frames[-1]["previous"] and
            all(frame["origin"] == frames[-1]["origin"] for frame in frames), "Raster original production anchor changed")
    return original, notice, None, files | previous_files


def _package_link(root, entry, manifest, *, replay, seen):
    prefix = entry["production"]["package"]
    require(prefix not in seen, "Cyclic editor package ancestry")
    seen.add(prefix)
    value = verify(io.safe(root,prefix), replay=replay)
    require(value == manifest and value["id"] == entry["id"] and value["revision"] == entry["production"]["revision"] and
            prefix == "content/packages/"+entry["id"]+"/"+value["revision"], "Raster package index differs")
    raw = io.read(root,prefix+"/definition.json",2*1024*1024)
    definition_value = rating.definition(raw)[0]
    old = value["previous"]["entry"]
    require(all(old[k] == entry[k] for k in ("id","key","save_slot","definition","reveal","category_id","visible")), "Raster package changes fixed identity")
    expected = deepcopy(old)
    expected["production"].update(package=prefix, package_sha256=io.file_hash(root,prefix+"/manifest.json"),
        revision=value["revision"], definition_sha256=io.checksum(raw), reveal_sha256=value["reveal_sha256"],
        width=definition_value["width"], height=definition_value["height"])
    require(expected == entry, "Raster package production entry differs")
    old_manifest = io.json_bytes(io.read(root,old["production"]["package"]+"/manifest.json",8*1024*1024),8*1024*1024)
    require(io.file_hash(root,old["production"]["package"]+"/manifest.json") == old["production"]["package_sha256"], "Raster predecessor changed")
    files = {prefix+"/"+name for name in value["files"]} | {prefix+"/manifest.json"}
    return old, old_manifest, (value, files)


def historical_repeat(root, entry, incoming):
    """Only complete normalized predecessor equality authorizes a register no-op."""
    seen = set()
    while True:
        prefix = entry["production"]["package"]
        require(prefix not in seen,"Cyclic raster ancestry")
        seen.add(prefix)
        manifest = io.json_bytes(io.read(root,prefix+"/manifest.json",8*1024*1024),8*1024*1024)
        if manifest.get("format") != PACKAGE: return False
        validate(manifest)
        previous = manifest["previous"]["entry"]
        normalized = reveal.package(root,previous,historical=True)[0]
        if normalized == incoming: return True
        entry = previous
