extends Control
## RAND-P1: six pilot originals, two passive drawings on the current leaf.
## Layout consumes existing geometry; it never changes a functional budget.
const ORIGINALS = {
	"wasserwelt": [preload("res://art/drawing/margins/water_left.png"),preload("res://art/drawing/margins/water_right.png")],
	"landschaften-natur": [preload("res://art/drawing/margins/nature_left.png"),preload("res://art/drawing/margins/nature_right.png")],
	"help": [preload("res://art/drawing/margins/help_left.png"),preload("res://art/drawing/margins/help_right.png")]
}
const REGIONS = {
	"wasserwelt": [Rect2(197,389,990,613),Rect2(33,18,1371,1081)],
	"landschaften-natur": [Rect2(91,35,1243,1029),Rect2(66,110,1283,990)],
	"help": [Rect2(66,557,1450,360),Rect2(66,106,1318,851)]
}
const OPACITY: float = 0.48
var family: String = ""
var boxes: Array[Rect2] = [Rect2(),Rect2()]
var textures: Dictionary = {}

func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	for key: String in ORIGINALS:
		var pair: Array[AtlasTexture] = []
		for i: int in range(2):
			var texture := AtlasTexture.new()
			texture.atlas = ORIGINALS[key][i]
			texture.region = REGIONS[key][i]
			pair.append(texture)
		textures[key] = pair
	texture_filter = TEXTURE_FILTER_LINEAR_WITH_MIPMAPS

static func placement(paper: Rect2, viewport: Vector2, u: float, hard: Array[Rect2], soft: Array[Rect2], regions: Array) -> Array[Rect2]:
	var result: Array[Rect2] = [Rect2(),Rect2()]
	# Same safety envelope as information: resting fold, rim and client bottom.
	var safe := Rect2(Vector2(paper.position.x+paper.size.x*0.075+24*u,maxf(24*u,paper.position.y+20*u)),Vector2.ZERO)
	safe.size = Vector2(paper.end.x-24*u,minf(viewport.y-24*u,paper.end.y-24*u))-safe.position
	if safe.size.x <= 0 or safe.size.y <= 0: return result
	for i: int in range(2):
		# Paper-relative size, not a shrink-to-fit loop. Drop each part separately.
		var width: float = minf(280 if i == 0 else 580,safe.size.x*(0.16 if i == 0 else 0.30))
		if width < (145 if i == 0 else 270): continue
		var region: Rect2 = regions[i]
		var extent := Vector2(width,width*region.size.y/region.size.x)
		var candidate := Rect2(Vector2(safe.position.x if i == 0 else safe.end.x-width,safe.end.y-extent.y),extent)
		# The help scrollbar occupies the outer paper edge. Keep a narrow gutter
		# beside it rather than hiding the whole large drawing for that strip.
		for rect: Rect2 in hard:
			if i == 1 and rect.size.x <= 32*u and rect.size.y >= extent.y and candidate.intersects(rect.grow(10*u)) and rect.position.x > candidate.position.x:
				candidate.position.x = rect.position.x-10*u-width
		# A fixed help register can leave a useful small lower-left margin even
		# when the larger nominal companion would enter the reading column.
		for rect: Rect2 in soft:
			if i == 0 and candidate.intersects(rect) and rect.position.x > candidate.position.x:
				var free: float = minf(width,rect.position.x-10*u-candidate.position.x)
				if free >= 145:
					candidate.size = Vector2(free,free*region.size.y/region.size.x)
					candidate.position.y = safe.end.y-candidate.size.y
		if not safe.encloses(candidate): continue
		var blocked: bool = false
		for rect: Rect2 in hard:
			if rect.has_area() and candidate.intersects(rect.grow(10*u)): blocked = true
		# A shallow intersection may keep a substantial sketch. Broad overlaps
		# disappear rather than covering a dense board or a narrow reading column.
		for rect: Rect2 in soft:
			if rect.has_area() and candidate.intersection(rect.grow(8*u)).get_area()/candidate.get_area() > 0.12: blocked = true
		if not blocked: result[i] = candidate
	return result

func arrange(key: String, paper: Rect2, viewport: Vector2, u: float, hard: Array[Rect2], soft: Array[Rect2]) -> void:
	var next: Array[Rect2] = [Rect2(),Rect2()]
	if textures.has(key): next = placement(paper,viewport,u,hard,soft,REGIONS[key])
	if family == key and boxes == next: return
	family = key
	boxes = next
	queue_redraw()

func _draw() -> void:
	if not textures.has(family): return
	for i: int in range(2):
		if boxes[i].has_area(): draw_texture_rect(textures[family][i],boxes[i],false,Color(1,1,1,OPACITY))
