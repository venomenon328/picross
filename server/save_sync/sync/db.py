import os
import secrets
from datetime import UTC
from hashlib import sha256

import psycopg
from psycopg.rows import dict_row


class Failure(Exception):
    def __init__(self, status, code, headers=None):
        self.status, self.code, self.headers = status, code, headers or {}


def connect():
    return psycopg.connect(connect_timeout=3, row_factory=dict_row)


def instance(db):
    row = db.execute("SELECT generation, cursor_key FROM instance WHERE singleton AND version=2").fetchone()
    if not row:
        raise Failure(503, "unavailable")
    return row


def stamp(value):
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def digest(value):
    return sha256(value.encode("utf-8")).digest()


def issue_code():
    return secrets.token_urlsafe(32)


def quota(name, default):
    return int(os.environ.get("SYNC_" + name, default))
