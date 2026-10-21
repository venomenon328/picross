"""Explicit late acceptance of a sealed, already drawn mono pixel source."""
from pathlib import Path

from .authoring_package import file_hash, relative, require, sha, string, timestamp
from .contract import digest, exact_keys, load_json
from .images import inspect_candidate, normalize, raster_image

FORMAT = "picross-manual-authorization-v6"
COMMON = {"puzzle_id", "revision", "handoff_sha256", "inventory_sha256", "selection",
          "accepted_motif", "historical_reveal", "superseded_content_blockers"}
PERMISSIONS = {"accepted_mono_pixel_source", "late_motif_acceptance", "historical_reveal_binding"}


def historical_reveal(package, binding):
    """Resolve only the bound historical prefix; never rewrite the original files."""
    exact_keys(binding, {"prefix", "approval", "provenance"})
    prefix = relative(binding["prefix"]) + "/"
    for key in ("approval", "provenance"):
        ref = exact_keys(binding[key], {"file", "sha256"})
        package.bound(ref)
    h, record = package.handoff, package.handoff["reveal"]
    approval = package.json(binding["approval"]["file"])
    provenance = package.json(binding["provenance"]["file"])
    require(isinstance(approval, dict) and isinstance(provenance, dict), "Invalid historical reveal records")
    original = relative(approval.get("file"))
    require(prefix + original == record["file"] and approval.get("sha256") == record["sha256"] and
            provenance.get("file") == original and provenance.get("sha256") == record["sha256"] and
            provenance.get("puzzle_id") == h["puzzle_id"] and
            approval.get("puzzle_id", h["puzzle_id"]) == h["puzzle_id"], "Historical reveal binding mismatch")
    require(approval.get("type") == "human_reveal_approval" and
            record.get("historical_approval") == binding["approval"]["file"] and
            record.get("approval") is None and
            prefix + relative(provenance.get("approval")) == binding["approval"]["file"],
            "Historical reveal approval mismatch")
    for key in ("actor", "statement", "revision"):
        string(approval.get(key), "historical reveal " + key)
    require(approval["revision"] == record.get("revision"), "Historical reveal revision mismatch")
    timestamp(approval.get("timestamp_utc"))
    package.file(prefix + relative(approval.get("evidence")))
    for key in ("author", "usage_basis"):
        string(provenance.get(key), "historical reveal " + key)
    for key in ("prompt_file", "input"):
        if provenance.get(key) is not None:
            package.file(prefix + relative(provenance[key]))
    return {**provenance, "file": record["file"]}


def authorization(package, path, raw):
    a = exact_keys(raw, COMMON | {"format", "original_zip_sha256", "owner_override"})
    require(a["format"] == FORMAT, "Unsupported accepted raster authorization")
    h, c = package.handoff, package.handoff.get("candidate")
    require(isinstance(c, dict) and c.get("source_type") == "manual" and h.get("repair") is None and
            h.get("state") == "raster_review" and h.get("manual_edit_record") is None and
            h.get("editorial_manual_derivation") is None, "V6 requires a sealed manual pixel source")
    original = package.derivation["original_zip_sha256"] if package.derivation else package.archive_sha256
    if a["original_zip_sha256"] is not None:
        sha(a["original_zip_sha256"])
    selection = {k: c.get(k) for k in ("variant", "matrix_hash", "logic_hash")}
    selection["reveal"] = {k: h["reveal"].get(k) for k in ("file", "sha256")}
    require(a["puzzle_id"] == h["puzzle_id"] and a["revision"] == h["revision"] and
            a["original_zip_sha256"] == original and a["selection"] == selection and
            a["handoff_sha256"] == file_hash(package.file("handoff.json")) and
            a["inventory_sha256"] == h["inventory"]["sha256"], "Accepted raster input binding mismatch")
    blockers = a["superseded_content_blockers"]
    require(h.get("content_blockers", []) == [] and isinstance(blockers, list) and
            len(blockers) <= 32 and all(isinstance(b, str) and 1 <= len(b) <= 4096 for b in blockers) and
            blockers == h.get("blockers", []), "Accepted raster blocker scope mismatch")
    motif = exact_keys(a["accepted_motif"], {"file", "sha256", "derived_from_reveal_sha256", "revision", "parameters"})
    require(all(motif[k] == h["motif"].get(k) for k in
                ("file", "sha256", "derived_from_reveal_sha256", "revision")) and
            isinstance(motif["parameters"], dict) and motif["parameters"] in h.get("proposed_parameters", []) and
            h.get("approved_parameters") == [] and h["gates"].get("motif") == "pending" and
            h["motif"].get("approval") is None, "Accepted raster motif/parameter binding mismatch")
    string(motif["revision"], "accepted raster revision", 32)
    historical_reveal(package, a["historical_reveal"])
    ref = exact_keys(a["owner_override"], {"file", "sha256"})
    require(ref["file"] == "owner-override.json", "Invalid owner override filename")
    owner_path = Path(path).parent / ref["file"]
    require(owner_path.is_file() and not owner_path.is_symlink() and
            file_hash(owner_path) == sha(ref["sha256"]), "Owner override file binding mismatch")
    owner = exact_keys(load_json(owner_path, 256 * 1024), COMMON |
                       {"format", "actor", "statement", "timestamp_utc", "package_sha256", "approval_sha256", "permissions"})
    require(owner["format"] == "picross-owner-override-v6" and
            all(owner[k] == a[k] for k in COMMON) and owner["package_sha256"] == original,
            "Accepted raster owner binding mismatch")
    for key in ("actor", "statement"):
        string(owner[key], "owner " + key)
    timestamp(owner["timestamp_utc"])
    sha(owner["approval_sha256"])
    permissions = exact_keys(owner["permissions"], PERMISSIONS)
    require(all(permissions[k] is True for k in PERMISSIONS), "Accepted raster permission scope mismatch")
    return {"record": a, "path": Path(path), "sha256": file_hash(path), "owner": owner, "owner_path": owner_path}


def inspect_source(package, budget):
    c = package.handoff["candidate"]
    directory = package.bundle(c["bundle"])
    candidate, proof, checked = inspect_candidate(directory, c["variant"], budget)
    design, matrix = candidate["design"], candidate["matrix"]
    result = package.json(c["bundle"] + "/" + c["variant"] + "-result.json")
    require(result.get("status") == "solved" and result.get("certified") is True and
            result.get("proof_verified") is True and checked["certified"] and checked["status"] == "solved",
            "Accepted pixel source is not certified solved")
    manifest = package.json(c["bundle"] + "/manifest.json")
    source = directory / manifest["original"]
    image, meta, _ = normalize(source)
    expected = raster_image(matrix, design)
    require(design["mode"] == "mono" and len(design["palette"]) == 1 and
            design["fit"] == "exact" and design["crop"] == [0, 0, design["width"], design["height"]] and
            meta["format"] == "PNG" and meta["orientation"] == 1 and meta["source_mode"] == "RGB" and
            image.size == (design["width"], design["height"]) and
            image.convert("RGB").tobytes() == expected.convert("RGB").tobytes(),
            "Accepted source must be exact mono RGB pixels, one per cell")
    source_record = {"kind": "manual", "origin": "accepted_mono_pixel_source", "variant": c["variant"],
                     "candidate_id": candidate["id"], "reference": {"variant": c["variant"],
                     "candidate_id": candidate["id"]}, "matrix_hash": digest(matrix)}
    return design, matrix, proof, checked, source_record, directory
