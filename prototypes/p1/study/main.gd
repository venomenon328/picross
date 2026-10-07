extends "res://ui/main.gd"
## This scene is never the regular main_scene. Isolation precedes Main._ready.
const StudyBoard = preload("res://study/board.gd")
const Samples = preload("res://study/samples.gd")
const Numerals = preload("res://study/numerals.gd")
var variant_button: Button
var font_button: Button
var animation_toggle: CheckBox
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
	for item: Node in album_content.get_children():
		if item is Label and item.text == "Neun Blätter zum Entdecken":
			item.text = "Drei Blätter für den Gestaltungsvergleich"
	font_button = _text_button("", cycle_font)
	# Reuses the title's free right-hand region, above every working surface.
	page.add_child(font_button)
	animation_toggle = CheckBox.new()
	animation_toggle.text = "Zellanimationen"
	animation_toggle.button_pressed = true
	animation_toggle.toggled.connect(func(enabled: bool) -> void: board.set_animations(enabled))
	settings_panel.add_child(animation_toggle)
	settings_panel.move_child(animation_toggle, 1)
	var study_label: Label = label("ZS-1 · Stift und Timing sind gewählt.\nHinweisfont oben wechseln: Bakso Daging / Chalkboard, zusätzlich Plex als bisherige Referenz. Der Zellstil lässt sich hier unabhängig umschalten.\nNeue Starts verwenden frische Studienstände.", 16)
	study_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	settings_panel.add_child(study_label)
	var quit_control: Node = settings_panel.get_child(settings_panel.get_child_count() - 2)
	variant_button = _text_button("", cycle_variant)
	settings_panel.add_child(variant_button)
	settings_panel.add_child(_text_button("Vergleichsstand dieses Blatts wiederherstellen", restore_sample))
	settings_panel.add_child(_text_button("Leeres Studienblatt", empty_sample))
	settings_panel.add_child(_text_button("Ziffernprobe bis 100", show_numerals))
	settings_panel.move_child(quit_control, settings_panel.get_child_count() - 1)
	for i: int in range(3, choices.size()):
		choices[i].hide()
		album_previews[i].get_parent().hide()
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
	dialog.title = "ZS-1 · " + StudyBoard.Fonts.LABELS[board.font_choice]
	dialog.min_size = Vector2i(740, 490)
	var specimen: Numerals = Numerals.new()
	specimen.session = Session.new(sessions[1].definition)
	specimen.style = board.style
	specimen.set_font_choice(board.font_choice)
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
	board.set_style(2 if board.style == 0 else 0)
	update_variant()

func cycle_font() -> void:
	if session.gesture.active:
		return
	board.set_font_choice((board.font_choice + 1) % 3)
	update_variant()

func update_variant() -> void:
	variant_button.text = "Zellstil: Baseline →" if board.style == 0 else "Zellstil: Stift →"
	variant_button.tooltip_text = "Zellstil wechseln; Hinweisfont bleibt erhalten"
	font_button.text = StudyBoard.Fonts.LABELS[board.font_choice] + " →"
	font_button.tooltip_text = "Hinweisfont wechseln; Zellstil und eigener Spielstand bleiben erhalten"
	_layout_book()
	refresh()

func _layout_book() -> void:
	super._layout_book()
	if font_button != null:
		var material: Rect2 = surface.material_rect()
		_place(font_button, Rect2(material.position + Vector2(material.size.x * 0.52, material.size.y * 0.039), Vector2(210 * ui_scale, 44 * ui_scale)))

func _undo() -> void:
	board.clear_effects()
	super._undo()

func _redo() -> void:
	board.clear_effects()
	super._redo()

func study_smoke() -> void:
	for choice: int in [1, 2]:
		var evidence: Dictionary = StudyBoard.Fonts.evidence(choice)
		if not evidence.digits_native or evidence.sha256 != StudyBoard.Fonts.HASHES[choice]:
			get_tree().quit(6)
			return
		print("ZS1_FONT_OK ", JSON.stringify(evidence))
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
