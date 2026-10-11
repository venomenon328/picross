extends Control
## Only the UI-free material is reflected for the right information page.
const ART = preload("res://art/book/bp2-a-inventarband.png")
const FRAMES = {
 "preview": preload("res://art/book/frame-preview.png"),
 "palette": preload("res://art/book/frame-palette.png"),
 "tools": preload("res://art/book/frame-tools.png")
}
var frames: Dictionary = FRAMES.duplicate()
var frame_metadata: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/frames.json"))
var information: bool = false
var card: Rect2
var miniature: Rect2
var palette: Rect2
var wells: Array[Rect2] = []
var work_visible: bool = false

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func material_rect() -> Rect2:
	# Contain the whole bound master; never stretch/crop away its protected paper.
	var ratio: float = minf(size.x/2560.0,size.y/1440.0)
	var extent: Vector2 = Vector2(2560,1440)*ratio
	return Rect2((size-extent)/2,extent)

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO,size),Color("332719"))
	var rect: Rect2 = material_rect()
	if information:
		draw_set_transform(Vector2(size.x,0),0,Vector2(-1,1))
	draw_texture_rect(ART, rect, false)
	draw_set_transform(Vector2.ZERO)
	if not work_visible:
		return
	for box: Rect2 in wells:
		draw_texture_rect(frames.tools,box,false)
	draw_texture_rect(frames.palette,palette,false)
	draw_texture_rect(frames.preview,card,false)

func frame_rect(content: Rect2, kind: String = "tools") -> Rect2:
	for item: Dictionary in frame_metadata.derivatives:
		if item.file == "frame-"+kind+".png":
			var safe: Rect2 = Rect2(item.safe[0],item.safe[1],item.safe[2],item.safe[3])
			var scale: Vector2 = content.size/safe.size
			return Rect2(content.position-safe.position*scale,Vector2(item.size[0],item.size[1])*scale)
	return Rect2()
