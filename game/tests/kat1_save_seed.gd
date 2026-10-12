extends SceneTree
## TEST ONLY: run against the bound pre-KAT-1 checkout to create compatibility inputs.
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")

func _initialize() -> void:
	var path: String = OS.get_environment("KAT1_SEED_OUTPUT")
	if path.is_empty():
		quit(4)
		return
	var store: Store = Store.new(path)
	for key: String in ["f01", "f02"]:
		var session: Session = Session.new(Definition.load_fixture(key))
		if key == "f01":
			session.gesture.begin(session.player, Vector2i(4, 3), 1)
			session.finish()
			session.gesture.begin(session.player, Vector2i(5, 3), 0)
			session.finish()
			session.undo()
		else:
			for y: int in range(session.player.height):
				for x: int in range(session.player.width):
					var value: int = int(session.definition.solution[y][x])
					if value > 0:
						session.gesture.begin(session.player, Vector2i(x, y), value)
						session.finish()
		var error: String = store.write_slot(session, session.view_state)
		if not error.is_empty() or session.completed != (key == "f02"):
			push_error(error)
			quit(4)
			return
	print("KAT1_LEGACY_SAVES_OK")
	quit(0)
