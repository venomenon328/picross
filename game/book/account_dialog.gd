extends VBoxContainer
const Help = preload("res://ui/settings_help.gd")
const Paper = preload("res://ui/book_style.gd")
const Controls = preload("res://ui/book_controls.gd")

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
var actions := VBoxContainer.new()
var action_buttons: Dictionary[String, Button] = {}
var logout_button: Button
var action := ""
var username := LineEdit.new()
var password := LineEdit.new()
var password_row := HBoxContainer.new()
var password_help := Help.new()
var code := LineEdit.new()
var username_caption: Label
var password_caption := Label.new()
var code_caption := Label.new()
var submit_button: Button
var message := Label.new()
var choices := VBoxContainer.new()
var choice_key := []
var notice := VBoxContainer.new()
var recovery_code := LineEdit.new()
var copy_status := Label.new()
var layout_scale := 0.0
var copy_stamp := 0
var copy_callbacks: Array[JavaScriptObject] = []

func configure(owner: Node) -> void:
	client = owner
	client.app.info_scroll.follow_focus = true
	for control: Control in [profile_status,sync_status,message,actions,auth_form]:
		add_child(control)
	for label: Label in [profile_status,sync_status,message,copy_status]:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	for id: String in MODES:
		var button := settings_button(actions,MODES[id][0],set_mode.bind(id))
		button.name = "account-"+id
		action_buttons[id] = button
	logout_button = settings_button(actions,"Abmelden",client.logout)
	logout_button.name = "account-logout"
	username_caption = client.app.label("Benutzername",14)
	for control: Control in [username_caption,username,password_caption,password_row,code_caption,code]:
		auth_form.add_child(control)
	password.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	password_row.add_child(password)
	password_help.tooltip_text = "Mindestens 8 Zeichen"
	password_help.accessibility_name = "Passwortanforderung erklären"
	password_row.add_child(password_help)
	username.name = "account-username"
	username.max_length = 32
	username.accessibility_name = "Benutzername"
	password.name = "account-password"
	password.secret = true
	code.name = "account-code"
	code.secret = true
	submit_button = settings_button(auth_form,"Anmelden",submit)
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
	auth_form.hide()

func layout(value: float) -> void:
	if is_equal_approx(layout_scale,value): return
	layout_scale = value
	for container: VBoxContainer in [self,actions,auth_form,choices,notice]:
		container.add_theme_constant_override("separation",roundi(8*value))
	password_row.add_theme_constant_override("separation",roundi(10*value))
	password_help.layout(value)
	for field: LineEdit in [username,password,code,recovery_code]:
		field.custom_minimum_size.y = 44*value
		var outline = Paper.make("settings/"+str(field.name),value,Color.TRANSPARENT)
		outline.content_margin_left = 12*value
		outline.content_margin_right = 12*value
		field.add_theme_stylebox_override("normal",outline)
		field.add_theme_stylebox_override("read_only",outline)
		var focus = Paper.make("settings/"+str(field.name)+"/focus",value,Color.TRANSPARENT)
		focus.focus = true
		field.add_theme_stylebox_override("focus",focus)
		for role: String in ["font_color","font_uneditable_color","font_selected_color","caret_color"]:
			field.add_theme_color_override(role,Controls.INK)
		field.add_theme_color_override("selection_color",Color("c5d6cd"))

func settings_button(parent: Control, caption: String, action: Callable) -> Button:
	var item: Button = client.app._text_button(caption,action)
	parent.add_child(item)
	return item

func set_mode(next_action: String) -> void:
	if client.changing or has_code() or not client.can_authenticate(next_action): return
	reset_form()
	action = next_action
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
	message.text = ""
	update_interaction()
	client.app._layout_book()
	var first: Control = username if username.visible else password
	first.grab_focus()

func reset_form() -> void:
	action = ""
	clear_secrets()
	password_help.dismiss_tooltip()

func clear_secrets() -> void:
	password.clear()
	code.clear()

func submit() -> void:
	if not action.is_empty():
		await client.authenticate(action,username.text,password.text,code.text)

func has_code() -> bool:
	return notice.visible

func show_code(value: String) -> void:
	recovery_code.text = value
	copy_status.text = ""
	reset_form()
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
	focus_actions()

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

func focus_actions() -> void:
	var target: Button = logout_button if client.signed_in() else action_buttons["login"]
	if target.is_visible_in_tree():
		target.grab_focus()
		client.app.info_scroll.ensure_control_visible(target)

func update_interaction() -> void:
	var configured: bool = not client.access.server.is_empty()
	var signed_in: bool = client.signed_in()
	var focused := get_viewport().gui_get_focus_owner()
	var restore_focus := focused != null and auth_form.is_visible_in_tree() and auth_form.is_ancestor_of(focused)
	if not action.is_empty() and not client.can_authenticate(action): reset_form()
	actions.visible = configured and not has_code()
	for id: String in action_buttons:
		var button := action_buttons[id]
		button.visible = signed_in == (id == "recovery-code")
		button.disabled = client.changing
	logout_button.visible = signed_in
	logout_button.disabled = client.changing
	auth_form.visible = actions.visible and not action.is_empty()
	submit_button.disabled = client.changing
	for field: LineEdit in [username,password,code]:
		field.editable = not client.changing
	choices.visible = actions.visible
	for button: Button in choices.get_children():
		button.disabled = client.changing
	if restore_focus and not auth_form.is_visible_in_tree() and not has_code() and not client.changing:
		focus_actions()

func refresh_choices() -> void:
	var active: bool = client.profile != null
	var signed_in: bool = client.signed_in()
	var accounts: Dictionary = client.access.accounts() if not signed_in else {}
	var recovery: bool = not client.recovery_session.is_empty()
	var has_request: bool = signed_in and not client.profile.resume_request().is_empty()
	var key := [client.epoch,accounts,recovery,has_request,signed_in]
	if key == choice_key: return
	choice_key = key
	for child: Node in choices.get_children():
		choices.remove_child(child)
		child.queue_free()
	if recovery: settings_button(choices,"Geschützten Bestand abgleichen",client.inspect_recovery)
	for account: String in accounts:
		if active and accounts[account] == client.identity.account_id: continue
		settings_button(choices,account+" lokal öffnen",client.resume_local.bind(accounts[account]))
	if active:
		if not signed_in: settings_button(choices,"Zum Gastprofil wechseln",client.logout)
		settings_button(choices,"Lokale Sicherung erneut versuchen",client.profile.retry_local)
		if has_request: settings_button(choices,"Offenen Auftrag abbrechen …",abandon)
	update_interaction()
	client.app._layout_book()

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

func abandon() -> void:
	var original: Dictionary = client.profile.resume_request()
	if not original.is_empty(): confirm_choice("Diesen offenen Übertragungsauftrag ausdrücklich beenden? Der Spielstand bleibt lokal erhalten.",client.abandon.bind(original))
