extends "res://ui/book_button.gd"
## Local focus entry for the same styled tooltip used by mouse hover.
var focus_tip: Control
var focus_layer: CanvasLayer

func _ready() -> void:
	super._ready()
	focus_entered.connect(func() -> void: call_deferred("show_focus_tooltip"))
	pressed.connect(show_focus_tooltip)

func _get_tooltip(at_position: Vector2) -> String:
	return "" if is_instance_valid(focus_tip) else super._get_tooltip(at_position)

func show_focus_tooltip() -> void:
	if not has_focus() or not is_visible_in_tree() or is_instance_valid(focus_tip): return
	focus_layer = CanvasLayer.new()
	focus_layer.layer = 90
	add_child(focus_layer)
	focus_tip = BookTooltip.new()
	focus_tip.configure(tooltip_text,ui_scale,get_viewport_rect().size.x,get_theme_font("font"))
	focus_layer.add_child(focus_tip)
	call_deferred("_position_tip")

func _position_tip() -> void:
	if not is_instance_valid(focus_tip): return
	var bounds: Vector2 = get_viewport_rect().size
	focus_tip.size = focus_tip.get_combined_minimum_size()
	var origin: Vector2 = global_position+Vector2(size.x,8*ui_scale)
	focus_tip.position = origin.clamp(Vector2.ONE*8,(bounds-focus_tip.size-Vector2.ONE*8).max(Vector2.ONE*8))

func dismiss_tooltip() -> void:
	super.dismiss_tooltip()
	if is_instance_valid(focus_layer): focus_layer.queue_free()
	focus_layer = null
	focus_tip = null

func _input(event: InputEvent) -> void:
	if is_instance_valid(focus_tip) and event.is_action_pressed("ui_cancel"):
		dismiss_tooltip()
		get_viewport().set_input_as_handled()
