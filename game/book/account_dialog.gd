extends AcceptDialog
const Session = preload("res://model/session.gd")
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
	client.add_child(notice)
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
		if not client.recovery_session.is_empty(): button(actions,"Geschützten Bestand abgleichen",client.inspect_recovery)
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
	if client.profile._state.entries.values().any(func(e: Dictionary) -> bool: return e.status == "recovery_choice"):
		button(bar,"Lokale Fassung erneut anbieten",recover_slot.bind(false))
		button(bar,"Serverfassung laden",recover_slot.bind(true))
	button(bar,"Lokale Sicherung erneut versuchen",client.profile.retry_local)
	if not client.profile.resume_request().is_empty():
		button(bar,"Offenen Auftrag abbrechen …",abandon)

func confirm_choice(caption: String, action: Callable) -> void:
	var stamp: int = client.epoch
	var question := ConfirmationDialog.new()
	question.dialog_text = caption
	client.add_child(question)
	question.confirmed.connect(func() -> void:
		question.queue_free()
		if client.epoch == stamp: action.call())
	question.canceled.connect(question.queue_free)
	question.popup_centered()

func import_guest(all_slots: bool) -> void:
	var ids: Array = client.app.session_indices.keys() if all_slots else [puzzles.get_selected_metadata()]
	confirm_choice("Validierte Gaststände ins aktive Konto übernehmen? Die Gaststände bleiben erhalten.",client.import_guest.bind(ids))

func recover_slot(remote: bool) -> void:
	var id: String = puzzles.get_selected_metadata()
	confirm_choice("Diese Fassung nach erneutem Abgleich ausdrücklich wählen?",client.choose_recovery_slot.bind(id,remote))

func versions() -> void:
	var id: String = puzzles.get_selected_metadata()
	var stamp: int = client.epoch
	if client.transport_busy or client.changing: return
	client.changing = true
	var conflicts: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/conflicts")
	var history: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/history")
	client.changing = false
	if not visible or stamp != client.epoch: return
	if conflicts.is_empty() or history.is_empty():
		message.text = "Konflikte und Versionen konnten nicht geladen werden."
		return
	var selection := version_window(self,"Konflikte und Versionen","Schließen")
	var list := scrolling_content(selection)
	var feedback := comparison_label(list,"")
	var number := 0
	for row: Variant in conflicts.items:
		if not row is Dictionary or row.get("puzzle_id") != id or not client.Protocol.uuid(row.get("candidate_id")): continue
		number += 1
		button(list,"Konflikt %d vergleichen" % number,compare.bind(selection,feedback,stamp,id,"resolve",row.candidate_id,"Konflikt %d" % number))
	for row: Variant in history.items:
		if not row is Dictionary or row.get("puzzle_id") != id or not client.Protocol.count(row.get("server_revision"),1): continue
		var heading := "Version %d" % int(row.server_revision)
		button(list,heading+" vergleichen",compare.bind(selection,feedback,stamp,id,"restore",row.server_revision,heading))
	if list.get_child_count() == 1:
		comparison_label(list,"Keine Konflikte oder früheren Fassungen vorhanden.")
	selection.popup_centered(dialog_size(Vector2i(460,320)))

func version_window(parent: Window, heading: String, close_caption: String) -> AcceptDialog:
	var window := AcceptDialog.new()
	window.title = heading
	window.theme = client.app.theme
	window.transient = true
	window.exclusive = true
	window.get_ok_button().text = close_caption
	parent.add_child(window)
	window.confirmed.connect(window.queue_free)
	window.canceled.connect(window.queue_free)
	return window

func dialog_size(base: Vector2i) -> Vector2i:
	var scaled := Vector2i(Vector2(base)*client.app.ui_scale)
	return scaled.min(Vector2i(client.app.size)-Vector2i(48,64))

func scrolling_content(parent: Node) -> VBoxContainer:
	var scroll := ScrollContainer.new()
	scroll.follow_focus = true
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(scroll)
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation",roundi(8*client.app.ui_scale))
	scroll.add_child(list)
	return list

func comparison_label(parent: Control, text: String, heading: bool = false) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size",roundi((18 if heading else 16)*client.app.ui_scale))
	parent.add_child(label)
	return label

