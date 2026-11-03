extends Control
## Passive ink only: no player, gesture, solver, timer or per-cell node.
const Atlas = preload("res://ui/cell_atlas.gd")
const Typography = preload("res://ui/clue_typography.gd")
const Scribble = preload("res://ui/scribble.gd")
const INK = Color("343f42")
var diagram: Dictionary
var identity: String
var ui_scale: float = 1.0
var cell_size: float
var font_size: int
var slot: Vector2
var grid: Rect2
var ink: Control
var textures: Dictionary = {}
static var atlas_material: ShaderMaterial

class Marks extends Control:
	var example: Control
	func _draw() -> void: example.paint_cells(self)

func configure(key: String, data: Dictionary) -> void:
	identity = "help/"+key
	diagram = data
	mouse_filter = MOUSE_FILTER_IGNORE
	size_flags_horizontal = SIZE_SHRINK_BEGIN
	ink = Marks.new()
	ink.example = self
	ink.show_behind_parent = true
	ink.mouse_filter = MOUSE_FILTER_IGNORE
	if atlas_material == null:
		atlas_material = ShaderMaterial.new()
		atlas_material.shader = preload("res://ui/atlas_mask.gdshader")
	ink.material = atlas_material
	ink.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	ink.texture_repeat = CanvasItem.TEXTURE_REPEAT_DISABLED
	add_child(ink)
	set_ui_scale(1.0)

func set_ui_scale(value: float) -> void:
	ui_scale = value
	cell_size = 32*value
	# Measure the same native numeric/X envelopes as the active board. One
	# common size/slot for every token; its state never changes geometry.
	font_size = 1
	for candidate: int in range(1,ceili(cell_size*4)):
		var envelope: Rect2 = Typography.envelope("5",candidate,value)
		if maxf(envelope.size.x,envelope.size.y) <= cell_size-4*value: font_size = candidate
	var hull: Rect2 = Typography.envelope("5",font_size,value)
	slot = Vector2(ceilf(hull.size.x+5*value),ceilf(hull.size.y+5*value))
	var rows: Array = diagram.get("rows",[])
	var columns: Array = diagram.get("columns",[])
	var reserve: int = 0
	for row: Array in rows: reserve = maxi(reserve,row.size())
	var origin := Vector2(4*value+reserve*slot.x,4*value+(slot.y if not columns.is_empty() else 0.0))
	var cells: Array = diagram.get("cells",[])
	grid = Rect2(origin,Vector2(cells[0].size(),cells.size())*cell_size) if not cells.is_empty() else Rect2()
	custom_minimum_size = grid.end+Vector2.ONE*4*value if not cells.is_empty() else Vector2(44,44)*value
	queue_redraw()
	if ink != null: ink.queue_redraw()

func paint_cells(canvas: CanvasItem) -> void:
	var lod: String = Atlas.level(cell_size)
	for y: int in range(diagram.get("cells",[]).size()):
		for x: int in range(diagram.cells[y].size()):
			var value: int = diagram.cells[y][x]
			if value < 0: continue
			var kind: String = "fill" if value > 0 else "x"
			var key: String = kind+"-"+lod
			if not textures.has(key): textures[key] = load("res://art/cells/"+key+".png")
			var cell := Rect2(grid.position+Vector2(x,y)*cell_size,Vector2.ONE*cell_size)
			var target: Rect2 = Atlas.mapped_box(cell,lod) if value > 0 else cell
			var color: Color = diagram.colors[value-1] if value > 0 else INK
			canvas.draw_texture_rect_region(textures[key],target,Atlas.region(lod,Atlas.variant(identity,1,Vector2i(x,y)),Atlas.FRAMES-1),color,false,true)

func token(center: Vector2, clue: Variant, status: int = 0, index: int = 0) -> void:
	var text: String = str(clue.length) if clue is Dictionary else str(clue)
	var color_id: int = clue.color if clue is Dictionary else 1
	var color: Color = diagram.colors[color_id-1]
	var face: Font = Typography.text_font(text)
	var baseline: Vector2 = center+Vector2(-face.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x/2,Typography.baseline(font_size))
	Typography.paint(self,baseline,text,font_size,color,status,identity+"/"+str(index),diagram.colors.size() > 1 and color_id in [2,4],ui_scale)

func _draw() -> void:
	if diagram.has("tokens"):
		for i: int in range(diagram.tokens.size()): token(custom_minimum_size/2,diagram.tokens[i],diagram.states[i],i)
		return
	var cells: Array = diagram.cells
	for y: int in range(cells.size()+1):
		var start: Vector2 = grid.position+Vector2(0,y*cell_size)
		var line: Dictionary = Scribble.grid_stroke(start,start+Vector2(grid.size.x,0),"row",y,cells.size(),cell_size,identity,1)
		Scribble.paint(self,line,line.color)
	for x: int in range(cells[0].size()+1):
		var start: Vector2 = grid.position+Vector2(x*cell_size,0)
		var line: Dictionary = Scribble.grid_stroke(start,start+Vector2(0,grid.size.y),"column",x,cells[0].size(),cell_size,identity,1)
		Scribble.paint(self,line,line.color)
	for y: int in range(diagram.rows.size()):
		var row: Array = diagram.rows[y]
		for i: int in range(row.size()): token(Vector2(grid.position.x-(row.size()-i-0.5)*slot.x,grid.position.y+(y+0.5)*cell_size),row[i],0,y*10+i)
	for x: int in range(diagram.columns.size()):
		token(Vector2(grid.position.x+(x+0.5)*cell_size,grid.position.y-slot.y/2),diagram.columns[x][0],0,100+x)
