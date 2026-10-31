extends SceneTree
## External script probes only the ACTUAL pack, without source project fallback.
var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	if not ok: failures.append(label); print("BOOK_PACK_FAIL ", label)

func _initialize() -> void: call_deferred("run")

func run() -> void:
	var expected: bool = OS.get_environment("BOOK_EXPECT_STUDY") == "1"
	check(ResourceLoader.exists("res://study/book/main.tscn") == expected, "study entry point inclusion/exclusion")
	check(FileAccess.file_exists("res://study/book/fixtures.json") == expected, "study inputs inclusion/exclusion")
	check(ResourceLoader.exists("res://study/book/paper.png") == expected,"organic paper inclusion/exclusion")
	check(ResourceLoader.exists("res://study/book/inputs.gd") == expected,"study adapter inclusion/exclusion")
	for key: String in ["t01","t06","t08"] + Array(range(13,37)).map(func(i: int) -> String: return "t%02d" % i):
		check(FileAccess.file_exists("res://study/book/data/"+key+".json") == expected,"definition instance inclusion/exclusion "+key)
		check(ResourceLoader.exists("res://study/book/art/"+key+".svg") == expected,"reveal instance inclusion/exclusion "+key)
	if expected:
		for resource: String in ["res://study/book/main.gd", "res://study/book/content.gd", "res://study/book/catalog.gd", "res://study/book/page.gdshader", "res://study/book/material.gdshader", "res://ui/main.gd"]:
			check(ResourceLoader.exists(resource), "study dependency present " + resource)
		var actual_script: Script = load("res://study/book/main.gd")
		check(actual_script != null and actual_script.can_instantiate(), "actual packed study compiles with its dependencies")
		check(ProjectSettings.get_setting("application/run/main_scene") == "res://study/book/main.tscn", "separate study startup")
		check(not FileAccess.file_exists("res://data/registry.json"), "no real catalog in study")
		check(not DirAccess.dir_exists_absolute("res://art/content"), "no real reveals in study")
		check(not ResourceLoader.exists("res://study/book/verify.gd") and not ResourceLoader.exists("res://study/book/pack_probe.gd"), "no verification programs in study pack")
		var input: Dictionary = load("res://study/book/inputs.gd").read()
		check(input.error.is_empty(),"normal validators accept packed study instances")
		check(input.definitions.size() == 27 and input.registry.entries.size() == 27, "bounded synthetic input")
		for data: Dictionary in input.definitions:
			check(ResourceLoader.exists(data.reveal.image), "fixed synthetic sentinel bundled")
	print("BOOK_PACK_OK expected_study=", expected, " failures=", failures.size())
	quit(0 if failures.is_empty() else 4)
