"""Final integration input: current data, deduction, rights and real decision.

Transport origin is deliberately absent. Export copies only the declared files.
"""
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import shutil
import tempfile

from . import current_content as content, catalog_io as io, catalog_rating as rating, current_qualification
from . import catalog_method, catalog_added, palette_quality, verifier
from .authoring_package import require
from .contract import exact_keys, digest, Budget
from .editor_raster import check_end
from .raster_parameters import frame_edges, frame_failures, require_color_count, used_foreground

FORMAT = "picross-integration-input-v1"
PW_SOURCE = "pw-source.json"
FINDING_FORMAT = "picross-integration-input-v2"
FIELDS = {"format", "entry", "metadata", "definition", "reveal", "background",
          "difficulty", "proof", "quality", "approval", "test_only"}
CHECKS = ("reveal", "motif", "raster", "palette", "hint_legibility", "background", "final_content", "integration")


def selection(value):
    return digest({k: v for k, v in value.items() if k != "approval"})


def decision(value):
    from .editor_image_source import decision as check
    check({k: value[k] for k in ("actor", "timestamp_utc", "statement")})


def from_current(directory, manifest, files, checked):
    """Consume the projection produced by current_authoring from its checked job."""
    job = checked.job
    from . import finding_decisions
    if job['format'] not in finding_decisions.FORMATS:
        return Input(directory)
    selected = job['selected']
    require(job['state'] in ('editorially_approved', 'registered')
            and manifest['format'] == FINDING_FORMAT and manifest['approval']['selection_sha256'] == selection(manifest),
            'Approved current selection required')
    value = Input.__new__(Input)
    value.root, value.raw, value.value = directory, files, manifest
    value.entry = manifest['entry']
    facts = checked.rasters[selected['raster']]
    value.definition, value.checked = facts['definition'], facts['difficulty']
    value.definition_raw = files[manifest['definition']['file']]
    require(value.definition['reveal']['image'] == 'res://'+value.entry['reveal']
            and value.definition['reveal']['name'] == manifest['metadata']['name']
            and value.checked['production_mode'] == value.entry['mode'], 'Delivery differs from qualified raster')
    def image(part):
        return {key: files[part[key]['file']] for key in ('asset', 'notice')}
    value.reveal = image(manifest['reveal'])
    require(Path(manifest['reveal']['asset']['file']).suffix == Path(value.entry['reveal']).suffix,
            'Reveal extension differs')
    part = manifest['background']['image']
    value.background = image(part) if part else None
    value.reveal_size = checked.image_sizes[selected['reveal']]
    return value