func compare(selection: Window, feedback: Label, stamp: int, id: String, operation: String, value: Variant, heading: String) -> void:
	if stamp != client.epoch or client.changing or client.transport_busy: return
	feedback.text = "Fassungen werden geladen …"
	client.changing = true
	var current: Dictionary = await client.read("/v1/puzzles/"+id)
	var base: int = client.current_choice_base(id,current)
	var selected: Dictionary = await client.read_choice(id,operation,value) if base >= 0 else {}
	client.changing = false
	if not is_instance_valid(selection) or not selection.visible or stamp != client.epoch: return
	if selected.is_empty():
		feedback.text = "Fassungen konnten nicht verglichen werden. Bitte erneut versuchen."
		return
	feedback.text = ""
	var index: int = client.app.session_indices[id]
	var slot: Session = client.app.sessions[index]
	var comparison := version_window(selection,"Fassungen vergleichen","Zurück")
	var panel := VBoxContainer.new()
	comparison.add_child(panel)
	var list := scrolling_content(panel)
	var size := dialog_size(Vector2i(920,400))
	comparison_label(list,slot.neutral_title(),true)
	var columns: BoxContainer = HBoxContainer.new() if size.x >= 720*client.app.ui_scale else VBoxContainer.new()
	columns.add_theme_constant_override("separation",roundi(16*client.app.ui_scale))
	list.add_child(columns)
	var server_summary := "Noch kein Stand auf dem Server." if base == 0 else remote_summary(current.body,slot,client.choice_compatible(current.body,slot))
	var compatible: bool = client.choice_compatible(selected,slot)
	comparison_column(columns,"Lokal · dieses Gerät",local_summary(slot,index),"LocalSummary")
	comparison_column(columns,"Aktueller Serverstand",server_summary,"ServerSummary")
	comparison_column(columns,heading,remote_summary(selected,slot,compatible),"ChoiceSummary")
	var result := comparison_label(panel,"")
	var actions := HFlowContainer.new()
	panel.add_child(actions)
	if operation == "restore":
		if compatible: button(actions,"Diese Version wiederherstellen",choose.bind(selection,comparison,result,actions,stamp,client.decide.bind(id,operation,value,base)))
	else:
		if compatible: button(actions,"Kandidatenfassung übernehmen",choose.bind(selection,comparison,result,actions,stamp,client.decide.bind(id,"resolve",value,base)))
		button(actions,"Kandidatenfassung verwerfen",choose.bind(selection,comparison,result,actions,stamp,client.decide.bind(id,"discard",value,base)))
	comparison.popup_centered(size)

func comparison_column(parent: BoxContainer, heading: String, text: String, summary_name: String) -> void:
	var column := VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(column)
	comparison_label(column,heading,true)
	comparison_label(column,text).name = summary_name

func local_summary(slot: Session, index: int) -> String:
	var raster := "Rasterrevision %d · %d × %d" % [slot.definition.revision,slot.player.width,slot.player.height]
	match client.app.slot_status[index]:
		"error":
			return raster+"\nLokaler Spielstand nicht lesbar."
		"fresh":
			if slot.definition.id in client.app.revision_reset_ids: return raster+"\nNach Rasterwechsel neu begonnen."
			return raster+"\nLeeres Raster · kein lokaler Spielstand."
	return raster+"\n"+progress_summary(slot.player.cells,slot.completed)

func remote_summary(row: Dictionary, slot: Session, compatible: bool) -> String:
	var own: String = " · dieses Gerät" if row.device_id == client.identity.device_id else ""
	var device := "%s · Gerätekennung %s%s" % [row.device_name,row.device_id.left(8),own]
	var timestamp: String = row.get("updated_at",row.get("created_at",""))
	var version := "Version %d · " % row.server_revision if row.has("server_revision") else ""
	var raster := "Rasterrevision %d" % row.definition_revision
	var progress := "Zurückgesetzt · leerer Stand"
	if row.kind == "snapshot":
		raster += " · %d × %d" % [row.save.width,row.save.height]
		progress = progress_summary(row.save.cells,row.save.completed)
	if row.definition_revision != slot.definition.revision:
		raster += " · inkompatibel mit Rasterrevision %d dieses Spiels" % slot.definition.revision
	elif not compatible:
		raster += " · für dieses Raster nicht verwendbar"
	return "%s\n%s%s UTC\n%s\n%s" % [device,version,timestamp.left(19).replace("T"," "),raster,progress]

func progress_summary(cells: Array, completed: bool) -> String:
	var filled := 0
	var crossed := 0
	for cell: int in cells:
		if cell > 0: filled += 1
		elif cell == 0: crossed += 1
	var state := "Abgeschlossen" if completed else ("Begonnen" if filled+crossed > 0 else "Keine Zelle markiert")
	return "%s · %d ausgefüllt · %d als leer markiert · %d Zellen" % [state,filled,crossed,cells.size()]

func choose(selection: Window, comparison: Window, result: Label, actions: Control, stamp: int, decision: Callable) -> void:
	if stamp != client.epoch or client.changing or client.transport_busy: return
	for action: Button in actions.get_children(): action.disabled = true
	result.text = "Auswahl wird erneut geprüft …"
	var accepted: bool = await decision.call()
	if not is_instance_valid(comparison) or not comparison.visible: return
	if accepted:
		comparison.queue_free()
		selection.queue_free()
	else:
		result.text = client.problem if not client.problem.is_empty() else "Auswahl konnte nicht gespeichert werden."
		for action: Button in actions.get_children(): action.disabled = false

func abandon() -> void:
	var original: Dictionary = client.profile.resume_request()
	if not original.is_empty(): confirm_choice("Diesen offenen Übertragungsauftrag ausdrücklich beenden? Der Spielstand bleibt lokal erhalten.",client.abandon.bind(original))
