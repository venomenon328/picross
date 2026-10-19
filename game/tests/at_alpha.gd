extends RefCounted
## Independent native pixel oracle: imported RGBA, original frame and hidden-art background.
const POINTS := {"outside":Vector2(4,4),"white":Vector2(76,76),"hole":Vector2(154,154),"soft":Vector2(16,128),"ink":Vector2(128,64)}

static func sample(probe: SceneTree, view: Control, name: String, opacity: float = 1.0) -> Dictionary:
	var image: Image = view.artwork.get_image()
	if image.is_compressed(): image.decompress()
	image.convert(Image.FORMAT_RGBA8)
	probe.check(image.get_size() == Vector2i(256,256), "AT imported actual image dimensions")
	probe.check(image.get_pixel(76,76).is_equal_approx(Color.WHITE), "AT opaque white motif remains white")
	probe.check(image.get_pixel(154,154).a == 0 and image.get_pixel(4,4).a == 0, "AT real hole and outside remain transparent")
	probe.check(absf(image.get_pixel(16,128).a-80.0/255.0) < 0.001, "AT soft alpha survives import")
	await RenderingServer.frame_post_draw
	var visible: Image = probe.surface.get_texture().get_image()
	var art: Control = view.art if view.get("art") != null else view
	art.hide()
	await RenderingServer.frame_post_draw
	var background: Image = probe.surface.get_texture().get_image()
	art.show()
	await RenderingServer.frame_post_draw
	var rect: Rect2 = view.artwork_rect()
	rect.position += view.global_position
	var rows: Array = []
	for kind: String in POINTS:
		var normalized: Vector2 = (POINTS[kind]+Vector2(0.5,0.5))/256.0
		var point := Vector2i(rect.position+normalized*rect.size)
		var foreground: Color = image.get_pixelv(Vector2i(POINTS[kind]))
		var paper: Color = background.get_pixelv(point)
		var actual: Color = visible.get_pixelv(point)
		var expected: Color = paper.lerp(Color(foreground.r,foreground.g,foreground.b,1),foreground.a*opacity)
		var error: float = maxf(absf(actual.r-expected.r),maxf(absf(actual.g-expected.g),absf(actual.b-expected.b)))
		probe.check(error <= 0.035, "AT native alpha composition "+name+"/"+kind)
		rows.append({"kind":kind,"point":[point.x,point.y],"source":[foreground.r,foreground.g,foreground.b,foreground.a],
			"background":[paper.r,paper.g,paper.b],"actual":[actual.r,actual.g,actual.b],"opacity":opacity,"max_error":error})
	var bounds := Rect2i(Vector2i(rect.position),Vector2i(rect.size)).intersection(Rect2i(Vector2i.ZERO,visible.get_size()))
	var file := "at-"+name+".png"
	var background_file := "at-"+name+"-paper.png"
	probe.check(visible.get_region(bounds).save_png(probe.output.path_join(file)) == OK,"AT original native image crop")
	probe.check(background.get_region(bounds).save_png(probe.output.path_join(background_file)) == OK,"AT original native background crop")
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(image.get_data())
	return {"file":file,"background_file":background_file,"framebuffer":[visible.get_width(),visible.get_height()],"bounds":[bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y],
		"rgba_sha256":hash.finish().hex_encode(),"samples":rows}
