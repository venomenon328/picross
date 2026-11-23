extends VBoxContainer
const Session = preload("res://model/session.gd")
const BookChoice = preload("res://ui/book_choice.gd")

const MODES := {
	"login": ["Anmelden", "Passwort", ""],
	"register": ["Registrieren", "Passwort", "Einladungscode"],
	"recover": ["Passwort wiederherstellen", "Neues Passwort", "Wiederherstellungscode"],
	"recovery-code": ["Neuen Wiederherstellungscode erzeugen", "Aktuelles Passwort", ""],
}
const COPY_FALLBACK := "Kopieren konnte nicht bestätigt werden. Code im Feld markieren und manuell kopieren."

var client: Node
var profile_status := Label.new()
var sync_status := Label.new()
var auth_form := VBoxContainer.new()
var mode := BookChoice.new()
var username := LineEdit.new()
var password := LineEdit.new()
var code := LineEdit.new()
var username_caption: Label
var password_caption := Label.new()
var code_caption := Label.new()
var submit_button: Button
var message := Label.new()
var puzzles: BookChoice
var choices := VBoxContainer.new()
var choice_key := []
var notice := VBoxContainer.new()
var recovery_code := LineEdit.new()
var copy_status := Label.new()
var copy_stamp := 0
var copy_callbacks: Array[JavaScriptObject] = []

func configure(owner: Node) -> void:
	client = owner
	client.app.info_scroll.follow_focus = true
	for control: Control in [profile_status,sync_status,auth_form,message]:
		add_child(control)
	for label: Label in [profile_status,sync_status,message,copy_status]:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	mode.name = "account-action"
	mode.accessibility_name = "Kontoaktion"
	mode.item_selected.connect(func(_index: int) -> void: set_mode(mode.get_selected_metadata()))
	username_caption = client.app.label("Benutzername",14)
	var hint: Label = client.app.label("8–128 Zeichen (Unicode-Codepunkte). Leerzeichen zählen mit.",14)
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	for control: Control in [mode,username_caption,username,password_caption,password,hint,code_caption,code]:
		auth_form.add_child(control)
	username.name = "account-username"
	username.max_length = 32
	username.accessibility_name = "Benutzername"
	password.name = "account-password"
	password.secret = true
	code.name = "account-code"
	code.secret = true
	submit_button = settings_button(self,"Anmelden",submit)
	add_child(notice)
	add_child(choices)
	submit_button.name = "submit-account-action"
	var caption: Label = client.app.label("Diesen Wiederherstellungscode sicher aufbewahren. Er wird einmal angezeigt.",16)
	caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	notice.add_child(caption)
	recovery_code.name = "issued-recovery-code"
	recovery_code.accessibility_name = "Wiederherstellungscode"
	recovery_code.editable = false
	recovery_code.drag_and_drop_selection_enabled = false
	notice.add_child(recovery_code)
	notice.add_child(copy_status)
	settings_button(notice,"Kopieren",copy_code)
	settings_button(notice,"Code schließen",clear_notice)
	notice.hide()
	refresh_choices()

func layout(value: float) -> void:
	mode.ui_scale = value
	if puzzles != null: puzzles.ui_scale = value
	for container: VBoxContainer in [self,auth_form,choices,notice]:
		container.add_theme_constant_override("separation",roundi(8*value))
	for field: LineEdit in [username,password,code,recovery_code]:
		field.custom_minimum_size.y = 44*value

func settings_button(parent: Control, caption: String, action: Callable) -> Button:
	var item: Button = client.app._text_button(caption,action)
	parent.add_child(item)
	return item

func set_mode(action: String, clear_fields: bool = true) -> void:
	for i: int in range(mode.item_count):
		if mode.get_item_metadata(i) == action:
			mode.select(i)
			break
	var labels: Array = MODES[action]
	submit_button.text = labels[0]
	submit_button.accessibility_name = labels[0]
	password_caption.text = labels[1]
	password.accessibility_name = labels[1]
	code_caption.text = labels[2]
	code.accessibility_name = labels[2]
	code_caption.visible = not code_caption.text.is_empty()
	code.visible = code_caption.visible
	username.visible = action != "recovery-code"
	username_caption.visible = username.visible
	if clear_fields: clear_secrets()

func clear_secrets() -> void:
	password.clear()
	code.clear()

func submit() -> void:
	await client.authenticate(mode.get_selected_metadata(),username.text,password.text,code.text)

func has_code() -> bool:
	return notice.visible

func show_code(value: String) -> void:
	recovery_code.text = value
	copy_status.text = ""
	notice.show()
	update_interaction()
	focus_code.call_deferred()

func focus_code() -> void:
	if has_code() and recovery_code.is_visible_in_tree():
		recovery_code.grab_focus()
		client.app.info_scroll.ensure_control_visible(recovery_code)

func clear_notice() -> void:
	copy_stamp += 1
	copy_callbacks.clear()
	recovery_code.clear()
	clear_secrets()
	copy_status.text = ""
	notice.hide()
	update_interaction()
	submit_button.grab_focus()

