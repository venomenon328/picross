"""PW-PERF-B: closed v10 registration authority, never an old-file audit.

Only shared indices and the selected new production are consumed. Historical
writers and explicit whole-checkout audits retain their independent contracts.
"""
from copy import deepcopy
from pathlib import Path

from . import catalog_io as io, catalog_transaction as tx, catalog_publication as pub
from . import categories, catalog_method as method, catalog_added as added
from . import catalog_rating as rating, catalog_background as bg, reveal_source as reveal
from . import content_registry as cr, catalog_difficulty, operation_diagnostics as diagnostic
from .authoring_package import require, relative, sha
from .contract import canonical_bytes, exact_keys, integer

SHARED = {tx.REGISTRY, tx.RUNTIME, categories.PATH, method.PATH, bg.CAPABILITY}


def encoded(value):
    return canonical_bytes(value) + b"\n"


def parse(raw, limit=8*1024*1024):
    return io.json_bytes(raw.encode() if isinstance(raw, str) else raw, limit)


def selected(registry, entry):
    return {**registry, "entries": [entry],
            "metadata": [r for r in registry["metadata"] if r["id"] == entry["id"]],
            "backgrounds": [r for r in registry["backgrounds"] if r["id"] == entry["id"]]}


def indices(texts):
    catalog = categories.validate(parse(texts[categories.PATH], categories.MAX_BYTES))
    registry = cr.validate(parse(texts[tx.REGISTRY]), catalog)
    cr.require_current(registry)
    runtime = exact_keys(parse(texts[tx.RUNTIME]), {"format", "categories", "entries"})
    require(runtime["format"] == cr.IMAGE_RUNTIME_FORMAT, "v10 requires runtime v8")
    require(isinstance(runtime["entries"], list) and len(runtime["entries"]) == len(registry["entries"])
            and runtime["categories"] == categories.ordered(catalog), "Invalid runtime index")
    for name, value in ((tx.REGISTRY, registry), (tx.RUNTIME, runtime)):
        raw = texts[name].encode() if isinstance(texts[name], str) else texts[name]
        require(raw == encoded(value), "Noncanonical registration index: " + name)
    paths = set()
    background_refs = bg.index(registry)
    def unique(name):
        relative(name)
        require(name.casefold() not in paths, "Index resource collision: " + name)
        paths.add(name.casefold())
    for row, entry, meta in zip(runtime["entries"], registry["entries"], registry["metadata"]):
        exact_keys(row, {"id", "key", "save_slot", "definition", "reveal", "visible", "category_id",
                         "difficulty", "added_at", "background", "name"})
        require(all(row[k] == entry[k] for k in ("id", "key", "save_slot", "definition", "visible"))
                and type(row["visible"]) is bool and row["name"] == meta["name"]
                and row["category_id"] == meta["category_id"], "Runtime identity/metadata differs")
        catalog_difficulty.validate_projection(row["difficulty"], version=5)
        added.timestamp(row["added_at"])
        require(isinstance(row["reveal"], str) and row["reveal"] in
                {str(Path(entry["reveal"]).with_suffix(ext)).replace("\\", "/") for ext in (".png", ".svg")},
                "Invalid current reveal reference")
        for name in ("game/" + row["definition"], "game/" + row["reveal"], entry["production"]["package"]):
            unique(name)
        require(entry["production"]["package"] == "content/packages/" + entry["id"] + "/" + entry["production"]["revision"],
                "Invalid package index reference")
        state = exact_keys(row["background"], {"status", "image_revision", "asset"})
        require(state["status"] in ("legacy", "standard", "none", "selected"), "Invalid background status")
        if state["status"] == "legacy":
            require(state["image_revision"] is None and state["asset"] is None, "Invalid legacy background")
        else:
            integer(state["image_revision"], 1, 1000000, "background revision")
            if state["status"] == "selected":
                ref = exact_keys(state["asset"], {"file", "bytes", "sha256"})
                require(ref["file"] == "art/backgrounds/" + entry["id"] + ".png", "Invalid background path")
                integer(ref["bytes"], 0, 64*1024*1024, "background bytes")
                sha(ref["sha256"])
                unique("game/" + ref["file"])
            else:
                require(state["asset"] is None, "Unexpected background asset")
        require((entry["id"] in background_refs) == (state["status"] != "legacy"), "Background index/runtime differs")
    method.from_bytes(texts[method.PATH].encode() if isinstance(texts[method.PATH], str) else texts[method.PATH])
    bg.capability(None, texts, required=any(r["background"]["status"] in ("selected", "none") for r in runtime["entries"]))
    tx.image_candidates(registry)
    return registry, catalog, runtime


