extends Button
## Shared KB paper button. Precise rectangular hits; identity-bound ink decoration.
const INK = Color("293e3d")
const PAPER = Color("fffaf0")
const Scribble = preload("res://ui/scribble.gd")
const BookTooltip = preload("res://ui/book_tooltip.gd")
const UiText = preload("res://ui/ui_text.gd")
const PaperStyle = preload("res://ui/book_style.gd")
var action_id: String = ""
var content_surface: bool = false
## Explicit study opt-in; the default product appearance is unchanged.
var paper_transparent: bool = false:
	set(value):
		paper_transparent = value
		# Opaque custom bodies used to cover Button's native caption. A
		# transparent body must suppress that caption, not draw it twice.
		for state: String in ["font_color","font_hover_color","font_pressed_color","font_hover_pressed_color","font_disabled_color","font_focus_color"]:
			if value: add_theme_color_override(state,Color.TRANSPARENT)
			else: remove_theme_color_override(state)
		queue_redraw()
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
	mouse_exited.connect(dismiss_tooltip)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	focus_exited.connect(dismiss_tooltip)
	visibility_changed.connect(func() -> void:
		if not is_visible_in_tree(): dismiss_tooltip())
	resized.connect(dismiss_tooltip)
	if accessibility_name.is_empty(): accessibility_name = text if not text.is_empty() else tooltip_text

func _get_tooltip(_at_position: Vector2) -> String:
	return tooltip_text.strip_edges()

func _make_custom_tooltip(for_text: String) -> Object:
	# Godot calls this virtual even for an empty tooltip. A non-null custom
	# panel then opens with just its margins. Decline before constructing it.
	var caption: String = for_text.strip_edges()
	if caption.is_empty(): return null
	var tip: BookTooltip = BookTooltip.new()
	tip.configure(caption, ui_scale, get_viewport_rect().size.x, get_theme_font("font"))
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
		body = Color("42645b") if is_pressed() else Color("34514d") if is_hovered() else Color("293f3e")
	elif is_pressed():
		body = Color("c5d6cd")
	elif is_hovered():
		body = Color("e0ece6")
	if swatch.a > 0:
		draw_colored_polygon(points(box.grow(-1.5*u), 3*u), body)
		for line: Dictionary in swatch_strokes():
			Scribble.paint(self,line,Color("68583f"))
	else:
		if paper_transparent: body = Color.TRANSPARENT
		var style = PaperStyle.make("button/"+action_id,u,body)
		style.ink = INK if paper_transparent else PAPER if selected else Color("6d624d")
		if paper_transparent:
			style.selected = selected
			if disabled: style.ink = Color("8a887d")
			elif is_pressed(): style.ink = Color("173e35")
			elif is_hovered(): style.ink = Color("376a60")
		draw_style_box(style,box)
		if paper_transparent and not disabled and (is_hovered() or is_pressed()):
			# Retrace the existing contour continuously: hover and pressure belong
			# to the button edge, with no floating short stroke above the caption.
			for line: PackedVector2Array in style.contours(box):
				draw_polyline(line,style.ink,(2.4 if is_pressed() else 1.6)*u,true)
	if swatch.a > 0:
		draw_rect(box.grow(-5*u), swatch)
		if selected:
			for corner: PackedVector2Array in [PackedVector2Array([Vector2(2,14)*u,Vector2(2,2)*u,Vector2(14,2)*u]),PackedVector2Array([size-Vector2(14,2)*u,size-Vector2(2,2)*u,size-Vector2(2,14)*u])]:
				draw_polyline(corner, INK, 3*u, true)
				draw_polyline(corner, PAPER, u, true)
	elif image != null:
		var ink: Color = PAPER if selected and not paper_transparent else (Color("757970") if disabled else INK)
		var offset: Vector2 = (size-Vector2(26,26)*u)/2 + Vector2(0,u if is_pressed() else 0)
		if not text.is_empty(): offset.x = 10*u
		draw_texture_rect(image, Rect2(offset,Vector2(26,26)*u), false, ink)
		if selected:
			draw_line(Vector2(11*u,size.y-6*u),size-Vector2(11,6)*u,INK if paper_transparent else PAPER,2*u,true)
	if disabled:
		draw_line(Vector2(6*u,size.y-7*u),Vector2(10*u,size.y-7*u),Color("757970"),1.5*u,true)
	if not text.is_empty():
		var font: Font = get_theme_font("font")
		var fs: int = get_theme_font_size("font_size")
		var bounds: Rect2 = UiText.ink(font, text, fs)
		# Honour theme alpha, including the existing native contrast probe.
		var ink: Color = (Color("757970") if disabled else INK) if paper_transparent else get_theme_color("font_color")
		if selected and ink.a > 0: ink = INK if paper_transparent else PAPER
		var origin: Vector2 = Vector2(roundf((size.x-bounds.size.x)/2-bounds.position.x), UiText.line_baseline(font, fs, size.y))
		if image != null: origin.x += 16*u
		draw_string(font,origin,text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,ink)
	if has_focus():
		# Keep focus outside the unchanged swatch; light ink remains visible on
		# selected dark paper and does not disappear into the selection colour.
		var inset: float = 3*u if swatch.a > 0 else 5*u
		if swatch.a > 0:
			draw_polyline(points(box.grow(-inset),2*u),PAPER if selected else INK,u,true)
		else:
			var focus_style = PaperStyle.make("button/"+action_id,u,Color.TRANSPARENT)
			focus_style.focus = true
			focus_style.ink = PAPER if selected and not paper_transparent else INK
			draw_style_box(focus_style,box)
