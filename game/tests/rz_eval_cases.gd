extends RefCounted
const Drawing = preload("res://book/rz_eval.gd")

static func run(r: SceneTree) -> void:
	var drawing := Drawing.new()
	r.app.page.add_child(drawing)
	var paper := Rect2(40,30,1900,2200)
	var screen := Vector2(1920,1080)
	var box: Rect2 = Drawing.placement(paper,screen,1)
	var image := Image.create(16,4,false,Image.FORMAT_RGBA8)
	image.fill(Color(0.2,0.2,0.2,0.5))
	var texture := ImageTexture.create_from_image(image)
	var saved: Dictionary = r.save_bytes()
	var geometry: Array = [r.app.board.get_rect(),r.app.tools_scroll.get_rect(),r.app.title.get_rect()]
	drawing.visit("synthetic-a","")
	r.check(drawing.state == "missing" and drawing.active_texture == null,"RZ: unexpected absence is distinct from intentional transparency")
	drawing.transparent_control = true
	drawing.visit("synthetic-empty","")
	r.check(drawing.state == "intentional-empty" and drawing.active_texture == null,"RZ: empty canvas uses no texture")
	drawing.transparent_control = false
	drawing.visit("synthetic-b","")
	var stale: int = drawing.generation
	drawing.visit("synthetic-c","")
	drawing.accept_result(stale,texture)
	r.check(drawing.active_texture == null and drawing.stale_count == 1,"RZ: late result cannot cross a visit/ID")
	drawing.accept_result(drawing.generation,null)
	r.check(drawing.state == "broken" and drawing.active_texture == null,"RZ: broken image never falls back to category art")
	drawing.publish_allowed = func() -> bool: return false
	drawing.accept_result(drawing.generation,texture)
	r.check(drawing.state == "late-omitted" and drawing.active_texture == null,"RZ: slow decoration cannot pop onto a presented page")
	drawing.publish_allowed = Callable()
	drawing.accept_result(drawing.generation,texture)
	for mode: int in range(4):
		drawing.mode = mode
		for size: Vector2 in [Vector2(150,100),Vector2(1800,900),Vector2(150,100)]:
			drawing.arrange(paper,screen,1,Rect2(Vector2(200,200),size),[])
			r.check(drawing.canvas == box and drawing.active_texture == texture,"RZ: zoom overlap never moves, scales, hides or reloads the canvas")
	r.check(drawing.mouse_filter == Control.MOUSE_FILTER_IGNORE and drawing.focus_mode == Control.FOCUS_NONE,"RZ: pointer/focus pass through")
	r.check(geometry == [r.app.board.get_rect(),r.app.tools_scroll.get_rect(),r.app.title.get_rect()] and saved == r.save_bytes(),"RZ: decoration leaves functional geometry and save bytes unchanged")
	drawing.visit("synthetic-load-a","res://art/book/fill.svg")
	drawing.visit("synthetic-load-b","res://art/book/erase.svg")
	var deadline: int = Time.get_ticks_msec()+2000
	while drawing.state in ["queued","loading"] and Time.get_ticks_msec() < deadline:
		await r.process_frame
	r.check(drawing.state == "ready" and drawing.active_id == "synthetic-load-b" and drawing.pending_path.is_empty() and drawing.stale_count == 2,"RZ: real threaded requests drain stale work and install only latest visit")
	var count: int = drawing.load_count
	drawing.arrange(paper,screen,1,Rect2(0,0,1800,900),[])
	r.check(count == drawing.load_count,"RZ: overlap geometry causes no reload")
	drawing.visit("","")
	r.check(drawing.active_texture == null and drawing.state == "idle","RZ: leaving drops active reference")
	drawing.free()
	await r.frames()