@diagnostic.measured("Registration indices", "registration_index_snapshots")
def capture(root, identifier=None):
    require(tx.read(root, tx.LOCK) is None and not pub.staging(root), "Interrupted registration: recovery required")
    texts = {n: tx.read(root, n) for n in SHARED}
    registry, _, _ = indices(texts)
    result = {"registry": registry, "texts": texts, "retained": {}, "namespaces": {}, "registration_v10": True}
    existing = next((e for e in registry["entries"] if isinstance(identifier, str) and e["id"].casefold() == identifier.casefold()), None)
    if existing is not None:
        result["repeat"] = repeat_binding(root, registry, existing)
    recheck(root, result)
    return result


def recheck(root, snapshot):
    require(tx.read(root, tx.LOCK) is None and not pub.staging(root), "Interrupted registration: recovery required")
    require(all(tx.read(root, n) == raw for n, raw in snapshot["texts"].items()), "Registration indices changed")


def entry_delta(before, after):
    entries = [e for e in after["entries"] if e not in before["entries"]]
    require(len(entries) == 1 and [e for e in after["entries"] if e not in entries] == before["entries"],
            "Invalid registration entry delta")
    return entries[0]


def names(entry, additions):
    from .content_update import notice_path
    own = {"format": cr.METADATA_FORMAT, "entries": [entry], "metadata": [], "backgrounds": []}
    return SHARED | {"game/" + entry["definition"], notice_path(entry), rating.path(entry["id"]),
                     added.path(entry["id"]), reveal.path(entry["id"]), bg.path(entry["id"]),
                     bg.notice_path(entry["id"])} | (tx.image_candidates(own) - set(additions))


def project(texts, registry, entry, prior_runtime):
    one = selected(registry, entry)
    row = parse(tx.projection(texts, one, version=8))["entries"][0]
    runtime = deepcopy(prior_runtime)
    runtime["entries"].append(row)
    runtime["entries"].sort(key=lambda r: r["id"])
    return encoded(runtime).decode()


def check_new(j, *, planned=False):
    before, _, runtime = indices(j["old"])
    after, _, _ = indices(j["new"])
    entry = entry_delta(before, after)
    require(set(j["old"]) == set(j["new"]) == names(entry, j["additions"]), "Invalid v10 text dependency set")
    require(all(j["old"][n] is None for n in set(j["old"]) - SHARED), "Occupied registration target")
    require(all(j["old"][n] == j["new"][n] for n in SHARED - {tx.REGISTRY, tx.RUNTIME}), "Shared source mutation")
    require(j["new"][reveal.path(entry["id"])] is None, "First registration cannot adopt a reveal source")
    package = tx._delta(j, before, after, planned=planned)
    require(j["new"][tx.RUNTIME] == project(j["new"], after, entry, runtime), "Invalid v10 runtime delta")
    # Everything beyond the closed registration delta must stay absent.
    allowed = {tx.REGISTRY, tx.RUNTIME, "game/" + entry["definition"], rating.path(entry["id"]),
               added.path(entry["id"]), bg.path(entry["id"]), bg.notice_path(entry["id"])}
    from .content_update import notice_path
    allowed.add(notice_path(entry))
    require(all(j["new"][n] is None for n in set(j["new"]) - SHARED - allowed), "Unexpected registration sidecar")
    if entry["id"] not in bg.index(after):
        require(j["new"][bg.path(entry["id"])] is None and j["new"][bg.notice_path(entry["id"])] is None,
                "Unindexed background source")
    return package, entry


@diagnostic.measured("Registration projection", "registration_projections")
def prepare(root, snapshot, changes, additions, *, planned=False):
    before = snapshot["registry"]
    after = parse(changes[tx.REGISTRY]); entry = entry_delta(before, after)
    targets = names(entry, additions)
    require(set(changes) <= targets and not set(additions) & targets, "Unexpected registration write target")
    old = {n: snapshot["texts"][n] if n in SHARED else tx.read(root, n) for n in targets}
    new = {**old, **changes}
    j = {"format": tx.registration_format("dependencies"), "operation": "registration", "old": {n: b.decode() if b is not None else None for n,b in old.items()},
         "new": {n: b.decode() if b is not None else None for n,b in new.items()}, "retained": {},
         "additions": {n: io.file_hash(p.parent, p.name, tx._addition_limit(after,n,p)) for n,p in additions.items()},
         "report_run": None, "replacements": {}}
    j["new"][tx.RUNTIME] = project(j["new"], after, entry, parse(snapshot["texts"][tx.RUNTIME]))
    validate_journal(root, j, before_write=True, planned=planned)
    stage_check(root, j, additions, planned=planned)
    recheck(root, snapshot)
    pub.journal_bytes(j)
    return j


