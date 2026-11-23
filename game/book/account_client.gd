extends Node
const Access = preload("res://model/sync_access.gd")
const Profile = preload("res://model/account_profile.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const Transport = preload("res://model/sync_transport.gd")
const Schedule = preload("res://model/sync_schedule.gd")
const Dialog = preload("res://book/account_dialog.gd")
const Session = preload("res://model/session.gd")
var app: Control
var profile: Profile
var access := Access.new()
var transport := Transport.new()
var schedule := Schedule.new()
var identity := {}
var inventory := {}
var transport_busy := false
var changing := false
var inventory_ready := false
var problem := ""
var dialog: AcceptDialog
var epoch := 0

func configure(owner: Control) -> void:
	app = owner
	add_child(transport)
	dialog = Dialog.new()
	add_child(dialog)
	dialog.configure(self)
	var group: VBoxContainer = app._settings_group("Spielerkonto","account-settings")
	group.add_child(app._text_button("Konto verwalten",dialog.open))
	if not access.server.is_empty() and not access.active().is_empty(): resume_local.call_deferred(access.active())

func safe_switch() -> bool:
	app._cancel_interaction()
	if not app._flush_current(): return false
	if profile != null and not profile.flush_confirmed():
		profile.retry_local()
		return false
	if OS.has_feature("web"):
		var storage: JavaScriptObject = JavaScriptBridge.get_interface("window").picrossStorage
		if storage.pending or storage.error != "" or storage.recentPending: return false
	return true

func activate(data: Dictionary, fresh: bool) -> bool:
	var target := Profile.new()
	if not target.open(access.server,data.account_id,data.device_id,data.generation,fresh):
		problem = target.last_error()
		return false
	if not await access.publish(access.session_path(data.account_id),data) or not await access.choose(data.account_id):
		problem = "Profilwahl konnte nicht dauerhaft gespeichert werden."
		return false
	bind(target,data)
	return true

func bind(target: Profile, data: Dictionary) -> void:
	epoch += 1
	identity = data
	profile = target
	inventory = {}
	inventory_ready = false
	schedule = Schedule.new()
	transport_busy = false
	problem = ""
	app.recent_signature = ""
	app.rebind_profile(profile)
	if profile:
		schedule.auth_paused = identity.token.is_empty() or Time.get_unix_time_from_datetime_string(identity.expires_at) <= Time.get_unix_time_from_system()
		schedule.connected()
	refresh_status()

func resume_local(account: String) -> void:
	if changing or not safe_switch(): return
	changing = true
	var data := access.credentials(account)
	if data.is_empty(): problem = "Lokales Kontoprofil unlesbar."
	else: await activate(data,false)
	changing = false
	refresh_status()

func authenticate(action: String, username: String, password: String, code: String) -> void:
	if changing or access.server.is_empty() or not safe_switch(): return
	changing = true
	var body := {}
	var saved: Dictionary = access.credentials(access.accounts().get(username.to_lower(),""))
	match action:
		"login":
			body = {"username":username,"password":password,"device_id":saved.get("device_id"),"device_name":OS.get_name()}
		"register":
			body = {"username":username,"password":password,"invitation":code,"device_name":OS.get_name()}
		"recover": body = {"username":username,"new_password":password,"recovery_code":code}
		"recovery-code": body = {"password":password}
	var session_headers := identity if action == "recovery-code" else {}
	var response := await transport.send(access.server,"/v1/auth/"+action,HTTPClient.METHOD_POST,JSON.stringify(body),session_headers)
	var result: Dictionary = response.body
	if response.status not in [200,201] or not Protocol.uuid(response.generation):
		problem = "Dienst nicht erreichbar." if response.status == 0 else "Kontoanfrage abgelehnt (HTTP %d)." % response.status
	elif action in ["recover","recovery-code"]:
		problem = ""
		dialog.show_code(result.get("recovery_code",""))
	elif Protocol.uuid(result.get("account_id")) and Protocol.uuid(result.get("device_id")) and Protocol.matches(result.get("token"),"\\A[A-Za-z0-9_-]{43}\\z") and result.get("username") == username.to_lower() and result.get("expires_at") is String and (saved.is_empty() or (saved.account_id == result.account_id and saved.device_id == result.device_id)):
		var data := {"server":access.server,"account_id":result.account_id,"device_id":result.device_id,"username":result.username,
			"generation":response.generation,"token":result.token,"expires_at":result.expires_at}
		var root := access.directory.path_join(data.account_id)
		if safe_switch():
			await activate(data,not DirAccess.dir_exists_absolute(root))
		if action == "register": dialog.show_code(result.get("recovery_code",""))
	else: problem = "Ungültige Kontobestätigung."
	changing = false
	refresh_status()

func logout() -> void:
	if changing or profile == null or not safe_switch(): return
	changing = true
	var original := identity.duplicate()
	var offline := original.duplicate()
	offline.token = ""
	if not await access.choose("") or not await access.publish(access.session_path(original.account_id),offline):
		problem = "Lokale Abmeldung konnte nicht gespeichert werden."
	else:
		bind(null,{})
		problem = "Lokal abgemeldet."
		refresh_status()
		if not original.token.is_empty():
			var result := await transport.send(access.server,"/v1/auth/logout",HTTPClient.METHOD_POST,"",original)
			if result.status == 204 and result.generation == original.generation: problem = "Abgemeldet."
	changing = false
	refresh_status()

func read(path: String, method: int = HTTPClient.METHOD_GET, raw: String = "") -> Dictionary:
	var stamp := epoch
	var result := await transport.send(access.server,path,method,raw,identity.duplicate())
	if epoch != stamp: return {}
	if result.status == 0 or result.status == 429 or result.status >= 500:
		schedule.transient(result.retry_after)
		problem = "Offline · lokal verfügbar"
		return {}
	if result.generation != identity.generation:
		if Protocol.uuid(result.generation): profile.observe_generation(result.generation)
		schedule.auth_paused = true
		problem = "Servergeneration prüfen."
		return {}
	if result.status == 401:
		schedule.auth_paused = true
		problem = "Erneut anmelden"
		return {}
	return result

func fetch_pages(path: String) -> Dictionary:
	var cursor := ""
	var seen := {}
	var items := []
	while true:
		var result := await read(path+("?cursor="+cursor.uri_encode() if cursor != "" else ""))
		if result.get("status") != 200: return {}
		var page: Dictionary = result.body
		if page.size() != 2 or not page.has_all(["items","next_cursor"]) or not page.items is Array or page.items.size() > 100: return {}
		items.append_array(page.items)
		if page.next_cursor == null: break
		if not Protocol.matches(page.next_cursor,"\\A[A-Za-z0-9_-]{1,1024}\\z") or seen.has(page.next_cursor) or page.items.is_empty() or seen.size() >= 2000: return {}
		cursor = page.next_cursor
		seen[cursor] = true
	return {"items":items}

func reconcile() -> bool:
	var own := await read("/v1/account")
	if own.get("status") != 200 or own.body.get("account_id") != identity.account_id or own.body.get("device_id") != identity.device_id or own.body.get("username") != identity.username: return false
	var pages := await fetch_pages("/v1/puzzles")
	if pages.is_empty(): return false
	var listing := {}
	for row: Variant in pages.items:
		if not row is Dictionary or row.size() != 3 or not Protocol.matches(row.get("puzzle_id"),"\\A[A-Za-z0-9_-]{1,128}\\z") or not Protocol.count(row.get("server_revision")) or not Protocol.count(row.get("conflict_count")) or listing.has(row.puzzle_id): return false
		listing[row.puzzle_id] = row
	var checkpoint := await read("/v1/device/checkpoint")
	if checkpoint.get("status") != 200 or not Protocol.valid_checkpoint(checkpoint.body,identity.account_id,identity.device_id): return false
	var state := profile.status()
	var request := profile.resume_request()
	var seq: int = int(checkpoint.body.last_request_seq)
	if not request.is_empty() and request.seq == seq and Protocol.request_hash(request) == checkpoint.body.last_request_hash:
		var raw: String = checkpoint.body.response_body
		if not Access.Registry.unique_keys(raw): return false
		var receipt: Variant = JSON.parse_string(raw)
		if not receipt is Dictionary or not profile.receive(request,identity.generation,int(checkpoint.body.response_status),receipt): return false
	elif seq != state.get("sequence"):
		problem = "Gerätebeleg widerspricht dem lokalen Auftrag."
		return false
	inventory = listing
	for id: String in inventory:
		if not app.session_indices.has(id):
			problem = "Unbekannte Rätseldefinition."
			continue
		if not await pull(id): return false
	inventory_ready = true
	return true

func pull(id: String) -> bool:
	if not profile.flush_confirmed(): return false
	var result := await read("/v1/puzzles/"+id)
	if result.get("status") == 404 and inventory[id].server_revision == 0: return true
	if result.get("status") != 200: return false
	var record: Dictionary = result.body
	var index: int = app.session_indices[id]
	var slot: Session = app.sessions[index]
	if record.get("puzzle_id") != id or not Protocol.count(record.get("server_revision"),1): return false
	if record.get("definition_revision") != slot.definition.revision:
		problem = "Inkompatible Rasterrevision."
		return true
	if record.get("kind") == "snapshot" and profile._store.received(record.get("save"),slot).is_empty(): return false
	var state := profile.status()
	for entry: Dictionary in state.entries.values():
		if entry.id == id: return true
	if app.presentation_locked or (slot == app.session and app._puzzle_view_active()): return false
	if not profile.accept_record(slot,record): return false
	app.slot_status[index] = "fresh" if record.kind == "reset" else "loaded"
	if slot == app.session: app._bind_session(index)
	if app.album.visible: app.album.present(app.sessions,app.slot_status,app.slot_errors,app.catalog_error,id)
	return true

func take_checkpoint(req: Dictionary, cp: Dictionary) -> bool:
	if not Protocol.valid_checkpoint(cp,identity.account_id,identity.device_id) or cp.last_request_seq != req.seq or cp.last_request_hash != Protocol.request_hash(req): return false
	if not Access.Registry.unique_keys(cp.response_body): return false
	var receipt: Variant = JSON.parse_string(cp.response_body)
	return receipt is Dictionary and profile.receive(req,identity.generation,int(cp.response_status),receipt)

func abandon(req: Dictionary) -> void:
	if changing or transport_busy or not inventory_ready or not profile: return
	changing = true
	var cp := await read("/v1/device/checkpoint")
	if cp.get("status") == 200 and Protocol.valid_checkpoint(cp.body,identity.account_id,identity.device_id):
		if cp.body.last_request_seq == req.seq:
			if not take_checkpoint(req,cp.body): problem = "Gerätebeleg prüfen."
		elif cp.body.last_request_seq == int(req.seq)-1 and profile.prepare_abandon(req):
			schedule.connected()
	changing = false

func import_guest(ids: Array) -> void:
	if changing or profile == null or not safe_switch(): return
	var guest: RefCounted = app.create_store()
	for id: String in ids:
		if not app.session_indices.has(id): continue
		var index: int = app.session_indices[id]
		var slot: Session = app.sessions[index]
		var key: String = guest.key_for_definition(id)
		# Read-only import: load_slot may run the guest's automatic revision reset.
		var src: Dictionary = guest._parse(guest.path_for(key),slot.definition)
		if src.status != "valid": continue
		var imported := Session.new(slot.definition)
		Profile.Store.apply(src.data,imported)
		if profile.save(imported,imported.view_state) == 0:
			problem = "Gastimport konnte nicht gespeichert werden."
			break
		app.sessions[index] = imported
		app.slot_status[index] = "loaded"
		if slot == app.session: app._bind_session(index)
	schedule.collect()
	app.present_album()

func decide(id: String, operation: String, value: Variant, base: int) -> void:
	if changing or transport_busy or profile == null or not safe_switch(): return
	changing = true
	var current := await read("/v1/puzzles/"+id)
	if current.get("status") not in [200,404] or current.body.get("server_revision",0) != base:
		problem = "Fassung geändert. Bitte erneut auswählen."
	else:
		var path := "/history/"+str(int(value)) if operation == "restore" else "/conflicts/"+str(value)
		var result := await read("/v1/puzzles/"+id+path)
		if result.get("status") != 200 or result.body.get("puzzle_id") != id: problem = "Fassung nicht mehr verfügbar."
		else:
			var slot: Session = app.sessions[app.session_indices[id]]
			var compatible: bool = result.body.get("definition_revision") == slot.definition.revision and (result.body.get("kind") == "reset" or not profile._store.received(result.body.get("save"),slot).is_empty())
			if operation != "discard" and not compatible: problem = "Inkompatible Rasterrevision."
			elif profile.decision(id,operation,value,base) > 0: schedule.collect()
	changing = false

func next_request() -> Dictionary:
	var req := profile.resume_request()
	if not req.is_empty(): return req
	var state := profile.status()
	if not state.has("entries"): return {}
	var chosen := {}
	for entry: Dictionary in state.entries.values():
		if entry.status != "pending" or not profile.locally_confirmed(int(entry.local)): continue
		if chosen.is_empty() or entry.local < chosen.local: chosen = entry
	if chosen.is_empty(): return {}
	return profile.prepare(int(chosen.local),int(chosen.base_server_revision))

func send_batch() -> void:
	if transport_busy or changing or profile == null or not profile.flush_confirmed() or schedule.auth_paused: return
	transport_busy = true
	var stamp := epoch
	schedule.due = INF
	if not inventory_ready and not await reconcile():
		if stamp != epoch: return
		if not schedule.auth_paused and schedule.due == INF: schedule.transient(0)
		if problem.is_empty(): problem = "Bestandsabgleich ausstehend."
	else:
		if stamp != epoch: return
		var req := next_request()
		if not req.is_empty() and not profile.status().abandon.is_empty():
			var order: Dictionary = profile.status().abandon
			var result := await read(order.path,HTTPClient.METHOD_POST,order.body)
			if epoch != stamp: return
			if result.get("status") == 200 and take_checkpoint(req,result.body):
				inventory_ready = false
				schedule.connected()
			elif not result.is_empty(): problem = "Abbruchbeleg prüfen."
		elif not req.is_empty():
			var response := await read(req.path,HTTPClient.METHOD_POST,req.body)
			if stamp != epoch: return
			if not response.is_empty():
				if profile.receive(req,response.generation,response.status,response.body):
					if JSON.parse_string(req.body).operation in ["resolve","discard","restore"] or response.body.get("outcome") == "conflict":
						inventory_ready = false
					problem = ""
					schedule.success()
					schedule.connected()
				else: problem = "Serverbeleg prüfen."
		elif not profile.flush_confirmed(): schedule.connected()
		else: schedule.success()
	transport_busy = false
	refresh_status()

func _process(_delta: float) -> void:
	if app == null or profile == null: return
	if schedule.ready() and not transport_busy: send_batch()
	refresh_status()

func exiting() -> void:
	if profile and inventory_ready and schedule.now() >= schedule.retry_at: send_batch()

func refresh_status() -> void:
	if app == null or app.account_status == null: return
	var value := "Gast"
	if profile:
		var state: Dictionary = profile.status()
		var detail := "Abgleich ausstehend"
		if not problem.is_empty(): detail = problem
		elif state.has("error"): detail = state.error
		elif schedule.auth_paused: detail = "Erneut anmelden"
		elif transport_busy: detail = "Abgleich läuft"
		elif not profile.flush_confirmed(): detail = "Lokale Sicherung ausstehend"
		elif state.entries.values().any(func(entry: Dictionary) -> bool: return entry.status != "pending"): detail = "Konflikt / Entscheidung nötig"
		elif inventory.values().any(func(row: Dictionary) -> bool: return row.conflict_count > 0): detail = "Konflikt"
		elif not state.entries.is_empty(): detail = "Übertragung ausstehend"
		elif inventory_ready: detail = "Synchronisiert"
		value = str(identity.username)+" · "+detail
	elif not problem.is_empty(): value += " · "+problem
	if app.account_status.text != value:
		app.account_status.text = value
		app._layout_book()
