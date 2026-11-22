"""Archive the selected Compose project's DB, or restore to a second empty project."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

DB = ["docker", "compose", "exec", "-T", "db"]
PSQL = [
    *DB,
    "psql",
    "-X",
    "-q",
    "-U",
    "picross",
    "-d",
    "picross",
    "-v",
    "ON_ERROR_STOP=1",
    "-v",
    "VERBOSITY=sqlstate",
]
EMPTY = """
DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname NOT IN ('public','information_schema')
            AND left(nspname, 3) <> 'pg_') OR EXISTS
    (SELECT 1 FROM pg_depend WHERE refclassid='pg_namespace'::regclass
     AND refobjid='public'::regnamespace) OR EXISTS
    (SELECT 1 FROM pg_largeobject_metadata) OR EXISTS
    (SELECT 1 FROM pg_event_trigger) OR EXISTS
    (SELECT 1 FROM pg_extension WHERE extname <> 'plpgsql') THEN
   RAISE EXCEPTION 'Restore requires an empty database';
 END IF;
END $$;
"""
LOCKDOWN = """
-- pg_restore clears search_path in the SQL stream; explicitly select the service schema.
SET LOCAL search_path = pg_catalog, public;
DO $$ BEGIN
 IF (SELECT count(*) FROM instance WHERE singleton AND version=1) <> 1 THEN
   RAISE EXCEPTION 'Unsupported backup';
 END IF;
END $$;
UPDATE instance SET generation=gen_random_uuid(), cursor_key=uuid_send(gen_random_uuid()) || uuid_send(gen_random_uuid());
DELETE FROM invitations;
DELETE FROM attempts;
UPDATE accounts SET locked=true, restored=true, recovery=NULL;
UPDATE devices SET token=NULL, needs_inventory=true;
"""


def backup(path):
    state = subprocess.check_output(
        [*PSQL, "-Atc", "SELECT version FROM instance WHERE singleton"], text=True
    )
    if state.strip() != "1":
        raise ValueError("Unsupported source database")
    # An incomplete dump never takes the name of a completed backup.
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as target:
        tmp = Path(target.name)
    try:
        with tmp.open("wb") as target:
            subprocess.run(
                [
                    *DB,
                    "pg_dump",
                    "-U",
                    "picross",
                    "-d",
                    "picross",
                    "--format=custom",
                    "--no-owner",
                    "--no-acl",
                ],
                stdout=target,
                check=True,
            )
            target.flush()
            os.fsync(target.fileno())
        with tmp.open("rb") as archive:
            subprocess.run([*DB, "pg_restore", "--file=/dev/null"], stdin=archive, check=True)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def restore(path):
    # Fully decode the trusted archive before opening the publication transaction.
    with tempfile.TemporaryFile(dir=path.parent) as sql, path.open("rb") as archive:
        subprocess.run(
            [*DB, "pg_restore", "--no-owner", "--no-acl", "--file=-"], stdin=archive, stdout=sql, check=True
        )
        sql.seek(0)
        subprocess.run(
            [*PSQL, "--single-transaction", "-c", EMPTY, "-f", "-", "-c", LOCKDOWN],
            stdin=sql,
            stdout=subprocess.DEVNULL,
            check=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["backup", "restore"])
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    (backup if args.operation == "backup" else restore)(args.archive)
