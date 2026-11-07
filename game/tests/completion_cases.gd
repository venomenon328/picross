extends RefCounted
## AR-A: bounded synthetic cases in the existing EA native process.
const Atlas = preload("res://ui/cell_atlas.gd")

static func box(rect: Rect2) -> Array:
	return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]

static func snapshot(app: Control) -> String:
	return JSON.stringify([app.session.player.cells,app.session.player.history,app.session.player.cursor,
		app.session.player.undo_used,app.session.completed,app.session.view_state,app.board.capture_view()])

static func hashes(bytes: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for name: String in bytes:
		var hash := HashingContext.new()
		hash.start(HashingContext.HASH_SHA256)
		hash.update(bytes[name])
		result[name] = hash.finish().hex_encode()
	return result

static func run(p: SceneTree) -> Array:
	var result: Array = []
	var app: Control = p.app
	# Original Mono/Farbe, independent portrait artwork, plus the intermediate
	# window size and a dense minimum-cell case. No production definitions.
	for context: Array in [[2,1280,720,1.25],[1,1920,1080,1.0],[5,2560,1440,1.25],[5,1600,900,1.0],[3,1280,720,1.25]]:
		p.surface.size = Vector2i(context[1],context[2])
		app.set_ui_scale(context[3])
		var last: Vector2i = p.prepare(context[0])
		if context[0] == 5:
			app.session.definition.reveal.name = "TEST ONLY Ein besonders langer deutscher Motivname mit mehreren Wörtern für den sicheren Zeilenumbruch"
		await p.frames()
		p.check(not app.completion_switch.is_visible_in_tree() and app.reveal_view.payload.is_empty(),"AR unsolved spoiler boundary")
		p.finish_stroke(last)
		var view: Control = app.reveal_view
		p.check(not app.completion_switch.visible and app.completion_switch.disabled,"AR switch unavailable during reveal")
		app._select_completion(true)
		p.check(not view.grid_selected,"AR early selection rejected")
		var initial_area: Rect2 = view.area
		var gated: bool = not app.completion_switch.visible and app.completion_switch.disabled and not view.grid_selected
		view.finish()
		await p.frames()
		p.check(not view.grid_selected and not app.completion_switch.button_pressed and app.completion_switch.visible,"AR stable entry starts image")
		p.check(view.area == initial_area,"AR switch and caption space reserved from start")
		var before: String = snapshot(app)
		var bytes: Dictionary = p.save_bytes()
		var row := {"window":context.slice(1),"width":app.session.player.width,"height":app.session.player.height,
			"palette":app.session.definition.palette.duplicate(true),"cells":app.session.player.cells.duplicate(),"samples":[],
			"gated":gated,"initial_image":not view.grid_selected,"selections":[],"slider_positions":[]}
		var original_dir: String = OS.get_environment("AR_REVIEW_DIR")
		var original_case: bool = result.size() < 3 and not original_dir.is_empty()
		for selected: bool in [false,true,false,true]:
			if view.grid_selected != selected: p.click(app.completion_switch)
			await p.frames()
			p.check(view.grid_selected == selected and not view.active and not view.is_processing(),"AR real pointer switch without replay")
			row.selections.append(view.grid_selected)
			row.slider_positions.append(app.completion_switch.slider_rect().get_center().x/app.ui_scale)
			p.check(view.stable_ink.visible == selected and view.art.visible != selected and not app.work.visible,"AR passive layer only")
			p.check(view.area == initial_area,"AR switching preserves common layout")
			if original_case and not row.has("grid_file" if selected else "image_file"):
				var name: String = "ar-%d-%s.png" % [result.size(),"raster" if selected else "bild"]
				await RenderingServer.frame_post_draw
				p.check(preload("res://tests/native_png.gd").write(p.surface.get_texture().get_image(),original_dir.path_join(name)) == OK,"AR review original written")
				row["grid_file" if selected else "image_file"] = name
		var rect: Rect2 = view.raster_rect()
		var step: float = rect.size.x/app.session.player.width
		p.check(view.area.grow(0.01).encloses(rect) and rect.get_center().is_equal_approx(view.area.get_center()),"AR full centered proportional raster")
		p.check(is_equal_approx(rect.size.aspect(),float(app.session.player.width)/app.session.player.height),"AR original square cells")
		for item: Control in [app.completion_switch,app.completion_title,app.completion_reset]:
			p.check(app.surface.material_rect().encloses(item.get_rect()),"AR controls within safe paper")
		p.check(rect.end.y < app.completion_switch.position.y and app.completion_switch.get_rect().end.y < app.completion_title.position.y,"AR separate image switch caption rows")
		p.check(app.completion_switch.size.y == 44*app.ui_scale and app.completion_switch.size.x >= 44*app.ui_scale,"AR 44/55 switch target")
		p.check(app.ending.get_children().filter(func(node: Node) -> bool: return node is Button).size() == 2 and app.completion_switch.toggle_mode,"AR exactly one toggle plus reset")
		row.control = "single-rectangular-toggle"
		row.hatch_count = app.completion_switch.hatch_strokes().size()
		var commands: Array = view.stable_ink.commands
		p.check(commands.size() == app.session.player.cells.filter(func(v: int) -> bool: return v>0).size(),"AR only confirmed fills, no X")
		p.check(view.strokes.size() == app.session.player.width+app.session.player.height+2,"AR all normal five outer lines")
		var ordinal := 0
		for i: int in range(app.session.player.cells.size()):
			var value: int = app.session.player.cells[i]
			if value <= 0: continue
			var command: Array = commands[ordinal]
			ordinal += 1
			p.check(command[3] == app.board.cell_color(value) and command[0].resource_path.ends_with("fill-"+Atlas.level(step)+".png"),"AR original palette and correct atlas detail")
			p.check(command[2] == Atlas.region(Atlas.level(step),Atlas.variant(str(app.session.definition.id),int(app.session.definition.revision),Vector2i(i%app.session.player.width,i/app.session.player.width)),23),"AR original stable atlas variant")
		await RenderingServer.frame_post_draw
		var rendered: Image = p.surface.get_texture().get_image()
		var track: Rect2 = app.completion_switch.track_rect()
		track.position += app.completion_switch.global_position
		var dark := 0
		var light := 0
		for y: int in range(ceili(track.position.y+5*app.ui_scale),floori(track.end.y-5*app.ui_scale)):
			for x: int in range(ceili(track.position.x+6*app.ui_scale),floori(track.position.x+35*app.ui_scale)):
				var pixel: Color = rendered.get_pixel(x,y)
				if pixel.get_luminance() < 0.72: dark += 1
				if pixel.get_luminance() > 0.80: light += 1
		p.check(dark > 0 and light > 0,"AR dark toggle rail contains pencil and open paper, no solid fill")
		row.hatch_pixels = [dark,light]
		view.stable_ink.hide()
		view.stable_lines.hide()
		await RenderingServer.frame_post_draw
		var paper: Image = p.surface.get_texture().get_image()
		view.stable_ink.show()
		view.stable_lines.show()
		# Pixels from every foreground colour, unknown background and marked X.
		var seen: Dictionary = {}
		for i: int in range(app.session.player.cells.size()):
			var value: int = app.session.player.cells[i]
			if seen.has(value): continue
			seen[value] = true
			var point := Vector2i(rect.position+Vector2(i%app.session.player.width+0.5,i/app.session.player.width+0.5)*step)
			var actual: Color = rendered.get_pixelv(point)
			var background: Color = paper.get_pixelv(point)
			var expected: Color = app.board.cell_color(value) if value>0 else background
			p.check(maxf(absf(actual.r-expected.r),maxf(absf(actual.g-expected.g),absf(actual.b-expected.b)))<0.16,"AR rendered confirmed color or empty background")
			row.samples.append({"value":value,"actual":[actual.r,actual.g,actual.b],"paper":[background.r,background.g,background.b]})
		row.area = box(view.area)
		row.raster = box(rect)
		row.step = step
		row.lod = Atlas.level(step)
		row.fill_count = commands.size()
		row.line_count = view.strokes.size()
		# Compare actual framebuffer strokes with the same cells and no lines.
		await RenderingServer.frame_post_draw
		var with_lines: Image = p.surface.get_texture().get_image()
		view.stable_lines.hide()
		await RenderingServer.frame_post_draw
		var no_lines: Image = p.surface.get_texture().get_image()
		view.stable_lines.show()
		row.line_pixels = []
		for index: int in [0,1,mini(5,app.session.player.height),app.session.player.height,
			app.session.player.height+1,app.session.player.height+2,app.session.player.height+1+mini(5,app.session.player.width),view.strokes.size()-1]:
			var stroke: Dictionary = view.strokes[index]
			var point := Vector2i(stroke.points[stroke.points.size()/2])
			var difference := 0.0
			for dy: int in range(-2,3):
				for dx: int in range(-2,3):
					var at := point+Vector2i(dx,dy)
					var a: Color = with_lines.get_pixelv(at)
					var b: Color = no_lines.get_pixelv(at)
					difference = maxf(difference,maxf(absf(a.r-b.r),maxf(absf(a.g-b.g),absf(a.b-b.b))))
			p.check(difference > 0.02,"AR actual normal five and four outer edge pixels")
			row.line_pixels.append(difference)
		app.refresh()
		app.set_ui_scale(1.0 if app.ui_scale == 1.25 else 1.25)
		p.surface.size = Vector2i(1600,900)
		await p.frames()
		app._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		p.check(view.grid_selected and not view.active,"AR refresh resize scale focus retain selection")
		row.retained = view.grid_selected
		# Reset cancellation keeps the view and bytes.
		p.click(app.completion_reset)
		await p.frames()
		p.click(app.reset_dialog.get_cancel_button())
		await p.frames()
		p.check(view.grid_selected and app.session.completed,"AR reset cancel retains grid")
		row.unchanged = snapshot(app) == before and p.save_bytes() == bytes
		row.state_before = before.sha256_text()
		row.state_after = snapshot(app).sha256_text()
		row.slots_before = hashes(bytes)
		row.slots_after = hashes(p.save_bytes())
		p.check(row.unchanged,"AR switch layout cancel preserve session history view and all disk bytes")
		app.show_album()
		p.check(view.solved.is_empty() and view.stable_ink.commands.is_empty() and view.strokes.is_empty() and view.stable_ink.material == null,"AR leave releases stable data")
		app.select_puzzle(context[0])
		p.check(not view.grid_selected and not app.completion_switch.button_pressed,"AR catalog reentry image")
		app._select_completion(true)
		app.show_information("settings")
		app.return_to_work()
		p.check(not view.grid_selected,"AR information reentry image")
		row.reentry_image = not view.grid_selected
		result.append(row)
	return result
