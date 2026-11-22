"""Synthetic black-box acceptance run against two private Compose projects."""

import concurrent.futures
import copy
import http.client
import json
import os
import secrets
import subprocess
import sys
import threading
import time
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

HERE = Path(__file__).resolve().parent


def compact(obj):
    return json.dumps(obj, separators=(",", ":")).encode()


def run(args, env, **options):
    return subprocess.run(args, cwd=HERE, env=env, check=True, **options)


class Project:
    def __init__(self, name, image, password):
        self.env = dict(
            os.environ, COMPOSE_PROJECT_NAME=name, SYNC_DB_PASSWORD=password, SYNC_PORT="0", SYNC_IMAGE=image
        )
        self.port = None

    def compose(self, *args, capture=False):
        proc = run(["docker", "compose", *args], self.env, capture_output=capture, text=True)
        return proc.stdout.strip() if capture else None

    def up(self, *options):
        self.compose("up", "-d", "--wait", *options)
        self.port = int(self.compose("port", "api", "8000", capture=True).split(":")[-1])

    def admin(self, *args):
        return self.compose("exec", "-T", "api", "python", "-m", "sync.admin", *args, capture=True)

    def sql(self, statement):
        return self.compose(
            "exec",
            "-T",
            "db",
            "psql",
            "-XAt",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            "picross",
            "-c",
            statement,
            capture=True,
        )

    def archive(self, operation, path, success=True):
        proc = subprocess.run(
            [sys.executable, "db_archive.py", operation, str(path)],
            env=self.env,
            cwd=HERE,
            check=False,
            capture_output=True,
        )
        if (proc.returncode == 0) != success:
            # Diagnostic identifiers only; archive rows and stderr may contain private data.
            errors = proc.stderr.decode(errors="replace").splitlines()
            category = next(
                (
                    code
                    for line in errors
                    if "ERROR:" in line
                    if (code := line.partition("ERROR:")[2].strip()).isalnum() and len(code) == 5
                ),
                "archive process",
            )
            raise AssertionError(f"{operation} returned {proc.returncode}: {category}")

    def down(self):
        self.compose("down", "--volumes", "--remove-orphans")


@dataclass
class Response:
    status: int
    raw: bytes
    generation: str | None
    headers: dict

    @property
    def body(self):
        return json.loads(self.raw) if self.raw else None


class Client:
    def __init__(self, project, name):
        self.project, self.name = project, name
        self.token = self.device = self.generation = self.code = None
        self.password = secrets.token_urlsafe(24)

    def http(self, method, path, body=None, status=200, headers=None, drop=False):
        data = body if isinstance(body, bytes) or body is None else compact(body)
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.generation:
            h["X-Picross-Generation"] = self.generation
        h.update(headers or {})
        conn = http.client.HTTPConnection("127.0.0.1", self.project.port, timeout=30)
        try:
            conn.request(method, path, body=data, headers=h)
            if drop:
                # Observe commit over a second transport, then close the first socket
                # without receiving even the status line. No test hook in the service.
                deadline = time.monotonic() + 15
                expected = json.loads(data)["request_seq"]
                while self.get("account")["last_request_seq"] != expected:
                    if time.monotonic() >= deadline:
                        raise AssertionError("Commit was not observed before disconnect")
                    time.sleep(0.02)
                return None
            res = conn.getresponse()
            result = Response(
                res.status, res.read(), res.getheader("X-Picross-Generation"), dict(res.getheaders())
            )
            assert res.getheader("Cache-Control") == "no-store"
            if path.startswith("/v1/"):
                assert result.generation
            if status is not None and result.status != status:
                code = result.body.get("code") if isinstance(result.body, dict) else None
                raise AssertionError(
                    f"{method} {path.split('?')[0]} expected {status}, got {result.status} ({code})"
                )
            return result
        finally:
            conn.close()

    def bind(self, response):
        data = response.body
        self.token, self.device, self.generation = data["token"], data["device_id"], response.generation
        if data["recovery_code"]:
            self.code = data["recovery_code"]

    def register(self):
        body = {
            "username": self.name,
            "password": self.password,
            "device_name": "synthetic",
            "invitation": self.project.admin("invite"),
        }
        self.bind(self.http("POST", "/v1/auth/register", body, 201))
        return body

    def login(self, status=200):
        res = self.http(
            "POST",
            "/v1/auth/login",
            {
                "username": self.name,
                "password": self.password,
                "device_id": self.device,
                "device_name": "technical client",
            },
            status,
        )
        if status == 200:
            self.bind(res)
        return res

    def get(self, path, status=200):
        return self.http("GET", "/v1/" + path, status=status).body

    def put(self, puzzle, seq, base, op, status=200, **fields):
        return self.http("POST", f"/v1/puzzles/{puzzle}/mutations", mutation(seq, base, op, **fields), status)


