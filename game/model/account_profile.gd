extends RefCounted
## Native, explicitly opened account context. B2 supplies authenticated bindings and transport.
const Store = preload("res://model/account_save_store.gd")
const Recent = preload("res://model/recent_puzzle.gd")
const Journal = preload("res://model/sync_journal.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
const ROOT = "user://p1/accounts"
var _store: Store
var _recent: Recent
var _journal: Journal
var _state: Dictionary = {}
var _context: Dictionary = {}
var _durable: Dictionary = {}
var _awaiting: Dictionary = {}
var _blocked := "Profil geschlossen."
var _last_error := ""
var _adapter: RefCounted
var _root := ""
var _barrier := {}
var _barrier_error := false

func open(server: String, account: String, device: String, generation: String, initialize: bool = false, adapter: RefCounted = null) -> bool:
	if not _context.is_empty() or not Protocol.uuid(account) or not Protocol.uuid(device) or not Protocol.uuid(generation):
		return false
	# The configured HTTPS API base is an opaque identity, never a filesystem component.
	var https := Protocol.matches(server, "\\Ahttps://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9_-]+)*/?\\z")
	var loopback := Protocol.matches(server, "\\Ahttp://(?:127\\.0\\.0\\.1|localhost|\\[::1\\])(:[0-9]+)?(/[A-Za-z0-9_-]+)*/?\\z")
	if not (https or loopback): return false
	_context = {"server":server,"account":account,"device":device}
	_root = ROOT.path_join(server.sha256_text()).path_join(account)
	_store = Store.new(_root.path_join("saves"))
	_recent = Recent.new(_root.path_join("recent-puzzle.json"))
	_store.profile_recent_path = _recent.path
	_journal = Journal.new(_root)
	_adapter = adapter if adapter != null else _journal
	_blocked = "Profilbestand erfordert Abgleich."
	if not Recent.safe_file(_journal.path):
		return false
	if initialize:
		if DirAccess.make_dir_recursive_absolute(_root.get_base_dir()) != OK or DirAccess.make_dir_absolute(_root) != OK:
			return false
	if not _journal.acquire():
		return false
	var success := _open_locked(generation, initialize)
	_journal.release()
	return success

func _open_locked(generation: String, initialize: bool) -> bool:
	if initialize:
		_state = {"context":_context.duplicate(), "generation":generation, "local":0, "sequence":0,
			"slots":{}, "entries":{}, "request":{}, "receipt":{}, "intent":{}, "revisions":{}, "archive":{}, "reconcile":"","abandon":{}}
		if not _journal.publish(_state):
			return false
	else:
		_state = _journal.read_image()
		if _journal.legacy:
			_blocked = "Altes Syncjournal; Originalrequest erfordert Bestandsabgleich."
			return false
		if not _valid_image() or _state.context != _context:
			return false
	if _journal.previous_format:
		var old_bytes := FileAccess.get_file_as_bytes(_journal.path)
		if old_bytes.is_empty() or old_bytes.get_string_from_utf8().sha256_text() != _journal.digest: return false
		var converted := _state.duplicate(true)
		converted.archive[_journal.digest] = {"format":"picross-local-sync/v2","bytes":Marshalls.raw_to_base64(old_bytes)}
		converted.abandon = {}
		for entry: Dictionary in converted.entries.values():
			if entry.local != converted.request.get("local",-1):
				_blocked = "Bearbeitungsbasis des Altbestands erfordert Bestandsabgleich."
				return false
			entry.base_server_revision = converted.request.base
			entry.parent_local = 0
		if not converted.intent.is_empty(): return false
		if not _publish(converted): return false
		_journal.previous_format = false
	if _state.generation != generation:
		_mark_generation(generation)
		return false
	if _state.reconcile != "" or not _recover_intent():
		return false
	_blocked = ""
	for key: String in _state.entries:
		_durable[key] = true
	for slot: Dictionary in _state.slots.values():
		_durable[str(int(slot.local))] = true
	return true

func _valid_image() -> bool:
	if _state.size() != (12 if _journal.previous_format else 13) or not _state.has_all(["context","generation","local","sequence","slots","entries","request","receipt","intent","revisions","archive","reconcile"]):
		return false
	for field: String in ["context","slots","entries","request","receipt","intent","revisions","archive"]:
		if not _state[field] is Dictionary: return false
	if not Protocol.uuid(_state.generation) or not Protocol.count(_state.local) or not Protocol.count(_state.sequence) or not _state.reconcile is String:
		return false
	for id: String in _state.revisions:
		var rev: Variant = _state.revisions[id]
		if not rev is Dictionary or rev.size() != 2 or not Protocol.count(rev.get("server")) or not Protocol.count(rev.get("confirmed_local")) or rev.confirmed_local > _state.local: return false
	for id: String in _state.slots:
		var slot: Variant = _state.slots[id]
		if not slot is Dictionary or slot.size() != 2 or not Protocol.count(slot.get("local"),1) or slot.local > _state.local:
			return false
		if not Protocol.matches(slot.get("digest"),"\\A[0-9a-f]{64}\\z"): return false
	for key: String in _state.entries:
		var e: Variant = _state.entries[key]
		if not _valid_entry(e) or key != str(int(e.local)) or e.local > _state.local:
			return false
	var intent: Dictionary = _state.intent
	if not intent.is_empty():
		if not _valid_entry(intent,true) or intent.local != _state.local + 1 or intent.operation not in ["snapshot","reset"]:
			return false
	if not _journal.previous_format and (not _state.get("abandon") is Dictionary or (not _state.abandon.is_empty() and (_state.request.is_empty() or _state.abandon != abandon_order(_state.request)))):
		return false
	var req: Dictionary = _state.request
	if not req.is_empty():
		if not req.has_all(["context","device","generation","local","seq","base","method","path","body"]) or not Protocol.count(req.local,1):
			return false
		var entry: Dictionary = _state.entries.get(str(int(req.local)),{})
		if entry.is_empty() or not req.body is String or not Protocol.count(req.base): return false
		if not _journal.previous_format and entry.base_server_revision != req.base: return false
		var expected := _request_for(entry, int(_state.sequence)+1, int(req.base))
		if expected.is_empty() or not Journal.Registry.unique_keys(req.body) or JSON.parse_string(req.body) != JSON.parse_string(expected.body): return false
		expected.body = req.body
		if req != JSON.parse_string(JSON.stringify(expected)):
			return false
	return true

func _valid_entry(entry: Variant, intent: bool = false) -> bool:
	if not entry is Dictionary or not entry.has_all(["local","id","operation","value","status"]) or not Protocol.count(entry.local,1):
		return false
	if not Protocol.matches(entry.id,"\\A[A-Za-z0-9_-]{1,128}\\z") or not entry.status is String:
		return false
	if not _journal.previous_format:
		if not Protocol.count(entry.get("base_server_revision")) or not Protocol.count(entry.get("parent_local")) or entry.parent_local >= entry.local:
			return false
		if entry.has("received_revision") and (not intent or not Protocol.count(entry.received_revision,1)): return false
	if entry.operation == "snapshot":
		if intent:
			var key := _store.key_for_definition(entry.id)
			return not key.is_empty() and entry.value is Dictionary and _store.validate_slot(entry.value,Definition.load_fixture(key)).is_empty()
		return Protocol.valid_progress(entry.value,entry.id)
	return not Protocol.mutation(entry,1,0).is_empty()

func reconciliation() -> Dictionary:
	return {"reason":_blocked, "root":_root, "context":_context.duplicate(), "journal":_journal.path if _journal else "",
		"state":_state.duplicate(true) if _state.get("context") == _context else {}}

func last_error() -> String:
	return _blocked if _blocked != "" else _last_error

func status() -> Dictionary:
	if not _blocked.is_empty(): return {"error":_blocked}
	return _state.duplicate(true)

func _begin() -> bool:
	if _blocked != "" or not _journal.acquire():
		return false
	if FileAccess.get_sha256(_journal.path) != _journal.digest:
		_blocked = "Profil wurde anderweitig verändert; erneut öffnen."
		_journal.release()
		return false
	return true

func _publish(next: Dictionary) -> bool:
	if not _journal.publish(next):
		_blocked = "Journal nicht bestätigt; Wiederanlauf erforderlich."
		return false
	_state = next
	return true

func _mark_generation(generation: String) -> void:
	var next := _state.duplicate(true)
	next.reconcile = generation
	_publish(next)
	_blocked = "Servergeneration geändert; Bestandsabgleich erforderlich."

func observe_generation(generation: String) -> bool:
	if not Protocol.uuid(generation) or not _begin(): return false
	if generation != _state.generation:
		_mark_generation(generation)
	_journal.release()
	return _blocked.is_empty()

func _safe_slot(key: String) -> bool:
	if not key in _store.registered_ids(): return false
	for suffix: String in Store.SaveRevision.SUFFIXES:
		if not Recent.safe_file(_store.path_for(key, suffix)): return false
	return true

func load_slot(definition: Dictionary) -> Dictionary:
	if not _begin(): return {"status":"error","error":_blocked}
	var key := _store.key_for_definition(str(definition.id))
	var result := {"status":"error","error":"Unsicherer Profilpfad."}
	if _safe_slot(key) and definition == Definition.load_fixture(key):
		var protect := _preserve_old(key, definition)
		result = _store.load_slot(definition) if protect else {"status":"error","error":"Alte Rasterfassung nicht gesichert."}
	_journal.release()
	return result

func _preserve_old(key: String, definition: Dictionary) -> bool:
	var next := _state.duplicate(true)
	# Capture original bytes before PE can publish a marker or remove any slot file.
	for suffix: String in Store.SaveRevision.SUFFIXES:
		var path := _store.path_for(key,suffix)
		if _store._parse(path,definition).status == "older":
			var bytes := FileAccess.get_file_as_bytes(path)
			var digest := FileAccess.get_sha256(path)
			var encoded := Marshalls.raw_to_base64(bytes)
			if bytes.is_empty() or encoded.is_empty() or digest != bytes.get_string_from_utf8().sha256_text(): return false
			next.archive[digest] = {"id":definition.id,"suffix":suffix,"bytes":encoded}
	return next.archive == _state.archive or _publish(next)

func recent_record() -> Dictionary:
	if not _begin(): return {}
	_recent.load_record()
	_journal.release()
	return _recent.record.duplicate()

func update_recent(session: Session) -> bool:
	if not _begin(): return false
	_recent.load_record()
	var ok := _recent.edited(session)
	_journal.release()
	return ok

func clear_recent(id: String) -> bool:
	if not _begin(): return false
	_recent.load_record()
	var ok := _recent.clear_matching(id)
	_journal.release()
	return ok


func save(session: Session, view: Dictionary) -> int:
	if _store == null: return 0
	var candidate := _store.slot_snapshot(session,view)
	var key := _store.key_for_definition(str(session.definition.id)) if _store else ""
	if key.is_empty() or not Store.validate_account(candidate, Definition.load_fixture(key)).is_empty() or not _begin(): return 0
	var version := _change_slot(key, {"id":session.definition.id,"operation":"snapshot","value":candidate},
		func() -> String: return _store._write_slot(session,view))
	_journal.release()
	return _confirm(version)

func reset(id: String) -> int:
	if not _begin(): return 0
	var key := _store.key_for_definition(id)
	var version := 0
	if _safe_slot(key):
		var definition := Definition.load_fixture(key)
		version = _change_slot(key, {"id":id,"operation":"reset","value":definition.revision},
			func() -> String: return _store._reset_slot(key))
	_journal.release()
	return _confirm(version)

## Apply only at a safe UI boundary, after validating against the bundled definition.
## A remote observation never changes a dirty entry's edit basis.
func confirm_equal(session: Session, record: Dictionary) -> bool:
	var id: String = session.definition.id
	if not flush_confirmed() or not _begin(): return false
	var next := _state.duplicate(true)
	var ok: bool = next.request.is_empty() and next.abandon.is_empty() and record.get("puzzle_id") == id and Protocol.count(record.get("server_revision"),1)
	var disk := _store.load_slot(session.definition) if ok else {}
	ok = ok and disk.get("status") == "loaded" and not _store.received(record.get("save"),session).is_empty() and Protocol.progress(disk.data) == Protocol.progress(record.save)
	if ok:
		for key: String in next.entries.keys():
			var entry: Dictionary = next.entries[key]
			if entry.id != id: continue
			if entry.operation != "snapshot" or entry.status != "pending" or Protocol.progress(entry.value) != Protocol.progress(record.save) or entry.get("imported",false):
				ok = false
				break
			next.entries.erase(key)
	if ok:
		next.revisions[id] = {"server":record.server_revision,"confirmed_local":next.slots[id].local}
		ok = _publish(next)
	_journal.release()
	if ok: _confirm_stage("comparison",int(next.slots[id].local))
	return ok

func accept_record(session: Session, record: Dictionary) -> bool:
	var id: String = session.definition.id
	if record.get("puzzle_id") != id or record.get("definition_revision") != session.definition.revision or not Protocol.count(record.get("server_revision"),1): return false
	var reset: bool = record.get("kind") == "reset"
	var copy_session := Session.new(session.definition)
	var candidate := {}
	if reset:
		if record.get("save") != null or record.get("validation") != null: return false
	else:
		if record.get("kind") != "snapshot" or record.get("validation") != "progress_structure_checked": return false
		candidate = _store.received(record.get("save"),session)
		if candidate.is_empty(): return false
		Store.apply(candidate,copy_session)
		candidate = _store.slot_snapshot(copy_session,copy_session.view_state)
	if not flush_confirmed() or not _begin(): return false
	var key := _store.key_for_definition(id)
	var ok := false
	var version := 0
	var dirty := false
	for entry: Dictionary in _state.entries.values():
		if entry.id == id and entry.status != "request_abandoned": dirty = true
	var prior := _store.load_slot(session.definition) if _safe_slot(key) else {"status":"error"}
	if not dirty and not session.gesture.active and prior.status in ["fresh","loaded"]:
		var same: bool = prior.status == "fresh" if reset else prior.status == "loaded" and Protocol.progress(prior.data) == Protocol.progress(record.save)
		if same:
			var next := _state.duplicate(true)
			next.revisions[id] = {"server":record.server_revision,"confirmed_local":next.slots.get(id,{}).get("local",0)}
			ok = next == _state or _publish(next)
		else:
			var intent := {"id":id,"operation":"reset" if reset else "snapshot","value":session.definition.revision if reset else candidate,"received_revision":record.server_revision}
			version = _change_slot(key,intent,func() -> String: return _store._reset_slot(key) if reset else _store._write_slot(copy_session,copy_session.view_state))
			ok = version > 0
	_journal.release()
	if version > 0:
		_confirm(version)
		if reset:
			Store.apply(_store.slot_snapshot(copy_session,copy_session.view_state),session)
		else:
			Store.apply(candidate,session)
	return ok

func repair_from_backup(definition: Dictionary) -> int:
	if not _begin(): return 0
	var key := _store.key_for_definition(str(definition.id))
	var version := 0
	if _safe_slot(key) and definition == Definition.load_fixture(key):
		var backup := _store._parse(_store.path_for(key,".bak"),definition)
		if backup.status == "valid" and _store._parse(_store.path_for(key),definition).status != "valid":
			version = _change_slot(key, {"id":definition.id,"operation":"snapshot","value":backup.data},
				func() -> String: return _store._repair_from_backup(definition))
	_journal.release()
	return _confirm(version)

func discard_invalid_backup(definition: Dictionary) -> bool:
	if not _begin(): return false
	var key := _store.key_for_definition(str(definition.id))
	var ok := _safe_slot(key) and definition == Definition.load_fixture(key) and _store._discard_invalid_backup(definition).is_empty()
	_journal.release()
	return ok

func _change_slot(key: String, entry: Dictionary, action: Callable) -> int:
	_last_error = ""
	if not _safe_slot(key) or _state.local >= Protocol.MAX_INTEGER:
		_last_error = "Slotpfad oder Generationsgrenze ungültig."
		return 0
	var next := _state.duplicate(true)
	entry.local = int(next.local) + 1
	entry.status = "pending"
	entry.base_server_revision = _state.revisions.get(entry.id,{}).get("server",0)
	entry.parent_local = 0
	# Inherit the actual local edit line, independently of later observations.
	var latest := 0
	for earlier: Dictionary in _state.entries.values():
		if not earlier.get("imported",false) and earlier.id == entry.id and earlier.operation == "snapshot" and earlier.status == "pending" and earlier.local > latest and entry.operation == "snapshot" and earlier.value.definition_revision == entry.value.definition_revision:
			latest = int(earlier.local)
			entry.base_server_revision = earlier.base_server_revision
			entry.parent_local = _state.request.get("local",0) if earlier.local == _state.request.get("local",-1) else earlier.parent_local
	if entry.operation == "snapshot":
		entry.primary_sha256 = (JSON.stringify(entry.value,"",true,true) + "\n").sha256_text()
	next.intent = entry
	if not _publish(next): return 0
	var before := _slot_hashes(key)
	var error: String = action.call()
	if not error.is_empty():
		_last_error = error
		# Only cancel an intent when all slot bytes are unchanged.
		if before == _slot_hashes(key):
			next = _state.duplicate(true)
			next.intent = {}
			_publish(next)
		else:
			_blocked = "Unterbrochene Speicherung; erneut öffnen."
		return 0
	if not _recover_intent(): return 0
	return int(entry.local)

func _slot_hashes(key: String) -> Array:
	var hashes := []
	for suffix: String in Store.SaveRevision.SUFFIXES:
		hashes.append(Store.SaveRevision.hash_file(_store.path_for(key,suffix)))
	return hashes

func _matches_primary(entry: Dictionary) -> bool:
	var key := _store.key_for_definition(str(entry.id))
	if not _safe_slot(key): return false
	if entry.operation == "reset":
		for suffix: String in Store.SaveRevision.SUFFIXES:
			if FileAccess.file_exists(_store.path_for(key,suffix)): return false
		return true
	var primary := _store._parse(_store.path_for(key), Definition.load_fixture(key))
	return FileAccess.get_sha256(_store.path_for(key)) == entry.get("primary_sha256") and primary.status == "valid" and primary.data == JSON.parse_string(JSON.stringify(entry.value,"",true,true))

func _recover_intent() -> bool:
	if _state.intent.is_empty(): return true
	var entry: Dictionary = _state.intent
	if not _matches_primary(entry):
		_blocked = "Spielstand und Schreibabsicht erfordern Wiederherstellung."
		return false
	var next := _state.duplicate(true)
	next.local = entry.local
	next.intent = {}
	if entry.operation == "snapshot":
		entry = entry.duplicate(true)
		entry.erase("primary_sha256")
		entry.value = Protocol.progress(entry.value)
		var digest := JSON.stringify(entry.value,"",true,true).sha256_text()
		var unchanged: bool = next.slots.get(entry.id,{}).get("digest") == digest
		next.slots[entry.id] = {"local":entry.local,"digest":digest}
		if unchanged and not entry.has("received_revision"): return _publish(next)
	else:
		next.slots.erase(entry.id)
	if entry.has("received_revision"):
		next.revisions[entry.id] = {"server":entry.received_revision,"confirmed_local":entry.local}
		return _publish(next)
	# A prepared request, a rejected/conflicting version or an old raster must
	# survive. Compact only superseded, already durable pending snapshots.
	for key: String in next.entries.keys():
		var previous: Dictionary = next.entries[key]
		if (entry.operation == "snapshot" and previous.operation == "snapshot"
				and previous.id == entry.id and previous.value.definition_revision == entry.value.definition_revision
				and not previous.get("imported",false) and previous.status == "pending" and _durable.get(key,false)
				and previous.local != next.request.get("local",-1)):
			next.entries.erase(key)
	next.entries[str(int(entry.local))] = entry
	return _publish(next)

func _confirm(version: int) -> int:
	if version > 0:
		var ticket := {"context":_context.duplicate(),"generation":_state.generation,"local":version,"ticket":ResourceUID.id_to_text(ResourceUID.create_id())}
		_awaiting[str(version)] = ticket
		_durable[str(version)] = false
		_adapter.confirm_local(ticket, _local_completed.bind(ticket.duplicate(true)))
	return version

func _local_completed(actual: Dictionary, success: bool, expected: Dictionary) -> void:
	var key := str(int(expected.local))
	if actual == expected and _awaiting.get(key) == expected:
		_awaiting.erase(key)
		_durable[key] = success

func locally_confirmed(version: int) -> bool:
	return _blocked.is_empty() and _durable.get(str(version),false)


func decision(id: String, operation: String, value: Variant, basis: int = -1) -> int:
	if not operation in ["discard","resolve","restore"] or not _begin(): return 0
	var version := int(_state.local) + 1
	var entry := {"local":version,"id":id,"operation":operation,"value":value,"status":"pending",
		"base_server_revision":basis if basis >= 0 else _state.revisions.get(id,{}).get("server",0),"parent_local":0}
	var ok := Protocol.count(version,1) and not _store.key_for_definition(id).is_empty() and not Protocol.mutation(entry,1,0).is_empty()
	if ok:
		var next := _state.duplicate(true)
		next.local = version
		next.entries[str(version)] = entry
		ok = _publish(next)
	_journal.release()
	return _confirm(version if ok else 0)

func _request_for(entry: Dictionary, sequence: int, base: int) -> Dictionary:
	var body := Protocol.mutation(entry, sequence, base)
	if body.is_empty(): return {}
	var raw := JSON.stringify(body, "", true, true)
	if raw.to_utf8_buffer().size() > 16*1024*1024: return {}
	return {"context":_root,"device":_context.device,"generation":_state.generation,"local":int(entry.local),
		"seq":sequence,"base":base,"method":"POST","path":"/v1/puzzles/%s/mutations" % entry.id,"body":raw}

func _first_pending_for_slot(entry: Dictionary) -> bool:
	for other: Dictionary in _state.entries.values():
		if other.id == entry.id and other.local < entry.local and other.status == "pending":
			return false
	return true

func prepare(version: int, base: int) -> Dictionary:
	if not locally_confirmed(version) or not _begin(): return {}
	var result := {}
	var entry: Dictionary = _state.entries.get(str(version),{})
	if _state.request.is_empty() and entry.get("status") == "pending" and _first_pending_for_slot(entry):
		if base != entry.base_server_revision or not _barrier.is_empty():
			_journal.release()
			return {}
		result = _request_for(entry,int(_state.sequence)+1,base)
		if not result.is_empty():
			var next := _state.duplicate(true)
			next.request = result
			if entry.operation == "snapshot" and not entry.get("imported",false):
				for younger: Dictionary in next.entries.values():
					if not younger.get("imported",false) and younger.local > version and younger.id == entry.id and younger.status == "pending" and younger.operation == "snapshot" and younger.value.definition_revision == entry.value.definition_revision and younger.base_server_revision == base:
						younger.parent_local = version
			if not _publish(next): result = {}
	_journal.release()
	if not result.is_empty(): _confirm_stage("request",version)
	return result.duplicate(true) if _barrier.is_empty() else {}

func _confirm_stage(stage: String, version: int) -> void:
	_barrier = {"ticket":ResourceUID.id_to_text(ResourceUID.create_id()),"context":_context.duplicate(),"generation":_state.generation,"stage":stage,"local":version,"digest":_journal.digest}
	_barrier_error = false
	_journal.confirm_local(_barrier.duplicate(true), _stage_complete.bind(_barrier.duplicate(true)))

func _stage_complete(actual: Dictionary, success: bool, expected: Dictionary) -> void:
	if actual != expected or _barrier != expected: return
	_barrier_error = not success
	if success: _barrier = {}

func retry_local() -> void:
	if _barrier_error:
		_confirm_stage(_barrier.stage,int(_barrier.local))
	for key: String in _durable.keys():
		if not _durable[key] and not _awaiting.has(key): _confirm(int(key))

func local_failed() -> bool:
	return _barrier_error or (_awaiting.is_empty() and _durable.values().has(false))

func flush_confirmed() -> bool:
	return _blocked.is_empty() and _awaiting.is_empty() and not _durable.values().has(false) and _barrier.is_empty()

func resume_request() -> Dictionary:
	if not _barrier.is_empty() or not _begin(): return {}
	var request: Dictionary = _state.request.duplicate(true)
	_journal.release()
	return request

func abandon_order(original: Dictionary) -> Dictionary:
	var body := {"format":"picross-request-abandon/v1","request_seq":int(original.seq),"expected_last_request_seq":int(original.seq)-1,
		"puzzle_id":str(original.path).get_slice("/",3),"request_hash":Protocol.request_hash(original)}
	return {"path":"/v1/device/abandon","method":"POST","context":original.context,"device":original.device,
		"generation":original.generation,"body":JSON.stringify(body,"",true,true)}

func prepare_abandon(original: Dictionary) -> bool:
	if not flush_confirmed() or original.is_empty() or not _begin(): return false
	var ok := false
	if _same_request(original) and _state.abandon.is_empty():
		var next := _state.duplicate(true)
		next.abandon = abandon_order(original)
		ok = _publish(next)
	_journal.release()
	if ok: _confirm_stage("abandon", int(original.local))
	return ok

func _same_request(original: Dictionary) -> bool:
	return JSON.parse_string(JSON.stringify(original)) == JSON.parse_string(JSON.stringify(_state.request))

func receive(original: Dictionary, generation: String, http_status: int, reply: Dictionary) -> bool:
	if original.is_empty() or not _barrier.is_empty() or not _begin(): return false
	if _same_request(original) and Protocol.uuid(generation) and generation != _state.generation:
		_mark_generation(generation)
		_journal.release()
		return false
	var ok: bool = _same_request(original) and generation == _state.generation and Protocol.valid_reply(original,http_status,reply)
	if ok:
		var next := _state.duplicate(true)
		var key := str(int(original.local))
		var entry: Dictionary = next.entries[key]
		next.receipt = {"request":original.duplicate(true),"status":http_status,"reply":reply.duplicate(true)}
		if reply.sequence_consumed:
			next.sequence = original.seq
			if reply.code == "ok" and not entry.get("imported",false):
				next.revisions[entry.id] = {"server":reply.server_revision,"confirmed_local":entry.local if reply.code == "ok" and entry.operation in ["snapshot","reset"] else next.revisions.get(entry.id,{}).get("confirmed_local",0)}
			next.request = {}
			next.abandon = {}
			if reply.code == "ok":
				for younger: Dictionary in next.entries.values():
					if not younger.get("imported",false) and younger.id == entry.id and younger.status == "pending" and younger.operation == "snapshot" and entry.operation == "snapshot" and younger.value.definition_revision == entry.value.definition_revision and younger.parent_local == entry.local and younger.base_server_revision == original.base:
						younger.base_server_revision = reply.server_revision
						younger.parent_local = 0
				if entry.operation in ["resolve","discard"]:
					for prior_key: String in next.entries.keys():
						var prior: Dictionary = next.entries[prior_key]
						if prior.id == entry.id and prior.status == "conflict_saved" and prior.get("response",{}).get("candidate_id") == entry.value:
							next.entries.erase(prior_key)
				next.entries.erase(key)
			else:
				if reply.code == "request_abandoned":
					next.archive[Protocol.request_hash(original)] = {"request":original.duplicate(true),"receipt":next.receipt.duplicate(true)}
				entry.status = reply.code
				entry.response = reply.duplicate(true)
		else:
			next.reconcile = reply.code
		ok = _publish(next)
		if ok and reply.sequence_consumed: _confirm_stage("receipt",int(original.local))
		if ok and not reply.sequence_consumed:
			_blocked = "Gerätesequenz erfordert Abgleich."
	_journal.release()
	return ok
