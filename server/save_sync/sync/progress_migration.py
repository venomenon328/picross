"""Database revision 2. Called under the migration lock in a single transaction."""

import json

from .models import Save


def unique_fields(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("Duplicate field in stored save")
    return obj


def invalid_constant(_):
    raise ValueError("Invalid JSON number in stored save")


def project(row):
    old = json.loads(row["save"], object_pairs_hook=unique_fields, parse_constant=invalid_constant)
    retained = Save.model_fields.keys() - {"format"}
    if not isinstance(old, dict) or old.keys() != retained | {"schema", "history", "cursor", "view"}:
        raise ValueError("Unknown stored save shape")
    if type(old["schema"]) is not int or old["schema"] != 1:
        raise ValueError("Unknown stored save version")
    if not isinstance(old["history"], list) or type(old["cursor"]) is not int or not isinstance(old["view"], dict):
        raise ValueError("Unknown legacy save shape")
    progress = Save(format="picross-progress/v1", **{key: old[key] for key in retained})
    if (progress.definition_id, progress.definition_revision) != (row["puzzle_id"], row["definition_revision"]):
        raise ValueError("Stored progress belongs to a different puzzle or revision")
    return progress.model_dump_json()


def migrate_v1(db):
    db.execute("LOCK TABLE versions, candidates IN ACCESS EXCLUSIVE MODE")
    for table, identity in (("versions", "server_revision"), ("candidates", "candidate_id")):
        with db.cursor(name="legacy_rows") as rows:
            rows.itersize = 1  # Legacy full saves can be up to 16 MiB each.
            rows.execute(
                f"SELECT account_id,puzzle_id,definition_revision,{identity},save "
                f"FROM {table} WHERE save IS NOT NULL"
            )
            for row in rows:
                db.execute(
                    f"UPDATE {table} SET save=%s WHERE account_id=%s AND puzzle_id=%s AND {identity}=%s",
                    (project(row), row["account_id"], row["puzzle_id"], row[identity]),
                )
    db.execute("UPDATE instance SET version=2 WHERE singleton AND version=1")
