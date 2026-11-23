extends SceneTree
const Definition = preload("res://model/definition.gd")
var failures := 0
var fixture: Dictionary
func check(ok: bool, label: String) -> void:
	print("PASS " if ok else "FAIL: ",label)
	if not ok: failures += 1
func _initialize() -> void:
	fixture = Definition.load_fixture("t01")
	preload("res://tests/sync_cases.gd").run(self)
	quit(0 if failures == 0 else 1)
