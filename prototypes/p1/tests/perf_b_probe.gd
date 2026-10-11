extends SceneTree
## Regular scene and exported PCK probe. Reference mapping is the frozen A
## equation, independent of the runtime's mapping, cache and vertex-color shader.
const Store = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
var app: Control
var output: String
var failures: int = 0
var checks: int = 0
var clock_us: int = 1000000
var samples: Array = []
var cycles: Array = []
var draw_counts: Array[int] = [0,0]
var reference: SubViewport
var background: TextureRect
var ink: ReferenceInk

class ReferenceInk extends Control:
	var texture: Texture2D
	var source: Rect2
	var target: Rect2
	func _draw() -> void:
		if texture != null: draw_texture_rect_region(texture,target,source,Color.WHITE,false,true)

func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("PERF_B_FAIL ",label)

func frame() -> void:
	await process_frame
	await RenderingServer.frame_post_draw

func settle() -> void:
	await frame()
	await frame()

func clear_sample() -> void:
	app.board.cancel_gesture()
	var fresh: Session = Session.new(app.session.definition)
	app.sessions[app.sessions.find(app.session)] = fresh
	app.session = fresh
	app.board.session = fresh
	app.refresh()
	app.board.clear_pointer_hover()
	await settle()

func mouse(cell: Vector2i, button: MouseButton, pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.position=app.board.global_position+app.board.view.cell_rect(cell).get_center()
	event.button_index=button
	event.pressed=pressed
	event.button_mask=(MOUSE_BUTTON_MASK_LEFT if button==MOUSE_BUTTON_LEFT else MOUSE_BUTTON_MASK_RIGHT) if pressed else 0
	root.push_input(event,true)

func difference(a: Image, b: Image) -> float:
	if a.get_size()!=b.get_size(): return INF
	var total: float = 0
	for y: int in range(1,a.get_height()-1):
		for x: int in range(1,a.get_width()-1):
			var c: Color = a.get_pixel(x,y)
			var d: Color = b.get_pixel(x,y)
			total += (absf(c.r-d.r)+absf(c.g-d.g)+absf(c.b-d.b))*255.0
	return total/(3*(a.get_width()-2)*(a.get_height()-2))

func expected(blank: Image, box: Rect2, cell: Vector2i, value: int, elapsed: int, alpha: float = 1.0, variant_shift: int = 0) -> Image:
	var size_px: int = 32 if box.size.x<18 else (64 if box.size.x<=36 else 96)
	var logical: float = 16 if box.size.x<18 else (24 if box.size.x<=36 else 72)
	var lod: String = "small" if box.size.x<18 else ("medium" if box.size.x<=36 else "large")
	var id: String = "pencil-atlas-1\n%s\n%d\n%d\n%d" % [app.session.definition.id,app.session.definition.revision,cell.x,cell.y]
	var variant: int = (id.sha256_text().substr(0,8).hex_to_int()+variant_shift)%16
	var f: int = clampi(floori(float(maxi(0,elapsed))*23/210000),0,23)
	var offset: Vector2 = box.position-Vector2(Vector2i(box.position))
	var scale: float = (box.size.x-4)/(logical-4)
	ink.target = Rect2(offset+Vector2.ONE*(2-2*scale),Vector2.ONE*logical*scale) if value>0 else Rect2(offset,box.size)
	ink.source=Rect2(f*(size_px+4)+2,variant*(size_px+4)+2,size_px,size_px)
	ink.texture=load("res://art/cells/%s-%s.png" % ["fill" if value>0 else "x",lod])
	ink.material.set_shader_parameter("base_color",app.board.cell_color(value) if value>0 else app.board.INK)
	ink.material.set_shader_parameter("opacity",alpha)
	background.texture=ImageTexture.create_from_image(blank)
	background.size=Vector2(blank.get_size())
	reference.size=blank.get_size()
	ink.queue_redraw()
	await settle()
	return reference.get_texture().get_image()

func capture(box: Rect2) -> Image:
	return root.get_texture().get_image().get_region(Rect2i(box))

func identity() -> void:
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PERF_B_MANIFEST")))
	for item: Dictionary in manifest.atlases:
		var texture: Texture2D = app.board.marks.textures[item.file.trim_suffix(".png")]
		var image: Image = texture.get_image()
		image.convert(Image.FORMAT_RGBA8)
		var hash := HashingContext.new()
		hash.start(HashingContext.HASH_SHA256)
		hash.update(image.get_data())
		check(hash.finish().hex_encode()==item.pixel_sha256,"actual imported texture identity "+item.file)
	check(app.board.marks.ink_material.shader.resource_path=="res://ui/atlas_mask.gdshader","active runtime shader")

func structural() -> void:
	await clear_sample()
	for i: int in range(1520): app.session.player.cells[i]=1 if i%5 else 0
	app.refresh()
	await settle()
	var before: Dictionary = app.board.marks.stats.duplicate()
	var draws: Array[int] = draw_counts.duplicate()
	for i: int in range(12):
		var event := InputEventMouseMotion.new()
		event.position=app.board.global_position+app.board.view.cell_rect(Vector2i(i,3)).get_center()
		root.push_input(event,true)
		await frame()
	check(app.board.marks.stats.rest_draws==before.rest_draws,"hover reuses entire resting population")
	check(draw_counts==draws,"hover leaves board clues and miniature cached")
	check(app.board.marks.stats.cursor_draws>before.cursor_draws,"hover actually redraws independent cursor")
	for chunk: Control in app.board.marks.chunks: chunk.queue_redraw()
	await settle()
	check(app.board.marks.stats.rest_draws>before.rest_draws,"negative: coupled full invalidation detected by same counter")
	clock_us=1000000
	app.board.animation_clock=func() -> int: return clock_us
	mouse(Vector2i(0,38),MOUSE_BUTTON_LEFT,true)
	mouse(Vector2i(0,38),MOUSE_BUTTON_LEFT,false)
	await settle()
	before=app.board.marks.stats.duplicate()
	draws=draw_counts.duplicate()
	for t: int in [30000,75000,105000,150000,209000]:
		clock_us=1000000+t
		await settle()
	check(app.board.marks.stats.rest_draws==before.rest_draws,"active ticks preserve resting cache")
	check(app.board.marks.stats.transition_draws>before.transition_draws,"active ticks update transitions")
	check(draw_counts==draws,"ticks leave board H1 and miniature cached")
	clock_us=1210000
	await settle()
	check(not app.board.is_processing() and app.board.effects.is_empty(),"elapsed deadline stops processing")
	check(app.board.marks.stats.rest_draws-before.rest_draws<=1,"completion rebuilds one bounded chunk")
	var ids: Array = [app.board.marks.ink_material.get_instance_id()]
	for texture: Texture2D in app.board.marks.textures.values(): ids.append(texture.get_instance_id())
	for i: int in range(24):
		app.select_puzzle([0,1,2,6][i%4])
		app.board.restore_view(app.board.capture_view().merged({"zoom":[16,18,20,72][i%4],"overview":false},true))
		await settle()
		var actual: Array = [app.board.marks.ink_material.get_instance_id()]
		for texture: Texture2D in app.board.marks.textures.values(): actual.append(texture.get_instance_id())
		check(actual==ids,"shared resource identity across page and zoom")
		check(app.board.marks.chunks.size()==ceili(float(app.session.player.cells.size())/64),"bounded chunk count")
		cycles.append({"cycle":i,"chunks":app.board.marks.chunks.size(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"static_bytes":OS.get_static_memory_usage(),"texture_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)})
		if i>=12:
			check(cycles[i].nodes==cycles[i-4].nodes and cycles[i].texture_bytes==cycles[i-4].texture_bytes,"resource/node plateau after warm page cycles")
	app.select_puzzle(1)

func lifecycle() -> void:
	app.board.restore_view(app.board.capture_view().merged({"zoom":20,"overview":false},true))
	await clear_sample()
	var cell := Vector2i(3,3)
	var index: int = 123
	var box: Rect2 = app.board.view.cell_rect(cell)
	box.position+=app.board.global_position
	var blank: Image = capture(box)
	app.board.set_animations(false)
	mouse(cell,MOUSE_BUTTON_LEFT,true)
	mouse(cell,MOUSE_BUTTON_LEFT,false)
	app.board.clear_pointer_hover()
	await settle()
	var filled: Image = capture(box)
	check(difference(filled,blank)>1,"native immediate commit visible")
	app._undo()
	app.board.clear_pointer_hover()
	await settle()
	check(difference(capture(box),blank)<=1,"undo removes cached fill")
	app._redo()
	app.board.clear_pointer_hover()
	await settle()
	check(difference(capture(box),filled)<=1,"redo restores exact cached fill")
	app.board.set_animations(true)
	mouse(cell,MOUSE_BUTTON_RIGHT,true)
	await settle()
	check(app.board.marks.suppressed.has(index) and app.board.marks.presentation(index).value==0 and app.board.marks.presentation(index).alpha==0.56,"preview suppresses old resting fill")
	mouse(cell,MOUSE_BUTTON_RIGHT,false)
	await settle()
	check(app.board.effects.has(index),"conversion effect started")
	# A new effective preview permanently supersedes the old effect.
	mouse(cell,MOUSE_BUTTON_LEFT,true)
	await settle()
	check(not app.board.effects.has(index),"new preview terminates prior effect")
	app.board.cancel_gesture()
	app.board.clear_pointer_hover()
	await settle()
	check(app.board.effects.is_empty() and app.board.preview.is_empty() and app.board.marks.suppressed.is_empty(),"cancel restores confirmed X without callbacks")
	var x_image: Image = capture(box)
	var expected_x: Image = await expected(blank,box,cell,0,210000)
	check(difference(x_image,expected_x)<=1,"cancel renders confirmed target, never previous fill")
	app.board.set_animations(false)
	app.board.set_animations(true)
	await settle()
	check(not app.board.is_processing() and difference(capture(box),x_image)<=1,"off/on never replays effects")
	await clear_sample()
	check(difference(capture(box),blank)<=1,"new/reset session clears cached marks")

func pictures() -> void:
	var cell := Vector2i(3,3)
	for zoom: int in [16,18,20,72]:
		app.board.restore_view(app.board.capture_view().merged({"zoom":zoom,"overview":false},true))
		for value: int in [1,2,3,4,0]:
			await clear_sample()
			var box: Rect2 = app.board.view.cell_rect(cell)
			box.position+=app.board.global_position
			var blank: Image = capture(box)
			var index: int = cell.y*40+cell.x
			app.session.player.cells[index]=value
			app.refresh()
			await settle()
			var actual: Image = capture(box)
			var end: Image = await expected(blank,box,cell,value,210000)
			var error: float = difference(actual,end)
			check(error<=1.0,"independent A native end/color/variant "+str([zoom,value,error]))
			var wrong: Image = await expected(blank,box,cell,value,210000,1.0,1)
			check(difference(actual,wrong)>1.0,"negative: wrong variant detected")
			# Stale cache mutation must be visible to the same native pixel oracle.
			app.board.marks.values[index]=4 if value==1 else 1
			app.board.marks.chunks[index/64].queue_redraw()
			await settle()
			check(difference(capture(box),end)>1.0,"negative: stale color/mark detected")
			app.board.marks.sync()
			await settle()
			check(difference(capture(box),end)<=1.0,"cache repairs from confirmed model")
			if zoom==18 and value==1:
				var color: String = app.session.definition.palette[0].color
				var variant: int = app.board.marks.variants[index]
				app.session.definition.palette[0].color="#bd604a"
				app.board.queue_redraw()
				await settle()
				check(difference(capture(box),end)>1.0 and app.board.marks.variants[index]==variant,"palette content invalidates colors without changing variant")
				app.session.definition.palette[0].color=color
				app.board.queue_redraw()
				await settle()
				check(difference(capture(box),end)<=1.0,"palette restoration repairs cache")
			if value!=0 and value!=1: continue
			var strip: Image = Image.create(blank.get_width()*9,blank.get_height(),false,Image.FORMAT_RGBA8)
			var column: int = 0
			for elapsed: int in [-1,0,30000,75000,105000,150000,180000,209000,210000]:
				clock_us=1000000+maxi(0,elapsed)
				app.board.effects[index]={"start":1000001 if elapsed<0 else 1000000,"after":value,"seconds":0.210}
				app.board.set_process(true)
				await settle()
				actual=capture(box)
				var expected_image: Image = await expected(blank,box,cell,value,210000 if elapsed<0 else elapsed,0.56 if elapsed<0 else 1.0)
				error=difference(actual,expected_image)
				check(error<=1.0,"regular temporal pixels no underpaint/fade/form jump "+str([zoom,value,elapsed,error]))
				strip.blit_rect(actual,Rect2i(Vector2i.ZERO,actual.get_size()),Vector2i(column*actual.get_width(),0))
				column+=1
				samples.append({"zoom":zoom,"actual_cell":box.size.x,"value":value,"elapsed_us":elapsed,"mean_channel_error":error})
			strip.save_png(output.path_join("runtime-%d-%d.png" % [zoom,value]))
	app.board.animation_clock=Time.get_ticks_usec

func run() -> void:
	output=OS.get_environment("PERF_B_OUTPUT")
	Store.test_root_override=output.path_join("isolated-saves")
	app=load("res://main.tscn").instantiate()
	root.add_child(app)
	root.size=Vector2i(1920,1080)
	await settle()
	app.select_puzzle(1)
	app.open_puzzle()
	await settle()
	app.board.draw.connect(func() -> void: draw_counts[0]+=1)
	app.mini.draw.connect(func() -> void: draw_counts[1]+=1)
	reference=SubViewport.new()
	reference.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(reference)
	background=TextureRect.new()
	reference.add_child(background)
	ink=ReferenceInk.new()
	ink.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	var shader := Shader.new()
	shader.code="shader_type canvas_item; uniform vec4 base_color = vec4(1.0); uniform float opacity = 1.0; void fragment(){vec4 m=texture(TEXTURE,UV); COLOR=vec4(m.r*base_color.rgb+vec3(m.g),m.a*opacity*base_color.a);}"
	var material := ShaderMaterial.new()
	material.shader=shader
	ink.material=material
	reference.add_child(ink)
	identity()
	await structural()
	await lifecycle()
	await pictures()
	var report: Dictionary = {"checks":checks,"failures":failures,"samples":samples,"cycles":cycles,"renderer":RenderingServer.get_video_adapter_name(),"pictures":[]}
	for file: String in DirAccess.get_files_at(output):
		if file.ends_with(".png"): report.pictures.append({"file":file,"sha256":FileAccess.get_sha256(output.path_join(file))})
	FileAccess.open(output.path_join("probe.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t")+"\n")
	print("PERF_B_PROBE_OK checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
