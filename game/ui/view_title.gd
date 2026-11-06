extends Control
## Three local illustrated headings; semantic text survives a missing resource.
const TITLES = {"catalog":"Rätselkatalog", "help":"Hilfe", "settings":"Einstellungen"}
# Measured alpha >=16 envelopes of the immutable V2-rev1 originals (manifest).
# Alpha-1 remnants can reach an image edge; they must not centre the lettering.
const OPTICAL_INK = {
	"catalog": Rect2(37,75,2096,597),
	"help": Rect2(88,102,1361,858),
	"settings": Rect2(50,86,2093,604)
}
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
		if source != null and source.get_used_rect().has_area(): ink = OPTICAL_INK[role]
	if not ink.has_area(): texture = null
	fallback.visible = texture == null
	queue_redraw()

func image_rect() -> Rect2:
	if texture == null: return Rect2()
	# Centre meaningful ink, but fit the WHOLE source about that optical centre.
	# Thus weak alpha, umlaut dots and f/g tails survive without cropping/stretching.
	var available := (size-Vector2(8,8)).max(Vector2.ONE)
	var centre: Vector2 = ink.get_center()
	var source_size: Vector2 = texture.get_size()
	var radius: Vector2 = centre.max(source_size-centre)
	var factor: float = minf(available.x/(2*radius.x),available.y/(2*radius.y))
	return Rect2(size/2-centre*factor,source_size*factor)

func ink_rect() -> Rect2:
	var image: Rect2 = image_rect()
	if not image.has_area(): return Rect2()
	var factor: float = image.size.x/texture.get_width()
	return Rect2(image.position+ink.position*factor,ink.size*factor)

func _draw() -> void:
	if texture != null: draw_texture_rect(texture,image_rect(),false)
