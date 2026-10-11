extends SceneTree
## Native resource/color/scale/motion probe, independent of the regular scene.
const Atlas = preload("res://perf_a/atlas.gd")
const Source = preload("res://tests/perf_a_source.gd")
const Store = preload("res://model/save_store.gd")
const Palette = [Color("343f42"), Color("edca78"), Color("bd604a"), Color("6c9aab")]
var output: String
var records: Array = []
var failures: int = 0
var checks: int = 0
var textures: Dictionary = {}
var actual_fits: Array = []
var pictures: Array = []

class Tiles extends Control:
	var texture: Texture2D
	var lod: String
	var kind: String
	var flat: bool = false
	var moving: bool = false
	var cell_size: float = 24.0
	var time_us: int = -1
	var wrong_variant: bool = false
	func _draw() -> void:
		var pitch: int = Atlas.pixels(lod) + 4
		if moving:
			for x: int in range(40):
				var cell: Rect2=Rect2(x*24+2,2,24,24)
				var v: int=Atlas.variant("F-02",2,Vector2i(x,38))
				var local_time: int=time_us-roundi(x*180000.0/39)
				var f: int=23 if local_time<0 else Atlas.frame(local_time)
				# Waiting target is the same endform, reduced to 56% opacity.
				var target: Rect2=Atlas.mapped_box(cell,lod) if kind=="fill" else cell
				draw_texture_rect_region(texture,target,Atlas.region(lod,v,f),Color(1,1,1,0.56 if local_time<0 else 1.0),false,true)
		elif flat:
			for y: int in range(16):
				for x: int in range(16):
					var cell: Rect2 = Rect2(Vector2(x,y)*cell_size+Vector2.ONE*2,Vector2.ONE*cell_size)
					var v: int = Atlas.variant("F-02",2,Vector2i(x,y))
					var f: int = Atlas.FRAMES-1 if time_us<0 else Atlas.frame(time_us-int(x*minf(12000,180000.0/39)))
					var target: Rect2 = Atlas.mapped_box(cell,lod) if kind=="fill" else cell
					draw_texture_rect_region(texture,target,Atlas.region(lod,v,f),Color.WHITE,false,true)
		else:
			for v: int in range(Atlas.VARIANTS):
				for f: int in range(Atlas.FRAMES):
					var source_v: int = (v+1)%Atlas.VARIANTS if wrong_variant else v
					draw_texture_rect_region(texture,Rect2(f*pitch+2,v*pitch+2,Atlas.pixels(lod),Atlas.pixels(lod)),Atlas.region(lod,source_v,f),Color.WHITE,false,true)

func _initialize() -> void: call_deferred("run")

func check(ok: bool, description: String) -> void:
	checks+=1
	if not ok:
		failures+=1
		print("FAIL ",description)

func capture(node: Control, dimensions: Vector2i, name: String) -> Image:
	var surface := SubViewport.new()
	surface.transparent_bg = true
	surface.size = dimensions
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	surface.add_child(node)
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	check(image.save_png(output.path_join(name+".png"))==OK,"save native "+name)
	pictures.append(name+".png")
	surface.queue_free()
	await process_frame
	return image

func tiles(kind: String, lod: String, color: Color, alpha: float = 1.0) -> Tiles:
	var node := Tiles.new()
	node.texture=textures[kind+"-"+lod]
	node.kind=kind
	node.lod=lod
	node.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	node.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
	node.material=Atlas.material(color,alpha)
	return node