def validate_journal(root, j, *, before_write=False, planned=False):
    exact_keys(j, {"format", "operation", "old", "new", "retained", "additions", "report_run", "replacements"})
    require(j["format"] == tx.registration_format("dependencies") and j["operation"] == "registration", "Unsupported v10 operation")
    require(j["retained"] == {} and j["replacements"] == {} and j["report_run"] is None, "Invalid v10 authority")
    require(all(isinstance(j[k], dict) for k in ("old", "new", "additions")), "Invalid v10 maps")
    require(all(isinstance(n, str) and (v is None or isinstance(v, str)) for side in ("old", "new") for n,v in j[side].items()), "Invalid v10 text")
    require(all(isinstance(j[s].get(n), str) for s in ("old", "new") for n in (tx.REGISTRY, tx.RUNTIME, categories.PATH)), "Missing v10 index")
    require(SHARED <= set(j["old"]) and SHARED <= set(j["new"]), "Missing v10 shared source")
    package, entry = check_new(j, planned=planned)
    require(root.resolve() != cr.ROOT.resolve() or not entry["production"]["test_only"], "Test-only content cannot enter real catalog")
    for n in j["old"]: relative(n); io.safe(root, n)
    for n,h in j["additions"].items(): relative(n); sha(h); io.safe(root,n)
    require(len({n.casefold() for n in set(j["old"]) | set(j["additions"])}) == len(j["old"]) + len(j["additions"]), "Target case collision")
    guard(root, j, old_only=before_write)
    return package, j["old"][tx.RUNTIME]


def stage_check(root, j, additions, *, planned=False):
    """Check the new view by bound bytes, with no old-file copy or reconstruction."""
    require(set(additions) == set(j["additions"]), "Staging addition set differs")
    for n,p in additions.items():
        require(io.file_hash(p.parent,p.name,tx.file_limit(root,n,j)) == j["additions"][n], "Staging addition changed")
    # Full independent verify_export(stage) has already checked exact package
    # files and decoding. This check binds its live outputs to the target view.
    package, entry = check_new(j, planned=planned)
    package_sources = {n[len(package)+1:]: p for n,p in additions.items() if n.startswith(package + "/")}
    require("manifest.json" in package_sources, "Missing staged manifest")
    stage = package_sources["manifest.json"].parent
    from .registration_verification import inventory
    _, hashes = inventory(stage)
    require(hashes == {n[len(package)+1:]:h for n,h in j["additions"].items() if n.startswith(package + "/")}, "Staged package inventory differs")
    manifest = parse(io.read(stage, "manifest.json", 8*1024*1024))
    background_source = j["new"][bg.path(entry["id"])]
    require((manifest.get("format") == "picross-target-export-v6") == (background_source is not None),
            "New package/background source generation differs")
    if background_source is not None:
        require(bg.encoded(bg.build(stage, manifest, None, entry)).decode() == background_source,
                "New background source differs from verified staged production")


def namespace(root, j, temps=()):
    before, after = (parse(j[s][tx.REGISTRY]) for s in ("old", "new"))
    entry = entry_delta(before, after)
    package = entry["production"]["package"]
    allowed = set(j["old"]) | set(j["additions"]) | set(temps)
    dirs = {p.as_posix() for n in allowed for p in Path(n).parents}
    # The canonical optional empty external transport root remains permissible.
    dirs.add(package + "/external")
    base = io.safe(root, package)
    if base.exists():
        require(base.is_dir(), "Registration package root is not a directory")
        for child in base.rglob("*"):
            n = child.relative_to(root).as_posix(); child = io.safe(root,n)
            require(n in (dirs if child.is_dir() else allowed), "Foreign registration package entry: " + n)
    # ID-owned rating subdirectories must not hide foreign children. Shared
    # directories are examined only for colliding names and transaction temps.
    for parent in {Path(n).parent.as_posix() for n in allowed}:
        directory = io.safe(root,parent)
        if not directory.exists(): continue
        for child in directory.iterdir():
            n = child.relative_to(root).as_posix()
            if child.name.casefold().startswith(".registration-"):
                require(n in temps or n in (tx.LOCK, "content/.registration-journal-" + io.checksum(pub.journal_bytes(j)) + ".tmp"), "Foreign registration temporary: " + n)
                io.safe(root,n)
            if parent == "content/difficulty/" + entry["id"]:
                require(n in allowed, "Foreign new rating sidecar: " + n)
                io.safe(root,n)