class Input:
    recheck_source = None
    @io.bounded
    def __init__(self, directory):
        self.root = io.external(directory)
        self.raw = {}
        self.value = self.json("manifest.json", 1024*1024)
        value = exact_keys(self.value, FIELDS)
        require(value["format"] in (FORMAT, FINDING_FORMAT), "Current integration input required")
        content.entries([value["entry"]])
        self.entry = value["entry"]
        require(type(value["test_only"]) is bool, "Invalid fixture declaration")
        meta = exact_keys(value["metadata"], {"id", "name", "category_id"})
        require(meta["id"] == self.entry["id"] and meta["category_id"] == self.entry["category_id"] and
                isinstance(meta["name"], str) and 1 <= len(meta["name"]) <= 128 and meta["name"].strip(), "Invalid input metadata")
        self.definition_raw = self.bound(value["definition"], 2*1024*1024)
        self.definition, puzzle, _, _ = rating.definition(self.definition_raw)
        require(self.definition["id"] == self.entry["id"], "Definition identity differs")
        require(self.definition["reveal"]["image"] == "res://"+self.entry["reveal"] and
                self.definition["reveal"]["name"] == meta["name"], "Final definition reveal/name differs")
        used = used_foreground(self.definition["solution"])
        require_color_count(self.entry["mode"], len(used))
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
            info = validate_reveal(path, self.definition["width"], self.definition["height"])
            self.reveal_size = (info["width"], info["height"])
            require(path.suffix == Path(self.entry["reveal"]).suffix, "Reveal extension differs")
        else:
            from .catalog_publication import _validate_background_image
            _validate_background_image(path)
        return {"asset": raw, "notice": notice}

    def quality(self, value):
        exact_keys(value, {"review", "exceptions"})
        structured = self.value['format'] == FINDING_FORMAT
        limit = 1024*1024 if structured else 65536
        review = io.json_bytes(self.bound(value['review'], limit), limit)
        candidate = None
        if structured:
            from .finding_decisions import check_selected, matching_modes
            from . import raster_parameters
            check_selected(review, self.value)
            require(self.entry['mode'] in matching_modes(review['parameters'], self.definition, len(self.definition['palette'])),
                    'Selected raster differs from approved parameters')
            candidate = review['components']['raster']['id']
            for option in review['parameters']:
                if option.get('format') == raster_parameters.FORMAT and self.entry['mode'] in matching_modes(
                        [option], self.definition, len(self.definition['palette'])):
                    actual = {axis: self.definition[axis] for axis in ('width', 'height')}
                    raster_parameters.result(option, {**actual, 'mode': self.entry['mode']}, self.definition['solution'], empty=0)
                    break
            if self.background:
                from io import BytesIO
                from PIL import Image
                from .background_contract import SIZES
                with Image.open(BytesIO(self.background['asset'])) as prepared:
                    require(SIZES.get(prepared.size) == review['components']['background']['profile'], 'Selected background profile differs')
            decision(review)
        else:
            self.legacy_review(review)
        self.exceptions(value["exceptions"], candidate=candidate)

    @staticmethod
    def legacy_review(review):
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

    def exceptions(self, exceptions, *, candidate):
        frame = frame_failures(frame_edges(self.definition["solution"]))
        findings = ["frame"] if frame else []
        palette = self.definition["palette"]
        for a, b in combinations(palette, 2):
            qa, qb = (palette_quality.quantized_oklab("#"+p["color"]) for p in (a, b))
            score = sum((x-y)**2 for x, y in zip(qa, qb))
            if palette_quality.pair_status(score) == "negative":
                findings.append("palette:"+str(a["id"])+":"+str(b["id"]))
        require(isinstance(exceptions, list) and len(exceptions) <= 29, "Invalid quality exceptions")
        actual = []
        for exception in exceptions:
            structured = self.value['format'] == FINDING_FORMAT
            fields = {'definition_sha256'} if structured else set()
            if structured and exception.get('criterion') == 'frame' and ('candidate_id' in exception or 'revision' in exception):
                fields |= {'candidate_id', 'revision'}
            exact_keys(exception, {"criterion", "actor", "timestamp_utc", "statement", "evidence"} | fields)
            if 'candidate_id' in exception:
                require(type(exception['revision']) is int and (exception['candidate_id'], exception['revision']) ==
                        (candidate, self.definition['revision']), 'Foreign or stale frame exception')
            if structured:
                require(exception['definition_sha256'] == self.value['definition']['sha256'], 'Stale technical exception')
            decision(exception)
            require(self.bound(exception["evidence"], 65536).decode("utf-8").strip(), "Missing explicit exception evidence")
            actual.append(exception["criterion"])
        require(sorted(actual) == sorted(findings), "Current frame/palette failures require their exact explicit exceptions")

    def recheck(self):
        if self.recheck_source is not None:
            self.recheck_source()
        for name, raw in self.raw.items():
            require(io.read(self.root, name, max(len(raw), 1)) == raw, "Input changed while validating: "+name)


def open_input(directory, *, pw_root=None, job_id=None):
    """Share a completed intake only inside the current batch, checking every byte."""
    root = io.external(directory)
    manifest = io.read(root, 'manifest.json', 1024 * 1024)
    binding = io.read(root, PW_SOURCE, 4096, missing=True)
    key = ('integration-input', io.checksum(manifest), binding)
    previous = current_qualification.lookup(key)
    if previous is not None:
        previous.root = root
        previous.recheck()
        return previous
    if binding is not None or pw_root is not None:
        from .current_authoring import open_worktree_input
        require(binding is not None and pw_root is not None, 'Bound delivery requires the PW worktree and source binding')
        result = open_worktree_input(root, pw_root, job_id or io.json_bytes(binding, 4096)['job'])
    else:
        result = Input(root)
    require(result.raw['manifest.json'] == manifest, 'Input changed while opening')
    current_qualification.remember(key, result)
    return result


@io.bounded
def export(source, output):
    """The sole current exporter; no original package or producer admission."""
    current = open_input(source)
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
        # Verify the staged inventory against the exact bytes qualified above.
        for name, raw in current.raw.items():
            require(io.read(stage, name, len(raw)) == raw, "Exported input differs: " + name)
        current.recheck()
        from .catalog_publication import rename
        rename(stage, output, replace=False)
    return {"status": "exported", "id": current.entry["id"], "output": str(output)}
