extends RefCounted
## Exercises the real settings controls, account controller and local publication.
const Transport = preload("res://model/sync_transport.gd")
const ACCOUNT := "a8170001-0000-4000-8000-000000000001"
const DEVICE := "a8170001-0000-4000-8000-000000000002"
const GENERATION := "a8170001-0000-4000-8000-000000000003"
const BROKEN_ACCOUNT := "a8170001-0000-4000-8000-000000000004"
const NAME := "konto-mit-zweiunddreissig-zeichn"
const DISPLAY_CODE := "x000000000000000000000000000000000000000000"

class Replies extends Transport:
	signal issued
	var calls := 0
	var next := {}
	var delayed := false

	func send(_server: String, path: String, _method: int, _raw: String, _session: Dictionary) -> Dictionary:
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

	await r.choose_option(settings.mode,1)
	settings.password.text = "synthetic-pass"
	settings.code.text = "synthetic-invitation"
	fixture.next = reply(201,session(BROKEN_ACCOUNT,DISPLAY_CODE))
	var denied_path: String = client.access.session_path(BROKEN_ACCOUNT)
	# Force the real publish path to fail after HTTP success. Freshness is derived
	# from this partial account directory, so open an actual journal first.
	var broken = client.Profile.new()
	r.check(broken.open(client.access.server,BROKEN_ACCOUNT,DEVICE,GENERATION,true),"SYNC-UX prepares isolated journal")
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

	await r.choose_option(settings.mode,0)
	settings.username.text = NAME
	settings.password.text = "synthetic-pass"
	fixture.next = reply(200,session(ACCOUNT))
	await press(r,settings.submit_button)
	r.check(client.profile != null and client.access.active() == ACCOUNT and app.session != original and
		app.information.visible and app.information_origin == "album" and client.dialog.profile_status.text.contains(NAME) and
		settings.message.text == "Angemeldet." and settings.sync_status.text.begins_with("Sync: "),
		"SYNC-UX persisted login binds the new profile and keeps action and sync status separate")
	if client.profile == null:
		client.transport = original_transport
		client.access = original_access
		return
	var count := fixture.calls
	client.profile._awaiting["test"] = true
	await press(r,r.caption_button(settings.choices,"Abmelden"))
	r.check(settings.message.text.contains("Lokale Sicherung") and fixture.calls == count and client.profile != null,
		"SYNC-UX pending local flush blocks logout with feedback")
	client.profile._awaiting.erase("test")

	fixture.next = reply(0)
	await press(r,r.caption_button(settings.choices,"Abmelden"))
	r.check(client.profile == null and app.information.visible and settings.message.text.contains("nicht bestätigt"),
		"SYNC-UX local logout distinguishes missing server confirmation")
	r.click(app.actions["nav-work"])
	await r.frames()
	r.check(app.album.visible and not app.work.visible,"SYNC-UX return leads to the active catalog after profile changes")

	app.show_information("settings")
	await r.frames()
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
	fixture.queue_free()
	app.show_album()
