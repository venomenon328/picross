extends SceneTree
## Render only data from a validated definition with the shipped drawing primitives.
const Atlas = preload("res://ui/cell_atlas.gd")
const Ink = preload("res://ui/clue_typography.gd")
const Grid = preload("res://ui/scribble.gd")

class SheetLayer extends Node2D:
	var definition: Dictionary
	var pitch: int
	var status: int
	var fills: bool
	var origin: Vector2
	var palette: Dictionary

	func _draw() -> void:
		if fills:
			var lod := Atlas.level(pitch)
			var atlas := load("res://art/cells/fill-" + lod + ".png") as Texture2D
			for y: int in range(definition.height):
				for x: int in range(definition.width):
					var color_id := int(definition.solution[y][x])
					if color_id == 0:
						continue
					var cell := Rect2(origin + Vector2(x,y) * pitch, Vector2.ONE * pitch)
					var variant := Atlas.variant(definition.id, int(definition.revision), Vector2i(x,y))
					draw_texture_rect_region(atlas, Atlas.mapped_box(cell,lod), Atlas.region(lod,variant,23), palette[color_id])
			return
		for axis: String in ["row", "column"]:
			var lines: Array = definition.rows if axis == "row" else definition.columns
			var along := Vector2.RIGHT if axis == "row" else Vector2.DOWN
			var down := Vector2.DOWN if axis == "row" else Vector2.RIGHT
			var span := float(definition.width if axis == "row" else definition.height) * pitch
			for i: int in range(lines.size()+1):
				var start := origin + down * i * pitch
				var stroke := Grid.grid_stroke(start,start+along*span,axis,i,lines.size(),pitch,definition.id,int(definition.revision))
				Grid.paint(self,stroke,stroke.color)
				if i == lines.size():
					break
				var clues: Array = lines[i]
				var tokens: Array = clues if not clues.is_empty() else [{"length": "–", "color": 0}]
				for j: int in range(tokens.size()):
					var token: Dictionary = tokens[j]
					var label := str(int(token.length)) if token.color != 0 else "–"
					var fs := 13 if pitch == 24 else 9
					var font := Ink.text_font(label)
					var center := start + down * 0.5 * pitch - along * (tokens.size()-j-0.5) * pitch
					var base := center + Vector2(-font.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x/2,Ink.baseline(fs))
					var color_id := int(token.color)
					var color: Color = palette[color_id] if palette.size()>1 and color_id>0 else Color("343f42")
					var outlined := palette.size()>1 and color_id in [2,4]
					Ink.paint(self,base,label,fs,color,status,"%s/%s/%d/%d" % [definition.id,axis,i,j],outlined,1.0,font)

func _initialize() -> void:
	render.call_deferred()

func render() -> void:
	var args := OS.get_cmdline_user_args()
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var palette: Dictionary = {}
	for p: Dictionary in definition.palette:
		palette[int(p.id)] = Color(p.color)
	var left := 1
	var top := 1
	for line: Array in definition.rows:
		left = maxi(left,line.size())
	for line: Array in definition.columns:
		top = maxi(top,line.size())
	var paper := load("res://book/paper.png") as Texture2D
	var mask := ShaderMaterial.new()
	mask.shader = preload("res://ui/atlas_mask.gdshader")
	for pitch: int in [24,14]:
		for status: int in range(3):
			var view := SubViewport.new()
			view.size = Vector2i((left+int(definition.width))*pitch+8,(top+int(definition.height))*pitch+8)
			view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
			view.disable_3d = true
			root.add_child(view)
			var page := TextureRect.new()
			page.texture = paper
			page.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			page.size = view.size
			view.add_child(page)
			var wash := ColorRect.new()
			wash.color = Color(1.0,0.98,0.93,0.55)
			wash.size = view.size
			view.add_child(wash)
			for fills: bool in [true,false]:
				var layer := SheetLayer.new()
				layer.definition = definition
				layer.pitch = pitch
				layer.status = status
				layer.palette = palette
				layer.fills = fills
				layer.origin = Vector2(left,top)*pitch + Vector2(4,4)
				if fills:
					layer.material = mask
				view.add_child(layer)
			await process_frame
			await RenderingServer.frame_post_draw
			var snapshot := view.get_texture().get_image()
			if snapshot == null or snapshot.save_png(args[1].path_join("%d-%d.png" % [pitch,status])) != OK:
				quit(1)
				return
			view.queue_free()
			await process_frame
	quit(0)
