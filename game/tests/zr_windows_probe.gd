extends SceneTree
## Read-only layout plan from the delivered PCK; native EXE input is external.
var app: Control

func _initialize() -> void:
	call_deferred("run")

func point(item: Control) -> Array:
	var p: Vector2 = item.get_global_rect().get_center()
	return [p.x,p.y]

func run() -> void:
	app=load("res://main.tscn").instantiate()
	root.add_child(app)
	root.size=Vector2i(1280,720)
	await process_frame
	await process_frame
	var card: Array = point(app.choices[0])
	app.select_puzzle(0)
	await process_frame
	await process_frame
	var b: Control = app.board
	var width: int = app.session.player.width
	var height: int = app.session.player.height
	var starts: Array = []
	for cell: Vector2i in [Vector2i(4,4),Vector2i(width-5,4),Vector2i(4,8)]:
		var p: Vector2 = b.get_global_transform_with_canvas()*b.view.cell_rect(cell).get_center()
		starts.append([p.x,p.y])
	var result: Dictionary = {"client":[root.size.x,root.size.y],"ui":app.ui_scale,"card":card,
		"definition_id":app.session.definition.id,"slot":app.store.key_for_definition(str(app.session.definition.id)),
		"save_file":app.store.path_for(app.store.key_for_definition(str(app.session.definition.id))).get_file(),
		"dimensions":[width,height],"starts":starts,"actions":[point(app.undo_button),point(app.redo_button)],
		"font":b.clue_font().get_font_name(),"cell":b.view.cell_size,"layout_valid":b.layout_valid}
	var path: String = OS.get_environment("ZR_WINDOWS_PLAN")
	var f: FileAccess = FileAccess.open(path,FileAccess.WRITE)
	f.store_string(JSON.stringify(result)+"\n")
	f.close()
	print("ZR_WINDOWS_LAYOUT_OK")
	quit()
