"""Trusted subprocess entry. The selected checkout is data, never an import path."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

from tools.puzzle_production import catalog_io as io, catalog_transaction as tx
from tools.puzzle_production import catalog_metadata as metadata, catalog_images as images
from tools.puzzle_production import catalog_raster as raster, content_registry, editor_image_input
from tools.puzzle_production import editor_raster, target_adapter
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import digest
from tools.puzzle_production import operation_diagnostics as diagnostic


def snapshot(root):
    return digest(tx.image_snapshot(tx.capture(root)))


def run(root, work, action, body):
    with io.budget(300):
        root, work = io.external(root), io.external(work)
        if action == "detail":
            captured = tx.capture_detail(root, body["id"])
            sources = tx.image_snapshot(captured)
            before = digest(sources)
            # Both projections are pure: no second filesystem observation can
            # replace a part of this already checked, consistent source view.
            with diagnostic.phase("Selected puzzle"):
                value = images.view_from_snapshot(captured, body["id"])
                grid = raster.view_from_snapshot(captured, body["id"])
            row = value["runtime"]
            names = ["game/"+row["reveal"]]
            if row["background"]["status"] == "selected": names.append("game/"+row["background"]["asset"]["file"])
            return {"detail": value, "raster": grid, "snapshot": before,
                    "_resources": {name: sources["sources"][name] for name in names}}
        if action == "recover":
            from .server import pending
            if not pending(root):
                content_registry.check_checkout(root)
                return {"status": "noop", "registered": False}
            return content_registry.recover(root)
        if action == "validate_upload":
            path = io.safe(work, body["file"])
            if body["kind"] == "background":
                return editor_image_input.validate_background(io.read(work, body["file"], 32*1024*1024))
            target_adapter.validate_reveal(path, 1, 1)
            return {"valid": True}
        if action == "apply":
            kind = body["kind"]
            plan = io.json_bytes(io.read(work, "plan.json", 32*1024*1024), 32*1024*1024)
            if kind == "metadata": result = metadata.apply(root, plan)
            elif kind == "migration": result = images.apply_migration(root, plan)
            elif kind == "images": result = images.apply(root, work/"bundle/plan.json")
            elif kind == "raster": result = raster.apply(root, work/"bundle")
            else: raise ValueError("Unknown internal plan kind")
            with diagnostic.phase("Readback"):
                from .server import catalog, pending
                require(not pending(root), "Recovery erforderlich; noch keine vollständige Übernahmequittung.")
                actual = catalog(root)
                if kind == "migration":
                    require(actual["runtime_format"] == content_registry.IMAGE_RUNTIME_FORMAT,
                            "Migration ohne bestätigten v8-Readback. Neu laden und Journal prüfen.")
            return result
        if body.get("catalog_snapshot") is not None:
            from .server import catalog
            require(catalog(root)["snapshot"] == body["catalog_snapshot"], "Katalog während Prüfstart geändert.")
        if action == "migration":
            plan = images.plan_migration(root)
            kind = "migration"
        else:
            captured = None
            if body["bound_snapshot"] is not None:
                captured = tx.capture(root)
                require(digest(tx.image_snapshot(captured)) == body["bound_snapshot"], "Auswahl ist veraltet. Neu laden und erneut prüfen.")
            item = body["request"]
            if item["id"] is None:
                plan, kind = metadata.plan(root, item["metadata"]), "metadata"
            elif item["text"] is None and item["reveal"] is None and item["background"] is None:
                operation = {"op": "set_metadata", "id": item["id"], **(item["metadata"] or {})}
                require(len(operation) > 2, "Keine Änderungen ausgewählt.")
                plan, kind = metadata.plan(root, [operation], _snapshot=captured), "metadata"
            else:
                authority = item["authority"]
                require(isinstance(authority, dict) and authority["confirmed"] is True,
                        "Manuelle Entscheidung bitte ausdrücklich bestätigen.")
                decision = {"actor": authority["actor"], "statement": authority["statement"],
                            "timestamp_utc": body["confirmed_at"]}
                request = {"format": images.REQUEST, "id": item["id"], "metadata": item["metadata"],
                           "reveal": item["reveal"], "background": item["background"], "decision": decision}
                if item["text"] is not None:
                    request.update(format=editor_raster.REQUEST, text=item["text"],
                                   provenance=authority["provenance"], profile=item["profile"])
                    kind = "raster"
                else: kind = "images"
                inputs = work/"inputs"
                inputs.mkdir()
                for name, raw in body["uploads"].items():
                    # These bytes are copied by the parent after a fresh bounded hash check.
                    import base64
                    (inputs/name).write_bytes(base64.b64decode(raw, validate=True))
                (inputs/"request.json").write_bytes(images.encoded(request))
                plan = (raster if kind == "raster" else images).plan(root, inputs/"request.json", work/"bundle", _snapshot=captured)
        (work/"plan.json").write_bytes(images.encoded(plan))
        before, after = plan.get("old"), plan.get("new")
        if kind == "metadata": before, after = plan["changes"], plan["changes"]
        if kind == "raster":
            logic_changed = before["definition"]["revision"] != after["definition"]["revision"]
        else: logic_changed = False
        return {"kind": kind, "files": plan["files"], "before": before, "after": after,
                "quality": plan.get("quality"), "logic_changed": logic_changed}


def main(path):
    path = io.external(path)
    job = io.json_bytes(io.read(path.parent, path.name, 96*1024*1024), 96*1024*1024)
    from .progress import Progress, public_error, state
    root = Path(job["root"])
    observation = Progress(job["action"], path.parent)
    with diagnostic.observe(observation):
        try:
            result = run(root, Path(job["work"]), job["action"], job["body"])
            response = {"result": result, "error": None}
        except Exception as exc:
            phase = getattr(observation, "failure_phase", None) or observation.last_stage or job["action"]
            response = {"result": None, "error": public_error(exc, root, path.parent) +
                        " · Phase: " + phase + " · " + state(root)}
    response["diagnostics"] = observation.summary()
    (path.parent/"result.json").write_bytes(images.encoded(response))


if __name__ == "__main__": main(sys.argv[1])