def guard(root, j, *, raw=None, expected=None, old_only=False, additions=None, _view=None):
    raw = pub.journal_bytes(j) if raw is None else raw
    view = pub._JournalView(j,raw) if _view is None else _view
    if not old_only: require(pub.read_journal(root) == raw, "Journal changed; preserve all transaction files")
    temps = pub.check_temps(root,j,raw,additions=additions,temps=view.temps,restore=view.restore)
    require(not old_only or not temps, "Transaction temporary already exists")
    for n,old in j["old"].items():
        data = tx.read(root,n,j)
        candidates = [old] if old_only else [old,j["new"][n]]
        require(data in [s.encode() if s is not None else None for s in candidates], "Foreign registration source/target: " + n)
        if expected is not None: require(io.checksum(data) == expected[n], "Registration target phase changed: " + n)
    for n,h in j["additions"].items():
        data = io.read(root,n,tx.file_limit(root,n,j),missing=True)
        require(data is None if old_only else data is None or io.checksum(data) == h, "Foreign registration addition: " + n)
        if expected is not None: require(io.checksum(data) == expected[n], "Registration addition phase changed: " + n)
    namespace(root,j,view.temps.values())
    return temps


def checkout(root, j, *, old=False, verification=None, raw=None):
    side = "old" if old else "new"
    require(all(tx.read(root,n,j) == (s.encode() if s is not None else None) for n,s in j[side].items()), "Registration checkout differs")
    indices(j[side])
    if not old:
        package, entry = check_new(j)
        if verification is not None:
            verification.written(root,package,raw)
        else:
            from .target_adapter import verify_export
            verify_export(io.safe(root,package))
        for n,h in j["additions"].items():
            require(tx.file_hash(root,n,j) == h, "Published registration addition differs")
    namespace(root,j,pub.inventory(j,pub.journal_bytes(j)).values())


def repeat_binding(root, registry, entry):
    """Bind just the repeated ID before consuming its comparison sources."""
    from .registration_verification import inventory
    one = selected(registry, entry)
    texts = {n: tx.read(root, n) for n in tx.text_names(one)}
    active = tx.active_reveal(entry, texts)
    backgrounds = bg.projection(one, texts)
    asset = backgrounds[entry["id"]]["asset"]
    live = {active}
    if asset is not None:
        live.add("game/" + asset["file"])
    absent = tx.image_candidates(one) - live
    require(all(tx.read(root, n) is None for n in absent), "Unexpected inactive image of repeated ID")
    raw = texts[added.path(entry["id"])]
    if raw is not None:
        record = added.validate(parse(raw, added.LIMIT), entry["id"])
        evidence = record["provenance"]["evidence"]
        if evidence is not None:
            from .catalog_added_history import validate_plan, record_for
            report = io.read(root, evidence["path"], added.REPORT_LIMIT)
            plan = validate_plan(parse(report, added.REPORT_LIMIT))
            require(io.checksum(report) == evidence["sha256"] and report == encoded(plan) and
                    record_for(plan, entry["id"], report) == record, "Repeated Added evidence differs")
            texts[evidence["path"]] = report
    package = io.safe(root, entry["production"]["package"])
    tree = inventory(package)
    expected_dirs = {"."} | {parent.as_posix() for n in tree[1] for parent in Path(n).parents}
    manifest = parse(io.read(package, "manifest.json", 8*1024*1024))
    if (manifest.get("format") == "picross-target-export-v6" and
            not any(n.startswith("external/") for n in tree[1]) and
            all(manifest["background"][k]["storage"] != "external" for k in ("manifest", "decision", "derivation"))):
        expected_dirs.add("external")
    require(set(tree[0]) <= set(tree[1]) | expected_dirs, "Unexpected repeated package directory")
    return {"texts": texts, "live": {n: tx.file_hash(root, n) for n in live}, "tree": tree}


def check_repeat(root, snapshot, entry):
    """Fresh selected-ID audit; unrelated old files never become dependencies."""
    registry, catalog, runtime = indices(snapshot["texts"])
    one = selected(registry, entry)
    binding = snapshot["repeat"]
    texts = binding["texts"]
    expected = parse(tx.projection({n: b.decode() if b is not None else None for n,b in texts.items()}, one, version=8))
    require(expected["entries"][0] == next(r for r in runtime["entries"] if r["id"] == entry["id"]), "Repeated runtime is stale")
    cr._check_entry(root, registry, catalog, entry, image_runtime=True)
    require(repeat_binding(root, registry, entry) == binding, "Repeated sources changed")
    recheck(root, snapshot)
