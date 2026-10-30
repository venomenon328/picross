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
	if expected:
		for resource: String in ["res://study/book/main.gd", "res://study/book/content.gd", "res://study/book/page.gdshader", "res://study/book/material.gdshader", "res://ui/main.gd"]:
			check(ResourceLoader.exists(resource), "study dependency present " + resource)
		var actual_script: Script = load("res://study/book/main.gd")
		check(actual_script != null and actual_script.can_instantiate(), "actual packed study compiles with its dependencies")
		check(ProjectSettings.get_setting("application/run/main_scene") == "res://study/book/main.tscn", "separate study startup")
		check(not FileAccess.file_exists("res://data/registry.json"), "no real catalog in study")
		check(not DirAccess.dir_exists_absolute("res://art/content"), "no real reveals in study")
		check(not ResourceLoader.exists("res://study/book/verify.gd") and not ResourceLoader.exists("res://study/book/pack_probe.gd"), "no verification programs in study pack")
		var input: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://study/book/fixtures.json"))
		check(input.definitions.size() == 3, "bounded synthetic input")
		for data: Dictionary in input.definitions:
			check(ResourceLoader.exists(data.reveal.image), "fixed synthetic sentinel bundled")
	print("BOOK_PACK_OK expected_study=", expected, " failures=", failures.size())
	quit(0 if failures.is_empty() else 4)