def mutation(seq, base, op, **fields):
    return dict(format="picross-sync/v1", request_seq=seq, base_server_revision=base, operation=op, **fields)


def save(puzzle, revision=1):
    return {
        "schema": 1,
        "definition_id": puzzle,
        "definition_revision": revision,
        "width": 2,
        "height": 1,
        "cells": [91, -1],
        "history": [[{"index": 0, "before": -1, "after": 91}], [{"index": 1, "before": -1, "after": 0}]],
        "cursor": 1,
        "undo_used": True,
        "completed": False,
        "view": {
            "center": [1, 0.5],
            "zoom": 20,
            "overview": False,
            "active_color": 91,
            "tool": "fill",
            "row_clue_reads": [{"anchor": "grid_end"}],
            "column_clue_reads": [{"anchor": "outer_start"}, {"anchor": "grid_end"}],
        },
    }


def service(p, a):
    p.up("--build")
    assert p.compose("port", "api", "8000", capture=True).startswith("127.0.0.1:")
    ports = json.loads(p.compose("ps", "--format", "json", "db", capture=True))
    if isinstance(ports, list):
        ports = ports[0]
    assert not any(x.get("PublishedPort") for x in (ports.get("Publishers") or []))
    p.admin("migrate")
    for health in ("live", "ready"):
        assert a.http("GET", "/health/" + health).body == {"status": "ok"}
    api = a.http("GET", "/openapi.json").body
    assert len(api["paths"]) == 15 and api["components"]["schemas"]["Save"]["additionalProperties"] is False
    print("PostgreSQL", p.sql("SHOW server_version"), flush=True)


def access(p, a, foreign):
    body = a.register()
    a.http("POST", "/v1/auth/register", dict(body, username="other"), 409)
    foreign.register()
    alien = Client(p, foreign.name)
    alien.password, alien.device = foreign.password, a.device
    alien.login(401)
    a.put("private", 1, 0, "snapshot", save=save("private"))
    assert foreign.get("puzzles")["items"] == []
    foreign.get("puzzles/private", 404)
    assert foreign.put("private", 1, 1, "reset", 409, definition_revision=1).body["code"] == "conflict_saved"
    assert a.get("puzzles/private")["save"] == save("private")
    revoked = copy.copy(a)
    a.http("POST", "/v1/auth/logout", status=204)
    revoked.get("puzzles", 401)
    revoked.put("private", 2, 1, "reset", 401, definition_revision=1)
    a.login()
    p.sql("UPDATE devices SET expires_at=now()-interval '1 second' WHERE device_id='" + a.device + "'")
    a.get("account", 401)
    a.login()
    guest = copy.copy(a)
    guest.token = None
    guest.get("puzzles", 401)
    guest.put("private", 2, 1, "reset", 401, definition_revision=1)
    expired = p.admin("invite")
    p.sql("UPDATE invitations SET expires_at=now()")
    a.http("POST", "/v1/auth/register", dict(body, username="unused", invitation=expired), 409)
    unknown = Client(p, "unknown")
    for _ in range(10):
        unknown.login(401)
    limited = unknown.login(429)
    assert limited.body == {"code": "rate_limited"} and int(limited.headers["retry-after"]) > 0
    p.env["SYNC_AUTH_IP"] = "2"
    p.up()
    assert Client(p, "another-name").login(429).body["code"] == "rate_limited"
    p.env["SYNC_AUTH_IP"] = "100"
    p.up()


