"""Local operator entry points. Secrets are printed only after commit."""
import argparse
from pathlib import Path

from .db import connect, digest, instance, issue_code


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("migrate")
    commands.add_parser("invite")
    commands.add_parser("restore-code").add_argument("username")
    args = parser.parse_args()
    code = None
    with connect() as db:
        if args.action == "migrate":
            db.execute("SELECT pg_advisory_xact_lock(821001)")
            if not db.execute("SELECT to_regclass('public.instance') AS t").fetchone()["t"]:
                db.execute(Path("migrations/001.sql").read_text())
            instance(db)
        else:
            instance(db)
            code = issue_code()
            if args.action == "invite":
                db.execute("DELETE FROM invitations WHERE expires_at <= now()")
                db.execute("INSERT INTO invitations VALUES (%s, now() + interval '7 days')", (digest(code),))
            elif not db.execute("UPDATE accounts SET recovery=%s WHERE username=%s AND locked",
                                (digest(code), args.username)).rowcount:
                raise SystemExit("Expected one locked account")
    if code:
        print(code)


if __name__ == "__main__":
    main()
