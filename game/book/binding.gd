extends RefCounted
## Joined study surfaces. The block crown follows page.gdshader's resting arch.
const MATERIAL = preload("res://book/material.gdshader")
const LEATHER = preload("res://book/leather.png")
const TABLE = preload("res://book/table.png")
var vertices: int = 0
var triangles: int = 0
var surfaces: int = 0

static func column(index: int) -> float:
	# Resolve the narrow valley without increasing the existing mesh budget.
	return index*0.75/16.0 if index <= 16 else 0.75+(index-16)*9.25/48.0

static func fold_height(d: float) -> float:
	# Same two C1-continuous shoulders as fold.gdshaderinc; flat UI starts at .75.
	return 0.22*smoothstep(0,0.28,d) if d < 0.28 else 0.22*(1.0-smoothstep(0.28,0.75,d))

static func hinge_height(x: float) -> float:
	x = absf(x)
	if x < 0.16: return lerpf(0.25,0.20,smoothstep(0,0.16,x))
	if x < 0.30: return lerpf(0.20,0.02,smoothstep(0.16,0.30,x))
	if x < 0.42: return lerpf(0.02,-0.06,smoothstep(0.30,0.42,x))
	if x < 0.60: return lerpf(-0.06,-0.01,smoothstep(0.42,0.60,x))
	return lerpf(-0.01,0,smoothstep(0.60,0.75,x))

func material(kind: float, color: Color) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = MATERIAL
	result.set_shader_parameter("kind",kind)
	if kind == 2: result.set_shader_parameter("table_source",TABLE)
	result.set_shader_parameter("base_color",color)
	result.set_shader_parameter("leather_source",LEATHER)
	return result

func mesh(parent: Node3D, rings: Array, mat: Material, cap: bool = false) -> void:
	var positions := PackedVector3Array()
	var normals := PackedVector3Array()
	var indices := PackedInt32Array()
	var count: int = rings[0].size()
	for row: int in range(rings.size()):
		for col: int in range(count):
			var tangent: Vector3 = rings[row][(col+1)%count]-rings[row][(col+count-1)%count]
			var radial: Vector3 = rings[mini(row+1,rings.size()-1)][col]-rings[maxi(row-1,0)][col]
			positions.append(rings[row][col])
			normals.append(radial.cross(tangent).normalized())
			if row < rings.size()-1:
				var i: int = row*count+col
				var next: int = row*count+(col+1)%count
				indices.append_array([i,next,i+count,next,next+count,i+count])
	if cap:
		var center := Vector3.ZERO
		for p: Vector3 in rings[0]: center += p/count
		var index: int = positions.size()
		positions.append(center)
		normals.append(Vector3.BACK)
		for col: int in range(count): indices.append_array([index,col,(col+1)%count])
	add_surface(parent,positions,normals,indices,mat)

func add_surface(parent: Node3D, positions: PackedVector3Array, normals: PackedVector3Array, indices: PackedInt32Array, mat: Material) -> void:
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = positions
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	var surface := ArrayMesh.new()
	surface.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var instance := MeshInstance3D.new()
	instance.mesh = surface
	instance.material_override = mat
	parent.add_child(instance)
	vertices += positions.size()
	triangles += indices.size()/3
	surfaces += 1

func cover(parent: Node3D, mat: Material) -> void:
	# One continuous shaped cover, including both joints and the spine. No band
	# placed over the leather, separate coplanar caps, or intersecting end threads.
	var rings: Array = []
	var hinge_x: Array[float] = [0.75,0.60,0.51,0.42,0.36,0.30,0.23,0.16,0.08,0.0,-0.08,-0.16,-0.23,-0.30,-0.36,-0.42,-0.51,-0.60,-0.75]
	for profile: Vector2 in [Vector2(0.09,-0.45),Vector2(0.025,-0.47),Vector2(0,-0.53),Vector2(0.015,-0.63),Vector2(0.065,-0.68)]:
		var ring := PackedVector3Array()
		var edge: PackedVector3Array = rounded(Rect2(-10.43,-6.55,20.86,13.10).grow(-profile.x),0.17,profile.y)
		for i: int in range(edge.size()):
			ring.append(edge[i])
			if i == 8:
				for x: float in hinge_x: ring.append(Vector3(x,6.55-profile.x,profile.y))
			elif i == 26:
				for j: int in range(hinge_x.size()-1,-1,-1): ring.append(Vector3(hinge_x[j],-6.55+profile.x,profile.y))
		for i: int in range(ring.size()): ring[i].z += hinge_height(ring[i].x)
		rings.append(ring)
	mesh(parent,rings,mat)
	# The top uses matching ruled strips, not a fan that flattens the joints.
	var top: Array[Vector3] = []
	for point: Vector3 in rings[0]:
		if point.y > 0: top.append(point)
	top.sort_custom(func(a: Vector3,b: Vector3) -> bool: return a.x < b.x)
	var positions := PackedVector3Array()
	var normals := PackedVector3Array()
	var indices := PackedInt32Array()
	for i: int in range(top.size()):
		var point: Vector3 = top[i]
		var slope: float = (hinge_height(point.x+0.001)-hinge_height(point.x-0.001))/0.002
		positions.append_array([point,Vector3(point.x,-point.y,point.z)])
		normals.append_array([Vector3(-slope,0,1).normalized(),Vector3(-slope,0,1).normalized()])
		if i < top.size()-1:
			var n: int = i*2
			indices.append_array([n,n+1,n+2,n+1,n+3,n+2])
	add_surface(parent,positions,normals,indices,mat)

