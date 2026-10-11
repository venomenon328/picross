extends RefCounted
const Runtime = preload("res://ui/cell_atlas.gd")

static func run(t: SceneTree) -> void:
	# Golden identities calculated independently with Python hashlib.
	var golden: Array = [7,0,14,8,2,2,7,3]
	for x: int in range(golden.size()):
		t.check(Runtime.variant("F-02",2,Vector2i(x,0))==golden[x],"PERF-B stable golden cell identity")
	var selected: Dictionary = {}
	for y: int in range(40):
		for x: int in range(40): selected[Runtime.variant("F-02",2,Vector2i(x,y))]=true
	t.check(selected.size()==16,"PERF-B dense load uses every variant")
	for sample: Array in [[-1,0],[0,0],[9130,0],[9131,1],[105000,11],[209999,22],[210000,23],[900000,23]]:
		t.check(Runtime.frame(sample[0])==sample[1],"PERF-B elapsed-time golden frames")
	for sample: Array in [[17.99,"small"],[18.0,"medium"],[36.0,"medium"],[36.01,"large"]]:
		t.check(Runtime.level(sample[0])==sample[1],"PERF-B detail boundaries")
	for sample: Array in [["small",32,16.0],["medium",64,24.0],["large",96,72.0]]:
		var lod: String = sample[0]
		var pitch: int = sample[1]+4
		t.check(Runtime.region(lod,0,23)==Rect2(23*pitch+2,2,sample[1],sample[1]),"PERF-B exact final frame region")
		t.check(Runtime.region(lod,1,0)==Rect2(2,pitch+2,sample[1],sample[1]),"PERF-B padded variant row")
		var cell := Rect2(13.3,29.1,26.77,26.77)
		var mapped: Rect2 = Runtime.mapped_box(cell,lod)
		var scale: float = (26.77-4)/(sample[2]-4)
		var expected := Rect2(cell.position+Vector2.ONE*(2-2*scale),Vector2.ONE*sample[2]*scale)
		t.check(mapped.is_equal_approx(expected),"PERF-B independent nonintegral interior mapping")
