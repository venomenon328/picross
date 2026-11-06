extends VBoxContainer
## Existing settings-page controls plus a viewport-local confirmation card.
const Preference = preload("res://model/display_preference.gd")
const Policy = preload("res://model/display_policy.gd")
const Controller = preload("res://ui/display_controller.gd")
const Backend = preload("res://ui/display_backend.gd")
const Choice = preload("res://ui/book_choice.gd")
const Paper = preload("res://ui/book_style.gd")
const Text = preload("res://ui/ui_text.gd")
const NAMES: Array[String] = ["Fenster", "Rahmenloses Fenster", "Exklusives Vollbild"]
var app: Control
var controller: Controller
var mode_choice: OptionButton
var size_choice: OptionButton
var feedback: Label
var save_current: Button
var shield: Control
var card: PanelContainer
var prompt: Label
var accept: Button
var reject: Button

static func supported(owner: Control) -> bool:
	return OS.has_feature("windows") and not OS.has_feature("web") and DisplayServer.get_name() != "headless" and owner.get_viewport() == owner.get_tree().root and not OS.get_cmdline_user_args().has("--p1-capture")

func configure(owner: Control, control: Controller) -> void:
	app = owner
	controller = control
	name = "display-settings"
	add_child(app.label("Anzeigemodus",16))
	mode_choice = Choice.new()
	mode_choice.name = "display-mode"
	mode_choice.paper_transparent = true
	for caption: String in NAMES: mode_choice.add_item(caption)
	mode_choice.item_selected.connect(func(index: int) -> void:
		app._cancel_interaction()
		controller.request(Preference.MODES[index],controller.active.preset))
	add_child(mode_choice)
	add_child(app.label("Fenstergröße",16))
	size_choice = Choice.new()
	size_choice.name = "display-size"
	size_choice.paper_transparent = true
	for preset: String in Preference.PRESETS: size_choice.add_item(preset.replace("x"," × "))
	size_choice.item_selected.connect(func(index: int) -> void:
		app._cancel_interaction()
		controller.request("window",Preference.PRESETS[index]))
	add_child(size_choice)
	feedback = app.label("",16)
	feedback.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(feedback)
	save_current = app._text_button("Aktuelle Anzeige übernehmen",func() -> void:
		controller.request(controller.active.mode,controller.active.preset))
	save_current.paper_transparent = true
	add_child(save_current)
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	shield = Control.new()
	shield.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shield.mouse_filter = Control.MOUSE_FILTER_STOP
	layer.add_child(shield)
	card = PanelContainer.new()
	shield.add_child(card)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation",16)
	card.add_child(column)
	column.add_child(app.label("Anzeige beibehalten?",26))
	prompt = app.label("",16)
	prompt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(prompt)
	accept = app._text_button("Beibehalten",controller.confirm)
	reject = app._text_button("Abbrechen",controller.cancel)
	column.add_child(accept)
	column.add_child(reject)
	controller.changed.connect(refresh)
	app.resized.connect(layout_card)
	refresh()

func refresh() -> void:
	if controller.backend == null: return
	var state: Dictionary = controller.active
	var busy: bool = controller.preview or controller.applying
	var choices: Array[String] = Policy.available(controller.backend.context())
	mode_choice.select(Preference.MODES.find(state.mode))
	size_choice.select(Preference.PRESETS.find(state.preset))
	size_choice.text = size_choice.get_item_text(size_choice.selected)
	if state.mode != "window":
		var desktop: Vector2i = controller.backend.context().desktop
		size_choice.text = "%d × %d (Desktop)" % [desktop.x,desktop.y]
	mode_choice.disabled = busy
	size_choice.disabled = busy or state.mode != "window"
	for index: int in range(Preference.PRESETS.size()):
		size_choice.set_item_disabled(index,Preference.PRESETS[index] not in choices)
	feedback.text = "" if controller.message == "Anzeige gespeichert." else controller.message
	feedback.visible = not feedback.text.is_empty()
	save_current.visible = not busy and state != controller.saved and state.mode in Preference.MODES
	var was_visible: bool = shield.visible
	shield.visible = (busy and controller.purpose == "preview") or controller.preview
	prompt.text = "Anzeige wird geprüft …" if controller.applying else "Diese Anzeige innerhalb von %d Sekunden bestätigen. Danach wird die vorherige Anzeige wiederhergestellt." % controller.seconds_left()
	accept.disabled = controller.applying
	reject.disabled = controller.applying
	if shield.visible and not was_visible:
		Choice.dismiss_all(get_tree())
		accept.grab_focus()
	layout_card()

func layout_card() -> void:
	if app == null: return
	var u: float = app.ui_scale
	add_theme_constant_override("separation",roundi(10*u))
	for choice: OptionButton in [mode_choice,size_choice]:
		choice.ui_scale = u
		choice.custom_minimum_size.y = 44*u
	var style = Paper.make("display-confirmation",u)
	style.set_content_margin_all(20*u)
	card.add_theme_stylebox_override("panel",style)
	card.theme = app.theme
	for button: Button in [accept,reject,save_current]:
		button.ui_scale = u
		button.custom_minimum_size.y = 44*u
		button.add_theme_font_override("font",Text.small_font(Text.small_size(u)))
		button.add_theme_font_size_override("font_size",Text.small_size(u))
	var bounds: Vector2 = app.get_viewport_rect().size
	card.size.x = minf(560*u,maxf(1,bounds.x-32))
	card.size.y = card.get_combined_minimum_size().y
	card.position = ((bounds-card.size)/2).max(Vector2.ZERO)

func _input(event: InputEvent) -> void:
	if controller.preview and event.is_action_pressed("ui_cancel"):
		controller.cancel()
		get_viewport().set_input_as_handled()