def recovery(a, b):
    b.password = a.password
    b.login()
    original = a.code
    args = {"username": a.name, "recovery_code": original, "new_password": secrets.token_urlsafe(24)}
    a.code = a.http("POST", "/v1/auth/recover", args).body["recovery_code"]
    a.get("account", 401)
    b.get("account", 401)
    a.http("POST", "/v1/auth/recover", args, 401)
    a.password = b.password = args["new_password"]
    a.login()
    assert a.get("account")["last_request_seq"] == 1
    assert a.get("puzzles/private")["save"] == save("private")
    # The low default was tested above; allow the remaining recovery/rotation cases.
    a.project.env["SYNC_AUTH_NAME"] = "200"
    a.project.up()
    a.http("POST", "/v1/auth/recovery-code", {"password": "wrong-password"}, 401)
    replaced = a.code
    a.code = a.http("POST", "/v1/auth/recovery-code", {"password": a.password}).body["recovery_code"]
    a.http("POST", "/v1/auth/recover", dict(args, recovery_code=replaced), 401)
    b.login()


def validation(a):
    path = "/v1/puzzles/check/mutations"
    good = mutation(2, 0, "snapshot", save=save("check"))
    for raw, status in (
        (b'{"x":0,"x":1}', 400),
        (b"\xff", 400),
        (b"NaN", 400),
        (b" " * ((16 << 20) + 1), 413),
    ):
        a.http("POST", path, raw, status)
    a.http("POST", "/v1/auth/login", b" " * 16385, 413)
    a.http("POST", path, good, 415, {"Content-Type": "text/plain"})
    a.http("POST", path, good, 422, {"X-Picross-Generation": "bad"})
    a.http("POST", path, good, 409, {"X-Picross-Generation": str(uuid4())})
    for target, value in (
        (["format"], "v2"),
        (["extra"], 0),
        (["request_seq"], True),
        (["save", "schema"], 2),
        (["save", "definition_id"], "other"),
        (["save", "width"], 51),
        (["save", "cells"], [-1, -1]),
        (["save", "history", 1, 0, "before"], 0),
        (["save", "history", 0], [{"index": 0, "before": -1, "after": 91}] * 2),
        (["save", "cursor"], 3),
        (["save", "undo_used"], False),
        (["save", "view", "zoom"], 1),
        (["save", "view", "center"], [-1, 0]),
        (["save", "view", "row_clue_reads"], []),
        (["save", "view", "column_clue_reads", 0], {"anchor": "middle", "start": 1, "end": 2}),
        (["save", "completed"], 1),
        (["save", "history"], None),
    ):
        body = copy.deepcopy(good)
        node = body
        for part in target[:-1]:
            node = node[part]
        node[target[-1]] = value
        a.http("POST", path, body, 422)
    palette = copy.deepcopy(good)
    palette["save"]["history"] += [
        [{"index": 0, "before": 91 if color == 1 else color - 1, "after": color}] for color in range(1, 9)
    ]
    a.http("POST", path, palette, 422)
    assert a.get("account")["last_request_seq"] == 1
    a.get("puzzles/check", 404)
    assert a.http("POST", path, good).body["sequence_consumed"]
    assert a.get("puzzles/check")["validation"] == "schema_history_checked"


def competition(a, b):
    gate = threading.Barrier(2)

    def write(client, seq, value):
        snapshot = save("race")
        snapshot["view"]["overview"] = value
        gate.wait(timeout=15)
        return client.put("race", seq, 0, "snapshot", None, save=snapshot)

    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        jobs = [pool.submit(write, a, 3, True), pool.submit(write, b, 1, False)]
        results = sorted((job.result() for job in jobs), key=lambda r: r.status)
    assert [r.status for r in results] == [200, 409]
    cid = results[1].body["candidate_id"]
    assert results[1].body["code"] == "conflict_saved" and cid
    old = a.get("puzzles/race")
    other = a.get("puzzles/race/conflicts/" + cid)
    assert old["save"]["view"]["overview"] != other["save"]["view"]["overview"]
    assert a.put("race", 4, 0, "resolve", 409, candidate_id=cid).body["code"] == "revision_conflict"
    assert a.put("check", 5, 1, "discard", 409, candidate_id=cid).body["code"] == "candidate_missing"
    assert a.get("puzzles/race") == old
    assert a.put("race", 6, 1, "resolve", candidate_id=cid).body["candidate_id"] == cid
    assert a.get("puzzles/race")["save"] == other["save"]
    assert a.get("puzzles/race/history/1") == old


