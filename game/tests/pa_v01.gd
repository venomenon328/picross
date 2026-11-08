extends SceneTree
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
const Fixture = preload("res://tests/book_fixture.gd")
var output: String
var records: Array = []

class SyntheticContent extends "res://tests/book_fixture.gd".ImmediateContent:
	func puzzle_definitions() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		for i: int in range(1,9):
			result.append(JSON.parse_string(FileAccess.get_file_as_string("res://../review-evidence/pa-v01/F%02d.json" % i)))
		return result
	func validate_definition(data: Dictionary) -> String:
		return Definition.validate(data,{data.id:"res://book/paper.png"})

class Tokens extends "res://ui/full_view_board.gd":
	func _layout() -> void: pass
	func prepare(source: Control) -> void:
		ui_scale = source.ui_scale
		view.cell_size = source.view.cell_size
		type_tokens = source.type_tokens.duplicate(true)
		for axis: String in ["row","column"]:
			for token: String in ["1","11"]: type_tokens[axis][token] = true
		configure_typography(view.cell_size)
	func _draw() -> void:
		var fs: int = clue_font_size()
		var step: float = size.x / session.definition.palette.size()
		var font: Font = BODY_FONT
		var label_size: int = 12
		for i: int in range(session.definition.palette.size()):
			var id: int = i+1
			var x: float = i*step+step/2
			var color: Color = cell_color(id)
			draw_string(font,Vector2(x-step/2+2,18),"c%02d / ID%d" % [id,id],HORIZONTAL_ALIGNMENT_LEFT,-1,label_size,INK)
			draw_string(font,Vector2(x-step/2+2,35),session.definition.palette[i].color,HORIZONTAL_ALIGNMENT_LEFT,-1,label_size,INK)
			draw_rect(Rect2(x-step/2+3,43,step-6,22),color)
			for state: int in range(3):
				var y: float = 98+state*40
				draw_string(font,Vector2(x-step/2+2,y-18),"row "+["OPEN","FILLED","CLOSED"][state],HORIZONTAL_ALIGNMENT_LEFT,-1,label_size,INK)
				for j: int in range(2):
					var token: String = ["1","11"][j]
					var width: float = clue_font().get_string_size(token,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x
					var baseline := Vector2(x+(j-0.5)*slot_pitch.x-width/2,y+clue_baseline_offset(fs))
					draw_clue_number(clue_font(),baseline,token,fs,color,state,clue_identity("row",id,j))
			for state: int in range(3):
				var y: float = 230+state*72
				draw_string(font,Vector2(x-step/2+2,y-18),"col "+["OPEN","FILLED","CLOSED"][state],HORIZONTAL_ALIGNMENT_LEFT,-1,label_size,INK)
				for j: int in range(2):
					var token: String = ["1","11"][j]
					var width: float = clue_font().get_string_size(token,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x
					var baseline := Vector2(x-width/2,y+j*slot_pitch.y+clue_baseline_offset(fs))
					draw_clue_number(clue_font(),baseline,token,fs,color,state,clue_identity("column",id,j))

class CellPatch extends "res://ui/full_view_board.gd":
	var measured_cell: float
	func _layout() -> void:
		if session == null: return
		view.cell_size = measured_cell
		view.configure(Rect2(Vector2.ONE,Vector2(10,5)*measured_cell),Vector2i(10,5))
		view.center = Vector2(5,2.5)
		view.reframe()
		layout_valid = true
	func _draw_clues(_first: Vector2i, _last: Vector2i) -> void: pass

func _initialize() -> void: call_deferred("run")

func settle() -> void:
	for i: int in range(5): await process_frame
	await RenderingServer.frame_post_draw

func save_image(name: String) -> Dictionary:
	await settle()
	var image: Image = root.get_texture().get_image()
	assert(image.save_png(output.path_join(name)) == OK)
	return {"file":name,"sha256":FileAccess.get_sha256(output.path_join(name)),"bytes":FileAccess.get_file_as_bytes(output.path_join(name)).size(),"size":[image.get_width(),image.get_height()]}

func run() -> void:
	output = OS.get_environment("PA_OUTPUT")
	assert(not output.is_empty() and DisplayServer.get_name() != "headless")
	Store.test_root_override = output.path_join("isolated-saves")
	var app: Control = Fixture.attach(root,SyntheticContent)
	await settle()
	assert(app.sessions.size()==8,app.catalog_error)
	var book: Node3D = app.book
	# SaveStore validates registry-bound production saves. This isolated
	# diagnostic owns no production slot; mark its synthetic sessions fresh.
	for i: int in range(8):
		app.slot_status[i] = "fresh"
		app.slot_errors[i] = ""
	for context: Dictionary in [{"id":"small","size":Vector2i(1280,720),"ui":1.25},{"id":"normal","size":Vector2i(1920,1080),"ui":1.0}]:
		root.size = context.size
		DisplayServer.window_set_size(context.size)
		app.size = Vector2(context.size)
		app.set_ui_scale(context.ui)
		await settle()
		for index: int in range(8):
			app.select_puzzle(index)
			assert(app.work.visible and not app.album.visible,"synthetic work must actually open")
			app.save_timer.stop()
			var board: Control = app.board
			board.set_animations(false)
			board.requested_cell = 24
			board.mode = "G"
			var matrix: Array = app.session.definition.solution
			for y: int in range(30):
				for x: int in range(40):
					app.session.player.cells[y*40+x] = int(matrix[y][x]) if (x+y)%9!=0 else -1
			app._layout_book()
			board._layout()
			board.queue_redraw()
			await settle()
			assert(board.layout_valid)
			var prefix: String = "F%02d-%s" % [index+1,context.id]
			var rec: Dictionary = {"family":"F%02d" % (index+1),"context":context.id,"ui":context.ui,"client":[root.size.x,root.size.y],"cell":board.view.cell_size,"font_size":board.clue_font_size(),"slot_pitch":[board.slot_pitch.x,board.slot_pitch.y],"board_rect":[board.position.x,board.position.y,board.size.x,board.size.y],"files":[]}
			rec.files.append(await save_image(prefix+"-board.png"))
			var panel := Tokens.new()
			panel.session = app.session
			panel.book_layout = true
			panel.position = board.position
			panel.size = board.size
			panel.prepare(board)
			app.work.add_child(panel)
			# Same-size native cell/rule context in each explicit status panel.
			# This is a display-only swatch, not extra uses in the fixed matrix.
			var patch := CellPatch.new()
			var patch_data: Dictionary = app.session.definition.duplicate(true)
			patch_data.id += "-display-patch"
			patch_data.width = 10
			patch_data.height = 5
			patch_data.rows = [[],[],[],[],[]]
			patch_data.columns = [[],[],[],[],[],[],[],[],[],[]]
			patch.session = Session.new(patch_data)
			patch.measured_cell = board.view.cell_size
			patch.book_layout = true
			patch.ui_scale = board.ui_scale
			patch.position = Vector2(panel.size.x/2-5*patch.measured_cell,430)
			patch.size = Vector2(10,5)*patch.measured_cell+Vector2.ONE*2
			for y: int in range(5):
				for x: int in range(10):
					patch.session.player.cells[y*10+x] = -1 if x==8 else (0 if x==9 else 1+(x+y)%app.session.definition.palette.size())
			panel.add_child(patch)
			board.hide()
			panel.queue_redraw()
			rec["panel_font_size"] = panel.clue_font_size()
			rec["panel_slot_pitch"] = [panel.slot_pitch.x,panel.slot_pitch.y]
			rec["panel_tokens"] = ["1","11"]
			rec["panel_states"] = ["OPEN","FILLED","CLOSED"]
			rec["panel_axes"] = ["row","column"]
			rec["c1_runtime_ids"] = [2,4]
			rec["display_patch"] = {"dimensions":[10,5],"cell":patch.measured_cell,"palette":"same IDs/RGB; display-only uses excluded from reference matrix counts","native_draw":"unmodified inherited full_view_board/drawing_board/atlas_marks/grid_stroke; clue drawing handled above"}
			rec.files.append(await save_image(prefix+"-tokens.png"))
			panel.free()
			board.show()
			records.append(rec)
			print(prefix," cell=",rec.cell," fs=",rec.font_size," panel_fs=",rec.panel_font_size)
	var report: Dictionary = {"source_commit":"059bb003dc761e862b304957143b0dd45d92bb82","plan_sha256":FileAccess.get_sha256("res://../review-evidence/pa-v01/plan.json"),"engine":Engine.get_version_info(),"os":OS.get_name(),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"screen_dpi":DisplayServer.screen_get_dpi(),"screen_scale":DisplayServer.screen_get_scale(),"records":records,"limitations":"Static native diagnostics. Token statuses injected into unchanged draw_clue_number, not an H1 proof. Book/cells/hint renderer unchanged; no perception or owner approval asserted."}
	FileAccess.open(output.path_join("native.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t")+"\n")
	book.free()
	quit(0)