func run() -> void:
	output=OS.get_environment("PERF_A_OUTPUT")
	check(DisplayServer.get_name()!="headless","native driver")
	Store.test_root_override=output.path_join("isolated-saves")
	var app: Control=load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	root.mode=Window.MODE_MAXIMIZED
	await create_timer(0.15).timeout
	var largest: float=0
	var smallest: float=72
	for sheet: int in range(app.sessions.size()):
		app.select_puzzle(sheet)
		for scale: float in [1.0,1.25]:
			app.set_ui_scale(scale)
			for mode: String in ["G","V"]:
				app.board.set_mode(mode)
				app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
				app.open_puzzle()
				await process_frame
				largest=maxf(largest,app.board.view.cell_size)
				if app.board.layout_valid: smallest=minf(smallest,app.board.view.cell_size)
				actual_fits.append({"puzzle":app.session.definition.id,"ui":scale,"mode":mode,"actual_cell":app.board.view.cell_size,"client":[root.size.x,root.size.y]})
	app.queue_free()
	await process_frame
	root.mode=Window.MODE_WINDOWED
	root.size=Vector2i(1920,1080)
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PERF_A_ATLAS_PLAN")))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://perf_a/atlases/manifest.json"))
	check(manifest.atlases.size()==6 and manifest.plan.render_version==Atlas.VERSION,"complete bound atlas version")
	for item: Dictionary in manifest.atlases:
		var path: String = "res://perf_a/atlases/"+item.file
		var texture: Texture2D = load(path)
		var image: Image = texture.get_image()
		image.convert(Image.FORMAT_RGBA8)
		var hash := HashingContext.new()
		hash.start(HashingContext.HASH_SHA256)
		hash.update(image.get_data())
		check(hash.finish().hex_encode()==item.pixel_sha256,"actual imported decoded pixels "+item.file)
		check(not image.has_mipmaps(),"no mipmaps "+item.file)
		textures[item.kind+"-"+item.level]=texture
	# Fixed identities and time selection survive fresh processes. Other model
	# operations cannot influence this pure identity function; no Save field added.
	var identities: Array = []
	for y: int in range(40):
		for x: int in range(40): identities.append(Atlas.variant("F-02",2,Vector2i(x,y)))
	check(identities.size()==1600,"every F02 cell identity")
	var identity_path: String=output.path_join("identities.json")
	var restarted: bool=FileAccess.file_exists(identity_path)
	# JSON parses numbers as floats; compare the canonical persisted sequence,
	# not Array equality between differently typed numeric Variants.
	if restarted: check(FileAccess.get_file_as_string(identity_path)==JSON.stringify(identities),"fresh-process variants identical")
	else: FileAccess.open(identity_path,FileAccess.WRITE).store_string(JSON.stringify(identities))
	check(Atlas.frame(-100)==0 and Atlas.frame(0)==0 and Atlas.frame(209999)==22 and Atlas.frame(210000)==23 and Atlas.frame(1000000)==23,"elapsed time including dropped frames")
	check(Atlas.level(17.99)=="small" and Atlas.level(18.0)=="medium" and Atlas.level(72)=="large","LOD boundaries")
	for level: Dictionary in plan.levels:
		var dimensions: Vector2i=Vector2i(24,16)*(int(level.pixels)+4)
		var x_source := Source.Sheet.new()
		var x_harness := Source.SourceBoard.new()
		x_harness.INK=Color("343f42")
		x_source.board=x_harness
		x_source.plan=plan
		x_source.level=level
		x_source.kind="x"
		await capture(x_source,dimensions,"reference-x-"+level.name)
		x_harness.free()
		await capture(tiles("x",level.name,Color("343f42")),dimensions,"color-x-"+level.name)
		for color_index: int in range(4):
			var source := Source.Sheet.new()
			var harness := Source.SourceBoard.new()
			harness.basis=Palette[color_index]
			source.board=harness
			source.plan=plan
			source.level=level
			source.kind="fill"
			await capture(source,dimensions,"reference-%s-%d"%[level.name,color_index])
			harness.free()
			await capture(tiles("fill",level.name,Palette[color_index]),dimensions,"color-%s-%d"%[level.name,color_index])
		# Preview/waiting use the exact same region as resting; only opacity changes.
		await capture(tiles("fill",level.name,Palette[0],0.56),dimensions,"preview-"+level.name)
		var wrong: Tiles=tiles("fill",level.name,Palette[0])
		wrong.wrong_variant=true
		await capture(wrong,dimensions,"wrong-variant-"+level.name)
		if level.name=="medium":
			var tinted: Tiles=tiles("fill",level.name,Palette[0])
			var shader := Shader.new()
			shader.code=Atlas.SHADER.code.replace("base_color.rgb * mask.r + vec3(mask.g)","base_color.rgb * (mask.r + mask.g)")
			tinted.material.shader=shader
			await capture(tinted,dimensions,"wrong-gray-tint")
	var sizes: Array[float]=[8.0,14.81,16.0,17.06,17.99,18.0,18.77,20.0,21.75,24.0,25.71,26.77,36.0,48.0,72.0]
	if not sizes.has(largest): sizes.append(largest)
	if not sizes.has(smallest): sizes.append(smallest)
	for size: float in sizes:
		for kind: String in ["fill","x"]:
			var node: Tiles=tiles(kind,Atlas.level(size),Palette[2] if kind=="fill" else Color("343f42"))
			node.flat=true
			node.cell_size=size
			var name: String="flat-%s-%s"%[kind,str(size)]
			await capture(node,Vector2i.ONE*ceili(size*16+4),name)
			records.append({"size":size,"kind":kind,"lod":Atlas.level(size),"inset":2,"file":name+".png"})
	for kind: String in ["fill","x"]:
		var clipped := Control.new()
		clipped.position=Vector2(11.3,13.7)
		clipped.size=Vector2(91.1,77.2)
		clipped.clip_contents=true
		var child: Tiles=tiles(kind,"medium",Palette[2])
		child.flat=true
		child.cell_size=18.77
		child.position=Vector2(-7.6,-5.2)
		clipped.add_child(child)
		await capture(clipped,Vector2i(120,110),"clipped-"+kind)
	# Real-time native sequence with time-derived indices and 40-cell stagger.
	var motion: Array=[]
	for kind: String in ["fill","x"]:
		for state: String in ["waiting","rest"]:
			var expected: Tiles=tiles(kind,"medium",Palette[2] if kind=="fill" else Color("343f42"))
			expected.moving=true
			expected.time_us=-1 if state=="waiting" else 450000
			await capture(expected,Vector2i(964,28),"motion-%s-%s"%[kind,state])
		var surface := SubViewport.new()
		surface.transparent_bg=true
		surface.size=Vector2i(964,28)
		surface.render_target_update_mode=SubViewport.UPDATE_ALWAYS
		root.add_child(surface)
		var moving: Tiles=tiles(kind,"medium",Palette[2] if kind=="fill" else Color("343f42"))
		moving.moving=true
		moving.cell_size=24
		surface.add_child(moving)
		var started: int=Time.get_ticks_usec()
		while Time.get_ticks_usec()-started<450000:
			moving.time_us=Time.get_ticks_usec()-started
			moving.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			var elapsed: int=moving.time_us
			var name: String="motion-%s-%02d.png"%[kind,motion.size()]
			check(surface.get_texture().get_image().save_png(output.path_join(name))==OK,"save native motion")
			pictures.append(name)
			motion.append({"kind":kind,"elapsed_us":elapsed,"first_frame":Atlas.frame(elapsed),"last_frame":23 if elapsed<180000 else Atlas.frame(elapsed-180000),"last_state":"waiting" if elapsed<180000 else ("active" if elapsed<390000 else "rest"),"file":name})
		surface.queue_free()
		await process_frame
	FileAccess.open(output.path_join("probe.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"failures":failures,"records":records,"pictures":pictures,"platform":OS.get_name(),"actual_fits":actual_fits,"smallest_actual_cell":smallest,"largest_actual_cell":largest,"motion":motion,"fresh_process_compared":restarted,"renderer":RenderingServer.get_current_rendering_driver_name(),"video_adapter":RenderingServer.get_video_adapter_name(),"texture_memory_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"static_memory_bytes":OS.get_static_memory_usage()},"\t"))
	print("PERF_A_ATLAS_PROBE_OK" if failures==0 else "PERF_A_ATLAS_PROBE_FAILED"," checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
