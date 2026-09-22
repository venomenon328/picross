extends SceneTree
## Optional rendering inspection. Set P1_CAPTURE_DIR to an isolated output path.
const Main = preload("res://ui/main.gd")

func _initialize() -> void:
	call_deferred("run")

func snapshot(app: Main, filename: String) -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var target: String = OS.get_environment("P1_CAPTURE_DIR").path_join(filename + ".png")
	var error: Error = app.get_viewport().get_texture().get_image().save_png(target)
	if error != OK:
		quit(4)

func run() -> void:
	if OS.get_environment("P1_CAPTURE_DIR").is_empty():
		quit(2)
		return
	var app: Main = load("res://main.tscn").instantiate()
	root.add_child(app)
	root.size = Vector2i(1280, 720)
	await snapshot(app, "album")
	app.open_puzzle()
	await snapshot(app, "board")
	for y: int in range(20):
		for x: int in range(20):
			if app.session.definition.solution[y][x] > 0:
				app.session.gesture.begin(app.session.player, Vector2i(x, y), 1)
				app.session.finish()
	app.refresh()
	await snapshot(app, "reveal")
	print("P1_CAPTURE_OK")
	quit()