func rounded(rect: Rect2, radius: float, z: float) -> PackedVector3Array:
	var ring := PackedVector3Array()
	var p: Vector2 = rect.position
	var e: Vector2 = rect.end
	var centers: Array[Vector2] = [e-Vector2(radius,radius),Vector2(p.x+radius,e.y-radius),p+Vector2(radius,radius),Vector2(e.x-radius,p.y+radius)]
	for corner: int in range(4):
		for step: int in range(9):
			var angle: float = (corner+step/8.0)*PI/2
			var point: Vector2 = centers[corner]+Vector2(cos(angle),sin(angle))*radius
			ring.append(Vector3(point.x,point.y,z))
	return ring

func block_ring(side: float, depth: float) -> PackedVector3Array:
	var ring := PackedVector3Array()
	var perimeter: Array[Vector2] = []
	for i: int in range(65): perimeter.append(Vector2(column(64-i),6.2))
	for i: int in range(1,17): perimeter.append(Vector2(0,6.2-i*12.4/16))
	for i: int in range(1,65): perimeter.append(Vector2(column(i),-6.2))
	for i: int in range(1,16): perimeter.append(Vector2(10,-6.2+i*12.4/16))
	for p: Vector2 in perimeter:
		var arch: float = pow(1.0-clampf(p.x/0.75,0,1),2)
		var crown: float = fold_height(p.x)
		var x: float = p.x+0.004*arch+depth*0.13*(p.x/10.0)
		# Gather the signatures into the joint instead of covering its exposed ends.
		var end_splay: float = lerpf(0.08,0.16,smoothstep(0,0.75,p.x))
		var y: float = p.y*(1.0-0.004*crown/0.22)+signf(p.y)*depth*end_splay
		var z: float = lerpf(crown-0.006,-0.436+hinge_height(p.x),depth)
		# Broad, shallow deckle keeps the normal field resolved at all three
		# scales; subpixel high-frequency ridges formed diagonal moire patches.
		var uneven: float = sin(p.x*1.7+p.y*0.8+depth*5)*0.0015*sin(depth*PI)*smoothstep(0,0.75,p.x)
		ring.append(Vector3(side*(x+uneven),y+uneven,z))
	if side < 0: ring.reverse()
	return ring

func build(parent: Node3D) -> void:
	var leather: ShaderMaterial = material(0,Color.WHITE)
	var edges: ShaderMaterial = material(1,Color("e2d5b9"))
	cover(parent,leather)
	for side: float in [-1.0,1.0]:
		var block: Array = []
		for i: int in range(25): block.append(block_ring(side,i/24.0))
		mesh(parent,block,edges)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.orientation = PlaneMesh.FACE_Z
	plane.size = Vector2(48,32)
	ground.mesh = plane
	ground.position.z = -0.72
	ground.material_override = material(2,Color("554b3f"))
	parent.add_child(ground)

func report() -> Dictionary:
	return {"surfaces":surfaces+1,"vertices":vertices+4,"triangles":triangles+2,"leather_rgba_bytes":1254*1254*4,"leather_with_mipmaps_upper_bytes":1254*1254*4*4/3,
		"table_size":[TABLE.get_width(),TABLE.get_height()],"table_rgba_bytes":TABLE.get_width()*TABLE.get_height()*4,"table_with_mipmaps_upper_bytes":TABLE.get_width()*TABLE.get_height()*4*4/3}
