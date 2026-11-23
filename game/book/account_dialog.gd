extends AcceptDialog
## Every destructive choice captures the owning profile and the displayed server revision.
var client: Node
var form := VBoxContainer.new()
var username := LineEdit.new()
var password := LineEdit.new()
var code := LineEdit.new()
var message := Label.new()
var puzzles: OptionButton
var choices := VBoxContainer.new()
var notice := AcceptDialog.new()

func configure(owner: Node) -> void:
	client = owner
	title = "Spielerkonto"
	add_child(form)
	message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	form.add_child(message)
	for pair: Array in [[username,"Benutzername"],[password,"Passwort (bei Wiederherstellung das neue Passwort)"],[code,"Einladung oder Wiederherstellungscode"]]:
		pair[0].placeholder_text = pair[1]
		pair[0].accessibility_name = pair[1]
		form.add_child(pair[0])
	username.max_length = 32
	password.secret = true
	password.max_length = 128
	code.secret = true
	form.add_child(choices)
	add_child(notice)
	notice.title = "Wiederherstellungscode"
	notice.confirmed.connect(clear_notice)
	notice.canceled.connect(clear_notice)
	visibility_changed.connect(func() -> void:
		if not visible:
			password.clear()
			code.clear())

func clear_notice() -> void: notice.dialog_text = ""

func show_code(value: String) -> void:
	if not client.Protocol.matches(value,"\\A[A-Za-z0-9_-]{43}\\z"): return
	notice.dialog_text = "Diesen Code sicher aufbewahren. Er wird einmal angezeigt.\n"+value
	notice.popup_centered()

func button(parent: Control, caption: String, action: Callable) -> void:
	var item := Button.new()
	item.text = caption
	item.pressed.connect(action)
	parent.add_child(item)

func submit(action: String) -> void:
	var name_value := username.text
	var secret_value := password.text
	var code_value := code.text
	hide()
	await client.authenticate(action,name_value,secret_value,code_value)

func open() -> void:
	for child in choices.get_children():
		choices.remove_child(child)
		child.queue_free()
	var configured: bool = not client.access.server.is_empty()
	message.text = client.app.account_status.text if configured else "Der Kontodienst ist für diesen Spielbau noch nicht eingerichtet."
	for field: LineEdit in [username,password,code]: field.visible = configured
	if configured:
		var actions := HFlowContainer.new()
		choices.add_child(actions)
		for pair: Array in [["Anmelden","login"],["Registrieren","register"],["Konto wiederherstellen","recover"]]:
			button(actions,pair[0],submit.bind(pair[1]))
		var accounts: Dictionary = client.access.accounts()
		for name_value: String in accounts:
			button(actions,name_value+" lokal öffnen",local_choice.bind(accounts[name_value]))
		if client.profile:
			button(actions,"Neuer Wiederherstellungscode",submit.bind("recovery-code"))
			button(actions,"Abmelden",sign_out)
			add_puzzle_actions()
	popup_centered(Vector2i(mini(640,client.app.size.x-40),0))

func local_choice(id: String) -> void:
	hide()
	await client.resume_local(id)

func sign_out() -> void:
	hide()
	await client.logout()

func add_puzzle_actions() -> void:
	puzzles = OptionButton.new()
	choices.add_child(puzzles)
	for slot in client.app.sessions:
		puzzles.add_item(slot.album_title())
		puzzles.set_item_metadata(puzzles.item_count-1,slot.definition.id)
	if puzzles.item_count == 0: return
	var bar := HFlowContainer.new()
	choices.add_child(bar)
	button(bar,"Gaststand übernehmen",import_guest.bind(false))
	button(bar,"Alle Gaststände übernehmen",import_guest.bind(true))
	button(bar,"Konflikte und Versionen",versions)
	button(bar,"Lokale Sicherung erneut versuchen",client.profile.retry_local)
	if not client.profile.resume_request().is_empty():
		button(bar,"Offenen Auftrag abbrechen …",abandon)

func confirm_choice(caption: String, action: Callable) -> void:
	var stamp: int = client.epoch
	var question := ConfirmationDialog.new()
	question.dialog_text = caption
	add_child(question)
	question.confirmed.connect(func() -> void:
		question.queue_free()
		if client.epoch == stamp: action.call())
	question.canceled.connect(question.queue_free)
	question.popup_centered()

func import_guest(all_slots: bool) -> void:
	var ids: Array = client.app.session_indices.keys() if all_slots else [puzzles.get_selected_metadata()]
	confirm_choice("Validierte Gaststände ins aktive Konto übernehmen? Die Gaststände bleiben erhalten.",client.import_guest.bind(ids))

func versions() -> void:
	var id: String = puzzles.get_selected_metadata()
	var stamp: int = client.epoch
	if client.transport_busy or client.changing: return
	client.changing = true
	var current: Dictionary = await client.read("/v1/puzzles/"+id)
	var conflicts: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/conflicts")
	var history: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/history")
	client.changing = false
	if not visible or stamp != client.epoch or current.get("status") not in [200,404] or conflicts.is_empty() or history.is_empty(): return
	var base: int = int(current.body.get("server_revision",0))
	var selection := AcceptDialog.new()
	selection.title = "Konflikte und Versionen"
	add_child(selection)
	var scroll := ScrollContainer.new()
	selection.add_child(scroll)
	var list := VBoxContainer.new()
	scroll.add_child(list)
	for row: Dictionary in conflicts.items:
		if row.get("puzzle_id") != id or not client.Protocol.uuid(row.get("candidate_id")): continue
		for action: String in ["resolve","discard"]:
			var caption := ("Fassung übernehmen" if action == "resolve" else "Fassung verwerfen")+" · "+str(row.get("created_at",""))
			button(list,caption,choose.bind(selection,stamp,id,action,row.candidate_id,base))
	for row: Dictionary in history.items:
		if row.get("puzzle_id") == id and client.Protocol.count(row.get("server_revision"),1):
			button(list,"Version %d wiederherstellen" % row.server_revision,choose.bind(selection,stamp,id,"restore",row.server_revision,base))
	if list.get_child_count() == 0:
		var empty := Label.new()
		empty.text = "Keine früheren Fassungen vorhanden."
		list.add_child(empty)
	selection.confirmed.connect(selection.queue_free)
	selection.canceled.connect(selection.queue_free)
	selection.popup_centered(Vector2i(450,320))

func choose(window: Window, stamp: int, id: String, action: String, value: Variant, base: int) -> void:
	window.queue_free()
	if client.epoch == stamp: confirm_choice("Auswahl für dieses Blatt bestätigen?",client.decide.bind(id,action,value,base))

func abandon() -> void:
	var original: Dictionary = client.profile.resume_request()
	if not original.is_empty(): confirm_choice("Diesen offenen Übertragungsauftrag ausdrücklich beenden? Der Spielstand bleibt lokal erhalten.",client.abandon.bind(original))
