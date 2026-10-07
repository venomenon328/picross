extends "res://ui/main.gd"
## This scene is never the regular main_scene. Isolation precedes Main._ready.
const StudyBoard = preload("res://study/board.gd")
const Samples = preload("res://study/samples.gd")
const Details = preload("res://study/details.gd")
const Numerals = preload("res://study/numerals.gd")
var variant_button: Button
var animation_toggle: CheckBox
var details: Details
var study_root: String

func create_board() -> Board:
	return StudyBoard.new()

func _ready() -> void:
	study_root = OS.get_cache_dir().path_join("picross-zs1/session-%d-%d" % [OS.get_process_id(), Time.get_ticks_usec()])
	var previous_override: String = SaveStore.test_root_override
	SaveStore.test_root_override = study_root
	super._ready()
	SaveStore.test_root_override = previous_override
	get_window().title = "picross · ZS-1 · isolierte Gestaltungsprobe"
	variant_button = _text_button("", cycle_variant)
	# Reuses the title's free right-hand region, above every working surface.
	page.add_child(variant_button)
	animation_toggle = CheckBox.new()
	animation_toggle.text = "Zellanimationen"
	animation_toggle.button_pressed = true
	animation_toggle.toggled.connect(func(enabled: bool) -> void: board.set_animations(enabled))
	settings_panel.add_child(animation_toggle)
	settings_panel.move_child(animation_toggle, 1)
	var study_label: Label = label("ZS-1 · isolierte Studie\nDer Variantenknopf oben wechselt Baseline / Tinte / Stift am selben Stand.\nNeue Starts verwenden frische Studienstände. Eigene P1-Spielstände bleiben getrennt.", 16)
	study_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	settings_panel.add_child(study_label)
	settings_panel.add_child(_text_button("Vergleichsstand dieses Blatts wiederherstellen", restore_sample))
	settings_panel.add_child(_text_button("Leeres Studienblatt", empty_sample))
	settings_panel.add_child(_text_button("Ziffernprobe bis 100", show_numerals))
	for i: int in range(3, choices.size()):
		choices[i].hide()
		album_previews[i].get_parent().hide()
	details = Details.new()
	details.app = self
	details.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(details)
	for i: int in range(3):
		sessions[i] = Samples.create(sessions[i].definition)
	session = sessions[0]
	board.session = session
	select_puzzle(0)
	update_variant()
	if OS.get_cmdline_user_args().has("--zs1-smoke"):
		call_deferred("study_smoke")

func restore_sample() -> void:
	replace_sample(true)

func show_numerals() -> void:
	var dialog: AcceptDialog = AcceptDialog.new()
	dialog.title = "ZS-1 · " + ["Baseline", "Tinte", "Stift"][board.style]
	dialog.min_size = Vector2i(740, 490)
	var specimen: Numerals = Numerals.new()
	specimen.session = Session.new(sessions[1].definition)
	specimen.style = board.style
	specimen.custom_minimum_size = Vector2(720, 445)
	specimen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dialog.add_child(specimen)
	add_child(dialog)
	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	dialog.popup_centered()

func empty_sample() -> void:
	replace_sample(false)

func replace_sample(pattern: bool) -> void:
	_cancel_interaction()
	var index: int = sessions.find(session)
	if index < 0 or index > 2:
		return
	var replacement: Session = Samples.create(session.definition) if pattern else Session.new(session.definition)
	sessions[index] = replacement
	session = replacement
	board.session = replacement
	board.restore_view(replacement.view_state)
	_save_current()
	open_puzzle()

func cycle_variant() -> void:
	if session.gesture.active:
		return
	board.set_style((board.style + 1) % 3)
	update_variant()

func update_variant() -> void:
	variant_button.text = ["ZS-1 · Baseline →", "ZS-1 · Tinte →", "ZS-1 · Stift →"][board.style]
	variant_button.tooltip_text = "Nächste Variante am identischen eigenen Spielerstand"
	_layout_book()
	refresh()

func _layout_book() -> void:
	super._layout_book()
	if variant_button != null:
		var material: Rect2 = surface.material_rect()
		_place(variant_button, Rect2(material.position + Vector2(material.size.x * 0.52, material.size.y * 0.039), Vector2(210 * ui_scale, 44 * ui_scale)))
	if details != null:
		details.size = size
		details.queue_redraw()

func _undo() -> void:
	board.clear_effects()
	super._undo()

func _redo() -> void:
	board.clear_effects()
	super._redo()

func study_smoke() -> void:
	if store.root != study_root or store.root.contains("app_userdata"):
		get_tree().quit(4)
		return
	board.pointer_press(board.view.cell_rect(Vector2i(0, 0)).get_center(), MOUSE_BUTTON_LEFT)
	board.pointer_release(board.view.cell_rect(Vector2i(0, 0)).get_center(), true)
	if session.player.cells[0] != 1 or not FileAccess.file_exists(store.path_for("f01")):
		get_tree().quit(5)
		return
	print("ZS1_STUDY_OK root=", store.root, " style=", board.style, " own_cell=", session.player.cells[0])
	get_tree().quit(0)
