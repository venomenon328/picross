extends RefCounted
const Profile = preload("res://model/account_profile.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const Store = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Publisher = preload("res://model/windows_publisher.gd")
const HOST = "https://sync.example.invalid"
const ACCOUNT = "10000000-0000-4000-8000-000000000001"
const OTHER = "10000000-0000-4000-8000-000000000002"
const DEVICE = "10000000-0000-4000-8000-000000000003"
const EPOCH = "10000000-0000-4000-8000-000000000004"

class Deferred extends RefCounted:
	var deliveries: Array = []
	func confirm_local(ticket: Dictionary, callback: Callable) -> void:
		deliveries.append([ticket,callback])

class InterruptJournal extends "res://model/sync_journal.gd":
	var interrupt := true
	func publish(state: Dictionary) -> bool:
		if interrupt and state.intent.is_empty():
			return false
		return super.publish(state)

static func reply(request: Dictionary, code: String, revision: int, candidate: Variant = null) -> Dictionary:
	var body: Dictionary = JSON.parse_string(request.body)
	var outcome := "rejected"
	if code == "ok": outcome = "discarded" if body.operation == "discard" else "applied"
	if code == "conflict_saved": outcome = "conflict"
	return {"format":Protocol.FORMAT,"request_seq":request.seq,"outcome":outcome,"server_revision":revision,
		"candidate_id":candidate,"code":code,"sequence_consumed":not code in Protocol.SEQUENCE_ERRORS}

static func write(path: String, raw: String) -> void:
	var file := FileAccess.open(path,FileAccess.WRITE)
	file.store_string(raw)
	file.close()

static func run(t: SceneTree) -> void:
	var start: int = t.failures
	var checkpoint := {"format":"picross-device-checkpoint/v1","account_id":ACCOUNT,"device_id":DEVICE,
		"last_request_seq":1,"last_request_hash":"0".repeat(64),"response_status":200,"response_body":"{}"}
	t.check(Protocol.valid_checkpoint(JSON.parse_string(JSON.stringify(checkpoint)),ACCOUNT,DEVICE),"B2 accepts the actual JSON-number receipt after browser restart")
	checkpoint.response_status = 200.5
	t.check(not Protocol.valid_checkpoint(checkpoint,ACCOUNT,DEVICE),"B2 rejects fractional receipt status")
	var snapshot := {"format":Protocol.PROGRESS_FORMAT,"definition_id":"p","definition_revision":1,"width":1,"height":1,"cells":[0],"completed":false,"undo_used":false}
	t.check(Protocol.progress(snapshot) == Protocol.progress(JSON.parse_string(JSON.stringify(snapshot))),"B2 identical HTTP progress keeps the local undo history")
	var linked := Profile.ROOT.path_join((HOST+"/linked").sha256_text()).path_join(ACCOUNT)
	t.check(DirAccess.dir_exists_absolute(linked) and not Profile.new().open(HOST+"/linked",ACCOUNT,DEVICE,EPOCH,true) and not Store.SaveRevision.Recent.safe_file(linked.path_join("journal.json")),"B1 real linked ancestor rejected")
	if t.failures != start: return
	var adapter := Deferred.new()
	var p := Profile.new()
	var b := Profile.new()
	var c := Profile.new()
	var host := HOST + "/core"
	t.check(p.open(host,ACCOUNT,DEVICE,EPOCH,true,adapter),"B1 native initialization")
	t.check(b.open(host,OTHER,DEVICE,EPOCH,true) and c.open(HOST+"/other",ACCOUNT,DEVICE,EPOCH,true),"B1 independent accounts and servers")
	if OS.get_name() == "Windows": publisher_timeout(t, Session.new(t.fixture))
	t.check(not Profile.new().open(host,"../x",DEVICE,EPOCH,true),"B1 unsafe identity")
	var b_hash := FileAccess.get_sha256(b._journal.path)
	var c_hash := FileAccess.get_sha256(c._journal.path)
	var session := Session.new(t.fixture)
	t.check(p.load_slot(t.fixture).status == "fresh" and p.status().entries.is_empty(),"B1 empty profile has no reset")
	var n := p.save(session,session.view_state)
	session.gesture.begin(session.player,Vector2i(1,1),1)
	session.finish()
	session.undo()
	var n2 := p.save(session,session.view_state)
	t.check(n == 1 and n2 == 2 and not p.locally_confirmed(n2),"B1 generations await own adapter")
	if n2 != 2: return
	var first: Array = adapter.deliveries[0]
	var second: Array = adapter.deliveries[1]
	second[1].call(first[0],true)
	first[1].call(first[0],true)
	t.check(p.locally_confirmed(n) and not p.locally_confirmed(n2) and p.prepare(n2,0).is_empty(),"B1 swapped acknowledgements rejected")
	second[1].call(second[0],false)
	second[1].call(second[0],true)
	t.check(not p.locally_confirmed(n2),"B1 failed callback is terminal for this ticket")
	var request := p.prepare(n,0)
	t.check(not request.is_empty() and p.resume_request() == request and p.prepare(n,0).is_empty(),"B1 durable single request")
	if request.is_empty(): return
	var foreign := request.duplicate(true)
	foreign.device = OTHER
	t.check(not p.receive(foreign,EPOCH,200,reply(request,"ok",1)) and not b.receive(request,EPOCH,200,reply(request,"ok",1)),"B1 foreign confirmations")
	t.check(p.receive(request,EPOCH,200,reply(request,"ok",1)) and not p.receive(request,EPOCH,200,reply(request,"ok",1)),"B1 consumed receipt applied once")
	t.check(p.status().entries.has("2") and p.status().revisions[session.definition.id].confirmed_local == n,"B1 old server success preserves newer generation")
	var reopened := Profile.new()
	t.check(reopened.open(host,ACCOUNT,DEVICE,EPOCH),"B1 native journal opens")
	request = reopened.prepare(n2,1)
	if request.is_empty(): return
	t.check(reopened.receive(request,EPOCH,409,reply(request,"conflict_saved",2,OTHER)) and reopened.status().entries["2"].value == JSON.parse_string(JSON.stringify(Protocol.progress(Store.snapshot(session,session.view_state)))),"B1 candidate receipt preserves progress")
	for operation: String in ["resolve","discard","restore"]:
		var value: Variant = 1 if operation == "restore" else OTHER
		var version := reopened.decision(session.definition.id,operation,value,2)
		request = reopened.prepare(version,2)
		if request.is_empty(): return
		var candidate: Variant = null if operation == "restore" else OTHER
		t.check(reopened.receive(request,EPOCH,200,reply(request,"ok",2 if operation == "discard" else 3,candidate)),"B1 "+operation)
	var reset := reopened.reset(session.definition.id)
	request = reopened.prepare(reset,3)
	if request.is_empty(): return
	t.check(JSON.parse_string(request.body).definition_revision == t.fixture.revision and reopened.receive(request,EPOCH,409,reply(request,"storage_limit",3)),"B1 versioned reset and quota refusal")
	t.check(reopened.status().entries[str(reset)].status == "storage_limit","B1 rejected reset retained")
	var snap := reopened.save(session,session.view_state)
	request = reopened.prepare(snap,3)
	if request.is_empty(): return
	t.check(reopened.receive(request,EPOCH,409,reply(request,"sequence_gap",3)) and reopened.resume_request().is_empty(),"B1 unconsumed sequence blocks replay")
	t.check(reopened.reconciliation().state.request == request and not Profile.new().open(host,ACCOUNT,DEVICE,EPOCH),"B1 reconciliation survives restart")
	t.check(FileAccess.get_sha256(b._journal.path) == b_hash and FileAccess.get_sha256(c._journal.path) == c_hash,"B1 foreign profile bytes unchanged")
	t.check(c.observe_generation(OTHER) == false and not Profile.new().open(HOST+"/other",ACCOUNT,DEVICE,EPOCH),"B1 restore generation persists reconciliation")
	basis_and_schedule(t,b,session)
	if not filesystem_cases(t,b,session): return
	if not interruption(t,session) or not progress_cases(t,session): return
	for code: String in ["sequence_reused","sequence_stale","sequence_gap","storage_limit","history_missing","candidate_missing","revision_conflict","conflict_limit"]:
		var rejected := reply(request,code,3)
		t.check(Protocol.valid_reply(request,409,rejected),"B1 closed reply " + code)
		rejected.sequence_consumed = not rejected.sequence_consumed
		t.check(not Protocol.valid_reply(request,409,rejected),"B1 inconsistent consumption " + code)
	if t.failures == start: print("SYNC_PROGRESS_CORE_OK")

static func publisher_timeout(t: SceneTree, session: Session) -> void:
	var host := HOST + "/publisher-timeout"
	var old := Profile.new()
	if not old.open(host,ACCOUNT,DEVICE,EPOCH,true):
		t.check(false,"SYNC-PERF timeout profile opens")
		return
	var journal: String = old._journal.path
	var before := FileAccess.get_file_as_bytes(journal)
	var delayed := Publisher.new()
	var source: String = Publisher.COMMAND.replace("    $ok = $false", """
    if ($flags -eq '9') {
        [IO.File]::WriteAllText($target + '.tmp', 'occupied')
        [IO.File]::WriteAllText($target + '.entered-test', $source)
        while (![IO.File]::Exists($target + '.release-test') -and !$owner.HasExited) {
            [Threading.Thread]::Sleep(10)
        }
    }
    $ok = $false""")
	delayed._start(source)
	var publisher := Store.SaveRevision.Recent.windows_publisher()
	var live: Dictionary = publisher.child
	publisher.child = delayed.child
	publisher.available = delayed.available
	session.player.commit([{"index":0,"before":-1,"after":0}])
	var failed := old.save(session,session.view_state)
	publisher.child = live
	publisher.available = true
	publisher.set_process(false)
	var stranded := FileAccess.get_file_as_string(journal + ".entered-test").replace("\\","/")
	t.check(failed == 0 and FileAccess.file_exists(stranded) and FileAccess.get_file_as_string(journal+".tmp") == "occupied"
		and FileAccess.get_file_as_bytes(journal) == before and old.load_slot(session.definition).status == "error",
		"SYNC-PERF expired request reports failure with the old candidate still present and no local generation")
	var newer := Profile.new()
	t.check(newer.open(host,ACCOUNT,DEVICE,EPOCH),"SYNC-PERF competing writer acquires the released profile")
	session.player.commit([{"index":1,"before":-1,"after":1}])
	var version := newer.save(session,session.view_state)
	var confirmed := FileAccess.get_sha256(journal)
	write(journal+".release-test","released")
	await_worker_exit(delayed)
	var reader := Profile.new()
	var readable := reader.open(host,ACCOUNT,DEVICE,EPOCH)
	var restored := reader.load_slot(session.definition) if readable else {}
	t.check(not OS.is_process_running(delayed.child.pid) and FileAccess.file_exists(stranded)
		and FileAccess.get_sha256(journal) == confirmed and version == 1 and readable
		and reader.locally_confirmed(1) and reader.status().intent.is_empty()
		and restored_slot(restored, session, 2),
		"SYNC-PERF late publisher cannot overwrite the independently reopened newer journal and Primary")
	delayed._exit_tree()
	delayed.free()

	# Lose the second acknowledgement only: its Primary and confirmed journal
	# are already durable, but the initiating caller still must report failure.
	var lost := Publisher.new()
	var after_move: String = Publisher.COMMAND.replace("$held = $null\nwhile", "$held = $null\n$moves = 0\nwhile")
	after_move = after_move.replace("    [Console]::WriteLine($id + ' ' + [int]$ok)", """
    if ($flags -eq '9' -and $ok) {
        $moves += 1
        if ($moves -eq 2) {
            [IO.File]::WriteAllText($target + '.moved-test', 'moved')
            [Threading.Thread]::Sleep(2600)
        }
    }
    [Console]::WriteLine($id + ' ' + [int]$ok)""")
	lost._start(after_move)
	publisher.child = lost.child
	publisher.available = lost.available
	session.player.commit([{"index":2,"before":-1,"after":0}])
	failed = newer.save(session,session.view_state)
	publisher.child = live
	publisher.available = true
	publisher.set_process(false)
	var reopened := Profile.new()
	readable = reopened.open(host,ACCOUNT,DEVICE,EPOCH)
	restored = reopened.load_slot(session.definition) if readable else {}
	t.check(failed == 0 and FileAccess.file_exists(journal+".moved-test") and readable
		and reopened.locally_confirmed(2) and reopened.status().intent.is_empty()
		and restored_slot(restored, session, 3),
		"SYNC-PERF lost acknowledgement never confirms to the caller and reopening reads the completed generation")
	await_worker_exit(lost)
	lost._exit_tree()
	lost.free()

	var target := old._root.path_join("recent-puzzle.json")
	var previous := JSON.stringify({"format":Store.SaveRevision.Recent.FORMAT,"id":"T-01","revision":1})
	var latest := JSON.stringify({"format":Store.SaveRevision.Recent.FORMAT,"id":"T-04","revision":1})
	write(target,previous)
	write(target+".tmp",previous)
	var marker := Publisher.new()
	marker._start(source)
	t.check(not marker.replace(target+".tmp",target,true),"SYNC-PERF marker reports the same lost publication")
	write(target+".tmp",latest)
	t.check(not publisher.replace(target+".tmp",target,false) and publisher.replace(target+".tmp",target,true),
		"SYNC-PERF create-only preserves the existing marker and replacement publishes newer bytes")
	t.check(not publisher.clear(target,previous.sha256_text()) and publisher.clear(target,latest.sha256_text()),
		"SYNC-PERF marker removal compares the current bytes inside the publication gate")
	write(target+".release-test","released")
	await_worker_exit(marker)
	t.check(not FileAccess.file_exists(target),"SYNC-PERF late marker publication cannot undo a newer deletion")
	marker._exit_tree()
	marker.free()

static func restored_slot(restored: Dictionary, session: Session, cursor: int) -> bool:
	if restored.get("status") != "loaded": return false
	var independent := Session.new(session.definition)
	Store.apply(restored.data, independent)
	return independent.player.cursor == cursor and independent.player.cells == session.player.cells

static func await_worker_exit(publisher: Publisher) -> void:
	if publisher.child.is_empty(): return
	var deadline := Time.get_ticks_msec()+5000
	while OS.is_process_running(publisher.child.pid) and Time.get_ticks_msec()<deadline:
		OS.delay_msec(5)

static func basis_and_schedule(t: SceneTree, p: Profile, source: Session) -> void:
	var slot := Session.new(source.definition)
	var progress := Protocol.progress(Store.snapshot(slot,slot.view_state))
	progress.cells[0] = 0
	var data := p._store.received(progress,slot)
	t.check(not data.is_empty() and data.baseline.cells == progress.cells and data.history.is_empty(),"account receives actual progress as basis")
	if data.is_empty(): return
	t.check(not Store.validate(data,source.definition).is_empty(),"guest rejects account envelope")
	Store.apply(data,slot)
	t.check(not slot.player.undo() and slot.player.commit([{"index":0,"before":0,"after":-1}]) and slot.player.undo() and slot.player.cells[0] == 0,"undo stops at nonempty received basis")
	var identical := p._store.received(Protocol.progress(p._store.slot_snapshot(slot,slot.view_state)),slot)
	t.check(identical.history == slot.player.history and identical.cursor == 0,"identical progress preserves redo")
	var invalid := identical.duplicate(true)
	invalid.baseline.cells[0] = -1
	t.check(not p._store.validate_account(invalid,slot.definition).is_empty(),"reject corrupted replay basis")
	var timer := preload("res://model/sync_schedule.gd").new()
	var clock := [1000]
	timer.clock = func() -> int: return clock[0]
	timer.enter()
	t.check(not timer.ready(),"cell edit does not schedule request")
	timer.collect()
	clock[0] += 1999
	t.check(not timer.ready(),"two second coalescing")
	clock[0] += 1
	t.check(timer.ready(),"coalesced batch ready")
	for delay: int in [30,60,120,240,300,300]:
		timer.transient(0)
		t.check(timer.retry_at == timer.now()+delay,"bounded device backoff")
	timer.transient(400)
	timer.connected()
	t.check(timer.retry_at == timer.now()+400 and not timer.ready(),"reconnect respects Retry-After")
	timer.success()
	timer.due = INF
	clock[0] = 601000
	t.check(timer.ready(),"600 seconds since entry")

static func progress_cases(t: SceneTree, session: Session) -> bool:
	var p := Profile.new()
	var host := HOST + "/progress"
	if not p.open(host,ACCOUNT,DEVICE,EPOCH,true): return false
	var view := session.view_state.duplicate(true)
	var first := p.save(session,view)
	var req := p.prepare(first,0)
	if req.is_empty(): return false
	var progress: Dictionary = JSON.parse_string(req.body).save
	t.check(Protocol.valid_progress(progress,session.definition.id), "progress-only request")
	view.overview = not view.overview
	var second := p.save(session,view)
	t.check(second == first+1 and p.locally_confirmed(second) and p.status().entries.size() == 1 and p.resume_request() == req,"view saved with pending request untouched")
	if not p.receive(req,EPOCH,200,reply(req,"ok",1)): return false
	view.overview = not view.overview
	var third := p.save(session,view)
	var restarted := Profile.new()
	if not restarted.open(host,ACCOUNT,DEVICE,EPOCH): return false
	t.check(restarted.locally_confirmed(third) and restarted.status().entries.is_empty() and restarted.prepare(third,1).is_empty(),"confirmed progress needs no second upload")
	# Construct an original v1 request in its checksummed journal envelope.
	var image := restarted.status()
	image.erase("slots")
	image.request = req.duplicate(true)
	var body: Dictionary = JSON.parse_string(req.body)
	body.save = Store.snapshot(session,view)
	image.request.body = JSON.stringify(body," ",false,true)
	image.local = first
	image.entries[str(first)] = {"id":session.definition.id,"local":first,"operation":"snapshot","value":body.save,"status":"pending"}
	image.receipt = {}
	image.sequence = 0
	image.revisions = {}
	var payload := JSON.stringify(image,"",true,true)
	var raw := JSON.stringify({"format":"picross-local-sync/v1","payload":payload,"sha256":payload.sha256_text()})+"\n"
	write(p._journal.path,raw)
	var legacy := Profile.new()
	t.check(not legacy.open(host,ACCOUNT,DEVICE,EPOCH) and legacy.resume_request().is_empty() and legacy.reconciliation().state.request.body == image.request.body and FileAccess.get_file_as_string(p._journal.path) == raw,"v1 original bytes and sequence retained for reconciliation")
	print("SYNC_PROGRESS_WINDOWS_CASES local=%d sync_entries=0 legacy_sha256=%s" % [third,raw.sha256_text()])
	return true

static func filesystem_cases(t: SceneTree, p: Profile, session: Session) -> bool:
	var key := p._store.key_for_definition(session.definition.id)
	var path := p._store.path_for(key)
	var first := p.save(session,session.view_state)
	t.check(first > 0 and p.update_recent(session),"B1 profile recent and slot")
	var request := p.prepare(first,0)
	if request.is_empty(): return false
	var old := Store.snapshot(session,session.view_state)
	old.definition_revision = int(old.definition_revision)-1
	write(path,JSON.stringify(old))
	var old_hash := FileAccess.get_sha256(path)
	# A directory at the journal temporary path prevents publication before PE touches the slot.
	DirAccess.make_dir_absolute(p._journal.path+".tmp")
	t.check(p.load_slot(session.definition).status == "error" and FileAccess.get_sha256(path) == old_hash,"B1 preservation failure leaves old bytes")
	DirAccess.remove_absolute(p._journal.path+".tmp")
	var loaded := p.load_slot(session.definition)
	t.check(loaded.get("revision_reset",false) and p.resume_request() == request and p.status().archive.has(old_hash),"B1 archived old raster and original request")
	t.check(p.status().entries.size() == 1 and p.status().entries.values()[0].operation == "snapshot","B1 PE reset produces no server reset")
	var a := p.save(session,session.view_state)
	var b := p.save(session,session.view_state)
	t.check(a > 0 and b > a,"B1 save and backup rotate")
	DirAccess.remove_absolute(path)
	t.check(p.load_slot(session.definition).status == "recovered" and p.save(session,session.view_state) == 0,"B1 recovered backup write protection")
	t.check(p.repair_from_backup(session.definition) > b,"B1 explicit backup recovery")
	var journal := p._journal.path
	var bytes := FileAccess.get_file_as_string(journal)
	write(journal,"{}")
	t.check(not Profile.new().open(HOST+"/core",OTHER,DEVICE,EPOCH),"B1 damaged journal blocks")
	DirAccess.remove_absolute(journal)
	t.check(not Profile.new().open(HOST+"/core",OTHER,DEVICE,EPOCH,true),"B1 missing journal cannot reinitialize")
	write(journal,bytes)
	t.check(not Profile.new().open(HOST+"/core",OTHER,OTHER,EPOCH),"B1 foreign device blocks")
	return true

static func interruption(t: SceneTree, session: Session) -> bool:
	var profile := Profile.new()
	var host := HOST + "/interrupt"
	if not profile.open(host,ACCOUNT,DEVICE,EPOCH,true): return false
	var fault := InterruptJournal.new(profile._root)
	fault.digest = profile._journal.digest
	profile._journal = fault
	t.check(profile.save(session,session.view_state) == 0 and not profile.locally_confirmed(1),"B1 interruption after slot, before journal commit reports no success")
	var key := profile._store.key_for_definition(session.definition.id)
	var primary := profile._store.path_for(key)
	var original := FileAccess.get_file_as_string(primary)
	var different: Dictionary = JSON.parse_string(original)
	different.view.overview = not different.view.overview
	write(primary,JSON.stringify(different))
	t.check(not Profile.new().open(host,ACCOUNT,DEVICE,EPOCH),"recovery rejects another local view with identical progress")
	write(primary,original)
	var recovered := Profile.new()
	if not recovered.open(host,ACCOUNT,DEVICE,EPOCH): return false
	t.check(recovered.locally_confirmed(1) and recovered.load_slot(session.definition).status == "loaded" and not recovered.prepare(1,0).is_empty(),"B1 rebuild pending generation from actual primary and intent")
	# Simulate an interruption after rotation and before the new primary. The
	# last good bytes remain in backup; pending request and intent remain inspectable.
	recovered._store.fail_step = "after_rotation"
	t.check(recovered.save(session,session.view_state) == 0,"B1 interrupted rotation is a save error")
	var blocked := Profile.new()
	t.check(not blocked.open(host,ACCOUNT,DEVICE,EPOCH) and not blocked.reconciliation().state.intent.is_empty() and not blocked.reconciliation().state.request.is_empty(),"B1 interrupted rotation retains intent and previous request")
	return true
