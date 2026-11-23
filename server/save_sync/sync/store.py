"""Account lock held by caller throughout reads, comparison, rotation and receipt."""

import base64
import hashlib
import hmac
import json

from fastapi.responses import Response

from .db import Failure, quota, stamp

VERSION = " FROM versions WHERE account_id=%s AND puzzle_id=%s"
CANDIDATE = " FROM candidates WHERE account_id=%s AND puzzle_id=%s"
META = "puzzle_id, definition_revision, device_id, device_name, CASE WHEN save IS NULL THEN 'reset' ELSE 'snapshot' END AS kind"
VMETA = META + ", server_revision, updated_at"
CMETA = META + ", base_server_revision, candidate_id, created_at"


def export(row, *, full=False):
    if row is None:
        raise Failure(404, "not_found")
    result = dict(row)
    for key in ("created_at", "updated_at"):
        if key in result:
            result[key] = stamp(result[key])
    for key in ("candidate_id", "device_id"):
        if key in result:
            result[key] = str(result[key])
    if full:
        if result["save"] is not None:
            result["save"] = json.loads(result["save"])
        result["validation"] = "progress_structure_checked" if result["kind"] == "snapshot" else None
    return result


def version(db, key, revision=None):
    if revision is None:
        suffix = " ORDER BY server_revision DESC LIMIT 1"
    else:
        suffix = " AND server_revision=%s AND server_revision < (SELECT server_revision FROM puzzles WHERE account_id=%s AND puzzle_id=%s)"
        key = (*key, revision, *key)
    return export(db.execute("SELECT " + VMETA + ",save" + VERSION + suffix, key).fetchone(), full=True)


def candidate(db, key, cid):
    return export(
        db.execute("SELECT " + CMETA + ",save" + CANDIDATE + " AND candidate_id=%s", (*key, cid)).fetchone(),
        full=True,
    )


def cursor_token(key, scope, position):
    data = json.dumps(position, separators=(",", ":")).encode()
    tag = hmac.digest(key, scope + data, "sha256")
    return base64.urlsafe_b64encode(tag + data).decode().rstrip("=")


def page(db, device, request, puzzle=None, kind="inventory"):
    params = request.query_params
    limit = int(params.get("limit", 100))
    token = params.get("cursor")
    account = device["account_id"]
    scope = f"{account}/{kind}/{puzzle or ''}/".encode()
    key = request.state.instance["cursor_key"]
    after = None
    if token is not None:
        try:
            raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
            after = json.loads(raw[32:])
            if not hmac.compare_digest(cursor_token(key, scope, after), token):
                raise ValueError()
        except (ValueError, UnicodeError, RecursionError):
            raise Failure(422, "invalid_request") from None
    args = (account,) if puzzle is None else (account, puzzle)
    if kind == "inventory":
        sql = """SELECT puzzle_id,server_revision,(SELECT count(*) FROM candidates c
                 WHERE c.account_id=p.account_id AND c.puzzle_id=p.puzzle_id) AS conflict_count
                 FROM puzzles p WHERE account_id=%s"""
        seek, order = " AND puzzle_id>%s", "puzzle_id"
        fields = ("puzzle_id",)
    elif kind == "history":
        sql = (
            "SELECT "
            + VMETA
            + VERSION
            + " AND server_revision < (SELECT server_revision FROM puzzles WHERE account_id=%s AND puzzle_id=%s)"
        )
        args += args
        seek, order = " AND server_revision<%s", "server_revision DESC"
        fields = ("server_revision",)
    else:
        sql = "SELECT " + CMETA + CANDIDATE
        seek, order = " AND (created_at,candidate_id)>(%s,%s)", "created_at,candidate_id"
        fields = ("created_at", "candidate_id")
    if after is not None:
        sql += seek
        args += tuple(after)
    rows = db.execute(sql + " ORDER BY " + order + " LIMIT %s", (*args, limit + 1)).fetchall()
    items = [export(row) for row in rows[:limit]]
    next_cursor = None
    if len(rows) > limit:
        next_cursor = cursor_token(key, scope, [items[-1][f] for f in fields])
    elif kind == "inventory" and device["needs_inventory"]:
        db.execute("UPDATE devices SET needs_inventory=false WHERE device_id=%s", (device["device_id"],))
    return {"items": items, "next_cursor": next_cursor}


class Rejected(Exception):
    pass


def check_quota(db, account):
    sizes = db.execute(
        """
        SELECT (SELECT count(*) FROM puzzles WHERE account_id=%s) AS puzzles,
               coalesce((SELECT sum(octet_length(save)) FROM versions WHERE account_id=%s),0)
               + coalesce((SELECT sum(octet_length(save)) FROM candidates WHERE account_id=%s),0) AS bytes
    """,
        (account, account, account),
    ).fetchone()
    if sizes["puzzles"] > quota("PUZZLES", 2000) or sizes["bytes"] > quota("BYTES", 512 << 20):
        raise Rejected("storage_limit")


