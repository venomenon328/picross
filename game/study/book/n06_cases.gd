extends RefCounted
## Render the production mesh and vertex shader, replacing only the fragment
## output with depth bands. The wide-gap and flat-sheet mutants must fail.
var p: SceneTree

func metrics(image: Image) -> Dictionary:
	var gap: int = 0
	for x: int in range(300,340):
		var c: Color = image.get_pixel(x,64)
		if c.r > 0.9 and c.b > 0.9 and c.g < 0.1: gap += 1
	var shoulders: bool = true
	var flat: bool = true
	for x: int in [230,409]: shoulders = shoulders and image.get_pixel(x,64).r > 0.9
	for x: int in [48,312,327,591]:
		var c: Color = image.get_pixel(x,64)
		flat = flat and c.g > c.r*1.5 and c.g > c.b*1.5
	return {"gap_pixels":gap,"raised_shoulders":shoulders,"low_valley_flat_outer":flat,"accepted":gap <= 3 and shoulders and flat}

func run(proof: SceneTree) -> Dictionary:
	p = proof
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640,128)
	viewport.own_world_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	p.root.add_child(viewport)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color.MAGENTA
	viewport.add_child(environment)
	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 0.4
	camera.position.z = 20
	viewport.add_child(camera)
	var source: String = FileAccess.get_file_as_string("res://study/book/page.gdshader")
	source = source.left(source.find("void fragment()"))
	source = source.replace("varying vec2 original;","varying float measured_z;\nvarying vec2 original;")
	source = source.replace("NORMAL = paper_normal;","NORMAL = paper_normal; measured_z = VERTEX.z;")
	source += "void fragment() { ALBEDO = measured_z > 0.12 ? vec3(1.0) : vec3(0.1,0.6,0.1); }"
	var materials: Array[ShaderMaterial] = []
	for side: float in [-1,1]:
		var material := ShaderMaterial.new()
		material.shader = Shader.new()
		material.shader.code = source
		material.set_shader_parameter("side",side)
		var sheet: MeshInstance3D = p.study._page(material)
		sheet.reparent(viewport,false)
		materials.append(material)
	var rows: Array = []
	for label: String in ["rest","landed","wide-gap","flat-sheet"]:
		var shader := Shader.new()
		shader.code = source
		if label == "wide-gap": shader.code = source.replace("d+0.004*","d+0.035*")
		if label == "flat-sheet": shader.code = source.replace("vec2 fold = fold_profile(d);","vec2 fold = vec2(0.0);")
		for material: ShaderMaterial in materials:
			material.shader = shader
			material.set_shader_parameter("turn",1.0 if label == "landed" else 0.0)
		await p.frames(3)
		var image: Image = viewport.get_texture().get_image()
		var row: Dictionary = metrics(image)
		row["case"] = label
		row["file"] = "fold-depth-"+label+".png"
		p.check(image.save_png(p.output.path_join(row.file)) == OK,"N06 depth original "+label)
		p.check(row.accepted == (label in ["rest","landed"]),"N06 actual vertex depth counterprobe "+label)
		rows.append(row)
	viewport.queue_free()
	await p.frames()
	# Check the actual binding arrays: the leather top is a ruled joint, not a
	# coplanar decoration; paper blocks and cover retain positive clearance.
	var holder := Node3D.new()
	var binding = p.study.Binding.new()
	binding.build(holder)
	var top: PackedVector3Array = holder.get_child(1).mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var low: float = INF
	var high: float = -INF
	for point: Vector3 in top:
		low = minf(low,point.z)
		high = maxf(high,point.z)
	var clearance: float = INF
	for side: float in [-1,1]:
		var block: PackedVector3Array = binding.block_ring(side,1)
		for point: Vector3 in block:
			# Use the cover's sampled strip, not a second call to its height helper.
			for i: int in range(0,top.size()-2,2):
				var a: Vector3 = top[i]
				var b: Vector3 = top[i+2]
				if point.x >= a.x and point.x <= b.x and b.x > a.x:
					var cover_z: float = lerpf(a.z,b.z,(point.x-a.x)/(b.x-a.x))
					clearance = minf(clearance,point.z-cover_z)
	var counts: Dictionary = binding.report()
	p.check(high-low > 0.30,"N06 structural leather joint depth")
	p.check(clearance > 0.005,"N06 block clears actual leather strips")
	p.check(counts.vertices <= 8511 and counts.triangles <= 16262 and counts.surfaces <= 6,"N06 existing binding budgets")
	holder.free()
	return {"depth_cases":rows,"joint_depth":high-low,"minimum_cover_clearance":clearance,"binding":counts}
