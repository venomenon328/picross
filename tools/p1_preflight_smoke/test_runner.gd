extends SceneTree


func _initialize() -> void:
	if OS.get_environment("P1_PREFLIGHT_FORCE_FAILURE") == "1":
		print("P1_PREFLIGHT_EXPECTED_FAILURE")
		quit(23)
		return
	print("P1_PREFLIGHT_TEST_OK")
	quit(0)
