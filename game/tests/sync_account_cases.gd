extends RefCounted
## Exercises the real settings controls, account controller and local publication.
const Transport = preload("res://model/sync_transport.gd")
const ACCOUNT := "a8170001-0000-4000-8000-000000000001"
const DEVICE := "a8170001-0000-4000-8000-000000000002"
const GENERATION := "a8170001-0000-4000-8000-000000000003"
const NAME := "konto-mit-zweiunddreissig-zeichn"
const DISPLAY_CODE := "x000000000000000000000000000000000000000000"

class Replies extends Transport:
	signal issued
	var calls := 0
	var next := {}
	var delayed := false
	var account_status := 0
	var paths: Array[String] = []

	func send(_server: String, path: String, _method: int, _raw: String, _session: Dictionary) -> Dictionary:
		paths.append(path)
		if path == "/v1/account":
			return {"status":account_status,"retry_after":0,"generation":GENERATION,
				"body":{"account_id":ACCOUNT,"device_id":DEVICE,"username":NAME}}
		if path == "/v1/puzzles": return {"status":200,"generation":GENERATION,"body":{"items":[],"next_cursor":null}}
		if path == "/v1/device/checkpoint":
			return {"status":200,"generation":GENERATION,"body":{"format":"picross-device-checkpoint/v1",
				"account_id":ACCOUNT,"device_id":DEVICE,"last_request_seq":0,"last_request_hash":null,
				"response_status":null,"response_body":null}}
		if not path.begins_with("/v1/auth/"): return {"status":0,"retry_after":0}
		calls += 1
		if delayed: await issued
		return next

static func reply(status: int, body: Dictionary = {}) -> Dictionary:
	return {"status":status,"generation":GENERATION,"body":body}

static func session(account: String, value: Variant = null) -> Dictionary:
	return {"account_id":account,"device_id":DEVICE,"token":"a".repeat(43),"username":NAME,
		"expires_at":"2099-01-01T00:00:00.123456Z","last_request_seq":0,"recovery_code":value}

static func press(r: SceneTree, control: Control) -> void:
	r.app.info_scroll.ensure_control_visible(control)
	await r.frames()
	r.click(control)
	await r.frames()

static func cell_transport(r: SceneTree, fixture: Replies) -> void:
	var app: Control = r.app
	var client: Node = app.accounts
	client.schedule.success()
	await client.send_batch()
	r.check(client.inventory_ready and not client.transport_busy and client.schedule.due == INF,
		"SYNC-PERF inventory and startup batch settled")
	var calls := fixture.paths.size()
	var version: int = client.profile.status().local
	var point: Vector2 = app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center()
	r.click_at(point, MOUSE_BUTTON_RIGHT)
	r.click(app.undo_button)
	r.click(app.redo_button)
	await r.frames()
	r.check(app.session.player.cells[0] == 0 and client.profile.locally_confirmed(version + 3)
		and app.recent.record.get("id") == app.session.definition.id and fixture.paths.size() == calls
		and client.schedule.due == INF, "SYNC-PERF cell/undo/redo publish locally without arming or sending HTTP")

