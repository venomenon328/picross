"""Final integration input: current data, deduction, rights and real decision.

Transport origin is deliberately absent. Export copies only the declared files.
"""
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import shutil
import tempfile

from . import current_content as content, catalog_io as io, catalog_rating as rating
from . import catalog_method, catalog_added, palette_quality, verifier
from .authoring_package import require
from .contract import exact_keys, digest, Budget
from .editor_raster import check_end

FORMAT = "picross-integration-input-v1"
FIELDS = {"format", "entry", "metadata", "definition", "reveal", "background",
          "difficulty", "proof", "quality", "approval", "test_only"}
CHECKS = ("reveal", "motif", "raster", "palette", "hint_legibility", "background", "final_content", "integration")


def selection(value):
    return digest({k: v for k, v in value.items() if k != "approval"})


def decision(value):
    from .editor_image_source import decision as check
    check({k: value[k] for k in ("actor", "timestamp_utc", "statement")})


class Input:
    @io.bounded
    def __init__(self, directory):
        self.root = io.external(directory)
        self.raw = {}
        self.value = self.json("manifest.json", 1024*1024)
        value = exact_keys(self.value, FIELDS)
        require(value["format"] == FORMAT, "Current integration input required")
        content.entries([value["entry"]])
        self.entry = value["entry"]
        require(type(value["test_only"]) is bool, "Invalid fixture declaration")
        meta = exact_keys(value["metadata"], {"id", "name", "category_id"})
        require(meta["id"] == self.entry["id"] and meta["category_id"] == self.entry["category_id"] and
                isinstance(meta["name"], str) and 1 <= len(meta["name"]) <= 128 and meta["name"].strip(), "Invalid input metadata")
        self.definition_raw = self.bound(value["definition"], 2*1024*1024)
        self.definition, puzzle, _, _ = rating.definition(self.definition_raw)
        require(self.definition["id"] == self.entry["id"], "Definition identity differs")
        require(self.entry["mode"] != "mono" or len(puzzle.colors) == 1, "Mono requires one color")
        require(self.definition["reveal"]["image"] == "res://"+self.entry["reveal"] and
                self.definition["reveal"]["name"] == meta["name"], "Final definition reveal/name differs")
        used = {cell for row in self.definition["solution"] for cell in row if cell}
        require(used == {p["id"] for p in self.definition["palette"]}, "Palette must contain exactly the used colors")
        proof = io.json_bytes(self.bound(value["proof"], 64*1024*1024), 64*1024*1024)
        verified = verifier.verify(puzzle, proof, Budget(300, 1000000))
        require(verified["proof_verified"] and verified["certified"], "Complete independent deduction required")
        check_end(self.definition, proof)
        from . import current_rating
        self.checked = current_rating.validate(io.json_bytes(self.bound(value["difficulty"], rating.LIMIT), rating.LIMIT),
                                       active=False, definition_bytes=self.definition_raw, production_mode=self.entry["mode"])
        self.reveal = self.image(value["reveal"], "reveal")
        background = exact_keys(value["background"], {"status", "image"})
        require(background["status"] in ("standard", "none", "selected"), "Invalid background preference")
        require((background["image"] is not None) == (background["status"] == "selected"), "Missing/unexpected background image")
        self.background = self.image(background["image"], "background") if background["image"] else None
        self.quality(value["quality"])
        approval = exact_keys(value["approval"], {"actor", "timestamp_utc", "statement", "selection_sha256", "evidence", "checks"})
        decision(approval)
        require(approval["selection_sha256"] == selection(value), "Decision does not bind current selection")
        exact_keys(approval["checks"], set(CHECKS))
        require(all(v is True for v in approval["checks"].values()), "Actual content and integration decision required")
        evidence = self.bound(approval["evidence"], 65536)
        require(evidence.decode("utf-8").strip(), "Empty decision evidence")
        self.recheck()

    def read(self, name, limit):
        if name not in self.raw:
            self.raw[name] = io.read(self.root, name, limit)
        require(len(self.raw[name]) <= limit, "Oversized integration input")
        return self.raw[name]

    def json(self, name, limit):
        return io.json_bytes(self.read(name, limit), limit)

    def bound(self, value, limit):
        content.reference(value, limit=limit)
        raw = self.read(value["file"], limit)
        require(content.ref(value["file"], raw) == value, "Changed final input: "+value["file"])
        return raw

    def image(self, value, kind):
        exact_keys(value, {"asset", "notice", "rights"})
        from .reveal_source import provenance, make_notice
        provenance(value["rights"])
        notice = self.bound(value["notice"], 65536)
        make_notice(notice)
        require(all(text in notice.decode("utf-8") for text in value["rights"].values()),
                "Current notice must preserve all supplied rights information")
        raw = self.bound(value["asset"], 32*1024*1024)
        path = io.safe(self.root, value["asset"]["file"])
        if kind == "reveal":
            from .image_validation import validate_reveal
            validate_reveal(path, self.definition["width"], self.definition["height"])
            require(path.suffix == Path(self.entry["reveal"]).suffix, "Reveal extension differs")
        else:
            from .catalog_publication import _validate_background_image
            _validate_background_image(path)
        return {"asset": raw, "notice": notice}

    def quality(self, value):
        exact_keys(value, {"review", "exceptions"})
        review=io.json_bytes(self.bound(value["review"],65536),65536)
        exact_keys(review,{"actor","timestamp_utc","statement","criteria"})
        decision(review)
        from .palette_gate import CRITERIA
        exact_keys(review["criteria"],CRITERIA)
        for criterion,finding in review["criteria"].items():
            exact_keys(finding,{"result","accepted","reason"})
            require(finding["result"] in ("fulfilled","borderline","failed") and type(finding["accepted"]) is bool and
                    isinstance(finding["reason"],str) and finding["reason"].strip(),"Invalid visual criterion: "+criterion)
            require(finding["result"]=="fulfilled" or finding["accepted"],
                    "Visual criterion needs actual acceptance: "+criterion)
        matrix = self.definition["solution"]
        frame_ok = (any(row[0] for row in matrix) or any(row[-1] for row in matrix)) and (any(matrix[0]) or any(matrix[-1]))
        findings = [] if frame_ok else ["frame"]
        palette = self.definition["palette"]
        for a, b in combinations(palette, 2):
            qa, qb = (palette_quality.quantized_oklab("#"+p["color"]) for p in (a, b))
            score = sum((x-y)**2 for x, y in zip(qa, qb))
            if palette_quality.pair_status(score) == "negative":
                findings.append("palette:"+str(a["id"])+":"+str(b["id"]))
        exceptions = value["exceptions"]
        require(isinstance(exceptions, list) and len(exceptions) <= 29, "Invalid quality exceptions")
        actual = []
        for exception in exceptions:
            exact_keys(exception, {"criterion", "actor", "timestamp_utc", "statement", "evidence"})
            decision(exception)
            require(self.bound(exception["evidence"], 65536).decode("utf-8").strip(), "Missing explicit exception evidence")
            actual.append(exception["criterion"])
        require(sorted(actual) == sorted(findings), "Current frame/palette failures require their exact explicit exceptions")

    def recheck(self):
        for name, raw in self.raw.items():
            require(io.read(self.root, name, max(len(raw), 1)) == raw, "Input changed while validating: "+name)


@io.bounded
def export(source, output):
    """The sole current exporter; no original package or producer admission."""
    current = Input(source)
    output = io.external(output)
    require(not output.exists(), "Export output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".integration-", dir=output.parent) as temporary:
        stage = Path(temporary)/"input"
        stage.mkdir()
        for name, raw in current.raw.items():
            target = io.safe(stage, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        Input(stage)
        current.recheck()
        from .catalog_publication import rename
        rename(stage, output, replace=False)
    return {"status": "exported", "id": current.entry["id"], "output": str(output)}