def retry(a):
    path = "/v1/puzzles/race/mutations"
    raw = compact(mutation(7, 2, "reset", definition_revision=1))
    a.http("POST", path, raw, drop=True)
    assert a.get("account")["last_request_seq"] == 7
    result = a.http("POST", path, raw)
    a.login()
    assert a.http("POST", path, raw).raw == result.raw
    assert a.http("POST", path, raw + b" ", 409).body["code"] == "sequence_reused"
    assert a.put("race", 9, 3, "reset", 409, definition_revision=1).body["code"] == "sequence_gap"
    assert a.get("puzzles/race")["server_revision"] == 3
    assert len(a.get("puzzles/race/history")["items"]) == 2


def reset(a, b):
    p = a.project
    generation = a.generation
    p.compose("stop")
    p.up()
    assert a.get("puzzles/race")["kind"] == "reset"
    assert a.http("GET", "/v1/account").generation == generation
    for seq, base, rev in ((2, 2, 1), (3, 3, 2)):
        result = b.put("race", seq, base, "snapshot", 409, save=save("race", rev))
        assert result.body["code"] == "conflict_saved"
    assert a.get("puzzles/race")["server_revision"] == 3
    assert len(a.get("puzzles/race/conflicts")["items"]) == 2


def limits(a, b, foreign):
    for seq in range(8, 20):
        a.put("race", seq, seq - 5, "reset", definition_revision=1)
    history = a.get("puzzles/race/history")["items"]
    assert [row["server_revision"] for row in history] == list(range(14, 4, -1))
    assert a.put("race", 20, 15, "restore", 409, history_revision=1).body["code"] == "history_missing"
    assert a.put("race", 21, 15, "restore", history_revision=5).body["server_revision"] == 16
    assert a.put("race", 7, 2, "reset", 409, definition_revision=1).body["code"] == "sequence_stale"
    for seq in range(4, 7):
        assert b.put("race", seq, 0, "snapshot", 409, save=save("race")).body["candidate_id"]
    assert b.put("race", 7, 0, "reset", 409, definition_revision=1).body["code"] == "conflict_limit"
    page = a.get("puzzles?limit=1")
    cursor = quote(page["next_cursor"])
    assert a.get("puzzles?limit=1&cursor=" + cursor)["items"][0]["puzzle_id"] > page["items"][0]["puzzle_id"]
    foreign.get("puzzles?cursor=" + cursor, 422)
    a.get("puzzles/race/history?cursor=" + cursor, 422)
    a.get("puzzles?offset=0", 422)
    p = a.project
    p.env.update(SYNC_BYTES="1", SYNC_DEVICES="1")
    p.up()
    fresh = Client(p, a.name)
    fresh.password = a.password
    fresh.login(409)
    b.login()
    body = mutation(22, 0, "snapshot", save=save("over"))
    res = a.http("POST", "/v1/puzzles/over/mutations", body, 409)
    assert res.body["code"] == "storage_limit" and res.body["sequence_consumed"]
    assert a.http("POST", "/v1/puzzles/over/mutations", body, 409).raw == res.raw
    a.get("puzzles/over", 404)
    # Exercise puzzle count independently from the byte quota.
    p.env.update(SYNC_BYTES=str(512 << 20), SYNC_PUZZLES="1")
    p.up()
    assert b.put("new-puzzle", 8, 0, "reset", 409, definition_revision=1).body["code"] == "storage_limit"
    b.get("puzzles/new-puzzle", 404)
    cid = a.get("puzzles/race/conflicts")["items"][0]["candidate_id"]
    assert a.put("race", 23, 16, "discard", candidate_id=cid).body["outcome"] == "discarded"
    assert len(a.get("puzzles/race/conflicts")["items"]) == 4
    assert a.get("puzzles/race")["server_revision"] == 16


