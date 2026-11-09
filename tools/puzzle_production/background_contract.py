"""Closed HP-W2 data forms and byte-bound decision graph; no approval engine.

The reader supplied to ``load_inputs`` owns safe filesystem access, unique-file
accounting and the final recheck of every consumed input. Only the active chosen
subset is opened here; the complete manifest still receives structural checks.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
import re

from .authoring_package import relative as _package_relative
from .contract import InvalidInput


MAX_JSON = 2 * 1024 * 1024
MAX_PNG = 32 * 1024 * 1024
MAX_FILES = 256
MAX_BYTES = 96 * 1024 * 1024
MAX_DEPTH = 32
MAX_LIST = 64

PROFILE = {
    "id": "picross-background-png2304-v1",
    "width": 2304,
    "height": 576,
    "format": "PNG",
    "mode": "RGBA",
    "fit": "contain",
    "anchor": "bottom-center",
    "upscale": True,
    "resample": "pillow-rgba-premultiplied-lanczos",
    "color_space": "sRGB",
    "transparent_rgb": "zero",
    "png_compress_level": 9,
    "png_optimize": False,
    "metadata": "sRGB-only",
}

ERROR_STATUS = {
    **dict.fromkeys((
        "invalid_json", "invalid_request", "unsupported_format", "invalid_binding",
        "missing_file", "unsafe_path", "invalid_image", "opaque_image", "empty_image",
        "resource_limit", "tool_mismatch",
    ), "invalid_input"),
    **dict.fromkeys(("source_changed", "target_conflict"), "conflict"),
    **dict.fromkeys(("interrupted", "deadline_exceeded", "resource_exhausted"), "aborted"),
    **dict.fromkeys(("io_error", "internal_error"), "technical_error"),
}


class BackgroundError(Exception):
    """A closed-contract error, with a safe optional source-relative path."""

    def __init__(self, code, message, path=None):
        self.code = code
        self.status = ERROR_STATUS[code]
        self.message = (str(message).replace("\x00", "")[:4096]
                        .encode("utf-8", errors="replace").decode("utf-8").strip()
                        or "Background operation failed")
        self.path = None
        if type(path) is str and not any(0xD800 <= ord(c) <= 0xDFFF for c in path):
            try:
                self.path = _package_relative(path)
            except InvalidInput:
                pass
        super().__init__(self.message)


def _require(condition, message, *, code="invalid_request", path=None):
    if not condition:
        raise BackgroundError(code, message, path)


def relative(value):
    """Reuse the package path grammar, translating only its error category."""
    _require(type(value) is str, "A relative POSIX path must be a string")
    _require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value),
             "Relative path must contain valid Unicode scalar values", code="unsafe_path")
    try:
        return _package_relative(value)
    except InvalidInput as exc:
        raise BackgroundError("unsafe_path", str(exc)) from exc


def _json_tree(value, *, code="invalid_request"):
    """Bound API values before serialization; reject coercion and cycles."""
    ancestors = set()
    budget = 0

    def visit(item, depth):
        nonlocal budget
        kind = type(item)
        _require(kind in (dict, list, str, int, float, bool, type(None)),
                 "Only JSON objects, arrays and scalar values are supported", code=code)
        if kind in (dict, list):
            _require(depth < MAX_DEPTH, "JSON nesting exceeds 32", code="resource_limit")
            _require(id(item) not in ancestors, "Cyclic API object", code=code)
            _require(len(item) <= MAX_JSON, "JSON collection exceeds byte limit", code="resource_limit")
            separators = len(item) * 2 - 1 if kind is dict else len(item) - 1
            budget += 2 + max(separators, 0)
            _require(budget <= MAX_JSON, "JSON exceeds 2 MiB", code="resource_limit")
            ancestors.add(id(item))
            for key, child in item.items() if kind is dict else enumerate(item):
                if kind is dict:
                    _require(type(key) is str, "JSON object keys must be strings", code=code)
                    visit(key, depth + 1)
                visit(child, depth + 1)
            ancestors.remove(id(item))
        elif kind is str:
            budget += len(item) + 2
            _require(budget <= MAX_JSON, "JSON exceeds 2 MiB", code="resource_limit")
            _require(not any(0xD800 <= ord(c) <= 0xDFFF for c in item),
                     "JSON strings must contain valid Unicode scalar values", code=code)
        elif kind is float:
            _require(math.isfinite(item), "JSON numbers must be finite", code=code)
            budget += 1
        else:
            budget += 1
        _require(budget <= MAX_JSON, "JSON exceeds 2 MiB", code="resource_limit")

    visit(value, 0)


def canonical(value):
    """C(value), with no newline or silent JSON type conversions."""
    _json_tree(value)
    try:
        raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as exc:
        raise BackgroundError("invalid_request", "Value cannot be represented as canonical JSON") from exc
    _require(len(raw) <= MAX_JSON, "JSON exceeds 2 MiB", code="resource_limit")
    return raw


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_json(raw, path=None):
    """Parse bounded UTF-8 JSON, checking depth before the recursive decoder."""
    _require(type(raw) is bytes, "JSON input must be bytes", code="invalid_json", path=path)
    _require(len(raw) <= MAX_JSON, "JSON exceeds 2 MiB", code="resource_limit", path=path)
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise BackgroundError("invalid_json", "JSON is not valid UTF-8", path) from exc
    _require(not text.startswith("\ufeff"), "JSON must not have a BOM", code="invalid_json", path=path)
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            _require(depth <= MAX_DEPTH, "JSON nesting exceeds 32", code="resource_limit", path=path)
        elif char in "]}":
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "Duplicate JSON object key", code="invalid_json", path=path)
            result[key] = value
        return result

    def constant(_value):
        raise BackgroundError("invalid_json", "Nonfinite JSON number", path)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
        _json_tree(value, code="invalid_json")
    except (ValueError, RecursionError) as exc:
        raise BackgroundError("invalid_json", "Malformed JSON", path) from exc
    except BackgroundError as exc:
        if exc.path is None:
            exc.path = BackgroundError(exc.code, exc.message, path).path
        raise
    return value


def _isolated(value):
    # The public API and file API obtain identical plain JSON values. A caller's
    # subsequent mutations cannot change an in-progress operation.
    return parse_json(canonical(value))


def _keys(value, keys, label):
    _require(type(value) is dict and set(value) == set(keys),
             f"{label} must contain exactly: {', '.join(sorted(keys))}")
    return value


def _text(value, label, maximum=4096):
    _require(type(value) is str and bool(value.strip()) and "\x00" not in value,
             f"Invalid {label}")
    _require(len(value) <= maximum, f"{label} exceeds {maximum} characters", code="resource_limit")


def _pattern(value, expression, label):
    _require(type(value) is str and re.fullmatch(expression, value) is not None, f"Invalid {label}")


def _id(value):
    _pattern(value, r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", "ID")


def _puzzle_id(value):
    _pattern(value, r"pz-[a-z0-9][a-z0-9-]{0,59}", "puzzle ID")


def _revision(value):
    _pattern(value, r"[A-Za-z0-9][A-Za-z0-9._-]{0,31}", "revision")


def _sha(value):
    _pattern(value, r"[0-9a-f]{64}", "SHA-256")


def _integer(value, label, low=0, high=None):
    _require(type(value) is int and value >= low, f"{label} must be an integer >= {low}")
    if high is not None:
        _require(value <= high, f"{label} exceeds {high}", code="resource_limit")


def _boolean(value, label):
    _require(type(value) is bool, f"{label} must be a boolean")


def _enum(value, choices, label):
    _require(type(value) is str and value in choices, f"Invalid {label}")


def _list(value, label, maximum=MAX_LIST):
    _require(type(value) is list, f"{label} must be a JSON array")
    _require(len(value) <= maximum, f"{label} exceeds {maximum} entries", code="resource_limit")
    return value


def _utc(value):
    _text(value, "UTC timestamp", 64)
    _require(value.endswith(("Z", "+00:00")) and ("T" in value or "t" in value),
             "Timestamp must be ISO-8601 with Z or +00:00")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BackgroundError("invalid_request", "Invalid UTC timestamp") from exc
    _require(parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0,
             "Timestamp must be in UTC")


def _ref(value):
    _keys(value, ("file", "sha256", "bytes"), "File reference")
    relative(value["file"])
    _sha(value["sha256"])
    _integer(value["bytes"], "Reference bytes")
    return value


def _optional_ref(value):
    if value is not None:
        _ref(value)


def _human(value):
    _keys(value, ("actor", "timestamp_utc", "statement", "evidence"), "Human declaration")
    for key in ("actor", "statement"):
        _text(value[key], key)
    _utc(value["timestamp_utc"])
    _ref(value["evidence"])


def _format(value, expected):
    _require(type(value) is str, "Declared format must be a string")
    _require(value == expected, "Unsupported declared background format", code="unsupported_format")


def _profile(value):
    _keys(value, PROFILE, "Derivation profile")
    _require(all(type(value[key]) is type(expected) and value[key] == expected
                 for key, expected in PROFILE.items()), "Only the fixed PNG2304 profile is supported")


def validate_request(value):
    value = _isolated(value)
    _keys(value, ("format", "manifest", "decision", "source", "profile",
                  "expected_tool_sha256", "output"), "Derivation request")
    _format(value["format"], "picross-background-derive-request-v1")
    _ref(value["manifest"])
    _ref(value["decision"])
    _optional_ref(value["source"])
    _profile(value["profile"])
    _sha(value["expected_tool_sha256"])
    relative(value["output"])
    return value


def _provenance(value):
    _keys(value, ("author", "source", "usage_basis", "rights_status", "attribution", "evidence"),
          "Provenance")
    _text(value["source"], "provenance source")
    for key in ("author", "usage_basis", "attribution"):
        if value[key] is not None:
            _text(value[key], key)
    _enum(value["rights_status"], ("resolved", "unresolved"), "rights status")
    for ref in _list(value["evidence"], "Provenance evidence"):
        _ref(ref)
    if value["rights_status"] == "resolved":
        _require(value["author"] is not None and value["usage_basis"] is not None and value["evidence"],
                 "Resolved rights require author, usage basis and evidence")


def _generation(value):
    fields = ("tool", "model", "prompt", "parameters", "seed")
    _keys(value, (*fields, "unknown"), "Generation")
    for key in ("tool", "model", "seed"):
        if value[key] is not None:
            _text(value[key], key)
    _optional_ref(value["prompt"])
    if value["parameters"] is not None:
        names = set()
        for parameter in _list(value["parameters"], "Generation parameters"):
            _keys(parameter, ("name", "value"), "Generation parameter")
            _text(parameter["name"], "parameter name")
            _require(parameter["name"] not in names, "Duplicate parameter name")
            names.add(parameter["name"])
            _require(type(parameter["value"]) in (str, int, float, bool, type(None)),
                     "Generation parameter value must be a JSON scalar")
    unknown = set()
    for item in _list(value["unknown"], "Unknown generation fields"):
        _keys(item, ("field", "reason"), "Unknown generation field")
        _enum(item["field"], fields, "unknown generation field")
        _enum(item["reason"], ("not_exposed", "not_recorded"), "unknown reason")
        _require(item["field"] not in unknown, "Duplicate unknown generation field")
        unknown.add(item["field"])
    _require(unknown == {key for key in fields if value[key] is None},
             "Unknown generation fields must exactly match the null fields")


def _review(value, original):
    if value is None:
        return
    _keys(value, ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04"), "Isolated review")
    for judgment in value.values():
        _keys(judgment, ("result", "reason", "method", "norm", "actor", "timestamp_utc", "evidence"),
              "Quality judgment")
        _enum(judgment["result"], ("erfüllt", "Warnung", "nicht erfüllt", "nicht geprüft"), "judgment")
        for key in ("reason", "method", "actor"):
            _text(judgment[key], key)
        _utc(judgment["timestamp_utc"])
        norm = _keys(judgment["norm"], ("file", "contract", "document_revision", "commit", "sha256"),
                     "Quality norm")
        _require(norm["file"] == "docs/PUZZLE_QUALITY.md" and norm["contract"] == "1.0",
                 "Quality judgment requires the declared quality contract")
        _integer(norm["document_revision"], "Quality document revision", low=1)
        _pattern(norm["commit"], r"[0-9a-f]{40}", "quality norm commit")
        _sha(norm["sha256"])
        for ref in _list(judgment["evidence"], "Judgment evidence"):
            _ref(ref)
        if judgment["result"] != "nicht geprüft":
            _require(original in judgment["evidence"], "Executed judgment must bind the candidate original",
                     code="invalid_binding")


def validate_manifest(value):
    value = _isolated(value)
    _keys(value, ("format", "puzzle_id", "job_id", "revision", "created_utc", "context", "briefing",
                  "candidate_policy", "presentation", "candidates", "test_only"), "Background manifest")
    _format(value["format"], "picross-background-work-v1")
    _puzzle_id(value["puzzle_id"])
    _id(value["job_id"])
    _revision(value["revision"])
    _utc(value["created_utc"])
    _boolean(value["test_only"], "test_only")
    _text(value["briefing"], "briefing")
    context = _keys(value["context"], ("summary", "protected_features", "excluded_subjects", "reveal",
                                      "reveal_approval"), "Background context")
    _text(context["summary"], "context summary")
    for key in ("protected_features", "excluded_subjects"):
        for text in _list(context[key], key):
            _text(text, key)
    _optional_ref(context["reveal"])
    _optional_ref(context["reveal_approval"])
    _require((context["reveal"] is None) == (context["reveal_approval"] is None),
             "Reveal and its approval must be supplied together")
    policy = _keys(value["candidate_policy"], ("count", "exception"), "Candidate policy")
    _integer(policy["count"], "Candidate count", high=20)
    if policy["exception"] is not None:
        _human(policy["exception"])
    _require(policy["count"] == 3 or policy["exception"] is not None,
             "A nonstandard candidate count requires an explicit owner declaration")
    presentation = _keys(value["presentation"], ("status", "evidence"), "Presentation")
    _enum(presentation["status"], ("pending", "offered"), "presentation status")
    _optional_ref(presentation["evidence"])
    _require((presentation["status"] == "offered") == (presentation["evidence"] is not None),
             "Only an offered presentation has mandatory presentation evidence")
    candidates = _list(value["candidates"], "Background candidates", maximum=20)
    _require(not candidates or context["reveal"] is not None,
             "Candidates require a bound approved reveal", code="invalid_binding")
    if presentation["status"] == "offered":
        _require(len(candidates) == policy["count"] and policy["count"] > 0,
                 "Offered candidates must be the complete nonempty declared set", code="invalid_binding")
    ids, paths = set(), set()
    for candidate in candidates:
        _keys(candidate, ("id", "revision", "description", "original", "provenance", "generation", "review"),
              "Background candidate")
        _id(candidate["id"])
        _require(candidate["id"] != "none" and candidate["id"] not in ids,
                 "Candidate IDs must be unique and must not use none")
        ids.add(candidate["id"])
        _revision(candidate["revision"])
        _text(candidate["description"], "candidate description")
        _ref(candidate["original"])
        key = candidate["original"]["file"].casefold()
        _require(key not in paths, "Candidate original paths must be unique without casefold aliases",
                 code="unsafe_path", path=candidate["original"]["file"])
        paths.add(key)
        _provenance(candidate["provenance"])
        _generation(candidate["generation"])
        _review(candidate["review"], candidate["original"])
    return value


def validate_decision(value):
    value = _isolated(value)
    _keys(value, ("format", "puzzle_id", "job_id", "revision", "background_revision", "manifest", "outcome",
                  "candidate_id", "original", "profile", "actor", "timestamp_utc", "statement", "evidence",
                  "presented_package", "previous_decision", "carried_from", "accepted_deviations", "test_only"),
          "Background decision")
    _format(value["format"], "picross-background-decision-v1")
    _puzzle_id(value["puzzle_id"])
    _id(value["job_id"])
    _revision(value["revision"])
    _revision(value["background_revision"])
    _ref(value["manifest"])
    _enum(value["outcome"], ("selected", "none", "rejected"), "decision outcome")
    _human({key: value[key] for key in ("actor", "timestamp_utc", "statement", "evidence")})
    _boolean(value["test_only"], "test_only")
    for key in ("previous_decision", "carried_from"):
        _optional_ref(value[key])
    if value["outcome"] == "selected":
        _id(value["candidate_id"])
        _require(value["candidate_id"] != "none", "none is not a candidate ID")
        _ref(value["original"])
        _keys(value["profile"], ("id", "sha256"), "Decision profile binding")
        _require(value["profile"]["id"] == PROFILE["id"], "Invalid decision profile ID", code="invalid_binding")
        _sha(value["profile"]["sha256"])
        _require(value["profile"]["sha256"] == digest(PROFILE), "Decision profile hash mismatch",
                 code="invalid_binding")
    else:
        _require(value["candidate_id"] is None and value["original"] is None and value["profile"] is None,
                 "A none/rejected decision must have null candidate, original and profile")
    if value["presented_package"] is not None:
        package = _keys(value["presented_package"], ("puzzle_id", "revision", "original_zip_sha256",
                        "handoff_sha256", "inventory_sha256"), "Presented package binding")
        _puzzle_id(package["puzzle_id"])
        _revision(package["revision"])
        for key in ("original_zip_sha256", "handoff_sha256", "inventory_sha256"):
            _sha(package[key])
        _require(package["puzzle_id"] == value["puzzle_id"], "Presented package puzzle ID mismatch",
                 code="invalid_binding")
    criteria = set()
    for deviation in _list(value["accepted_deviations"], "Accepted deviations"):
        _keys(deviation, ("criterion", "reason"), "Accepted deviation")
        _enum(deviation["criterion"], ("Q-HG02", "Q-HG03", "Q-HG04"), "deviation criterion")
        _text(deviation["reason"], "deviation reason")
        _require(deviation["criterion"] not in criteria, "Duplicate accepted deviation")
        criteria.add(deviation["criterion"])
    _require(value["outcome"] == "selected" or not criteria,
             "A none/rejected decision must have no accepted deviations")
    return value


def _bind_decision(manifest, decision):
    _require(all(manifest[key] == decision[key] for key in ("puzzle_id", "job_id", "test_only")) and
             manifest["revision"] == decision["background_revision"],
             "Decision identity/revision does not match its manifest", code="invalid_binding")
    candidate = None
    if decision["outcome"] == "selected":
        _require(manifest["presentation"]["status"] == "offered", "Selection requires an offered manifest",
                 code="invalid_binding")
        candidate = next((c for c in manifest["candidates"] if c["id"] == decision["candidate_id"]), None)
        _require(candidate is not None and decision["original"] == candidate["original"],
                 "Selected candidate/original does not match the manifest", code="invalid_binding")
        for deviation in decision["accepted_deviations"]:
            review = candidate["review"]
            _require(review is not None and review[deviation["criterion"]]["result"] in ("Warnung", "nicht erfüllt"),
                     "Accepted deviation must name a recorded negative judgment", code="invalid_binding")
    elif decision["outcome"] == "none" and manifest["presentation"]["status"] != "offered":
        _require(manifest["candidate_policy"]["exception"] is not None,
                 "none without a complete offered set requires an explicit candidate waiver", code="invalid_binding")
    return candidate


def _carry(manifest, decision, candidate, previous):
    old_manifest, old_decision, old_candidate = previous
    _require(decision["outcome"] == old_decision["outcome"] and
             decision["candidate_id"] == old_decision["candidate_id"] and
             manifest["context"] == old_manifest["context"] and decision["profile"] == old_decision["profile"],
             "carried_from changes the chosen image, context or profile", code="invalid_binding")
    _require(all(decision[key] == old_decision[key] for key in ("actor", "timestamp_utc", "statement", "evidence")),
             "carried_from must preserve the actual declaration byte for byte", code="invalid_binding")
    _require(decision["accepted_deviations"] == old_decision["accepted_deviations"],
             "carried_from cannot introduce a different acceptance of deviations", code="invalid_binding")
    if candidate is not None:
        _require(old_candidate is not None and candidate["revision"] == old_candidate["revision"] and
                 all(candidate["original"][key] == old_candidate["original"][key] for key in ("sha256", "bytes")),
                 "carried_from requires unchanged original bytes and image revision", code="invalid_binding")


def load_inputs(request, reader):
    """Validate the explicit current decision and its complete predecessor DAG.

    The reader must reject conflicting path occupancy, aliases and ZIPs, enforce
    graph limits and reread the consumed sources before publication. Evidence is
    byte-bound here; it is not interpreted as authentication, rights or Q-HG pass.
    """
    request = validate_request(request)
    manifests, decisions, consumed, active, edges = {}, {}, {}, set(), {}
    manifest_revisions, decision_revisions, image_revisions = {}, {}, {}

    def read(ref, limit):
        _require(ref["bytes"] <= limit, "Declared file size exceeds its limit", code="resource_limit", path=ref["file"])
        previous = consumed.get(ref["file"])
        _require(previous is None or previous == ref, "Conflicting source references occupy the same path",
                 code="target_conflict", path=ref["file"])
        raw = reader.read_ref(ref, limit=limit)
        consumed[ref["file"]] = ref
        return raw

    def dependency(owner, ref, limit=MAX_PNG):
        if ref is None:
            return
        edges.setdefault(owner, set()).add(ref["file"])
        _require(owner != ref["file"], "Self-referencing background source", code="invalid_binding", path=owner)
        if ref["file"] not in consumed or consumed[ref["file"]] != ref:
            read(ref, limit)
        else:
            _require(ref["bytes"] <= limit, "Declared file size exceeds its limit", code="resource_limit", path=ref["file"])

    def unchanged(table, key, ref, label):
        identity = (ref["sha256"], ref["bytes"])
        _require(key not in table or table[key] == identity, f"Changed bytes reuse an existing {label} revision",
                 code="invalid_binding", path=ref["file"])
        table[key] = identity

    def manifest_for(ref):
        key = (ref["file"], ref["sha256"], ref["bytes"])
        if key not in manifests:
            value = validate_manifest(parse_json(read(ref, MAX_JSON), ref["file"]))
            unchanged(manifest_revisions, (value["puzzle_id"], value["job_id"], value["revision"]), ref, "manifest")
            for item in value["candidates"]:
                unchanged(image_revisions, (value["puzzle_id"], value["job_id"], item["id"], item["revision"]),
                          item["original"], "image")
            manifests[key] = value
        return manifests[key]

    current_manifest = manifest_for(request["manifest"])
    job = tuple(current_manifest[key] for key in ("puzzle_id", "job_id", "test_only"))

    def visit(ref):
        path = ref["file"]
        key = (path, ref["sha256"], ref["bytes"])
        _require(path not in active, "Cyclic decision predecessor graph", code="invalid_binding", path=path)
        if key in decisions:
            return decisions[key]
        active.add(path)
        value = validate_decision(parse_json(read(ref, MAX_JSON), path))
        _require(tuple(value[key] for key in ("puzzle_id", "job_id", "test_only")) == job,
                 "Predecessor decision belongs to a different puzzle, job or test_only identity",
                 code="invalid_binding", path=path)
        unchanged(decision_revisions, (*job, value["revision"]), ref, "decision")
        edges.setdefault(path, set()).add(value["manifest"]["file"])
        _require(value["manifest"]["file"] != path, "Decision cannot bind itself as a manifest",
                 code="invalid_binding", path=path)
        manifest = manifest_for(value["manifest"])
        candidate = _bind_decision(manifest, value)
        owner = value["manifest"]["file"]
        for field in ("reveal", "reveal_approval"):
            dependency(owner, manifest["context"][field])
        if manifest["candidate_policy"]["exception"] is not None:
            dependency(owner, manifest["candidate_policy"]["exception"]["evidence"])
        dependency(owner, manifest["presentation"]["evidence"])
        dependency(path, value["evidence"])
        if candidate is not None:
            dependency(owner, candidate["original"])
            dependency(owner, candidate["generation"]["prompt"])
            for proof in candidate["provenance"]["evidence"]:
                dependency(owner, proof)
            if candidate["review"] is not None:
                for judgment in candidate["review"].values():
                    for proof in judgment["evidence"]:
                        dependency(owner, proof)
        predecessors = {}
        for field in ("previous_decision", "carried_from"):
            predecessor = value[field]
            if predecessor is not None:
                edges[path].add(predecessor["file"])
                predecessors[field] = visit(predecessor)
        if "carried_from" in predecessors:
            _carry(manifest, value, candidate, predecessors["carried_from"])
        active.remove(path)
        decisions[key] = manifest, value, candidate
        return decisions[key]

    manifest, decision, candidate = visit(request["decision"])
    _require(decision["manifest"] == request["manifest"], "Request and decision bind different manifests",
             code="invalid_binding")
    _require(decision["outcome"] in ("selected", "none"), "Rejected decision cannot be derived",
             code="invalid_binding")
    _require(request["source"] == decision["original"], "Request source does not match the explicit decision",
             code="invalid_binding")

    # Also rule out cycles through evidence/manifest edges, not just decisions.
    done, visiting = set(), set()

    def acyclic(node):
        _require(node not in visiting, "Cyclic background reference graph", code="invalid_binding", path=node)
        if node in done:
            return
        visiting.add(node)
        for child in edges.get(node, ()):
            acyclic(child)
        visiting.remove(node)
        done.add(node)

    for node in edges:
        acyclic(node)
    return manifest, decision, candidate
