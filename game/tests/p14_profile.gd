extends SceneTree
## Narrow diagnostic for the F-03 row-slot redraw regression; not an FPS claim.
const SaveStore = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if isolated.is_empty():
		print("P1_PROFILE_FAIL: isolated test root required")
		quit(4)
		return
	SaveStore.test_root_override = isolated
	root.size = Vector2i(1600, 900)
	var app: Main = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	app.select_puzzle(2)
	await process_frame
	await process_frame
	var started: int = Time.get_ticks_usec()
	for i: int in range(20):
		app.board.shared_clue_slot_extent("row", ThemeDB.fallback_font, app.board.clue_font_size())
	var slots_usec: int = Time.get_ticks_usec() - started
	var board_frames: Array[int] = []
	for i: int in range(5):
		app.board.queue_redraw()
		app.mini.queue_redraw()
		started = Time.get_ticks_usec()
		await process_frame
		board_frames.append(Time.get_ticks_usec() - started)
	app.board.hide()
	var without_board: Array[int] = []
	for i: int in range(5):
		app.mini.queue_redraw()
		started = Time.get_ticks_usec()
		await process_frame
		without_board.append(Time.get_ticks_usec() - started)
	print("P1_PROFILE_OK ", JSON.stringify({"slots_20_us": slots_usec,
		"board_frames_us": board_frames, "without_board_us": without_board,
		"display": DisplayServer.get_name(), "window": [root.size.x, root.size.y],
		"engine": Engine.get_version_info().string}))
	quit(0)
