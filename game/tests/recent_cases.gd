extends RefCounted
const Recent = preload("res://model/recent_puzzle.gd")

static func raw(path: String, text: String) -> void:
	var file := FileAccess.open(path,FileAccess.WRITE)
	file.store_string(text)
	file.close()

static func run(probe) -> void:
	var app = probe.app
	var path: String = app.store.root.path_join("recent-tests/recent-puzzle.json")
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var marker := Recent.new(path)
	marker.load_record()
	probe.check(marker.record.is_empty() and not FileAccess.file_exists(path),"K-B missing marker load has no write")
	var valid: String = '{"format":"picross-recent-puzzle-v1","id":"pz-test-kat2-001","revision":1}'
	for invalid: String in ["", "null", "[]", valid+"x", valid.replace('"revision":1','"revision":0'),valid.replace('"revision":1','"revision":1.5'),valid.replace('"revision":1','"revision":true'),valid.replace('"revision":1','"revision":"1"'),valid.replace('"revision":1','"revision":1,"x":2'),valid.replace('"revision":1','"id":"x"'),valid.replace('"revision":1','"i\\u0064":"x"'),valid.replace('v1','v2'),valid.replace('"revision":1','"revision":{}'),valid+" ".repeat(1024)]:
		raw(path,invalid)
		marker.load_record()
		probe.check(marker.record.is_empty() and FileAccess.get_file_as_string(path) == invalid,"K-B invalid bytes ignored without rewrite")
	probe.check(Recent.decode(valid.to_utf8_buffer()).revision == 1,"K-B exact format accepted")
	var first = app.Session.new(app.sessions[1].definition)
	var second = app.Session.new(app.sessions[3].definition)
	first.player.commit([{"index":0,"before":-1,"after":1}])
	second.player.commit([{"index":0,"before":-1,"after":0}])
	probe.check(marker.edited(first),"K-B real Windows atomic initial publication")
	var original: PackedByteArray = FileAccess.get_file_as_bytes(path)
	for step: String in ["open","after_temp","replace"]:
		marker.fail_step = step
		probe.check(not marker.edited(second) and FileAccess.get_file_as_bytes(path) == original,"K-B "+step+" keeps previous valid bytes")
		var restart := Recent.new(path)
		restart.load_record()
		probe.check(restart.record.id == first.definition.id,"K-B interrupted temp never becomes startup marker")
	marker.fail_step = ""
	probe.check(marker.retry() and marker.record.id == second.definition.id,"K-B explicit replacement retry publishes latest candidate")
	probe.check(marker.clear_matching(str(first.definition.id)) and marker.record.id == second.definition.id,"K-B foreign reset leaves marker")
	marker.fail_step = "delete"
	original = FileAccess.get_file_as_bytes(path)
	probe.check(not marker.clear_matching(str(second.definition.id)) and FileAccess.get_file_as_bytes(path) == original,"K-B failed deletion reported and old bytes retained")
	marker.fail_step = ""
	probe.check(marker.retry() and not FileAccess.file_exists(path),"K-B deletion retry")
	probe.check(marker.edited(first),"K-B marker restored")
	var items: Dictionary = {str(first.definition.id):first}
	var statuses: Dictionary = {str(first.definition.id):"loaded"}
	probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B canonical ID resolution")
	for status: String in ["recovered","backup_invalid"]:
		statuses[first.definition.id] = status
		probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B valid reconstructed progress retains recovery route")
	statuses[first.definition.id] = "error"
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B invalid slot hidden")
	statuses[first.definition.id] = "loaded"
	marker.record.revision += 1
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B stale revision hidden")
	marker.record.revision -= 1
	probe.check(marker.resolve({},statuses).is_empty(),"K-B hidden/deleted/foreign ID has no fallback")
	first.player.undo()
	probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B redo-only remains begun")
	first.completed = true
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B completion immediately hides offer")
	first.completed = false
	# Restore these synthetic sessions before exercising the actual app boundary.
	app.sessions[1] = app.Session.new(first.definition)
	app.sessions[3] = app.Session.new(second.definition)
	app.select_puzzle(1)
	await probe.frames()
	app.recent.clear_matching(app.recent.record.get("id",""))
	app._save_current()
	probe.check(app.recent.record.is_empty(),"K-B view-only save never marks")
	app.store.fail_step = "after_temp"
	app.session.gesture.begin(app.session.player,Vector2i.ZERO,1)
	app.session.finish()
	app._on_commit()
	probe.check(app.recent.record.is_empty() and app.pending_edits.has(app.session.definition.id),"K-B failed action save retains its reason")
	app.store.fail_step = ""
	probe.check(app._save_current() and app.recent_id() == app.session.definition.id and app.pending_edits.is_empty(),"K-B explicit save retry completes action reason")
	var id: String = app.recent_id()
	app._undo()
	probe.check(app.recent_id() == id and app.session.player.cursor == 0,"K-B real Undo updates begun redo-only marker")
	app._redo()
	probe.check(app.recent_id() == id and app.session.player.cursor == 1,"K-B real Redo updates marker")
	app.show_album()
	app.album.apply_filters("solved","all",0,0,"","")
	await probe.frames()
	probe.check(not app.album.filtered_ids.has(id) and app.recent_panel.visible,"K-B recent offer independent of excluding filters")
	var positions: Vector2i = app.album.positions()
	var filters: Dictionary = app.album.filters.duplicate()
	probe.click(app.recent_panel)
	await probe.frames()
	probe.check(app.work.visible and app.session.definition.id == id,"K-B actual panel pointer opens canonical ID")
	probe.click(app.album_button)
	await probe.frames()
	probe.check(app.album.filters == filters and app.album.positions() == positions,"K-B return preserves filter and both scrolls")
	app._ask_reset_id(id)
	await probe.frames()
	probe.click(app.reset_dialog.get_ok_button())
	await probe.frames()
	probe.check(app.recent_id().is_empty() and not app.recent_panel.visible,"K-B reset removes marker and panel")
	app.album.reset_filters()
	probe.catalog_case("k-b-recent")
