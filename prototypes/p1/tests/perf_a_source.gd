extends SceneTree
## Offline manufacture only. The orchestrator installs this in a pinned Git archive.
const Pencil = preload("res://ui/pencil_marks.gd")
const Grid = preload("res://ui/grid_view.gd")

class SourceBoard extends Control:
	var INK: Color = Color.WHITE # Manufacture X alpha as a neutral ink mask.
	const PREVIEW_ALPHA = 0.56
	var overview: bool = false
	var preview: Dictionary = {}
	var effects: Dictionary = {}
	var view = Grid.new()
	var basis: Color = Color.BLACK
	var elapsed: int = 0
	var animation_clock: Callable = func() -> int: return elapsed
	func cell_color(_value: int) -> Color: return basis

class Sheet extends Pencil:
	var plan: Dictionary
	var level: Dictionary
	var kind: String
	func _draw() -> void:
		var n: int = int(plan.frames)
		var pixels: int = int(level.pixels)
		var pitch: int = pixels + 2 * int(plan.padding)
		var logical: float = float(level.logical_cell)
		board.view.viewport = Rect2(0, 0, logical, logical)
		for variant: int in range(int(plan.variants)):
			for frame: int in range(n):
				draw_set_transform(Vector2(frame * pitch + int(plan.padding), variant * pitch + int(plan.padding)), 0, Vector2.ONE * pixels / logical)
				var box: Rect2 = Rect2(0, 0, logical, logical)
				board.elapsed = ceili(float(frame) * int(plan.duration_us) / (n - 1))
				board.effects = {variant: {"start": 0, "seconds": 0.210}}
				draw_cell(box, 0 if kind == "x" else 1, variant)
			draw_set_transform(Vector2.ZERO)

func _initialize() -> void: call_deferred("run")

func run() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Offline source requires a real rendering driver")
		quit(1)
		return
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PERF_A_ATLAS_PLAN")))
	var output: String = OS.get_environment("PERF_A_OUTPUT")
	for level: Dictionary in plan.levels:
		for kind: String in ["fill", "x"]:
			for basis: String in (["black", "white"] if kind == "fill" else ["white"]):
				var surface := SubViewport.new()
				surface.transparent_bg = true
				surface.size = Vector2i(int(plan.frames), int(plan.variants)) * (int(level.pixels) + 2 * int(plan.padding))
				surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
				root.add_child(surface)
				var sheet := Sheet.new()
				var harness := SourceBoard.new()
				harness.basis = Color.BLACK if basis == "black" else Color.WHITE
				sheet.board = harness
				sheet.plan = plan
				sheet.level = level
				sheet.kind = kind
				surface.add_child(sheet)
				await process_frame
				await RenderingServer.frame_post_draw
				var image: Image = surface.get_texture().get_image()
				if image.save_png(output.path_join("%s-%s-%s.png" % [kind, level.name, basis])) != OK:
					push_error("Cannot save offline source")
					quit(2)
					return
				surface.queue_free()
				harness.free()
				await process_frame
	print("PERF_A_SOURCE_OK")
	quit()
