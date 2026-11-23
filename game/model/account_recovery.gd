extends RefCounted
## Recovery is scoped to the freshly authenticated account and its exclusive journal.
const Protocol = preload("res://model/sync_protocol.gd")
const Store = preload("res://model/account_save_store.gd")
const Journal = preload("res://model/sync_journal.gd")
const Definition = preload("res://model/definition.gd")
var root: String
var context: Dictionary
var generation: String
var journal: Journal
var store: Store
var image := {}
var original := {}
var source_hash := ""
var result := ""
var effect := ""
var old_epoch := false
var old_device := false
var unknown_bytes := false

func _init(server: String, account: String, device: String, gen: String) -> void:
	context = {"server":server,"account":account,"device":device}
	generation = gen
	root = "user://p1/accounts".path_join(server.sha256_text()).path_join(account)
	journal = Journal.new(root)
	store = Store.new(root.path_join("saves"))

func inspect(checkpoint: Dictionary, new_device: bool) -> bool:
	if not Protocol.valid_checkpoint(checkpoint,context.account,context.device) or not journal.acquire(): return false
	image = journal.read_image()
	source_hash = FileAccess.get_sha256(journal.path) if FileAccess.file_exists(journal.path) else ""
	journal.release()
	if image.is_empty():
		unknown_bytes = true
		effect = "Metadaten fehlen oder sind beschädigt. Frühere Serverwirkung unbekannt."
		return true
	var bound: Variant = image.get("context")
	if not bound is Dictionary or bound.get("server") != context.server or bound.get("account") != context.account or not Protocol.uuid(bound.get("device")): return false
	old_device = bound.device != context.device
	old_epoch = image.get("generation") != generation
	if not Protocol.uuid(image.get("generation")) or (old_device and not new_device): return false
	if not image.get("request") is Dictionary: return false
	original = image.request.duplicate(true)
	if original.is_empty():
		effect = "Lokalen und aktuellen Serverbestand neu vergleichen."
		return true
	if not original.has_all(["seq","local","body","method","path","base","context","device","generation"]) or original.context != root or original.device != bound.device or original.generation != image.generation: return false
	if original.method != "POST" or not Protocol.matches(original.path,"\\A/v1/puzzles/[A-Za-z0-9_-]{1,128}/mutations\\z") or not original.body is String or not Journal.Registry.unique_keys(original.body): return false
	var body: Variant = JSON.parse_string(original.body)
	if not body is Dictionary or not Protocol.count(original.seq,1) or original.seq != body.get("request_seq") or not Protocol.count(original.base) or original.base != body.get("base_server_revision") or body.get("format") != Protocol.FORMAT: return false
	if old_epoch or old_device or original.seq < checkpoint.last_request_seq:
		effect = "Ursprünglicher Auftrag nicht mehr ausführbar. Seine frühere Wirkung ist unbekannt."
	elif original.seq == checkpoint.last_request_seq:
		if not verify_receipt(checkpoint): return false
		effect = "Vorhandenen Originalbeleg sichern und Bestände vergleichen."
	elif original.seq == checkpoint.last_request_seq+1:
		effect = "Offenen Originalauftrag ausdrücklich beenden und beide Bestände erhalten."
	else: return false
	return true

func verify_receipt(cp: Dictionary) -> bool:
	if not Protocol.valid_checkpoint(cp, context.account,context.device) or original.is_empty() or cp.last_request_seq != original.seq or cp.last_request_hash != Protocol.request_hash(original): return false
	if not Journal.Registry.unique_keys(cp.response_body): return false
	var inner: Variant = JSON.parse_string(cp.response_body)
	return inner is Dictionary and Protocol.valid_reply(original,int(cp.response_status),inner) and inner.sequence_consumed

func archive(path: String) -> bool:
	if not Journal.Recent.safe_file(path): return false
	if not FileAccess.file_exists(path): return true
	var bytes := FileAccess.get_file_as_bytes(path)
	var hash := FileAccess.get_sha256(path)
	if hash.is_empty(): return false
	var dest := root.path_join("recovery").path_join(hash)
	if not Journal.Recent.safe_file(dest) or DirAccess.make_dir_recursive_absolute(dest.get_base_dir()) != OK: return false
	if not FileAccess.file_exists(dest):
		var file := FileAccess.open(dest,FileAccess.WRITE)
		if not file: return false
		if not file.store_buffer(bytes): return false
		file.flush()
		if file.get_error() != OK: return false
		file.close()
	return FileAccess.get_sha256(dest) == hash and FileAccess.get_sha256(path) == hash

func current_source() -> bool:
	if source_hash.is_empty(): return not FileAccess.file_exists(journal.path)
	return FileAccess.get_sha256(journal.path) == source_hash

func order() -> Dictionary:
	var raw := {"format":"picross-request-abandon/v1","request_seq":int(original.seq),"expected_last_request_seq":int(original.seq)-1,
		"request_hash":Protocol.request_hash(original),"puzzle_id":str(original.path).get_slice("/",3)}
	return {"original":original.duplicate(true),"context":context.duplicate(),"generation":generation,
		"source_hash":source_hash,"path":"/v1/device/abandon","method":"POST","body":JSON.stringify(raw,"",true,true)}

func finish(cp: Dictionary, listings: Dictionary) -> bool:
	if not Protocol.valid_checkpoint(cp,context.account,context.device) or not journal.acquire(): return false
	var ok := current_source() and archive(journal.path) and archive(journal.path+".tmp")
	if ok: ok = publish_recovery(cp,listings)
	journal.release()
	return ok

func publish_recovery(cp: Dictionary, listings: Dictionary) -> bool:
	if not original.is_empty() and not old_epoch and not old_device:
		if original.seq > cp.last_request_seq or (original.seq == cp.last_request_seq and not verify_receipt(cp)): return false
	var next := {"context":context.duplicate(),"generation":generation,"local":0,"sequence":cp.last_request_seq,
		"slots":{},"entries":{},"request":{},"receipt":{},"intent":{},"revisions":{},"archive":{},"reconcile":"","abandon":{}}
	next.archive["recovery"] = {"original_sha256":source_hash,"checkpoint":cp.duplicate(true),"effect":effect,"prior_request":original.duplicate(true)}
	for key: String in store.registered_ids():
		var definition := Definition.load_fixture(key)
		for suffix: String in Store.SaveRevision.SUFFIXES:
			var path := store.path_for(key,suffix)
			if not archive(path): return false
			if FileAccess.file_exists(path) and store._parse(path,definition).status != "valid": return false
		var primary := store._parse(store.path_for(key),definition)
		if primary.status == "missing":
			if FileAccess.file_exists(store.path_for(key,".bak")) or FileAccess.file_exists(store.path_for(key,".tmp")): return false
			continue
		var progress := Protocol.progress(primary.data)
		var version: int = int(next.local)+1
		next.local = version
		var digest := JSON.stringify(progress,"",true,true).sha256_text()
		next.slots[definition.id] = {"local":version,"digest":digest}
		next.entries[str(version)] = {"local":version,"id":definition.id,"operation":"snapshot","value":progress,"status":"recovery_choice",
			"base_server_revision":listings.get(definition.id,{}).get("server_revision",0),"parent_local":0}
	journal.digest = source_hash
	return journal.publish(next)
