"""One integration core shared by CLI, assistant and batch."""
from copy import deepcopy
from pathlib import Path
from . import current_content as content, current_registration as transaction
from . import catalog_rating as rating, catalog_added as added, catalog_method, categories
from . import catalog_io as io, operation_diagnostics as diagnostic
from .integration_input import Input
from .authoring_package import require


def rating_result(value):
    """Current assessment, excluding how the assessment was produced."""
    return {key: value[key] for key in ("current_source", "logic_binding", "production_mode")} | {"rating": value["rating"], "compact_analysis": value["compact_analysis"]}


def same(current, incoming):
    value = incoming.value
    return (current["entry"] == incoming.entry and current["definition"] == incoming.definition_raw and
            current["metadata"] == value["metadata"] and current["reveal_bytes"] == incoming.reveal["asset"] and
            current["notice"] == incoming.reveal["notice"] and
            current["background"]["current"]["status"] == value["background"]["status"] and
            (incoming.background is None or
             current.get("background_bytes") == incoming.background["asset"] and
             current.get("background_notice") == incoming.background["notice"]) and
            rating_result(current["rating"]) == rating_result(incoming.checked))


@diagnostic.measured("Input/Plan")
def integrate(export_dir, root, *, apply=False, fail_step=None, publication_seconds=None, recovery_seconds=None):
    diagnostic.seconds(publication_seconds); diagnostic.seconds(recovery_seconds)
    require(apply or publication_seconds is None and recovery_seconds is None, "Publication budgets require writing")
    incoming = Input(export_dir)
    from .content_registry import ROOT
    require(not incoming.value["test_only"] or Path(root).resolve() != ROOT.resolve(), "Test-only input cannot enter product catalog")
    entry = incoming.entry
    snapshot = transaction.Snapshot(root, entry["id"])
    from .catalog_background import capability, image_profile
    capability(snapshot.root, snapshot.raw, required=incoming.value["background"]["status"] in ("none", "selected"),
               profile_id=image_profile(incoming.background["asset"]) if incoming.background else None)
    category = categories.lookup(snapshot.catalog, incoming.value["metadata"]["category_id"])
    if snapshot.existing is not None:
        require(same(snapshot.delivery, incoming), "Occupied ID differs; use the explicit revision operation")
        incoming.recheck(); snapshot.recheck()
        return {"status": "no-op", "registered": True, "id": entry["id"], "changes": [], "category": category}
    method_record = catalog_method.from_bytes(snapshot.raw[catalog_method.PATH])
    require(rating.method(incoming.checked) == catalog_method.current(method_record)["method"], "New input requires current difficulty method")
    value = deepcopy(snapshot.registry)
    value["entries"].append(entry); value["entries"].sort(key=lambda e: e["id"])
    value["metadata"].append(incoming.value["metadata"]); value["metadata"].sort(key=lambda e: e["id"])
    raw = incoming.definition_raw
    reveal = content.source(entry, raw, {"image_revision": 1, "asset": content.ref("game/"+entry["reveal"], incoming.reveal["asset"])}, "reveal")
    background = content.source(entry, raw, {"image_revision": 1, "status": incoming.value["background"]["status"],
        "asset": content.ref("game/art/backgrounds/"+entry["id"]+".png", incoming.background["asset"]) if incoming.background else None}, "background")
    background_name = content.source_path(entry["id"], "background")
    value["backgrounds"].append({"id": entry["id"], "source": content.ref(background_name, content.encoded(background))})
    value["backgrounds"].sort(key=lambda e: e["id"])
    content.validate(value, snapshot.catalog)
    active = rating.active_record(incoming.checked)
    # Planning uses no timestamp and writes nothing. Apply builds this anew.
    date = added.registration(entry["id"]) if apply else {"added_at": None}
    delivery = {"entry": entry, "metadata": incoming.value["metadata"], "reveal": reveal, "background": background,
                "rating": active, "added": date}
    runtime = deepcopy(snapshot.runtime)
    runtime["entries"].append(content.runtime_row(delivery)); runtime["entries"].sort(key=lambda e: e["id"])
    changes = {content.REGISTRY: content.encoded(value), content.RUNTIME: content.encoded(runtime),
               "game/"+entry["definition"]: raw, "game/"+entry["reveal"]: incoming.reveal["asset"],
               content.notice_path(entry): incoming.reveal["notice"],
               rating.path(entry["id"]): rating.encoded(active),
               content.source_path(entry["id"], "reveal"): content.encoded(reveal),
               background_name: content.encoded(background)}
    if incoming.background:
        changes["game/art/backgrounds/"+entry["id"]+".png"] = incoming.background["asset"]
        changes["game/art/backgrounds/"+entry["id"]+".txt"] = incoming.background["notice"]
    for name in set(changes) - {content.REGISTRY, content.RUNTIME}:
        require(snapshot.read(name, missing=True) is None, "Occupied current path: "+name)
    require(snapshot.read(added.path(entry["id"]), missing=True) is None, "Occupied added date")
    incoming.recheck(); snapshot.recheck()
    plan = {"status": "planned", "registered": False, "id": entry["id"], "category": category,
            "changes": [{"path": n, "operation": "replace" if n in (content.REGISTRY, content.RUNTIME) else "add"} for n in sorted(changes)] +
                       [{"path": added.path(entry["id"]), "operation": "add-on-success"}],
            "user_saves_modified": False}
    if not apply: return plan
    changes[added.path(entry["id"])] = added.encoded(date)
    journal = transaction.prepare(snapshot, changes)
    incoming.recheck()
    result = transaction.execute(snapshot, journal, publication_seconds=publication_seconds,
                                 recovery_seconds=recovery_seconds, fail_step=fail_step, source_check=incoming.recheck)
    return {**plan, **result}


def reached(export_dir, root):
    """Batch completion and resume use the same selected-ID validation."""
    result = integrate(export_dir, root)
    return result["status"] == "no-op"
