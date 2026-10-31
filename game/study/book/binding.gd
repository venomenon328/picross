extends RefCounted
## Joined study surfaces. The block crown follows page.gdshader's resting arch.
const MATERIAL = preload("res://study/book/material.gdshader")
const LEATHER = preload("res://study/book/leather.png")
var vertices: int = 0
var triangles: int = 0
var surfaces: int = 0

func material(kind: float, color: Color) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = MATERIAL
	result.set_shader_parameter("kind",kind)
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
	for i: int in range(65): perimeter.append(Vector2(10.0-i*10.0/64,6.2))
	for i: int in range(1,17): perimeter.append(Vector2(0,6.2-i*12.4/16))
	for i: int in range(1,65): perimeter.append(Vector2(i*10.0/64,-6.2))
	for i: int in range(1,16): perimeter.append(Vector2(10,-6.2+i*12.4/16))
	for p: Vector2 in perimeter:
		var arch: float = pow(1.0-clampf(p.x/0.75,0,1),2)
		var x: float = p.x+0.035*arch+depth*0.13*(p.x/10.0)
		var y: float = p.y*(1.0-0.012*arch)+signf(p.y)*depth*0.16
		var z: float = 0.26*pow(arch,1.5)*(1.0-depth*0.35)-depth*0.43-0.006
		var uneven: float = sin(p.x*11.7+p.y*8.3+depth*77)*0.004*sin(depth*PI)
		ring.append(Vector3(side*(x+uneven),y+uneven,z))
	if side < 0: ring.reverse()
	return ring

func build(parent: Node3D) -> void:
	var leather: ShaderMaterial = material(0,Color.WHITE)
	var edges: ShaderMaterial = material(1,Color("e2d5b9"))
	for side: float in [-1.0,1.0]:
		var rect := Rect2(0 if side > 0 else -10.43,-6.55,10.43,13.10)
		var covers: Array = []
		for profile: Vector2 in [Vector2(0.09,-0.45),Vector2(0.025,-0.47),Vector2(0,-0.53),Vector2(0.015,-0.63),Vector2(0.065,-0.68)]:
			covers.append(rounded(rect.grow(-profile.x),0.17,profile.y))
		mesh(parent,covers,leather,true)
		var block: Array = []
		for i: int in range(25): block.append(block_ring(side,i/24.0))
		mesh(parent,block,edges)
	# Narrow flexible binding, with rounded ends, seated below the paper crown.
	var spine: Array = []
	for profile: Vector2 in [Vector2(0.025,0.225),Vector2(0.0,0.18),Vector2(-0.06,-0.12),Vector2(-0.25,-0.50)]:
		spine.append(rounded(Rect2(-0.075,-6.30,0.15,12.60).grow(-profile.x),0.025,profile.y))
	mesh(parent,spine,leather,true)
	# Sewn head/tail bands follow the crown; no painted-on book edges.
	for end: float in [-1.0,1.0]:
		for i: int in range(23):
			var x: float = (i-11)*0.027
			var z: float = 0.26*pow(1.0-absf(x)/0.75,3)-0.09
			var y: float = end*(6.18+absf(x)*0.10)
			var thread: Array = [rounded(Rect2(x-0.010,y-0.031,0.020,0.062),0.009,z),rounded(Rect2(x-0.012,y-0.034,0.024,0.068),0.010,z-0.025)]
			mesh(parent,thread,material(3,Color("c4ac7f") if i%3 else Color("6e6551")),true)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.orientation = PlaneMesh.FACE_Z
	plane.size = Vector2(80,50)
	ground.mesh = plane
	ground.position.z = -0.72
	ground.material_override = material(2,Color("554b3f"))
	parent.add_child(ground)

func report() -> Dictionary:
	return {"surfaces":surfaces+1,"vertices":vertices+4,"triangles":triangles+2,"leather_rgba_bytes":1254*1254*4,"leather_with_mipmaps_upper_bytes":1254*1254*4*4/3}
