"""Single-use migration acceptance against two empty, isolated Compose projects."""
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from uuid import uuid4

root = Path.cwd()
sys.path.insert(0, str(root / "server/save_sync"))
from test_integration import Project, remove_image

head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
assert head == sys.argv[1]
group = "progress-proof-" + uuid4().hex[:12]
image = group + ":local"
p, target = (Project(group + suffix, image, secrets.token_urlsafe(32)) for suffix in ("", "-restore"))
account, device, candidate = (str(uuid4()) for _ in range(3))

def legacy(cell):
    return dict(schema=1, definition_id="grid", definition_revision=5, width=1, height=1, cells=[cell],
                completed=False, undo_used=False, history=[[dict(index=0, before=-1, after=cell)]], cursor=1,
                view=dict(active_color=1, tool="fill", overview=False, zoom=20, center=[0,0],
                          row_clue_reads=[{"anchor":"grid_end"}],column_clue_reads=[{"anchor":"grid_end"}]))

def rows(db, table, columns="*", order="1"):
    return json.loads(db.sql(f"SELECT json_agg(t) FROM (SELECT {columns} FROM {table} ORDER BY {order}) t"))

def state(db):
    return dict(versions=rows(db,"versions",order="puzzle_id, server_revision"),
                candidates=rows(db,"candidates"), puzzles=rows(db,"puzzles",order="puzzle_id"),
                devices=rows(db,"devices","account_id,device_id,last_request_seq,encode(request_hash,'hex') AS request_hash,response_status,response_body"),
                accounts=rows(db,"accounts","account_id,username"))

def fingerprint(db):
    return db.sql("""SELECT md5(row_to_json(instance)::text) FROM instance;
                     SELECT md5(row_to_json(accounts)::text) FROM accounts;
                     SELECT md5(row_to_json(devices)::text) FROM devices""")

def migrate(db):
    return db.compose("run","--rm","--no-deps","api","python","-m","sync.admin","migrate",capture=True)

def encoded(snapshot):
    return json.dumps(snapshot,separators=(",",":"))

with ExitStack() as stack:
    stack.callback(remove_image,image)
    stack.callback(p.down)
    stack.callback(target.down)
    work = Path(stack.enter_context(tempfile.TemporaryDirectory()))
    p.compose("build","api")
    p.compose("up","-d","--wait","db")
    target.compose("up","-d","--wait","db")
    p.sql((root/"server/save_sync/migrations/001.sql").read_text())
    p.sql(f"""
        INSERT INTO accounts(account_id,username,password_hash) VALUES ('{account}','synthetic','unused');
        INSERT INTO devices(device_id,account_id,device_name,expires_at,last_request_seq,request_hash,response_status,response_body)
          VALUES ('{device}','{account}','synthetic',now(),7,decode(repeat('ab',32),'hex'),200,'{{"proof":"exact bytes"}}');
        INSERT INTO puzzles VALUES ('{account}','grid',3),('{account}','empty',1);
        INSERT INTO versions(account_id,puzzle_id,server_revision,definition_revision,device_id,device_name,save) VALUES
          ('{account}','grid',1,5,'{device}','synthetic','{encoded(legacy(1))}'),
          ('{account}','grid',2,5,'{device}','synthetic',NULL),
          ('{account}','grid',3,5,'{device}','synthetic','{encoded(legacy(3))}'),
          ('{account}','empty',1,5,'{device}','synthetic',NULL);
        INSERT INTO candidates(account_id,puzzle_id,candidate_id,base_server_revision,definition_revision,device_id,device_name,save)
          VALUES ('{account}','grid','{candidate}',1,5,'{device}','synthetic','{encoded(legacy(2))}');
    """)
    before = state(p)
    identity = fingerprint(p)
    # Historical archive, created with the version-1 pg_dump contract.
    old = work / "v1.dump"
    with old.open("wb") as output:
        subprocess.run(["docker","compose","exec","-T","db","pg_dump","-U","picross","-d","picross","-Fc","--no-owner","--no-acl"],
                       cwd=root/"server/save_sync", env=p.env, stdout=output, check=True)
    refusal = subprocess.run([sys.executable,"db_archive.py","restore",str(old)],env=target.env,
                             cwd=root/"server/save_sync",capture_output=True)
    assert refusal.returncode and b"database version 2 required" in refusal.stderr, refusal.stderr[-500:]
    assert target.sql("SELECT to_regclass('public.instance') IS NULL") == "t"
    p.sql("UPDATE candidates SET save=jsonb_set(save::jsonb,'{completed}','1')::text")
    bad = state(p)
    try:
        migrate(p)
    except subprocess.CalledProcessError:
        pass
    else:
        raise AssertionError("invalid candidate accepted")
    assert state(p) == bad and fingerprint(p) == identity and p.sql("SELECT version FROM instance") == "1"
    p.sql(f"UPDATE candidates SET save='{encoded(legacy(2))}'")
    assert state(p) == before
    expected = json.loads(json.dumps(before))
    for table in ("versions","candidates"):
        for row in expected[table]:
            if row["save"] is not None:
                oldsave = json.loads(row["save"])
                row["save"] = dict(format="picross-progress/v1",
                    **{k:v for k,v in oldsave.items() if k not in ("schema","history","cursor","view")})
    def decoded(db):
        actual = state(db)
        for row in actual["versions"] + actual["candidates"]:
            if row["save"] is not None: row["save"] = json.loads(row["save"])
        return actual
    # The production start command performs the upgrade before becoming ready.
    p.up("--no-build")
    assert p.sql("SELECT version FROM instance") == "2" and decoded(p) == expected
    migrated = state(p)
    stable = fingerprint(p)
    assert identity.splitlines()[1:] == stable.splitlines()[1:]
    migrate(p)
    assert state(p) == migrated and fingerprint(p) == stable
    dump = work/"v2.dump"
    p.archive("backup",dump)
    target.archive("restore",dump)
    target.up("--no-build")
    assert decoded(target) == expected and target.sql("SELECT version FROM instance") == "2"
    assert target.sql("SELECT locked FROM accounts") == "t"
    report = dict(product=head, proof=os.environ["GITHUB_SHA"], run=os.environ["GITHUB_RUN_ID"], attempt=os.environ["GITHUB_RUN_ATTEMPT"],
                  platform=platform.platform(), postgres=p.sql("SHOW server_version"), before=before, after=decoded(p),
                  rollback_preserved_original_rows=True, old_archive_rejected_before_publication=True,
                  repeated_migration_byte_identical=True, restore_verified=True)
output = Path(os.environ["RUNNER_TEMP"]) / "migration-progress.json"
output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(output.name,output.stat().st_size,hashlib.sha256(output.read_bytes()).hexdigest())
