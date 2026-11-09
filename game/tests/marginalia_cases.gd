extends RefCounted
## Small deterministic cases in the existing native.catalog information process.
const Ink = preload("res://book/marginalia.gd")

static func run(r: SceneTree) -> void:
	var page := Rect2(0,0,1600,1800)
	var viewport := Vector2(1600,1200)
	var empty: Array[Rect2] = []
	var open: Array[Rect2] = Ink.placement(page,viewport,1,empty,empty,Ink.REGIONS.help)
	r.check(open[0].has_area() and open[1].has_area() and open[1].size.x > open[0].size.x,"RAND-P1: substantial separate lower corners on generous paper")
	var block: Array[Rect2] = [open[1]]
	var right_hidden: Array[Rect2] = Ink.placement(page,viewport,1,block,empty,Ink.REGIONS.help)
	r.check(right_hidden[0] == open[0] and not right_hidden[1].has_area(),"RAND-P1: hard UI removes only its colliding component")
	block = [open[0]]
	var left_hidden: Array[Rect2] = Ink.placement(page,viewport,1,block,empty,Ink.REGIONS.help)
	r.check(not left_hidden[0].has_area() and left_hidden[1] == open[1],"RAND-P1: independent left omission")
	block = [Rect2(0,0,1600,1200)]
	var dense: Array[Rect2] = Ink.placement(page,viewport,1.25,empty,block,Ink.REGIONS.help)
	r.check(not dense[0].has_area() and not dense[1].has_area(),"RAND-P1: dense content drops both, no tiny replacement")
	block = [Rect2(open[1].position-Vector2(500,0),Vector2(510,open[1].size.y))]
	var shallow: Array[Rect2] = Ink.placement(page,viewport,1,empty,block,Ink.REGIONS.help)
	r.check(shallow[1] == open[1],"RAND-P1: owner-permitted shallow content overlap keeps original size")
	var app: Control = r.app
	var drawing: Control = app.marginalia
	r.check(drawing.mouse_filter == Control.MOUSE_FILTER_IGNORE and drawing.focus_mode == Control.FOCUS_NONE and drawing.get_parent() == app.page and drawing.get_index() == 0,"RAND-P1: passive drawing is below actual page UI and inside shared capture hierarchy")
	var saved: Dictionary = r.save_bytes()
	for key: String in Ink.ORIGINALS:
		drawing.arrange(key,page,viewport,1,empty,empty)
		var boxes: Array[Rect2] = drawing.boxes.duplicate()
		drawing.arrange(key,page,viewport,1,empty,empty)
		r.check(drawing.boxes == boxes and drawing.family == key and drawing.textures[key].size() == 2,"RAND-P1: deterministic category/help pair "+key)
		for texture: AtlasTexture in drawing.textures[key]:
			r.check(texture.atlas.get_image().detect_alpha() != Image.ALPHA_NONE and texture.region.has_area(),"RAND-P1: actual imported original has alpha and separate display region")
	app.show_information("help")
	await r.frames()
	if app.size.x >= 1920 and app.ui_scale == 1.0:
		r.check(drawing.boxes[0].has_area() and drawing.boxes[1].has_area(),"RAND-P1: actual broad help layout keeps both components beside copy and scrollbar")
	var before: Array = [app.help_panel.get_rect(),app.help_panel.scroll.get_rect(),app.help_panel.navigation.get_rect(),app.info.help_heading.get_rect()]
	var boxes: Array = drawing.boxes.duplicate()
	drawing.hide()
	app._layout_book()
	await r.frames()
	r.check(before == [app.help_panel.get_rect(),app.help_panel.scroll.get_rect(),app.help_panel.navigation.get_rect(),app.info.help_heading.get_rect()],"RAND-P1: with/without does not change help budgets")
	drawing.show()
	app.help_panel.choose(2)
	app.info.help_scroll.scroll_vertical = 200
	await r.frames()
	r.check(drawing.family == "help" and drawing.boxes == boxes,"RAND-P1: chapter/scroll do not change marginal composition")
	app.show_information("settings")
	await r.frames()
	r.check(drawing.family.is_empty() and not drawing.boxes[0].has_area() and not drawing.boxes[1].has_area(),"RAND-P1: no settings illustrations")
	app.show_information("help")
	await r.frames()
	r.check(drawing.family == "help" and drawing.boxes == boxes and r.save_bytes() == saved,"RAND-P1: return preserves pair and all slot bytes")
	app.return_to_work()
	await r.frames()
	r.check(drawing.family.is_empty(),"RAND-P1: no catalog illustrations")
