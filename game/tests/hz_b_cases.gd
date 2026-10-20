extends RefCounted
## Fixed synthetic geometry and imported-resource regressions; no live corpus.
const Paper = preload("res://ui/book_style.gd")
const Controls = preload("res://ui/book_controls.gd")

static func run(runner: Object) -> void:
	for size: Vector2 in [Vector2(44,44),Vector2(160,44),Vector2(330,310),Vector2(700,32)]:
		for u: float in [1.0,1.25]:
			var rect := Rect2(Vector2.ZERO,size*u)
			var style = Paper.make("card/pz-test-stable",u)
			var initial: Array = style.contours(rect)
			style.selected = true
			style.paper = Color.RED
			runner.check(style.contours(rect) == initial,"HZ-B selection/colour never reseed contour")
			style.ui_scale = 1.25 if u == 1.0 else 1.0
			style.contours(rect)
			style.ui_scale = u
			runner.check(style.contours(rect) == initial,"HZ-B scale roundtrip is byte-stable")
			var rebuilt = Paper.make("card/pz-test-stable",u)
			runner.check(rebuilt.contours(rect) == initial,"HZ-B fresh resource/rebuild retains ID contour")
			runner.check(Paper.make("card/pz-test-other",u).contours(rect) != initial,"HZ-B different stable IDs vary")
			for line: PackedVector2Array in initial:
				for point: Vector2 in line:
					runner.check(rect.grow(-1.5*u).has_point(point),"HZ-B stroke plus AA envelope within hit rectangle")
			var polygon := PackedVector2Array()
			for line: PackedVector2Array in style.contours(rect,false): polygon.append_array(line.slice(0,24))
			runner.check(not Geometry2D.triangulate_polygon(polygon).is_empty(),"HZ-B fill has no self-intersecting pen overruns")
			runner.check(style.test_mask(Vector2(0.1,0.1),rect) and not style.test_mask(Vector2(-0.1,0),rect),"HZ-B rectangular boundary unchanged")
	var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
	runner.check(icons.size() == 23,"HZ-B complete active icon family")
	for id: String in icons:
		var texture: Texture2D = load("res://art/book/"+id+".svg")
		runner.check(texture != null and texture.get_size() == Vector2(26,26),"HZ-B imported texture "+id)
		var image: Image = texture.get_image()
		runner.check(image.is_invisible() == (id == "check-empty"),"HZ-B only native unselected placeholder has no ink "+id)
	runner.check(load("res://art/book/reset.svg").get_image().get_data() != load("res://art/book/undo.svg").get_image().get_data(),"HZ-B reset visually differs from undo")
	runner.check(Controls.icon("checkbox-checked",1.0).get_image().get_data() != Controls.icon("checkbox-empty",1.0).get_image().get_data(),"HZ-B checkbox state has shape difference")
