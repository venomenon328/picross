extends SceneTree
const Main = preload("res://ui/main.gd")
const Session = preload("res://model/session.gd")
const SaveStore = preload("res://model/save_store.gd")
var surface: SubViewport
var app: Main
var output: String
var variant: String
var captures: Array = []

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	SaveStore.test_root_override = "user://zv50-capture-%d" % Time.get_ticks_usec()
	output = OS.get_environment("P1_CAPTURE_DIR")
	variant = OS.get_environment("ZV50_VARIANT")
	if output.is_empty() or variant.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	await create_timer(0.3).timeout
	for spec: Array in [
		[3, 1920, 1080, 1.0, 24.0, "f04-1920-ui100-z100"],
		[3, 1920, 1080, 1.0, 32.0, "f04-1920-ui100-z133"],
		[3, 1920, 1080, 1.0, 36.0, "f04-1920-ui100-z150"],
		[3, 1920, 1080, 1.0, 40.0, "f04-1920-ui100-z167"],
		[3, 1280, 720, 1.25, 36.0, "f04-1280-ui125-z150"],
		[1, 1920, 1080, 1.0, 24.0, "f02-1920-ui100-z100"],
		[1, 1920, 1080, 1.0, 26.0, "f02-1920-ui100-z108"],
		[2, 1920, 1080, 1.0, 24.0, "f03-1920-ui100-z100"]]:
		surface.size = Vector2i(spec[1], spec[2])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[3])
		app.select_puzzle(spec[0])
		install_demo(spec[0])
		app.open_puzzle()
		app.board.working_size()
		while app.board.view.cell_size < float(spec[4]) - 0.01:
			app.board.zoom(1, app.board.view.viewport.get_center())
		while app.board.view.cell_size > float(spec[4]) + 0.01:
			app.board.zoom(-1, app.board.view.viewport.get_center())
		app.board.view.center = Vector2(app.session.player.width, app.session.player.height) / 2.0
		app.board.view.reframe()
		await shot(spec[5])
	var report: FileAccess = FileAccess.open(output.path_join("zv50-" + variant + ".json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"variant": variant, "renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(), "captures": captures}, "\t") + "\n")
	print("ZV50_CAPTURE_OK images=", captures.size())
	quit(0)

func install_demo(index: int) -> void:
	var fresh: Session = Session.new(app.sessions[index].definition)
	var width: int = fresh.player.width
	var height: int = fresh.player.height
	var changes: Array = []
	for y: int in range(mini(height, 12)):
		for x: int in range(mini(width, 20)):
			if (x + y) % 7 == 0:
				changes.append({"index": y * width + x, "before": -1, "after": 1})
			elif (x * 3 + y) % 11 == 0:
				changes.append({"index": y * width + x, "before": -1, "after": 0})
	if not changes.is_empty():
		fresh.player.commit(changes)
	app.sessions[index] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.ensure_clue_steps()

func rect_data(rect: Rect2) -> Array:
	return [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

func shot(name: String) -> void:
	app.board.clear_pointer_hover()
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	var file: String = "zv50-" + variant + "-" + name + ".png"
	if picture.save_png(output.path_join(file)) != OK:
		quit(5)
		return
	var visible: Rect2 = app.board.view.visible_bounds()
	var viewport: Rect2 = app.board.view.viewport
	var expected: Vector2 = Vector2(app.board.view.dimensions) * app.board.view.cell_size
	var visible_global: Rect2 = Rect2(app.board.global_position + visible.position, visible.size)
	var viewport_global: Rect2 = Rect2(app.board.global_position + viewport.position, viewport.size)
	captures.append({
		"file": file, "case": name, "fixture": app.session.definition.id,
		"size": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale, "pitch": app.board.view.cell_size,
		"cells_sha256": JSON.stringify(app.session.player.cells).sha256_text(),
		"viewport": rect_data(viewport_global), "grid": rect_data(visible_global),
		"visible_cells": [visible.size.x / app.board.view.cell_size, visible.size.y / app.board.view.cell_size],
		"full_grid": visible.size.is_equal_approx(expected),
		"normalized_view": rect_data(app.board.view.normalized_view()),
		"tools_top": app.actions.fill.global_position.y,
		"mini": rect_data(app.mini.get_global_rect())
	})