func copy_code() -> void:
	copy_stamp += 1
	var stamp := copy_stamp
	var value := recovery_code.text
	if not OS.has_feature("web"):
		DisplayServer.clipboard_set(value)
		copy_result(DisplayServer.clipboard_get() == value,stamp)
		return
	var clipboard: JavaScriptObject = JavaScriptBridge.get_interface("navigator").clipboard
	if clipboard == null:
		copy_result(false,stamp)
		return
	copy_status.text = "Kopieren läuft …"
	var success := JavaScriptBridge.create_callback(func(_args: Array) -> void: copy_result(true,stamp))
	var failure := JavaScriptBridge.create_callback(func(_args: Array) -> void: copy_result(false,stamp))
	copy_callbacks.assign([success,failure])
	clipboard.writeText(value).then(success,failure)
	await get_tree().create_timer(3.0).timeout
	if stamp == copy_stamp and not copy_callbacks.is_empty(): copy_result(false,stamp)

func copy_result(ok: bool, stamp: int) -> void:
	if stamp != copy_stamp or not has_code(): return
	copy_status.text = "Kopiert." if ok else COPY_FALLBACK
	copy_callbacks.clear()

func update_interaction() -> void:
	var configured: bool = not client.access.server.is_empty()
	auth_form.visible = configured and not has_code()
	submit_button.visible = auth_form.visible
	choices.visible = configured and not has_code()
	mode.disabled = client.changing
	submit_button.disabled = client.changing
	for button: Button in choices.find_children("*","Button",true,false):
		button.disabled = client.changing

func refresh_choices() -> void:
	var active: bool = client.profile != null
	var accounts: Dictionary = client.access.accounts()
	var recovery: bool = not client.recovery_session.is_empty()
	var local_choices: bool = active and client.profile._state.get("entries",{}).values().any(func(e: Dictionary) -> bool: return e.status == "recovery_choice")
	var has_request: bool = active and not client.profile.resume_request().is_empty()
	var key := [client.epoch,accounts,recovery,local_choices,has_request]
	if key == choice_key: return
	choice_key = key
	var previous: String = mode.get_selected_metadata() if mode.selected >= 0 else "login"
	var actions := ["login","register","recover"]
	if active: actions.append("recovery-code")
	if mode.item_count != actions.size():
		mode.clear()
		for action: String in actions:
			mode.add_item(MODES[action][0])
			mode.set_item_metadata(mode.item_count-1,action)
		set_mode(previous if previous in actions else "login",false)
	var selected: int = puzzles.selected if puzzles != null and puzzles.item_count > 0 else 0
	puzzles = null
	for child: Node in choices.get_children():
		choices.remove_child(child)
		child.queue_free()
	if recovery: settings_button(choices,"Geschützten Bestand abgleichen",client.inspect_recovery)
	for account: String in accounts:
		if active and accounts[account] == client.identity.account_id: continue
		settings_button(choices,account+" lokal öffnen",client.resume_local.bind(accounts[account]))
	if active:
		settings_button(choices,"Abmelden",client.logout)
		puzzles = BookChoice.new()
		puzzles.name = "account-puzzle"
		puzzles.accessibility_name = "Rätsel für Kontoaktionen"
		choices.add_child(puzzles)
		for slot in client.app.sessions:
			puzzles.add_item(slot.album_title())
			puzzles.set_item_metadata(puzzles.item_count-1,slot.definition.id)
		if puzzles.item_count > 0:
			puzzles.select(clampi(selected,0,puzzles.item_count-1))
			settings_button(choices,"Konflikte und Versionen",versions)
			settings_button(choices,"Gaststand übernehmen",import_guest.bind(false))
			settings_button(choices,"Alle Gaststände übernehmen",import_guest.bind(true))
			if local_choices:
				settings_button(choices,"Lokale Fassung erneut anbieten",recover_slot.bind(false))
				settings_button(choices,"Serverfassung laden",recover_slot.bind(true))
		settings_button(choices,"Lokale Sicherung erneut versuchen",client.profile.retry_local)
		if has_request: settings_button(choices,"Offenen Auftrag abbrechen …",abandon)
	update_interaction()
	client.app._layout_book()

func button(parent: Control, caption: String, action: Callable) -> void:
	var item := Button.new()
	item.text = caption
	item.pressed.connect(action)
	parent.add_child(item)

func confirm_choice(caption: String, action: Callable) -> void:
	var stamp: int = client.epoch
	var question := ConfirmationDialog.new()
	question.dialog_text = caption
	client.add_child(question)
	question.theme = client.app.theme
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
	if client.transport_busy or client.changing:
		message.text = "Bitte den laufenden Abgleich abwarten und erneut versuchen."
		return
	client.changing = true
	client.refresh_status()
	var conflicts: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/conflicts")
	var history: Dictionary = await client.fetch_pages("/v1/puzzles/"+id+"/history")
	client.changing = false
	client.refresh_status()
	if not is_visible_in_tree() or stamp != client.epoch: return
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

func version_window(parent: Node, heading: String, close_caption: String) -> AcceptDialog:
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
