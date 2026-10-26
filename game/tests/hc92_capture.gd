extends SceneTree
const Metrics = preload("res://tests/hc92_metrics.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
var failures: int = 0

class Swatch extends "res://ui/full_view_board.gd":
	var legacy: bool = false
	var status: int = 0
	var colored: bool = false
	var cell: float = 24
	func _layout() -> void:
		view.cell_size = cell
		type_tokens = {"row":{"1":true,"11":true,"17":true,"40":true,"…":true,"–":true},"column":{"1":true,"11":true,"17":true,"40":true,"…":true,"–":true}}
		configure_typography(cell)
	func clue_font() -> Font:
		return Fonts.selected() if legacy else Typography.selected()
	func clue_font_size() -> int:
		if not legacy: return type_size
		var nominal: int = mini(roundi((13 if cell<24 else 14)*ui_scale),maxi(8,floori(cell-4)))
		return mini(Fonts.pixel_size(nominal),maxi(Fonts.pixel_size(8),floori(cell-4)))
	func clue_text_font(font: Font, text: String) -> Font:
		return Fonts.REFERENCE if not text.is_valid_int() else font
	func clue_baseline_offset(fs: int) -> float:
		if not legacy: return Typography.baseline(fs)
		var bounds: Vector2 = Fonts.ink_vertical(fs)
		return -(bounds.x+bounds.y)/2
	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO,size),Color.WHITE)
		for axis: int in range(2):
			for i: int in range(4):
				var text: String = ["1","11","17","40"][i]
				var center: Vector2 = Vector2(70+110*i,60+100*axis)
				var fs: int = clue_font_size()
				var width: float = clue_font().get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x
				var pitch: float = (24*ui_scale if axis==0 else 18*ui_scale) if legacy else pitch_for("row" if axis==0 else "column")
				var area: Rect2 = Rect2(center-Vector2(pitch,cell)/2,Vector2(pitch,cell)) if axis==0 else Rect2(center-Vector2(cell,pitch)/2,Vector2(cell,pitch))
				draw_rect(area,Color(0.94,0.94,0.94),false,1)
				draw_clue_number(clue_font(),center+Vector2(-width/2,clue_baseline_offset(fs)),text,fs,cell_color(2 if i%2==0 else 4) if colored else INK,status)

func _initialize() -> void:
	call_deferred("run")

func pixels(image: Image, region: Rect2i) -> Array:
	var low: Vector2i = region.end
	var high: Vector2i = region.position
	for y: int in range(region.position.y,region.end.y):
		for x: int in range(region.position.x,region.end.x):
			var color: Color = image.get_pixel(x,y)
			if minf(color.r,minf(color.g,color.b)) < 0.85:
				low = low.min(Vector2i(x,y))
				high = high.max(Vector2i(x+1,y+1))
	return [low.x,low.y,high.x-low.x,high.y-low.y]

func run() -> void:
	var output: String = OS.get_environment("HC92_OUTPUT")
	if output.is_empty() or DisplayServer.get_name()=="headless": quit(2); return
	var canvas: SubViewport = SubViewport.new()
	canvas.size = Vector2i(470,220)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	var board: Swatch = Swatch.new()
	board.session = Session.new(Definition.load_fixture("t08"))
	board.size = Vector2(canvas.size)
	canvas.add_child(board)
	var records: Array = []
	for cell: float in [16,24,40]:
		for ui: float in [1,1.25]:
			for colored: bool in [false,true]:
				for status: int in range(3):
					for legacy: bool in [false]:
						board.cell = cell
						board.ui_scale = ui
						board.colored = colored
						board.status = status
						board.legacy = legacy
						board._layout()
						board.queue_redraw()
						await process_frame
						await RenderingServer.frame_post_draw
						var image: Image = canvas.get_texture().get_image()
						var boxes: Array = []
						for axis: int in range(2):
							for i: int in range(4): boxes.append(pixels(image,Rect2i(20+110*i,20+100*axis,100,80)))
						var name: String = "hc-%s-c%d-u%d-%s-s%d.png" % ["before" if legacy else "after",cell,roundi(ui*100),"color" if colored else "mono",status]
						if image.save_png(output.path_join(name)) != OK: failures += 1
						records.append({"file":name,"sha256":FileAccess.get_sha256(output.path_join(name)),"before":legacy,"cell":cell,"ui_scale":ui,"colored":colored,"status":status,"font_px":board.clue_font_size(),"pitch":[24*ui,18*ui] if legacy else [board.slot_pitch.x,board.slot_pitch.y],"pixels":boxes,"typography":Metrics.capture(board) if not legacy else {}})
	var report: Dictionary = {"failures":failures,"records":records,"digits":["1","11","17","40"],"pixel_threshold":0.85}
	FileAccess.open(output.path_join("hc92-native.json"),FileAccess.WRITE).store_string(JSON.stringify(report)+"\n")
	print("HC92_NATIVE_", "OK" if failures==0 else "FAILED", " records=",records.size())
	quit(0 if failures==0 else 1)
