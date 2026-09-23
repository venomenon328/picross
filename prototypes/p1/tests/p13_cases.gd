extends RefCounted
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const SaveStore = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")

static func run(t: SceneTree) -> void:
	for id: String in SaveStore.IDS:
		var definition: Dictionary = Definition.load_fixture(id)
		var session: Session = Session.new(definition)
		var store: SaveStore = SaveStore.new(SaveStore.test_root_override.path_join(id))
		var fresh: Dictionary = store.load_slot(definition)
		t.check(fresh.status == "fresh", "P1.3 %s isolated fresh slot" % id)
		var first: Dictionary = SaveStore.snapshot(session, session.view_state)
		t.check(SaveStore.validate(first, definition).is_empty(), "P1.3 %s empty save valid" % id)
		t.check(store.write_slot(session, session.view_state).is_empty(), "P1.3 %s empty save written" % id)
		t.check(store.load_slot(definition).status == "loaded" and int(store.load_slot(definition).data.cursor) == 0, "P1.3 %s empty disk roundtrip" % id)
		var action: Array[Dictionary] = [{"index": 0, "before": -1, "after": int(definition.palette[0].id)}]
		t.check(session.player.commit(action), "P1.3 %s first transaction" % id)
		session.completed = session.is_solution()
		t.check(store.write_slot(session, session.view_state).is_empty() and int(store.load_slot(definition).data.cursor) == 1, "P1.3 %s short history disk roundtrip" % id)
		var next: Array[Dictionary] = [{"index": 1, "before": -1, "after": 0}]
		t.check(session.player.commit(next), "P1.3 %s second transaction" % id)
		session.completed = session.is_solution()
		session.undo()
		session.view_state.tool = "hand"
		session.view_state.active_color = int(definition.palette[-1].id)
		session.view_state.zoom = 30
		session.view_state.center = [float(definition.width) * 0.6, float(definition.height) * 0.4]
		var row: int = -1
		var column: int = -1
		for i: int in range(definition.rows.size()):
			if definition.rows[i].size() >= 5:
				row = i
				break
		for i: int in range(definition.columns.size()):
			if definition.columns[i].size() >= 5:
				column = i
				break
		if row >= 0:
			session.view_state.row_clue_reads[row] = {"anchor": "middle", "start": 1, "end": 4}
		if column >= 0:
			session.view_state.column_clue_reads[column] = {"anchor": "outer_start"}
		var current: Dictionary = SaveStore.snapshot(session, session.view_state)
		t.check(SaveStore.validate(current, definition).is_empty(), "P1.3 %s branched history/view valid" % id)
		t.check(store.write_slot(session, session.view_state).is_empty(), "P1.3 %s primary write" % id)
		var loaded: Dictionary = store.load_slot(definition)
		t.check(loaded.status == "loaded" and SaveStore.validate(loaded.data, definition).is_empty() and int(loaded.data.cursor) == 1 and loaded.data.undo_used and loaded.data.view.tool == "hand" and int(loaded.data.view.zoom) == 30, "P1.3 %s complete primary roundtrip" % id)
		var restored: Session = Session.new(definition)
		SaveStore.apply(loaded.data, restored)
		t.check(restored.player.cursor == 1 and restored.player.history.size() == 2 and restored.player.undo_used and restored.player.redo(), "P1.3 %s redo and sticky undo after restore" % id)
		t.check(not restored.completed and restored.reveal().is_empty() and restored.album_title().begins_with("Blatt"), "P1.3 %s unfinished album stays spoiler-free" % id)
		var bad: Dictionary = current.duplicate(true)
		bad.schema = 2
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 unsupported schema rejected")
		bad = current.duplicate(true)
		bad.definition_id = "F-99"
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 definition mismatch rejected")
		bad = current.duplicate(true)
		bad.definition_revision = 999
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 revision mismatch rejected")
		bad = current.duplicate(true)
		bad.cells.pop_back()
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 matrix length rejected")
		bad = current.duplicate(true)
		bad.cells[0] = 999
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 palette value rejected")
		bad = current.duplicate(true)
		bad.history[0].append(bad.history[0][0].duplicate(true))
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 duplicate index rejected")
		bad = current.duplicate(true)
		bad.history[1][0].before = 1
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 redo replay contradiction rejected")
		bad = current.duplicate(true)
		bad.cursor = 2
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 cursor/matrix mismatch rejected")
		bad = current.duplicate(true)
		bad.completed = not bad.completed
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 completion mismatch rejected")
		bad = current.duplicate(true)
		bad.view.zoom = 23
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 invalid zoom rejected")
		bad = current.duplicate(true)
		bad.view.row_clue_reads[0] = {"anchor": "middle", "start": -1, "end": 4}
		t.check(not SaveStore.validate(bad, definition).is_empty(), "P1.3 invalid semantic read rejected")
		# Rotate one valid previous primary, then corrupt the new primary.
		session.redo()
		t.check(store.write_slot(session, session.view_state).is_empty(), "P1.3 %s backup rotation" % id)
		var previous: Dictionary = store._parse(store.path_for(id, ".bak"), definition)
		t.check(previous.status == "valid" and int(previous.data.cursor) == 1 and previous.data.undo_used, "P1.3 %s previous valid backup" % id)
		var file: FileAccess = FileAccess.open(store.path_for(id), FileAccess.WRITE)
		file.store_string("{broken")
		file.close()
		loaded = store.load_slot(definition)
		t.check(loaded.status == "recovered" and int(loaded.data.cursor) == 1 and loaded.data.undo_used and not loaded.error.is_empty(), "P1.3 %s visible backup recovery" % id)
		t.check(not store.write_slot(session, session.view_state).is_empty(), "P1.3 %s corrupt primary cannot rotate over backup" % id)
		t.check(store.repair_from_backup(definition).is_empty(), "P1.3 %s explicit backup repair" % id)
		t.check(store.load_slot(definition).status == "loaded", "P1.3 %s repaired primary" % id)
		for step: String in ["after_temp", "after_rotation"]:
			store.fail_step = step
			t.check(not store.write_slot(session, session.view_state).is_empty(), "P1.3 %s injected %s fails" % [id, step])
			t.check(store.load_slot(definition).status in ["loaded", "recovered"], "P1.3 %s valid data survives %s" % [id, step])
			store.fail_step = ""
		t.check(store.write_slot(session, session.view_state).is_empty(), "P1.3 %s resumes after interrupted replace" % id)
		file = FileAccess.open(store.path_for(id, ".bak"), FileAccess.WRITE)
		file.store_string("{broken backup")
		file.close()
		t.check(store.load_slot(definition).status == "backup_invalid" and not store.write_slot(session, session.view_state).is_empty(), "P1.3 %s valid primary plus invalid backup blocks silent rotation" % id)
		t.check(store.discard_invalid_backup(definition).is_empty() and store.write_slot(session, session.view_state).is_empty(), "P1.3 %s explicit invalid-backup renewal" % id)
		var solved_session: Session = Session.new(definition)
		var solution_changes: Array[Dictionary] = []
		for y: int in range(int(definition.height)):
			for x: int in range(int(definition.width)):
				var color: int = int(definition.solution[y][x])
				if color > 0:
					solution_changes.append({"index": y * int(definition.width) + x, "before": -1, "after": color})
		t.check(solved_session.player.commit(solution_changes), "P1.3 %s complete transaction" % id)
		solved_session.completed = solved_session.is_solution()
		var complete_store: SaveStore = SaveStore.new(SaveStore.test_root_override.path_join(id + "-complete"))
		t.check(complete_store.write_slot(solved_session, solved_session.view_state).is_empty(), "P1.3 %s completed save" % id)
		var complete_loaded: Dictionary = complete_store.load_slot(definition)
		var complete_restore: Session = Session.new(definition)
		if complete_loaded.status == "loaded":
			SaveStore.apply(complete_loaded.data, complete_restore)
		t.check(complete_loaded.status == "loaded" and complete_restore.completed and complete_restore.album_title() == definition.reveal.name and not complete_restore.reveal().is_empty(), "P1.3 %s earned reveal after completed restore" % id)
		# This slot's files only; a neighbouring byte marker survives reset.
		var neighbour: String = store.root.path_join("unrelated.bin")
		file = FileAccess.open(neighbour, FileAccess.WRITE)
		file.store_string("untouched")
		file.close()
		t.check(store.reset_slot(id).is_empty() and store.load_slot(definition).status == "fresh", "P1.3 %s selected reset" % id)
		t.check(FileAccess.get_file_as_string(neighbour) == "untouched", "P1.3 %s unrelated bytes untouched" % id)
	var shared: SaveStore = SaveStore.new(SaveStore.test_root_override.path_join("shared"))
	for id: String in SaveStore.IDS:
		var item: Session = Session.new(Definition.load_fixture(id))
		t.check(shared.write_slot(item, item.view_state).is_empty(), "P1.3 shared %s saved" % id)
	var sentinel: String = SaveStore.test_root_override.path_join("outside-p1.bin")
	var marker: FileAccess = FileAccess.open(sentinel, FileAccess.WRITE)
	marker.store_string("outside stays byte-identical")
	marker.close()
	shared.fail_step = "reset"
	t.check(not shared.reset_slot("f02").is_empty() and shared.load_slot(Definition.load_fixture("f02")).status == "loaded", "P1.3 failed reset stays visible and leaves slot intact")
	shared.fail_step = ""
	t.check(shared.reset_slot("f02").is_empty(), "P1.3 selected shared slot reset")
	t.check(shared.load_slot(Definition.load_fixture("f01")).status == "loaded" and shared.load_slot(Definition.load_fixture("f03")).status == "loaded" and shared.load_slot(Definition.load_fixture("f02")).status == "fresh", "P1.3 other two slots survive reset")
	t.check(FileAccess.get_file_as_string(sentinel) == "outside stays byte-identical", "P1.3 data outside save root untouched")
	var f01: Dictionary = Definition.load_fixture("f01")
	marker = FileAccess.open(shared.path_for("f01", ".tmp"), FileAccess.WRITE)
	marker.store_string("{orphan")
	marker.close()
	t.check(shared.load_slot(f01).status == "loaded", "P1.3 orphan temp never outranks valid primary")
	marker = FileAccess.open(shared.path_for("f01"), FileAccess.WRITE)
	marker.store_string("{corrupt")
	marker.close()
	t.check(shared.load_slot(f01).status == "error", "P1.3 corrupt primary plus temp is not silently fresh")
	t.check(not shared.write_slot(Session.new(f01), Session.new(f01).view_state).is_empty(), "P1.3 invalid data cannot be silently overwritten")
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	await t.process_frame
	var first_action: Array[Dictionary] = [{"index": 0, "before": -1, "after": 1}]
	t.check(app.session.player.commit(first_action), "P1.3 UI first slot action")
	app._save_current()
	app.select_puzzle(1)
	t.check(app.session.player.commit(first_action), "P1.3 UI second slot action")
	app._save_current()
	app.show_album()
	app._ask_reset()
	app.store.fail_step = "reset"
	app.reset_dialog.confirmed.emit()
	t.check(app.status_label.text.contains("Speicherfehler") and app.session.player.cells[0] == 1, "P1.3 failed confirmed reset is visible")
	app.store.fail_step = ""
	app._ask_reset()
	app.reset_dialog.confirmed.emit()
	t.check(app.session.player.cells[0] == -1 and app.store.load_slot(app.session.definition).status == "fresh", "P1.3 confirmed UI reset starts selected slot fresh")
	t.check(app.sessions[0].player.cells[0] == 1 and app.store.load_slot(app.sessions[0].definition).status == "loaded" and app.sessions[2].player.cells[0] == -1, "P1.3 UI reset preserves both other sessions")
	app.select_puzzle(0)
	app._save_current()
	var broken_backup: FileAccess = FileAccess.open(app.store.path_for("f01", ".bak"), FileAccess.WRITE)
	broken_backup.store_string("{bad backup")
	broken_backup.close()
	app.queue_free()
	await t.process_frame
	var recovery_ui: Main = load("res://main.tscn").instantiate()
	t.root.add_child(recovery_ui)
	await t.process_frame
	t.check(recovery_ui.slot_status[0] == "backup_invalid" and recovery_ui.status_label.visible and recovery_ui.repair_button.visible, "P1.3 broken backup visibly reported at startup")
	recovery_ui._ask_repair()
	recovery_ui.repair_dialog.confirmed.emit()
	t.check(recovery_ui.store.load_slot(f01).status == "loaded" and recovery_ui.status_label.text.is_empty(), "P1.3 confirmed backup renewal restores saving")
	var broken_primary: FileAccess = FileAccess.open(recovery_ui.store.path_for("f01"), FileAccess.WRITE)
	broken_primary.store_string("{bad primary")
	broken_primary.close()
	recovery_ui.queue_free()
	await t.process_frame
	var backup_ui: Main = load("res://main.tscn").instantiate()
	t.root.add_child(backup_ui)
	await t.process_frame
	t.check(backup_ui.slot_status[0] == "recovered" and backup_ui.status_label.visible and backup_ui.repair_button.visible, "P1.3 backup recovery visibly reported at startup")
	backup_ui._ask_repair()
	backup_ui.repair_dialog.confirmed.emit()
	t.check(backup_ui.store.load_slot(f01).status == "loaded" and backup_ui.status_label.text.is_empty(), "P1.3 confirmed recovery resumes saving")
	backup_ui.queue_free()
