extends RefCounted
const Atlas = preload("res://perf_a/atlas.gd")

static func run(t: SceneTree) -> void:
	# Golden identities calculated independently with Python hashlib.
	var golden: Array = [7,0,14,8,2,2,7,3]
	for x: int in range(golden.size()):
		t.check(Atlas.variant("F-02",2,Vector2i(x,0))==golden[x],"PERF-A stable golden cell identity")
	var selected: Dictionary={}
	for y: int in range(40):
		for x: int in range(40): selected[Atlas.variant("F-02",2,Vector2i(x,y))]=true
	t.check(selected.size()==16,"PERF-A dense load uses every variant")
	for sample: Array in [[-1,0],[0,0],[9130,0],[9131,1],[105000,11],[209999,22],[210000,23],[900000,23]]:
		t.check(Atlas.frame(sample[0])==sample[1],"PERF-A time index skips dropped frames and clamps end")
	for lod: String in ["small","medium","large"]:
		var a: Rect2=Atlas.region(lod,0,23)
		var b: Rect2=Atlas.region(lod,1,0)
		t.check(a.position.y==2 and b.position.x==2 and b.position.y-a.end.y==4,"PERF-A frame padding and variant row")
		var cell: Rect2=Rect2(13.3,29.1,26.77,26.77)
		var mapped: Rect2=Atlas.mapped_box(cell,lod)
		var source_inset: float=2.0/Atlas.logical(lod)*mapped.size.x
		t.check(absf(mapped.position.x+source_inset-cell.position.x-2)<0.00001,"PERF-A true interior maps to two-pixel gap")
