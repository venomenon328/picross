extends SceneTree
## Existing complete save/recovery suite against the isolated extended registry.
const Store = preload("res://model/save_store.gd")
const Cases = preload("res://tests/p13_cases.gd")
var checks: int = 0
var failures: int = 0

func check(ok: bool, description: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error(description)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if Store.test_root_override.is_empty(): quit(4); return
	root.size = Vector2i(1920,1080)
	await Cases.run(self)
	print("ZA1_SAVE_RESULT checks=",checks," failures=",failures)
	if failures == 0: print("ZA1_SAVE_OK")
	quit(0 if failures == 0 else 4)