static func run(r: SceneTree) -> void:
	var app: Control = r.app
	var client: Node = app.accounts
	var settings: Control = client.dialog
	var original_transport = client.transport
	var original_access = client.access
	client.access = client.Access.new()
	var fixture := Replies.new()
	client.add_child(fixture)
	client.transport = fixture
	client.access.server = "https://sync-ux-%d.invalid" % Time.get_ticks_usec()
	client.access.directory = client.Profile.ROOT.path_join(client.access.server.sha256_text())
	client.refresh_status()

	app.show_album()
	app.select_puzzle(0)
	await r.frames()
	app.show_information("settings")
	await r.frames()
	r.check(app.info.section == "settings" and app.information_origin == "work","SYNC-UX opens settings from a puzzle")
	var original: Variant = app.session
	r.check(not settings.auth_form.visible and not settings.logout_button.visible and
		not settings.action_buttons["recovery-code"].visible and settings.find_children("*","OptionButton",true,false).is_empty(),
		"SYNC-UX starts with the three guest actions, no fields or dropdowns")
	for id: String in ["register","recover","login"]:
		await press(r,settings.action_buttons[id])
		r.check(settings.auth_form.visible and settings.action == id and settings.username.visible and
			settings.password_row.visible and settings.code.visible == (id != "login") and
			settings.password.text.is_empty() and settings.code.text.is_empty() and fixture.calls == 0,
			"SYNC-UX opens exactly the requested form without sending or retaining secrets: "+id)
		settings.password.text = "synthetic-pass"
		settings.code.text = "synthetic-code"
	settings.code.clear()
	settings.username.text = NAME
	settings.password.text = "synthetic-pass"
	r.surface.size = Vector2i(1280,720)
	app.set_ui_scale(1.25)
	await r.frames()
	r.check(settings.password.text == "synthetic-pass" and settings.password.size.y >= 55,
		"SYNC-UX tight settings preserve input and 55 px controls")
	var scroll: Rect2 = app.info_scroll.get_global_rect()
	r.check(settings.get_global_rect().position.x >= scroll.position.x and settings.get_global_rect().end.x <= scroll.end.x+1,
		"SYNC-UX tight settings fit the scroll width")

	r.check(settings.password_help.tooltip_text == "Mindestens 8 Zeichen" and settings.password_help.text.is_empty() and
		settings.password_help.size.x >= 55 and settings.password_help.size.y >= 55,
		"SYNC-UX password help uses a scaled icon-only hit target")
	app.info_scroll.ensure_control_visible(settings.password_help)
	settings.password_help.grab_focus()
	await r.frames()
	r.check(is_instance_valid(settings.password_help.focus_tip),"SYNC-UX password help is reachable by focus")

	fixture.next = reply(401)
	fixture.delayed = true
	await press(r,settings.submit_button)
	r.check(settings.message.text.contains("Anmeldung läuft") and settings.submit_button.disabled,
		"SYNC-UX pending request is visible and disables submission")
	r.click(settings.submit_button)
	r.check(fixture.calls == 1 and not app.book.information_routes.request_return(),
		"SYNC-UX pending action prevents duplicate requests and invalidated return")
	fixture.issued.emit()
	await r.frames()
	r.check(settings.message.text.contains("Zugangsdaten ungültig") and not settings.submit_button.disabled and app.session == original,
		"SYNC-UX rejected credentials show retry and keep the original profile")
	fixture.delayed = false

	settings.password.text = "synthetic-pass"
	fixture.next = reply(0)
	await press(r,settings.submit_button)
	r.check(settings.message.text.contains("nicht erreichbar") and not settings.submit_button.disabled,
		"SYNC-UX failed or timed-out transport gives a retry in settings")
	settings.password.text = "synthetic-pass"
	fixture.next = reply(200,{"token":"malformed"})
	await press(r,settings.submit_button)
	r.check(settings.message.text.contains("Ungültige Antwort") and client.profile == null,
		"SYNC-UX malformed success cannot activate an account")

	await press(r,settings.action_buttons["register"])
	r.check(not is_instance_valid(settings.password_help.focus_tip),"SYNC-UX changing forms dismisses the password tooltip")
	settings.password.text = "synthetic-pass"
	settings.code.text = "synthetic-invitation"
	fixture.next = reply(201,session(ACCOUNT,DISPLAY_CODE))
	var denied_path: String = client.access.session_path(ACCOUNT)
	# Force the real publish path to fail after HTTP success. Freshness is derived
	# from this partial account directory, so open an actual journal first.
	var broken = client.Profile.new()
	r.check(broken.open(client.access.server,ACCOUNT,DEVICE,GENERATION,true),"SYNC-UX prepares isolated journal")
	DirAccess.make_dir_absolute(denied_path)
	await press(r,settings.submit_button)
	r.check(settings.message.text.contains("Konto erstellt, lokale Aktivierung fehlgeschlagen") and client.profile == null and settings.recovery_code.text == DISPLAY_CODE,
		"SYNC-UX publish failure leaves guest bound and presents the issued code")
	await r.frames()
	r.check(not app.book.information_routes.request("help") and not app.book.information_routes.request_return(),
		"SYNC-UX one-time code stays until closed")
	app.set_ui_scale(1.0)
	app.set_ui_scale(1.25)
	await r.frames()
	r.check(settings.recovery_code.text == DISPLAY_CODE and not settings.recovery_code.editable,
		"SYNC-UX reflow retains the exact selectable code")
	await press(r,r.caption_button(settings.notice,"Code schließen"))
	r.check(settings.recovery_code.text.is_empty() and settings.password.text.is_empty() and settings.code.text.is_empty(),
		"SYNC-UX closing clears transient fields")

	r.check(DirAccess.remove_absolute(denied_path) == OK,"SYNC-UX removes the synthetic publication obstruction")
	await press(r,settings.action_buttons["register"])
	settings.username.text = NAME
	settings.password.text = "synthetic-pass"
	settings.code.text = "synthetic-invitation"
	fixture.next = reply(201,session(ACCOUNT,DISPLAY_CODE))
	await press(r,settings.submit_button)
	r.check(client.profile != null and client.access.active() == ACCOUNT and app.session != original and
		app.information.visible and app.information_origin == "album" and client.dialog.profile_status.text.contains(NAME) and
		settings.message.text == "Konto erstellt und angemeldet." and settings.recovery_code.text == DISPLAY_CODE and
		not settings.auth_form.visible and settings.sync_status.text.begins_with("Sync: "),
		"SYNC-UX persisted registration binds the new profile and keeps action and sync status separate")
	if client.profile == null:
		client.transport = original_transport
		client.access = original_access
		return
	await press(r,r.caption_button(settings.notice,"Code schließen"))
	r.check(settings.logout_button.has_focus() and settings.action_buttons["recovery-code"].visible and
		not settings.action_buttons["login"].visible and not settings.action_buttons["register"].visible and
		not settings.action_buttons["recover"].visible and not settings.auth_form.visible,
		"SYNC-UX closing registration code focuses a visible authenticated action")
	var count := fixture.calls
	await client.authenticate("login",NAME,"synthetic-pass","")
	r.check(fixture.calls == count,"SYNC-UX authenticated controller rejects guest actions")

	fixture.account_status = 0
	await client.read("/v1/account")
	client.refresh_status()
	r.check(client.signed_in() and settings.logout_button.visible and settings.sync_status.text.contains("Offline"),
		"SYNC-UX transport outage preserves the authenticated actions")
	await press(r,settings.action_buttons["recovery-code"])
	r.check(settings.password.visible and not settings.username.visible and not settings.code.visible,
		"SYNC-UX code renewal asks only for the current password")
	settings.password.text = "synthetic-pass"
	fixture.account_status = 200
	fixture.next = reply(401)
	await press(r,settings.submit_button)
	r.check(client.signed_in() and settings.message.text.contains("Passwort prüfen") and settings.password.text.is_empty(),
		"SYNC-UX a wrong renewal password preserves a valid session")
	settings.password.text = "synthetic-pass"
	fixture.next = reply(200,{"recovery_code":DISPLAY_CODE})
	await press(r,settings.submit_button)
	r.check(settings.has_code() and settings.recovery_code.text == DISPLAY_CODE,"SYNC-UX code renewal shows the issued code")
	await press(r,r.caption_button(settings.notice,"Code schließen"))

	app.return_to_work()
	await r.frames()
	app.select_puzzle(0)
	await r.frames()
	await cell_transport(r,fixture)
	app.show_information("settings")
	await r.frames()
	var same_id: String = app.session.definition.id
	await press(r,settings.action_buttons["recovery-code"])
	settings.password.text = "synthetic-pass"
	fixture.account_status = 401
	fixture.next = reply(401)
	await press(r,settings.submit_button)
	count = fixture.calls
	await client.authenticate("recovery-code",NAME,"synthetic-pass","")
	r.check(fixture.calls == count and not client.signed_in() and client.profile != null and
		not settings.auth_form.visible and settings.password.text.is_empty() and
		not settings.action_buttons["recovery-code"].visible and settings.action_buttons["login"].visible,
		"SYNC-UX rejected session enables login without discarding the local profile")
	await press(r,settings.action_buttons["login"])
	settings.username.text = NAME
	fixture.next = reply(200,session(ACCOUNT))
	settings.password.text = "synthetic-pass"
	await press(r,settings.submit_button)
	r.check(settings.message.text == "Angemeldet." and app.information_origin == "work" and app.session.definition.id == same_id,
		"SYNC-UX same-profile login keeps the original puzzle return route")
	count = fixture.calls
	client.profile._awaiting["test"] = true
	await press(r,settings.logout_button)
	r.check(settings.message.text.contains("Lokale Sicherung") and fixture.calls == count and client.profile != null,
		"SYNC-UX pending local flush blocks logout with feedback")
	client.profile._awaiting.erase("test")

	var prior_digest: String = client.profile._journal.digest
	var path_count := fixture.paths.size()
	client.inventory[same_id] = {"conflict_count":1,"server_revision":1}
	client.inventory_ready = true
	client.refresh_status()
	r.check(settings.sync_status.text.contains("Konflikt – Lösung derzeit nicht verfügbar") and
		not settings.sync_status.text.contains("Synchronisiert") and settings.find_children("*","OptionButton",true,false).is_empty(),
		"SYNC-UX reports an unresolved server conflict without a puzzle or version selector")
	var captions: Array[String] = []
	for button: Button in settings.find_children("*","Button",true,false):
		captions.append(button.text)
	for caption: String in ["Gaststand übernehmen","Alle Gaststände übernehmen","Konflikte und Versionen","Lokale Fassung erneut anbieten","Serverfassung laden"]:
		r.check(caption not in captions,"SYNC-UX removed action is unavailable: "+caption)
	r.check(client.profile._journal.digest == prior_digest and fixture.paths.size() == path_count,
		"SYNC-UX displaying the conflict leaves local journal and transport untouched")

	fixture.next = reply(0)
	await press(r,settings.logout_button)
	r.check(client.profile == null and app.information.visible and settings.message.text.contains("nicht bestätigt"),
		"SYNC-UX local logout distinguishes missing server confirmation")
	r.click(app.actions["nav-work"])
	await r.frames()
	r.check(app.album.visible and not app.work.visible,"SYNC-UX return leads to the active catalog after profile changes")

	app.show_information("settings")
	await r.frames()
	await press(r,settings.action_buttons["recover"])
	settings.username.text = NAME
	settings.password.text = "synthetic-pass"
	settings.code.text = "synthetic-code"
	fixture.next = reply(200,{"recovery_code":DISPLAY_CODE})
	await press(r,settings.submit_button)
	r.check(client.profile == null and settings.has_code() and settings.recovery_code.text == DISPLAY_CODE and
		settings.message.text.contains("mit dem neuen Passwort anmelden"),"SYNC-UX password recovery issues a code without login")
	await press(r,r.caption_button(settings.notice,"Code schließen"))
	r.check(settings.action_buttons["login"].has_focus() and not settings.auth_form.visible,
		"SYNC-UX closing the recovery code returns focus to the login action")
	await press(r,settings.action_buttons["login"])
	settings.password.text = "synthetic-pass"
	fixture.next = reply(200,session(ACCOUNT))
	fixture.delayed = true
	await press(r,settings.submit_button)
	client.bind(null,{})
	fixture.issued.emit()
	await r.frames()
	r.check(not settings.message.text.contains("Angemeldet") and client.profile == null,
		"SYNC-UX response from a superseded context cannot report success")
	client.transport = original_transport
	client.access = original_access
	client.refresh_status()
	fixture.queue_free()
	app.show_album()
