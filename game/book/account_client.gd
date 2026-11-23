extends Node
const Access = preload("res://model/sync_access.gd")
const Profile = preload("res://model/account_profile.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const Recovery = preload("res://model/account_recovery.gd")
const Transport = preload("res://model/sync_transport.gd")
const Schedule = preload("res://model/sync_schedule.gd")
const Dialog = preload("res://book/account_dialog.gd")
const Session = preload("res://model/session.gd")
const FLUSH_FEEDBACK := "Lokale Sicherung ausstehend oder fehlgeschlagen. Sicherung prüfen und erneut versuchen."
const INVALID_REPLY := "Ungültige Antwort des Kontodiensts. Bitte erneut versuchen."
var app: Control
var profile: Profile
var access := Access.new()
var transport: Transport
var schedule := Schedule.new()
var identity := {}
var inventory := {}
var transport_busy := false
var changing := false
var inventory_ready := false
var problem := ""
var dialog: Dialog
var recovery_session := {}
var recovery_device := false
var epoch := 0
var status_key := []
var unresolved_inventory := false
var device_schedules := {}

func configure(owner: Control) -> void:
	app = owner
	transport = app.book.account_transport
	dialog = Dialog.new()
	var group: VBoxContainer = app._settings_group("Spielerkonto","account-settings")
	group.add_child(dialog)
	dialog.configure(self)
	refresh_status()
	if not access.server.is_empty() and not access.active().is_empty(): _startup.call_deferred(access.active())

func _startup(id: String) -> void:
	if OS.has_feature("web"):
		var storage: JavaScriptObject = JavaScriptBridge.get_interface("window").picrossStorage
		while storage.pending and storage.error == "": await get_tree().process_frame
	while app.presentation_locked: await get_tree().process_frame
	if epoch == 0 and not changing: await resume_local(id)

func safe_switch() -> bool:
	if app.presentation_locked: return false
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
	var marker := {"server":data.server,"account_id":data.account_id,"device_id":data.device_id,"username":data.username}
	if not await access.publish(access.session_path(data.account_id),data) or not await access.publish(access.directory.path_join(data.account_id).path_join("identity.json"),marker) or not await access.choose(data.account_id):
		problem = "Profilwahl konnte nicht dauerhaft gespeichert werden."
		return false
	bind(target,data)
	return true

func bind(target: Profile, data: Dictionary) -> void:
	var profile_changed: bool = identity.get("account_id","") != data.get("account_id","")
	epoch += 1
	recovery_session = {}
	identity = data
	profile = target
	inventory = {}
	unresolved_inventory = false
	inventory_ready = false
	if profile:
		var key := "%s/%s/%s" % [data.server,data.account_id,data.device_id]
		if not device_schedules.has(key): device_schedules[key] = Schedule.new()
		schedule = device_schedules[key]
		schedule.active_since = INF
	else: schedule = Schedule.new()
	transport_busy = false
	problem = ""
	app.recent_signature = ""
	app.rebind_profile(profile,profile_changed)
	if profile:
		schedule.auth_paused = identity.token.is_empty() or Time.get_unix_time_from_datetime_string(identity.expires_at) <= Time.get_unix_time_from_system()
		schedule.connected()
	refresh_status()

func resume_local(account: String) -> void:
	if changing or dialog.has_code(): return
	if not safe_switch():
		show_feedback(FLUSH_FEEDBACK)
		return
	start_action("Lokales Kontoprofil wird geöffnet …")
	var data := access.credentials(account)
	if data.is_empty():
		finish_action("Lokales Kontoprofil unlesbar. Bitte erneut anmelden.")
	elif await activate(data,false):
		finish_action("Lokales Kontoprofil geöffnet.")
	else:
		finish_action("Lokales Kontoprofil konnte nicht geöffnet werden. Bitte erneut anmelden.")

func authenticate(action: String, username: String, password: String, code: String, replace_lost: bool = false) -> void:
	if changing or dialog.has_code() or access.server.is_empty(): return
	if password.length() < 8 or password.length() > 128 or password.to_utf8_buffer().size() > 1024:
		show_feedback("Das Passwort muss 8–128 Unicode-Codepunkte enthalten.")
		return
	if not can_auth_switch():
		show_feedback(FLUSH_FEEDBACK)
		return
	var saved := access.login_binding(username.to_lower()) if action == "login" else {}
	if saved.has("error"):
		show_feedback("Lokale Gerätebindung widersprüchlich. Bitte den geschützten Bestand prüfen.")
		return
	if action == "login" and not saved.is_empty() and saved.device_id == "" and not replace_lost:
		dialog.confirm_choice("Lokale Gerätekennung verloren. Ausdrücklich ein neues Gerät anmelden und den Bestand abgleichen?",authenticate.bind(action,username,password,code,true))
		return
	var body := {}
	var running := ""
	match action:
		"login":
			running = "Anmeldung läuft …"
			body = {"username":username,"password":password,"device_id":saved.get("device_id") if not replace_lost else null,"device_name":OS.get_name()}
		"register":
			running = "Registrierung läuft …"
			body = {"username":username,"password":password,"invitation":code,"device_name":OS.get_name()}
		"recover":
			running = "Passwortwiederherstellung läuft …"
			body = {"username":username,"new_password":password,"recovery_code":code}
		"recovery-code":
			running = "Codeerneuerung läuft …"
			body = {"password":password}
	if action == "recovery-code" and (profile == null or identity.token.is_empty() or schedule.auth_paused):
		show_feedback("Bitte erneut anmelden und danach den Wiederherstellungscode erneuern.")
		return
	var stamp := epoch
	start_action(running)
	var session_headers := identity.duplicate() if action == "recovery-code" else {}
	var response := await transport.send(access.server,"/v1/auth/"+action,HTTPClient.METHOD_POST,JSON.stringify(body),session_headers)
	if stamp != epoch:
		finish_action("")
		return
	dialog.clear_secrets()
	var expected_status := 201 if action == "register" else 200
	if response.status != expected_status:
		finish_action(auth_error(action,response))
		return
	var result: Dictionary = response.body
	if not Protocol.uuid(response.generation):
		finish_action(INVALID_REPLY)
		return
	var issued: Variant = result.get("recovery_code")
	var valid_code := Protocol.matches(issued,"\\A[A-Za-z0-9_-]{43}\\z")
	if action in ["recover","recovery-code"]:
		if result.size() != 1 or not valid_code:
			finish_action(INVALID_REPLY)
			return
		if action == "recover":
			if identity.get("username") == username.to_lower(): schedule.auth_paused = true
			dialog.set_mode("login")
			finish_action("Passwort geändert. Bitte mit dem neuen Passwort anmelden.")
		else:
			finish_action("Neuer Wiederherstellungscode erstellt.")
		dialog.show_code(issued)
		return
	if not valid_session(result,username,saved,replace_lost) or (not valid_code if action == "register" else issued != null):
		finish_action(INVALID_REPLY)
		return
	var data := {"server":access.server,"account_id":result.account_id,"device_id":result.device_id,"username":result.username,
		"generation":response.generation,"token":result.token,"expires_at":result.expires_at}
	var feedback := ""
	if can_auth_switch():
		var fresh := not DirAccess.dir_exists_absolute(access.directory.path_join(data.account_id))
		if await activate(data,fresh):
			feedback = "Konto erstellt und angemeldet." if action == "register" else "Angemeldet."
		else:
			recovery_session = data
			recovery_device = replace_lost
	if feedback.is_empty():
		feedback = "Konto erstellt, lokale Aktivierung fehlgeschlagen." if action == "register" else "Lokale Aktivierung fehlgeschlagen."
		feedback += " Geschützten Bestand abgleichen oder erneut anmelden." if not recovery_session.is_empty() else " Lokale Sicherung prüfen und erneut anmelden."
	finish_action(feedback)
	if action == "register": dialog.show_code(issued)

func valid_session(result: Dictionary, username: String, saved: Dictionary, replace_lost: bool) -> bool:
	return (result.size() == 7 and result.has_all(["account_id","device_id","token","username","expires_at","last_request_seq","recovery_code"])
		and Protocol.uuid(result.account_id) and Protocol.uuid(result.device_id)
		and Protocol.matches(result.token,"\\A[A-Za-z0-9_-]{43}\\z") and result.username == username.to_lower()
		and Protocol.matches(result.expires_at,"\\A[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.][0-9]{6})?Z?\\z")
		and Protocol.count(result.last_request_seq)
		and (saved.is_empty() or (saved.account_id == result.account_id and (saved.device_id == result.device_id or replace_lost))))

func auth_error(action: String, response: Dictionary) -> String:
	match response.status:
		0,503:
			return "Kontodienst nicht erreichbar. Verbindung prüfen und erneut versuchen."
		401:
			if action == "recovery-code": return "Bestätigung fehlgeschlagen. Passwort prüfen oder erneut anmelden."
			return "Zugangsdaten ungültig. Eingaben prüfen und erneut versuchen."
		409:
			if action == "register": return "Registrierung nicht verfügbar. Einladung und Benutzername prüfen oder den Betreiber kontaktieren."
			return "Kontodienst verlangt einen neuen Abgleich. Bitte erneut anmelden."
		422:
			return "Eingaben ungültig. Benutzername, Passwort und gegebenenfalls Code prüfen."
		429:
			return "Zu viele Anfragen. Bitte später erneut versuchen."
	return INVALID_REPLY

func can_auth_switch() -> bool:
	if app.presentation_locked: return false
	return safe_switch() or (profile != null and not profile._blocked.is_empty() and app._flush_current())

func navigation_locked() -> bool:
	if dialog == null: return false
	if dialog.has_code():
		dialog.focus_code.call_deferred()
		return true
	return changing

func start_action(feedback: String) -> void:
	changing = true
	show_feedback(feedback)

func finish_action(feedback: String) -> void:
	changing = false
	show_feedback(feedback)

func show_feedback(feedback: String) -> void:
	dialog.message.text = feedback
	refresh_status()

func recover_inventory(session_data: Dictionary) -> Dictionary:
	var listing := {}
	var cursor := ""
	var seen := {}
	while true:
		var url := "/v1/puzzles"+("?cursor="+cursor.uri_encode() if cursor != "" else "")
		var response := await transport.send(access.server,url,HTTPClient.METHOD_GET,"",session_data)
		if response.status != 200 or response.generation != session_data.generation: return {}
		var page: Dictionary = response.body
		if page.size() != 2 or not page.has_all(["items","next_cursor"]) or not page.items is Array or page.items.size() > 100: return {}
		for row: Variant in page.items:
			if not row is Dictionary or row.size() != 3 or not Protocol.matches(row.get("puzzle_id"),"\\A[A-Za-z0-9_-]{1,128}\\z") or not Protocol.count(row.get("server_revision")) or not Protocol.count(row.get("conflict_count")) or listing.has(row.puzzle_id): return {}
			listing[row.puzzle_id] = row
		if page.next_cursor == null: return {"listing":listing}
		if not Protocol.matches(page.next_cursor,"\\A[A-Za-z0-9_-]{1,1024}\\z") or page.items.is_empty() or seen.has(page.next_cursor) or seen.size() >= 2000: return {}
		cursor = page.next_cursor
		seen[cursor] = true
	return {}

func recovery_checkpoint(data: Dictionary) -> Dictionary:
	var result := await transport.send(access.server,"/v1/device/checkpoint",HTTPClient.METHOD_GET,"",data)
	if result.status == 200 and result.generation == data.generation and Protocol.valid_checkpoint(result.body,data.account_id,data.device_id): return result.body
	return {}

func inspect_recovery() -> void:
	if changing or recovery_session.is_empty(): return
	start_action("Geschützter Bestand wird geprüft …")
	var data := recovery_session.duplicate()
	var reader := Recovery.new(access.server,data.account_id,data.device_id,data.generation)
	var pages := await recover_inventory(data)
	var cp := await recovery_checkpoint(data)
	if not pages.is_empty() and reader.inspect(cp,recovery_device):
		finish_action("Bestandsabgleich geprüft. Bitte die Wiederherstellung bestätigen.")
		dialog.confirm_choice(reader.effect+" Originale sichern und den Wiederanlauf fortsetzen?",finish_recovery.bind(reader,data))
	else: finish_action("Bindung, Sequenz oder Beleg widersprüchlich. Originale bleiben gesperrt.")

func finish_recovery(reader: Recovery, data: Dictionary) -> void:
	if changing or data != recovery_session: return
	if not can_auth_switch():
		show_feedback(FLUSH_FEEDBACK)
		return
	start_action("Wiederanlauf läuft …")
	if await recover_bound(reader,data) and await activate(data,false):
		finish_action("Kontoprofil wiederhergestellt und aktiviert.")
	else:
		finish_action("Wiederherstellung ausstehend. Erhaltene Originale erneut abgleichen.")

func recover_bound(reader: Recovery, data: Dictionary) -> bool:
	var pages := await recover_inventory(data)
	var cp := await recovery_checkpoint(data)
	if pages.is_empty() or cp.is_empty() or not reader.current_source(): return false
	if not reader.original.is_empty() and not reader.old_epoch and not reader.old_device and reader.original.seq == cp.last_request_seq+1:
		var order := reader.order()
		var path := reader.root.path_join("recovery-abandon.json")
		if FileAccess.file_exists(path) and access.read(path) != order: return false
		if not await access.publish(path,order) or not reader.current_source(): return false
		var result := await transport.send(access.server,order.path,HTTPClient.METHOD_POST,order.body,data)
		if result.status != 200 or result.generation != data.generation or not reader.verify_receipt(result.body): return false
		cp = result.body
	if not reader.finish(cp,pages.listing): return false
	# Publishing the exact receipt and new sequence precedes reopening the sender.
	return await access.publish(reader.root.path_join("recovery-receipt.json"),{"generation":data.generation,"checkpoint":cp,"source_hash":reader.source_hash})

func logout() -> void:
	if changing or dialog.has_code() or profile == null: return
	if not safe_switch():
		show_feedback(FLUSH_FEEDBACK)
		return
	start_action("Abmeldung läuft …")
	var original := identity.duplicate()
	var offline := original.duplicate()
	offline.token = ""
	if not await access.choose("") or not await access.publish(access.session_path(original.account_id),offline):
		finish_action("Lokale Abmeldung konnte nicht dauerhaft gespeichert werden. Bitte erneut versuchen.")
		return
	bind(null,{})
	show_feedback("Lokal abgemeldet. Serverbestätigung ausstehend.")
	var confirmed := false
	if not original.token.is_empty():
		var stamp := epoch
		var result := await transport.send(access.server,"/v1/auth/logout",HTTPClient.METHOD_POST,"",original)
		if epoch != stamp:
			finish_action("")
			return
		confirmed = result.status == 204 and result.generation == original.generation
	finish_action("Abgemeldet. Serversitzung beendet." if confirmed else "Lokal abgemeldet. Ende der Serversitzung nicht bestätigt.")
	dialog.clear_secrets()
	dialog.set_mode("login")

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
	if checkpoint.get("status") != 200 or not Protocol.valid_checkpoint(checkpoint.body,identity.account_id,identity.device_id):
		if problem.is_empty(): problem = "Gerätebeleg konnte nicht geprüft werden."
		return false
	var state := profile.status()
	if not state.has("sequence"): return false
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
	unresolved_inventory = false
	for id: String in inventory:
		if not app.session_indices.has(id):
			unresolved_inventory = true
			problem = "Unbekannte Rätseldefinition."
			continue
		if not await pull(id): return false
	if not await wait_for_disk(profile): return false
	inventory_ready = true
	problem = "" if not unresolved_inventory else problem
	return true

func wait_for_disk(owner: Profile) -> bool:
	if owner == null: return false
	while owner == profile and not owner.flush_confirmed():
		if not owner._blocked.is_empty() or owner.local_failed(): return false
		await get_tree().process_frame
	return owner == profile

func pull(id: String) -> bool:
	if not await wait_for_disk(profile): return false
	var result := await read("/v1/puzzles/"+id)
	if result.get("status") == 404 and inventory[id].server_revision == 0: return true
	if result.get("status") != 200: return false
	var record: Dictionary = result.body
	var index: int = app.session_indices[id]
	var slot: Session = app.sessions[index]
	if not Protocol.valid_record(record,id): return false
	if record.get("definition_revision") != slot.definition.revision:
		unresolved_inventory = true
		problem = "Inkompatible Rasterrevision."
		return true
	if record.get("kind") == "snapshot" and profile._store.received(record.get("save"),slot).is_empty(): return false
	var state := profile.status()
	for entry: Dictionary in state.entries.values():
		if entry.id == id and entry.status != "request_abandoned":
			if record.kind == "snapshot": profile.confirm_equal(slot,record)
			return true
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
		if profile.import_guest(imported) == 0:
			problem = "Gastimport konnte nicht gespeichert werden."
			break
		var disk := profile.load_slot(slot.definition)
		if disk.status == "loaded":
			Profile.Store.apply(disk.data,slot)
			app.slot_status[index] = "loaded"
			if slot == app.session: app._bind_session(index)
	schedule.collect()
	app.present_album()

func choose_recovery_slot(id: String, remote: bool) -> void:
	if changing or transport_busy or profile == null or not safe_switch(): return
	changing = true
	var result := await read("/v1/puzzles/"+id)
	if result.get("status") in [200,404]:
		var basis: int = int(result.body.get("server_revision",0))
		var slot: Session = app.sessions[app.session_indices[id]]
		var acceptable: bool = not remote or (result.status == 200 and result.body.get("definition_revision") == slot.definition.revision and (result.body.get("kind") == "reset" or not profile._store.received(result.body.get("save"),slot).is_empty()))
		if acceptable and profile.select_recovery(id,basis,remote):
			if remote:
				inventory_ready = false
			schedule.connected()
	changing = false

func current_choice_base(id: String, response: Dictionary) -> int:
	if response.get("status") == 404 and response.body.get("code") == "not_found": return 0
	if response.get("status") == 200 and Protocol.valid_record(response.body,id): return int(response.body.server_revision)
	return -1

func read_choice(id: String, operation: String, value: Variant) -> Dictionary:
	var path := "/history/"+str(int(value)) if operation == "restore" else "/conflicts/"+str(value)
	var result := await read("/v1/puzzles/"+id+path)
	if result.get("status") != 200: return {}
	var row: Dictionary = result.body
	if operation == "restore":
		return row if Protocol.valid_record(row,id) and row.server_revision == value else {}
	return row if Protocol.valid_candidate(row,id,value) else {}

func choice_compatible(row: Dictionary, slot: Session) -> bool:
	return row.definition_revision == slot.definition.revision and (row.kind == "reset" or not profile._store.received(row.save,slot).is_empty())

func decide(id: String, operation: String, value: Variant, base: int) -> bool:
	if changing or transport_busy or profile == null or not safe_switch(): return false
	changing = true
	var current := await read("/v1/puzzles/"+id)
	var accepted := false
	if current_choice_base(id,current) != base:
		problem = "Serverstand geändert oder nicht verfügbar. Bitte erneut vergleichen."
	else:
		var row := await read_choice(id,operation,value)
		if row.is_empty(): problem = "Fassung nicht mehr verfügbar."
		elif operation != "discard" and not choice_compatible(row,app.sessions[app.session_indices[id]]):
			problem = "Fassung mit diesem Raster nicht verwendbar."
		elif profile.decision(id,operation,value,base) > 0:
			schedule.collect()
			accepted = true
		else: problem = "Auswahl konnte lokal nicht gespeichert werden."
	changing = false
	return accepted

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

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_IN and profile != null and schedule.failures > 0: schedule.connected()

func exiting() -> void:
	if profile and inventory_ready and schedule.now() >= schedule.retry_at: send_batch()

func refresh_status() -> void:
	if app == null or dialog == null or app.account_status == null: return
	var key := [epoch,changing,recovery_session.is_empty(),access.server,problem,inventory_ready,unresolved_inventory,transport_busy,schedule.auth_paused,
		profile._journal.digest if profile else "",profile.flush_confirmed() if profile else true,profile.local_failed() if profile else false]
	if key == status_key: return
	status_key = key
	app.account_retry.visible = profile != null and profile.local_failed()
	var value := "Gast"
	var mode := "Gast · lokales Profil"
	var detail := "Kein Kontoabgleich"
	if profile:
		mode = ("Kontoprofil · lokal: " if schedule.auth_paused else "Angemeldet: ") + str(identity.username)
		var state: Dictionary = profile.status()
		detail = "Abgleich ausstehend"
		if profile.local_failed(): detail = "Lokale Sicherung fehlgeschlagen"
		elif not problem.is_empty(): detail = problem
		elif state.has("error"): detail = state.error
		elif schedule.auth_paused: detail = "Erneut anmelden"
		elif transport_busy: detail = "Abgleich läuft"
		elif not profile.flush_confirmed(): detail = "Lokale Sicherung ausstehend"
		elif state.entries.values().any(func(entry: Dictionary) -> bool: return entry.status != "pending"): detail = "Konflikt / Entscheidung nötig"
		elif inventory.values().any(func(row: Dictionary) -> bool: return row.conflict_count > 0): detail = "Konflikt"
		elif not state.entries.is_empty(): detail = "Übertragung ausstehend"
		elif unresolved_inventory: detail = "Rätselstand prüfen"
		elif inventory_ready: detail = "Synchronisiert"
		value = str(identity.username)+" · "+detail
	elif not problem.is_empty(): value += " · "+problem
	if access.server.is_empty(): detail = "Kontodienst für diesen Spielbau nicht eingerichtet"
	dialog.profile_status.text = mode
	dialog.sync_status.text = "Sync: "+detail
	dialog.refresh_choices()
	dialog.update_interaction()
	if app.account_status.text != value:
		app.account_status.text = value
		app._layout_book()
