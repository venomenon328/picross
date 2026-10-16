extends SceneTree
const Session = preload("res://model/session.gd")
var records: Array = []
var failures: int = 0

class Swatch extends "res://ui/full_view_board.gd":
	var layer: String = "open"
	var samples: Array = []
	func _layout() -> void: pass
	func prepare(cell: float, ui: float) -> void:
		ui_scale = ui
		view.cell_size = cell
		type_tokens = {"row":{}, "column":{}}
		for text: String in ["1", "11", "17", "23", "40", "50", "…", "–"]:
			type_tokens.row[text] = true
			type_tokens.column[text] = true
		configure_typography(cell)
		samples.clear()
		for axis: String in ["row", "column"]:
			for color_id: int in [0, 1, 2, 4]:
				for i: int in range(8):
					var text: String = ["1", "11", "17", "23", "40", "50", "…", "–"][i]
					var color_slot: int = [0, 1, 2, 4].find(color_id)
					var center: Vector2 = Vector2(50 + i * slot_pitch.x, 60 + 120 * color_slot) if axis == "row" else Vector2(500 + 100 * color_slot, 40 + i * slot_pitch.y)
					var fs: int = clue_font_size()
					var width: float = clue_text_font(clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
					var baseline: Vector2 = center + Vector2(-width / 2, clue_baseline_offset(fs))
					var box: Rect2 = glyph_box(text, baseline, fs)
					samples.append({"axis":axis,"text":text,"color_id":color_id,"identity":clue_identity(axis,color_id,i),"baseline":baseline,"box":box})
	func draw_clue_cross(font: Font, baseline: Vector2, text: String, fs: int, color: Color, outlined: bool, identity: String) -> void:
		if layer != "closed-number": super.draw_clue_cross(font, baseline, text, fs, color, outlined, identity)
	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO,size), Color.WHITE)
		for sample: Dictionary in samples:
			var color: Color = (INK if sample.color_id == 0 else cell_color(sample.color_id)) if sample.text.is_valid_int() else ACCENT
			if layer == "cross":
				if sample.text.is_valid_int():
					super.draw_clue_cross(clue_text_font(clue_font(),sample.text),sample.baseline,sample.text,clue_font_size(),color,sample.color_id in [2,4],sample.identity)
			else:
				var status: int = 0 if layer == "open" else (1 if layer == "filled" else 2)
				draw_clue_number(clue_font(),sample.baseline,sample.text,clue_font_size(),color,status,sample.identity)

func _initialize() -> void: call_deferred("run")

func capture(board: Swatch, canvas: SubViewport) -> Image:
	board.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	return canvas.get_texture().get_image()

func run() -> void:
	var output: String = OS.get_environment("HS186_OUTPUT")
	if output.is_empty() or DisplayServer.get_name() == "headless": quit(2); return
	var canvas: SubViewport = SubViewport.new()
	canvas.size = Vector2i(900,480)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	var board: Swatch = Swatch.new()
	board.size = Vector2(canvas.size)
	root.size = canvas.size
	# Self-contained synthetic swatch; also executable externally against a
	# shipped PCK that correctly excludes test catalog/fixture resources.
	board.session = Session.new({"id":"hs186-swatch","width":1,"height":1,"rows":[[]],"columns":[[]],"solution":[[0]],
		"palette":[{"id":1,"color":"#293e3d"},{"id":2,"color":"#d5ad46"},{"id":3,"color":"#9d5553"},{"id":4,"color":"#4b7c8a"}]})
	canvas.add_child(board)
	# Deliberately fixed drawing isolation, NOT a window/layout matrix. Real
	# main-scene layouts and their measured HS context come from hf149_probe.
	for ui: float in [1.0,1.25]:
		for cell: float in [16,24,40,23.37]:
			board.prepare(cell,ui)
			var files: Dictionary = {}
			var closed: Image
			for layer: String in ["open","filled","closed","closed-number","cross"]:
				board.layer = layer
				var image: Image = await capture(board,canvas)
				var name: String = "hs-swatch-u%d-c%s-%s.png" % [roundi(ui*100),str(cell).replace(".","_"),layer]
				if image.save_png(output.path_join(name)) != OK: failures += 1
				if image.get_size() != canvas.size or Vector2(canvas.size) != board.size: failures += 1
				files[layer] = {"file":name,"sha256":FileAccess.get_sha256(output.path_join(name)),"image_size":[image.get_width(),image.get_height()]}
				if layer == "closed": closed = image
			board.layer = "closed"
			var redraw: Image = await capture(board,canvas)
			board.prepare(20,ui)
			await capture(board,canvas)
			board.prepare(cell,ui)
			var zoom_back: Image = await capture(board,canvas)
			board.session = Session.new(board.session.definition)
			var restored: Image = await capture(board,canvas)
			var stable: bool = closed.get_data() == redraw.get_data() and closed.get_data() == zoom_back.get_data() and closed.get_data() == restored.get_data()
			if not stable: failures += 1
			var samples: Array = []
			for sample: Dictionary in board.samples:
				var box: Rect2 = sample.box
				var points: Array = []
				for stroke: PackedVector2Array in board.Typography.cross_strokes(sample.text,board.clue_font_size(),sample.identity,null,ui):
					var vertices: Array = []
					for p: Vector2 in stroke: vertices.append([p.x,p.y])
					points.append(vertices)
				samples.append({"axis":sample.axis,"text":sample.text,"color_id":sample.color_id,"box":[box.position.x,box.position.y,box.size.x,box.size.y],"strokes":points})
			records.append({"kind":"fixed-swatch","client":[DisplayServer.window_get_size().x,DisplayServer.window_get_size().y],"root_viewport":[root.size.x,root.size.y],"render_size":[canvas.size.x,canvas.size.y],"board_size":[board.size.x,board.size.y],"ui":ui,"cell":cell,"fs":board.clue_font_size(),"pitch":[board.slot_pitch.x,board.slot_pitch.y],"stable":stable,"files":files,"samples":samples})
	var hash: HashingContext = HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(board.clue_font().data)
	var report: Dictionary = {"failures":failures,"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"records":records,
		"dpi":DisplayServer.screen_get_dpi(),"screen_scale":DisplayServer.screen_get_scale(),"screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y],"font_sha256":hash.finish().hex_encode()}
	FileAccess.open(output.path_join("hs-native.json"),FileAccess.WRITE).store_string(JSON.stringify(report)+"\n")
	print("HS186_NATIVE_", "OK" if failures == 0 else "FAILED", " records=",records.size())
	quit(0 if failures == 0 else 1)
