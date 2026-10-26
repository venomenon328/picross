extends RefCounted
## Current synthetic native filtering, geometry and texture lifetime.
const Ink = preload("res://ui/catalog_ink.gd")
const Completion = preload("res://ui/completion.gd")

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
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		runner.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(float(spec[2]))
		var prefix: String = "%d-ui%d" % [spec[0],roundi(float(spec[2])*100)]
		for extension: String in ["png","svg"]:
			var path: String = "res://tests/fixtures/ke-reveal."+extension
			var source_hash: String = FileAccess.get_sha256(path)
			runner.ke_graphics_measurements.append({"source":path,"sha256":source_hash,"purpose":"current PNG/SVG filtering"})
			item.definition.reveal.image = path
			app.show_album()
			await runner.frames()
			var card = app.choices[0]
			var picture = card.picture
			var derived: Texture2D = picture.filtered_artwork
			var original: Texture2D = load(path)
			var rect: Rect2 = picture.artwork_rect()
			runner.check(derived != original and derived.get_size() == Vector2(Vector2i(ceilf(rect.size.x),ceilf(rect.size.y))),"KE derived texture matches display pixels "+extension)
			await capture(runner,picture,prefix+"-"+extension+"-catalog-after")
			runner.check(picture.artwork_rect() == rect and picture.texture_filter == CanvasItem.TEXTURE_FILTER_LINEAR,"KE full centred filtered region")
			if extension == "png":
				for icon_name: String in ["mode_icon","status_icon"]:
					var icon: Ink = card.get(icon_name)
					for kind: String in (["mono","color"] if icon_name == "mode_icon" else ["Begonnen"]):
						icon.kind = kind
						icon.queue_redraw()
						await capture(runner,icon,prefix+"-"+kind+"-after")
			app.select_puzzle(0)
			await runner.frames()
			var completion = app.reveal_view
			var artwork_rect: Rect2 = completion.artwork_rect()
			var complete_texture: Texture2D = completion.filtered_artwork
			# Current EA phase and exact end retain the same derived texture.
			completion.begin(app.board.get_global_rect(),[],null)
			completion.set_process(false)
			for phase: String in ["motion","end"]:
				completion.elapsed = 1.65 if phase == "motion" else completion.DURATION
				completion.apply_time()
				runner.check(completion.art.commands[0][0] == complete_texture,"KE animation uses derived texture")
				await capture(runner,completion,prefix+"-"+extension+"-"+phase+"-after")
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
	runner.check(runner.save_bytes() == saved,"KE presentation never writes saves")
