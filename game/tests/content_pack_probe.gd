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
