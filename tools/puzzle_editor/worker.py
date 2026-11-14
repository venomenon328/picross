"""Trusted subprocess entry. The selected checkout is data, never an import path."""
from pathlib import Path
import json
import sys
import time

from tools.puzzle_production import catalog_io as io, content_registry, editor_image_input
from tools.puzzle_production import target_adapter, editor_change
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import digest
from tools.puzzle_production import operation_diagnostics as diagnostic


def run(root, work, action, body, state=None):
    from tools.puzzle_production import editor_change as change
    import base64
    with io.budget(300):
        root, work = io.external(root), io.external(work)
        if action == "detail":
            return change.detail(root, body["id"], body["snapshot"])
        if action == "recover":
            if not change.pending(root): return {"status": "noop", "registered": False}
            return content_registry.recover(root)
        if action == "validate_upload":
            raw = io.read(work, body["file"], 32*1024*1024)
            checked = (editor_image_input.validate_background(raw) if body["kind"] == "background" else
                       editor_image_input.validate_reveal(raw, Path(body["file"]).suffix))
            if state is not None:
                state["plan"] = None
                state["uploads"][body["kind"]] = {"file": body["file"], "raw": raw,
                    "suffix": Path(body["file"]).suffix[1:], "checked": checked, "created": time.monotonic()}
            return checked
        if action == "apply":
            require(state is not None and state.get("plan") is not None, "Prepared plan no longer available; prepare again")
            prepared = state["plan"]
            require(prepared["work"] == work and time.monotonic()-prepared["created"] <= 600 and
                    prepared["value"]["plan_hash"] == body["plan_hash"], "Prepared plan binding expired/differs")
            result = change.apply(root, prepared["value"])
            state["plan"] = None
            return result
        require(action == "plan", "Unsupported editor action")
        require(state is not None, "Editor planning requires its local prepared-input session")
        state["plan"] = None
        uploads = {}
        for key, item in body.get("uploads", {}).items():
            candidate = next((row for row in state["uploads"].values() if row["file"] == item["file"]), None)
            require(candidate is not None and time.monotonic()-candidate["created"] <= 900 and
                    candidate["checked"]["sha256"] == item["sha256"], "Prepared input no longer available")
            uploads[key] = candidate
        plan = change.plan(root, body.get("request"), uploads=uploads, work=work,
                           expected=body["catalog_snapshot"], expected_definition=body.get("definition_sha256"))
        state["plan"] = {"value": plan, "work": work, "created": time.monotonic()}
        return {"plan_hash": plan["plan_hash"], "kind": plan["action"], "files": sorted(plan["changes"]), "before": plan["before"],
                "after": plan["after"], "quality": plan["quality"], "logic_changed": plan["quality"] is not None}


def main(path, state=None):
    path = io.external(path)
    job = io.json_bytes(io.read(path.parent, path.name, 96*1024*1024), 96*1024*1024)
    from .progress import Progress, public_error, state as observed_state
    root = Path(job["root"])
    observation = Progress(job["action"], path.parent)
    with diagnostic.observe(observation):
        try:
            result = run(root, Path(job["work"]), job["action"], job["body"], state)
            response = {"result": result, "error": None}
        except Exception as exc:
            phase = getattr(observation, "failure_phase", None) or observation.last_stage or job["action"]
            response = {"result": None, "error": public_error(exc, root, path.parent) +
                        " · Phase: " + phase + " · " + observed_state(root)}
    response["diagnostics"] = observation.summary()
    temporary = path.parent/"result.tmp"
    temporary.write_bytes(editor_change.encoded(response))
    temporary.replace(path.parent/"result.json")


def loop(directory):
    directory = io.external(directory)
    state = {"plan": None, "uploads": {}}
    for line in sys.stdin:
        name = line.strip()
        if name == "stop": return
        path = io.external(name)
        require(path.is_relative_to(directory) and path.name == "job.json", "Foreign session request")
        main(path, state)


if __name__ == "__main__": main(sys.argv[1])
