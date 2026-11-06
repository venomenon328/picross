extends Control
## Three local illustrated headings; semantic text survives a missing resource.
const TITLES = {"catalog":"Rätselkatalog", "help":"Hilfe", "settings":"Einstellungen"}
var role: String
var texture: Texture2D
var ink: Rect2
var fallback: Label

func configure(value: String, label: Label) -> void:
	role = value
	name = "title-"+role
	accessibility_name = TITLES[role]
	mouse_filter = MOUSE_FILTER_IGNORE
	clip_contents = true
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	fallback = label
	if fallback.get_parent() != null: fallback.reparent(self)
	else: add_child(fallback)
	fallback.text = TITLES[role]
	fallback.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fallback.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	fallback.mouse_filter = MOUSE_FILTER_IGNORE
	fallback.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	load_art("res://art/drawing/view_titles/"+role+".png")
	resized.connect(queue_redraw)

func load_art(path: String) -> void:
	texture = load(path) as Texture2D if ResourceLoader.exists(path,"Texture2D") else null
	ink = Rect2()
	if texture != null:
		var source: Image = texture.get_image()
		if source != null: ink = Rect2(source.get_used_rect())
	if not ink.has_area(): texture = null
	fallback.visible = texture == null
	queue_redraw()

func image_rect() -> Rect2:
	if texture == null: return Rect2()
	# Fit the visible ink, keeping safety space for antialiasing on every edge.
	var available := (size-Vector2(8,8)).max(Vector2.ONE)
	var factor: float = minf(available.x/ink.size.x,available.y/ink.size.y)
	var extent: Vector2 = ink.size*factor
	return Rect2((size-extent)/2,extent)

func _draw() -> void:
	if texture != null: draw_texture_rect_region(texture,image_rect(),ink)
