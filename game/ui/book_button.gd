extends Button
## Shared KB paper button. Precise rectangular hits; identity-bound ink decoration.
const INK = Color("293e3d")
const PAPER = Color("fffaf0")
const Scribble = preload("res://ui/scribble.gd")
const BookTooltip = preload("res://ui/book_tooltip.gd")
var action_id: String = ""
var content_surface: bool = false
var selected: bool = false:
	set(value):
		selected = value
		queue_redraw()
var swatch: Color = Color.TRANSPARENT
var image: Texture2D
var ui_scale: float = 1.0:
	set(value):
		if ui_scale != value: dismiss_tooltip()
		ui_scale = value
		queue_redraw()
var tooltip_ref: WeakRef

func _ready() -> void:
	add_to_group("book-buttons")
	for state: String in ["normal", "hover", "pressed", "disabled", "focus"]:
		if not content_surface: add_theme_stylebox_override(state, StyleBoxEmpty.new())
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	visibility_changed.connect(func() -> void:
		if not is_visible_in_tree(): dismiss_tooltip())
	resized.connect(dismiss_tooltip)
	if accessibility_name.is_empty(): accessibility_name = text if not text.is_empty() else tooltip_text

func _make_custom_tooltip(for_text: String) -> Object:
	var tip: BookTooltip = BookTooltip.new()
	tip.configure(for_text, ui_scale, get_viewport_rect().size.x, get_theme_font("font"))
	tooltip_ref = weakref(tip)
	return tip

func dismiss_tooltip() -> void:
	if tooltip_ref == null: return
	var tip: Control = tooltip_ref.get_ref()
	if tip != null and tip.is_inside_tree() and tip.get_window() != get_window():
		tip.get_window().hide()
	tooltip_ref = null

static func dismiss_all(tree: SceneTree) -> void:
	for item: Node in tree.get_nodes_in_group("book-buttons"): item.dismiss_tooltip()

static func points(box: Rect2, cut: float) -> PackedVector2Array:
	var p: Vector2 = box.position
	var e: Vector2 = box.end
	return PackedVector2Array([p + Vector2(cut, 0), Vector2(e.x-cut,p.y), Vector2(e.x,p.y+cut), e-Vector2(0,cut), e-Vector2(cut,0), Vector2(p.x+cut,e.y), Vector2(p.x,e.y-cut), p+Vector2(0,cut), p+Vector2(cut,0)])

func swatch_strokes() -> Array:
	return Scribble.outline_strokes(Rect2(Vector2.ZERO,size).grow(-1.0),"swatch/"+action_id,1.2)

func _draw() -> void:
	if content_surface: return
	var u: float = ui_scale
	var box: Rect2 = Rect2(Vector2.ZERO, size)
	var body: Color = Color("f6eedb")
	if disabled:
		body = Color("e9e2d4")
	elif selected:
		body = Color("293f3e")
	elif is_pressed():
		body = Color("c5d6cd")
	elif is_hovered():
		body = Color("e0ece6")
	draw_colored_polygon(points(box.grow(-1.5*u), 3*u), body)
	if swatch.a > 0:
		for line: Dictionary in swatch_strokes():
			Scribble.paint(self,line,Color("68583f"))
	else:
		for line: Dictionary in Scribble.outline_strokes(box.grow(-2*u),"book-button/"+action_id,1.2*u):
			Scribble.paint(self,line,Color("6d624d"))
	if swatch.a > 0:
		draw_rect(box.grow(-5*u), swatch)
		if selected:
			for corner: PackedVector2Array in [PackedVector2Array([Vector2(2,14)*u,Vector2(2,2)*u,Vector2(14,2)*u]),PackedVector2Array([size-Vector2(14,2)*u,size-Vector2(2,2)*u,size-Vector2(2,14)*u])]:
				draw_polyline(corner, INK, 3*u, true)
				draw_polyline(corner, PAPER, u, true)
	elif image != null:
		var ink: Color = PAPER if selected else (Color("757970") if disabled else INK)
		var offset: Vector2 = (size-Vector2(26,26)*u)/2 + Vector2(0,u if is_pressed() else 0)
		draw_texture_rect(image, Rect2(offset,Vector2(26,26)*u), false, ink)
		if selected:
			draw_line(Vector2(11*u,size.y-6*u),size-Vector2(11,6)*u,PAPER,2*u,true)
	if disabled:
		draw_line(Vector2(6*u,size.y-7*u),Vector2(10*u,size.y-7*u),Color("757970"),1.5*u,true)
	if not text.is_empty():
		var font: Font = get_theme_font("font")
		var fs: int = get_theme_font_size("font_size")
		var extent: Vector2 = font.get_multiline_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs)
		var ink: Color = PAPER if selected else Color("757970") if disabled else INK
		draw_multiline_string(font,Vector2((size.x-extent.x)/2,(size.y-extent.y)/2+font.get_ascent(fs)),text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,-1,ink)
	if has_focus():
		draw_polyline(points(box.grow(-5*u),2*u),INK,1.0,true)
