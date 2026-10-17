extends RefCounted
## TEST ONLY native before/after. Legacy draw is frozen from d2c66ba, not a player option.
const Ink = preload("res://ui/catalog_ink.gd")
const Completion = preload("res://ui/completion.gd")

class LegacyInk extends Ink:
	func pencil(origin: Vector2, angle: float, color: Color, scale_value: float) -> void:
		draw_set_transform(origin,angle,Vector2.ONE*scale_value)
		var shape := PackedVector2Array([Vector2(-3,-11),Vector2(2.5,-10.5),Vector2(3,8),Vector2(0,14),Vector2(-3.5,8),Vector2(-3,-11)])
		draw_colored_polygon(shape,color)
		draw_polyline(shape,GRAPHITE,0.9,true)
		draw_line(Vector2(-1,-8),Vector2(-1,7),Color("ead9ae"),0.8,true)
		draw_colored_polygon(PackedVector2Array([Vector2(-3,8),Vector2(2.5,8),Vector2(0,14)]),Color("d6bc8d"))
		draw_line(Vector2(0,11),Vector2(0,14),GRAPHITE,1.5,true)
		draw_set_transform(Vector2.ZERO)

static func capture(runner: SceneTree, control: Control, name: String) -> PackedByteArray:
	await runner.frames()
	await RenderingServer.frame_post_draw
	var rectangle: Rect2 = control.get_global_rect()
	if control is Completion: rectangle = control.artwork_rect()
	var image: Image = runner.surface.get_texture().get_image().get_region(Rect2i(rectangle))
	runner.check(image.save_png(runner.output.path_join("ke-graphics-"+name+".png")) == OK,"KE graphics native crop "+name)
	runner.ke_graphics_measurements.append({"file":"ke-graphics-"+name+".png","native_rect":[rectangle.position.x,rectangle.position.y,rectangle.size.x,rectangle.size.y],"viewport":[runner.surface.size.x,runner.surface.size.y],"ui_scale":runner.app.ui_scale})
	return image.get_data()

static func run(runner: SceneTree) -> void:
	var app = runner.app
	var item = app.sessions[0]
	# Complete the synthetic session through its unchanged transaction boundary.
	for y: int in range(item.player.height):
		for x: int in range(item.player.width):
			var value: int = int(item.definition.solution[y][x])
			if value > 0:
				item.gesture.begin(item.player,Vector2i(x,y),value)
				item.finish()
	runner.check(item.completed,"KE graphics only earned reveals")
	runner.check(app.store.write_slot(item,item.view_state).is_empty(),"KE graphics isolated completion save")
	var saved: Dictionary = runner.save_bytes()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1080,1.25]]:
		runner.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(float(spec[2]))
		var prefix: String = "%d-ui%d" % [spec[0],roundi(float(spec[2])*100)]
		for extension: String in ["png","svg"]:
			var path: String = "res://tests/fixtures/ke-reveal."+extension
			var source_hash: String = FileAccess.get_sha256(path)
			runner.ke_graphics_measurements.append({"source":path,"sha256":source_hash,"baseline":"d2c66baa60355d2e2a31f77b2952de7084ac885e: nearest catalog, linear completion, frozen pencil primitive"})
			item.definition.reveal.image = path
			app.show_album()
			await runner.frames()
			var card = app.choices[0]
			var picture = card.picture
			var derived: Texture2D = picture.filtered_artwork
			var original: Texture2D = load(path)
			var rect: Rect2 = picture.artwork_rect()
			runner.check(derived != original and derived.get_size() == Vector2(Vector2i(ceilf(rect.size.x),ceilf(rect.size.y))),"KE derived texture matches display pixels "+extension)
			picture.filtered_artwork = original
			picture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			picture.queue_redraw()
			var before: PackedByteArray = await capture(runner,picture,prefix+"-"+extension+"-catalog-before")
			picture.filtered_artwork = derived
			picture.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
			picture.queue_redraw()
			var after: PackedByteArray = await capture(runner,picture,prefix+"-"+extension+"-catalog-after")
			runner.check(before != after and picture.artwork_rect() == rect,"KE downscale changes pixels only, full centred region unchanged")
			if extension == "png":
				for icon_name: String in ["mode_icon","status_icon"]:
					var icon: Ink = card.get(icon_name)
					for kind: String in (["mono","color"] if icon_name == "mode_icon" else ["Begonnen"]):
						icon.kind = kind
						icon.queue_redraw()
						var newer: PackedByteArray = await capture(runner,icon,prefix+"-"+kind+"-after")
						var old := LegacyInk.new()
						old.kind = kind
						old.ui_scale = icon.ui_scale
						old.position = icon.position
						old.size = icon.size
						icon.get_parent().add_child(old)
						icon.hide()
						var older: PackedByteArray = await capture(runner,old,prefix+"-"+kind+"-before")
						runner.check(newer != older,"KE local polygon edge smoothing "+kind)
						old.queue_free()
						icon.show()
			app.select_puzzle(0)
			await runner.frames()
			var completion = app.reveal_view
			var artwork_rect: Rect2 = completion.artwork_rect()
			var complete_texture: Texture2D = completion.filtered_artwork
			# Same running EA phase, then exact end; old completion already used linear.
			completion.begin(app.board.get_global_rect(),[],null)
			completion.set_process(false)
			for phase: String in ["motion","end"]:
				completion.elapsed = 1.65 if phase == "motion" else completion.DURATION
				completion.apply_time()
				for variant: String in ["before","after"]:
					completion.art.commands[0][0] = original if variant == "before" else complete_texture
					completion.art.commands[0][2] = Rect2(Vector2.ZERO,completion.art.commands[0][0].get_size())
					completion.art.queue_redraw()
					await capture(runner,completion,prefix+"-"+extension+"-"+phase+"-"+variant)
			completion.finish()
			runner.check(completion.artwork_rect() == artwork_rect,"KE completion geometry unchanged")
			app.show_album()
			await runner.frames()
			runner.check(completion.artwork == null and completion.filtered_artwork == null and completion.art.commands.is_empty(),"KE leaving completion releases derived texture and commands")
			app.select_puzzle(0)
			await runner.frames()
			runner.check(not completion.active and completion.filtered_artwork != null,"KE solved reopen shows filtered end without replay")
			runner.check(FileAccess.get_sha256(path) == source_hash,"KE original asset bytes untouched")
			app.show_album()
			await runner.frames()
	runner.check(runner.save_bytes() == saved,"KE presentation comparisons never write saves")
