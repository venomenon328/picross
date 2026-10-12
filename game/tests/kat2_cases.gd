extends RefCounted
const Catalog = preload("res://ui/catalog.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")

static func run(runner: SceneTree) -> void:
	var item: Session = Session.new(Definition.load_f01())
	runner.check(Catalog.progress(item) == "Neu", "KAT2 empty validated state is new")
	item.player.commit([{"index": 0, "before": -1, "after": 0}])
	runner.check(Catalog.progress(item) == "Begonnen", "KAT2 X-only progress is begun")
	item.undo()
	runner.check(item.player.cursor == 0 and Catalog.progress(item) == "Begonnen", "KAT2 redo-only history remains begun")
	runner.check(item.reveal().is_empty() and item.album_title() == item.neutral_title(), "KAT2 unfinished labels reveal no motif")
	item = Session.new(Definition.load_f01())
	runner.check(Catalog.progress(item) == "Neu", "KAT2 reset state returns to new")
