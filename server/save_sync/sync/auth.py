import re
from hmac import compare_digest

from pwdlib import PasswordHash

from .db import Failure, connect, digest, issue_code, quota, stamp

passwords = PasswordHash.recommended()
DUMMY_HASH = passwords.hash(issue_code())


def throttle(username, ip):
    # Commit attempts even when the subsequent credential transaction rolls back.
    with connect() as db:
        db.execute("SELECT pg_advisory_xact_lock(821002)")
        db.execute("DELETE FROM attempts WHERE at <= clock_timestamp() - interval '15 minutes'")
        counts = db.execute("""
            SELECT count(*) FILTER (WHERE username=%s) AS names,
                   count(*) FILTER (WHERE ip=%s) AS addresses FROM attempts
            WHERE username=%s OR ip=%s
        """, (username, ip, username, ip)).fetchone()
        if counts["names"] >= quota("AUTH_NAME", 10) or counts["addresses"] >= quota("AUTH_IP", 100):
            raise Failure(429, "rate_limited", {"Retry-After": "900"})
        db.execute("INSERT INTO attempts(username,ip) VALUES (%s,%s)", (username, ip))


def denied():
    return Failure(401, "authentication_failed")


def session(db, request):
    auth = request.headers.get("authorization", "")
    match = re.fullmatch(r"Bearer ([A-Za-z0-9_-]{43})", auth, re.IGNORECASE)
    if not match:
        raise denied()
    token = digest(match[1])
    # All writers acquire the account lock first, including login and recovery.
    account = db.execute("""
        SELECT a.* FROM accounts a JOIN devices d USING(account_id)
        WHERE d.token=%s AND NOT a.locked FOR UPDATE OF a
    """, (token,)).fetchone()
    if not account:
        raise denied()
    device = db.execute("""
        SELECT * FROM devices WHERE account_id=%s AND token=%s AND expires_at>clock_timestamp()
    """, (account["account_id"], token)).fetchone()
    if not device:
        raise denied()
    return {**account, **device}


def info(device):
    return {key: str(device[key]) for key in ("account_id", "username", "device_id")} | {
        "last_request_seq": device["last_request_seq"]}


def start_session(db, account, name, device_id=None, recovery=None):
    token = issue_code()
    if device_id:
        row = db.execute("""
            UPDATE devices SET token=%s, device_name=%s, expires_at=now()+interval '30 days'
            WHERE account_id=%s AND device_id=%s RETURNING *
        """, (digest(token), name, account["account_id"], device_id)).fetchone()
        if not row:
            raise denied()
    else:
        count = db.execute("SELECT count(*) AS n FROM devices WHERE account_id=%s",
                           (account["account_id"],)).fetchone()["n"]
        if count >= quota("DEVICES", 100):
            raise Failure(409, "registration_unavailable")
        row = db.execute("""
            INSERT INTO devices(account_id,device_name,token,needs_inventory,expires_at)
            VALUES (%s,%s,%s,%s,now()+interval '30 days') RETURNING *
        """, (account["account_id"], name, digest(token), account["restored"])).fetchone()
    return info({**account, **row}) | dict(token=token, expires_at=stamp(row["expires_at"]), recovery_code=recovery)


def register(db, body):
    result = db.execute("DELETE FROM invitations WHERE digest=%s AND expires_at>clock_timestamp()",
                        (digest(body.invitation),))
    if not result.rowcount:
        raise Failure(409, "registration_unavailable")
    code = issue_code()
    account = db.execute("""
        INSERT INTO accounts(username,password_hash,recovery) VALUES (%s,%s,%s)
        ON CONFLICT (username) DO NOTHING RETURNING *
    """, (body.username, passwords.hash(body.password), digest(code))).fetchone()
    if not account:
        raise Failure(409, "registration_unavailable")
    return start_session(db, account, body.device_name, recovery=code)


def login(db, body):
    account = db.execute("SELECT * FROM accounts WHERE username=%s FOR UPDATE", (body.username,)).fetchone()
    if not passwords.verify(body.password, account["password_hash"] if account else DUMMY_HASH):
        raise denied()
    if not account or account["locked"]:
        raise denied()
    return start_session(db, account, body.device_name, body.device_id)


def recover(db, body):
    account = db.execute("SELECT * FROM accounts WHERE username=%s FOR UPDATE", (body.username,)).fetchone()
    if not account or not account["recovery"] or not compare_digest(account["recovery"], digest(body.recovery_code)):
        raise denied()
    code = issue_code()
    db.execute("UPDATE accounts SET recovery=%s,password_hash=%s,locked=false WHERE account_id=%s",
               (digest(code), passwords.hash(body.new_password), account["account_id"]))
    db.execute("UPDATE devices SET token=NULL WHERE account_id=%s", (account["account_id"],))
    return {"recovery_code": code}


def rotate(db, device, body):
    if not passwords.verify(body.password, device["password_hash"]):
        raise denied()
    code = issue_code()
    db.execute("UPDATE accounts SET recovery=%s WHERE account_id=%s", (digest(code), device["account_id"]))
    return {"recovery_code": code}