def apply(db, device, key, current, body):
    revision = current["server_revision"] if current else 0
    op = body.operation
    cid = None
    if op in ("snapshot", "reset"):
        save = body.save.model_dump_json(by_alias=True) if op == "snapshot" else None
        definition = body.save.definition_revision if save else body.definition_revision
        if not current:
            db.execute("INSERT INTO puzzles(account_id,puzzle_id) VALUES (%s,%s)", key)
        if revision != body.base_server_revision or (
            revision and current["definition_revision"] != definition
        ):
            if db.execute("SELECT count(*) AS n" + CANDIDATE, key).fetchone()["n"] >= 5:
                raise Rejected("conflict_limit")
            row = db.execute(
                """
                INSERT INTO candidates(account_id,puzzle_id,base_server_revision,definition_revision,save,device_id,device_name)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING candidate_id
            """,
                (
                    *key,
                    body.base_server_revision,
                    definition,
                    save,
                    device["device_id"],
                    device["device_name"],
                ),
            ).fetchone()
            check_quota(db, key[0])
            return "conflict_saved", revision, str(row["candidate_id"])
    else:
        if body.base_server_revision != revision:
            raise Rejected("revision_conflict")
        if op == "restore":
            source = db.execute(
                "SELECT save,definition_revision"
                + VERSION
                + " AND server_revision=%s AND server_revision<%s",
                (*key, body.history_revision, revision),
            ).fetchone()
            if not source:
                raise Rejected("history_missing")
        else:
            cid = body.candidate_id
            source = db.execute(
                "DELETE" + CANDIDATE + " AND candidate_id=%s RETURNING save,definition_revision", (*key, cid)
            ).fetchone()
            if not source:
                raise Rejected("candidate_missing")
            if op == "discard":
                if not revision:
                    db.execute(
                        """DELETE FROM puzzles WHERE account_id=%s AND puzzle_id=%s AND NOT EXISTS
                               (SELECT 1 FROM candidates WHERE account_id=%s AND puzzle_id=%s)""",
                        (*key, *key),
                    )
                return "ok", revision, cid
        save, definition = source["save"], source["definition_revision"]
    revision += 1
    db.execute(
        """INSERT INTO versions(account_id,puzzle_id,server_revision,definition_revision,save,device_id,device_name)
                  VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (*key, revision, definition, save, device["device_id"], device["device_name"]),
    )
    db.execute("UPDATE puzzles SET server_revision=%s WHERE account_id=%s AND puzzle_id=%s", (revision, *key))
    db.execute("DELETE" + VERSION + " AND server_revision<%s", (*key, revision - 10))
    check_quota(db, key[0])
    return "ok", revision, cid


def mutate(db, device, puzzle, body, request):
    if body.operation == "snapshot" and body.save.definition_id != puzzle:
        raise Failure(422, "invalid_request")
    if device["needs_inventory"]:
        raise Failure(409, "server_generation_changed")
    key = (device["account_id"], puzzle)
    seq = body.request_seq
    last = device["last_request_seq"]
    signature = hashlib.sha256(
        f"POST\n/v1/puzzles/{puzzle}/mutations\n".encode() + request.state.raw
    ).digest()
    if seq == last and signature == device["request_hash"]:
        return Response(device["response_body"], device["response_status"], media_type="application/json")
    current = db.execute(
        """SELECT p.server_revision,v.definition_revision FROM puzzles p
                            LEFT JOIN versions v USING(account_id,puzzle_id,server_revision)
                            WHERE p.account_id=%s AND p.puzzle_id=%s""",
        key,
    ).fetchone()
    revision = current["server_revision"] if current else 0
    consumed = seq == last + 1
    cid = None
    if consumed:
        try:
            with db.transaction():  # savepoint: a rejected quota check retains only its receipt
                code, revision, cid = apply(db, device, key, current, body)
        except Rejected as error:
            code = error.args[0]
    elif seq == last:
        code = "sequence_reused"
    else:
        code = "sequence_stale" if seq < last else "sequence_gap"
    status = 200 if code == "ok" else 409
    outcome = {
        "ok": "discarded" if body.operation == "discard" else "applied",
        "conflict_saved": "conflict",
    }.get(code, "rejected")
    payload = json.dumps(
        {
            "format": body.format,
            "request_seq": seq,
            "outcome": outcome,
            "server_revision": revision,
            "candidate_id": cid,
            "code": code,
            "sequence_consumed": consumed,
        },
        separators=(",", ":"),
    )
    if consumed:
        db.execute(
            """UPDATE devices SET last_request_seq=%s,request_hash=%s,response_status=%s,response_body=%s
                      WHERE device_id=%s""",
            (seq, signature, status, payload, device["device_id"]),
        )
    return Response(payload, status, media_type="application/json")
