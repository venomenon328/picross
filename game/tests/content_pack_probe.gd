extends SceneTree
## External probe runs against the actual embedded Windows PCK, never source fallbacks.
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
		check(not "proof" in name and not name in ["handoff.json","inventory.json","approval.json","derivation.json"],"technical file in PCK: "+name)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	walk("res://")
	var ids: Array[String] = Registry.catalog_ids()
	for key: String in ids:
		var entry: Dictionary = Registry.by_key(key)
		check(not Definition.load_fixture(key).is_empty(),"PCK definition missing "+key)
		check(Definition.validate(Definition.load_fixture(key)).is_empty(),"PCK content invalid "+key)
		if key.begins_with("pz-"):
			check(FileAccess.file_exists("res://"+str(entry.reveal).get_basename()+".txt"),"PCK usage notice missing")
	for key: String in ["f03","f05","f07"]:
		check(not FileAccess.file_exists("res://data/"+key+".json"),"reserved definition exported")
	check(ids.size() == int(OS.get_environment("ZA1_PACK_COUNT")),"PCK selection count")
	if failures == 0: print("CONTENT_PACK_OK count=",ids.size())
	quit(0 if failures == 0 else 4)
