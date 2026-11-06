extends "res://tests/run_tests.gd"
func run() -> void:
	SaveStore.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	root.size = Vector2i(1280,720)
	fixture = Definition.load_fixture("t01")
	await preload("res://tests/p12_cases.gd").run(self)
	await preload("res://tests/z2_cases.gd").run(self)
	finish()
