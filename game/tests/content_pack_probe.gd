extends SceneTree
## External probe runs against the actual separate Windows PCK, never source fallbacks.
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
var failures: int = 0

func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		push_error(message)

func walk(path: String) -> void:
	var directory: DirAccess = DirAccess.open(path)
	check(directory != null,"PCK directory available")
	if directory == null: return
	for name: String in directory.get_directories():
		if name == ".godot": continue
		check(not name in ["tests","production","input","packages","full_view_study","study","perf_a"],"technical directory in PCK: "+path+name)
		walk(path.path_join(name))
	for name: String in directory.get_files():
		check(not "proof" in name and not name.ends_with(".zip") and not name in ["handoff.json","inventory.json","approval.json","derivation.json","inspection.json","categories.json"],"technical file in PCK: "+name)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	walk("res://")
	var ids: Array[String] = Registry.catalog_ids()
	# Fixed shared KB resources, independent of the growing puzzle catalog.
	var book_manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/manifest.json"))
	var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
	check(icons.size() == 13 and icons.has("play") and icons.has("reset"), "PCK active KB icon inventory")
	for name: String in ["play","reset"]:
		var texture: Texture2D = load("res://art/book/"+name+".svg")
		check(texture != null and texture.get_size() == Vector2(26,26), "PCK imported KB icon available "+name)
		var bound: bool = false
		for entry: Dictionary in book_manifest.files:
			if entry.file == name+".svg": bound = true
		check(bound, "PCK icon bound to resource manifest "+name)
	check(FileAccess.file_exists("res://art/book/KB-168-NOTICE.txt"), "PCK KB icon provenance notice")
	# Actual exported font bytes/role, with controlled local fallbacks.
	var ui_text = load("res://ui/ui_text.gd")
	var normal: FontFile = ui_text.font()
	check(normal.data == ui_text.SOURCE.data and not normal.allow_system_fallback, "PCK HZ original Tidy Hand/local role")
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(normal.data)
	check(hash.finish().hex_encode() == "9eacc0d857ab9decbc34b0dab150641ba5b5a9560a8d163b6494dd5babbcdfd6", "PCK HZ Tidy Hand bytes")
	check(normal.fallbacks.size() == 1 and normal.fallbacks[0].get_font_name() == "IBM Plex Sans" and not normal.fallbacks[0].allow_system_fallback, "PCK HZ bundled fallback")
	check(FileAccess.file_exists("res://art/drawing/tidy-hand/NOTICE.txt"), "PCK HZ source and usage permission")
	check(Registry.load_error.is_empty(), "PCK registry/category format invalid")
	var categories: Array[Dictionary] = Registry.categories()
	check(not categories.is_empty(), "PCK categories projection missing")
	var category_ids: Array[String] = []
	for category: Dictionary in categories:
		category_ids.append(category.id)
	# Fixed runtime-contract samples; never extend this set when adding content.
	for key: String in ["t01", "t02", "t04", "t06", "t08", "t09", "pz-test-direct-mono", "pz-test-direct-color", "pz-test-repair-mono", "pz-test-repair-color"]:
		if not key in ids: continue
		var entry: Dictionary = Registry.by_key(key)
		check(entry.category_id in category_ids, "PCK category assignment missing " + key)
		check(not Definition.load_fixture(key).is_empty(),"PCK definition missing "+key)
		check(Definition.validate(Definition.load_fixture(key)).is_empty(),"PCK content invalid "+key)
		if key.begins_with("pz-"):
			check(FileAccess.file_exists("res://"+str(entry.reveal).get_basename()+".txt"),"PCK usage notice missing")
	check(ids.size() == int(OS.get_environment("ZA1_PACK_COUNT")),"PCK selection count")
	if failures == 0: print("CONTENT_PACK_OK count=",ids.size())
	quit(0 if failures == 0 else 4)
