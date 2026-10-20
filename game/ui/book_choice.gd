extends OptionButton
## Native OptionButton/PopupMenu with shared HZ-B paper and icon resources.
const Controls = preload("res://ui/book_controls.gd")
const Text = preload("res://ui/ui_text.gd")
var ui_scale: float = 1.0:
	set(value):
		if ui_scale == value: return
		ui_scale = value
		get_popup().hide()
		if is_inside_tree(): _style()

func _ready() -> void:
	add_to_group("book-choices")
	_style()
	resized.connect(func() -> void: get_popup().hide())
	visibility_changed.connect(func() -> void:
		if not is_visible_in_tree(): get_popup().hide())
	get_viewport().size_changed.connect(func() -> void: get_popup().hide())

func _input(event: InputEvent) -> void:
	# Embedded PopupMenu closes on focus loss, deferred by Godot. The same
	# outside press can reach its parent before that close is applied.
	# Consume only that parent event; native popup selection/closing stays native.
	var popup := get_popup()
	if popup.visible and event is InputEventMouseButton:
		if not Rect2(Vector2(popup.position),Vector2(popup.size)).has_point(event.position):
			get_viewport().set_input_as_handled()

func _style() -> void:
	theme = Theme.new()
	Controls.styles(theme,"OptionButton",str(name),ui_scale)
	theme.set_icon("arrow","OptionButton",Controls.icon("chevron-down",ui_scale))
	theme.set_constant("modulate_arrow","OptionButton",0)
	theme.set_constant("arrow_margin","OptionButton",roundi(10*ui_scale))
	get_popup().theme = Controls.popup_theme(str(name),ui_scale,Text.font())
	get_popup().prefer_native_menu = false

static func dismiss_all(tree: SceneTree) -> void:
	for item: Node in tree.get_nodes_in_group("book-choices"): item.get_popup().hide()