def archive(a, b, restored, work):
    p = a.project
    saved = {
        path: a.get(path)
        for path in (
            "puzzles",
            "puzzles/private",
            "puzzles/check",
            "puzzles/race",
            "puzzles/race/history",
            "puzzles/race/conflicts",
        )
    }
    cid = saved["puzzles/race/conflicts"]["items"][0]["candidate_id"]
    saved["puzzles/race/conflicts/" + cid] = a.get("puzzles/race/conflicts/" + cid)
    invite = p.admin("invite")
    backup = work / "synthetic.dump"
    p.archive("backup", backup)
    restored.compose("up", "-d", "--wait", "db")
    bad = work / "partial.dump"
    bad.write_bytes(backup.read_bytes()[:100])
    restored.archive("restore", bad, False)
    assert restored.sql("SELECT to_regclass('public.instance') IS NULL") == "t"
    # Fail inside the final access-revocation transaction, after the whole archive
    # has loaded. A source-only synthetic constraint makes that UPDATE fail.
    blocked = work / "lockdown-failure.dump"
    p.sql("ALTER TABLE accounts ADD CONSTRAINT synthetic_lock_check CHECK (NOT locked)")
    try:
        p.archive("backup", blocked)
    finally:
        p.sql("ALTER TABLE accounts DROP CONSTRAINT synthetic_lock_check")
    restored.archive("restore", blocked, False)
    assert restored.sql("SELECT to_regclass('public.accounts') IS NULL") == "t"
    restored.archive("restore", backup)
    restored.archive("restore", backup, False)
    restored.up("--no-build")
    client = copy.copy(a)
    client.project = restored
    res = client.http("GET", "/v1/account", status=409)
    assert res.body["code"] == "server_generation_changed" and res.generation != a.generation
    client.generation = res.generation
    client.get("account", 401)
    client.login(401)
    client.http(
        "POST",
        "/v1/auth/register",
        {"username": "restored", "password": a.password, "device_name": "new", "invitation": invite},
        409,
    )
    change = {"username": a.name, "new_password": secrets.token_urlsafe(24), "recovery_code": a.code}
    client.http("POST", "/v1/auth/recover", change, 401)
    change["recovery_code"] = restored.admin("restore-code", a.name)
    client.http("POST", "/v1/auth/recover", change)
    client.http("POST", "/v1/auth/recover", change, 401)
    client.password = change["new_password"]
    client.login()
    assert client.get("account")["last_request_seq"] == 23
    assert (
        client.put("race", 24, 16, "reset", 409, definition_revision=1).body["code"]
        == "server_generation_changed"
    )
    for path, original in saved.items():
        assert client.get(path) == original
    second = copy.copy(b)
    second.project, second.password = restored, client.password
    second.login()
    assert second.get("account")["last_request_seq"] == 8
    assert client.put("race", 7, 2, "reset", 409, definition_revision=1).body["code"] == "sequence_stale"
    assert client.put("race", 24, 16, "reset", definition_revision=1).body["server_revision"] == 17


def main():
    if not __debug__:
        raise RuntimeError("Checks require normal Python assertion mode")
    report = Path(sys.argv[1]).resolve()
    group = "picross-sync-test-" + uuid4().hex[:12]
    image = group + ":local"
    p, restored = (Project(group + suffix, image, secrets.token_urlsafe(32)) for suffix in ("", "-restore"))
    a, b, foreign = Client(p, "primary"), Client(p, "primary"), Client(p, "foreign")
    rows = {}
    scenarios = [
        (service, (p, a)),
        (access, (p, a, foreign)),
        (recovery, (a, b)),
        (validation, (a,)),
        (competition, (a, b)),
        (retry, (a,)),
        (reset, (a, b)),
        (limits, (a, b, foreign)),
        (archive, (a, b, restored, report.parent)),
    ]
    with ExitStack() as stack:
        stack.callback(lambda: subprocess.run(["docker", "image", "rm", image], check=False))
        stack.callback(p.down)
        stack.callback(restored.down)
        for n, (test, args) in enumerate(scenarios, 1):
            key = f"SYNC-A-{n:02}"
            test(*args)
            rows[key] = "passed"
            print(key, test.__name__, "passed", flush=True)
    binding = {
        "source_head": os.environ["P1_PREFLIGHT_SOURCE_COMMIT"],
        "base_commit": os.environ["P1_BASE_COMMIT"],
        "tested_checkout": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
        "run_attempt": os.environ["CI_SELECTION_ATTEMPT"],
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
    }
    report.write_text(json.dumps({"binding": binding, "results": rows}), encoding="utf-8")


if __name__ == "__main__":
    main()
