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
			var interrupted: Dictionary = store.load_slot(definition)
			t.check(interrupted.status in ["loaded", "recovered"], "P1.3 %s valid data survives %s" % [id, step])
			store.fail_step = ""
			if step == "after_rotation":
				var backup_bytes: String = FileAccess.get_file_as_string(store.path_for(id, ".bak"))
				t.check(interrupted.status == "recovered" and not FileAccess.file_exists(store.path_for(id)), "N-02 %s restart sees missing primary and valid backup" % id)
				t.check(not store.write_slot(session, session.view_state).is_empty() and not FileAccess.file_exists(store.path_for(id)) and FileAccess.get_file_as_string(store.path_for(id, ".bak")) == backup_bytes, "N-02 %s autosave remains blocked and backup unchanged" % id)
				t.check(store.repair_from_backup(definition).is_empty(), "N-02 %s explicit missing-primary recovery" % id)
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
	await t.process_frame
	var failure_ui: Main = load("res://main.tscn").instantiate()
	t.root.add_child(failure_ui)
	await t.process_frame
	failure_ui.open_puzzle()
	failure_ui.board.zoom(1, failure_ui.board.view.viewport.get_center())
	failure_ui.store.fail_step = "after_temp"
	failure_ui.show_album()
	t.check(failure_ui.work.visible and not failure_ui.album.visible and failure_ui.status_label.text.contains("Speicherfehler"), "N-01 album stays open on failed mandatory flush")
	failure_ui.store.fail_step = ""
	failure_ui.show_album()
	t.check(failure_ui.album.visible and failure_ui.status_label.text.is_empty(), "N-01 album transition succeeds after retry")
	failure_ui.open_puzzle()
	failure_ui.board.zoom(1, failure_ui.board.view.viewport.get_center())
	failure_ui.store.fail_step = "after_temp"
	failure_ui.select_puzzle(1)
	t.check(failure_ui.session == failure_ui.sessions[0] and failure_ui.status_label.text.contains("Speicherfehler"), "N-01 fixture switch is blocked on failed flush")
	failure_ui.store.fail_step = ""
	failure_ui.select_puzzle(1)
	t.check(failure_ui.session == failure_ui.sessions[1] and failure_ui.status_label.text.is_empty(), "N-01 fixture switch succeeds after retry")
	failure_ui.store.fail_step = "after_temp"
	t.check(failure_ui.session.player.commit(first_action) and not failure_ui._save_current(), "N-01 confirmed cell action remains unsaved after write failure")
	failure_ui.board.zoom(1, failure_ui.board.view.viewport.get_center())
	failure_ui.notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
	t.check(is_instance_valid(failure_ui) and failure_ui.is_inside_tree() and failure_ui.session.player.cells[0] == 1 and failure_ui.status_label.text.contains("Speicherfehler"), "N-01 WM-close failure keeps unsaved cell and visible error")
	failure_ui.leave_app()
	t.check(failure_ui.is_inside_tree() and failure_ui.status_label.text.contains("Speicherfehler"), "N-01 Beenden failure cannot quit")
	failure_ui.store.fail_step = ""
	t.check(failure_ui._flush_current() and failure_ui.status_label.text.is_empty(), "N-01 close retry clears error and persists view")
	# Reproduce the interruption after rotation, then build a genuinely new UI process.
	failure_ui.select_puzzle(0)
	failure_ui.store.fail_step = "after_rotation"
	failure_ui.board.zoom(1, failure_ui.board.view.viewport.get_center())
	t.check(not failure_ui._save_current() and failure_ui.slot_status[0] == "recovered" and failure_ui.work_repair_button.visible, "N-02 interrupted replacement exposes same-process recovery")
	failure_ui.store.fail_step = ""
	var saved_backup: String = FileAccess.get_file_as_string(failure_ui.store.path_for("f01", ".bak"))
	failure_ui.queue_free()
	await t.process_frame
	var missing_ui: Main = load("res://main.tscn").instantiate()
	t.root.add_child(missing_ui)
	await t.process_frame
	t.check(missing_ui.slot_status[0] == "recovered" and missing_ui.repair_button.visible and not FileAccess.file_exists(missing_ui.store.path_for("f01")), "N-02 missing primary loads backup visibly after restart")
	missing_ui.open_puzzle()
	t.check(missing_ui.work_repair_button.visible, "N-02 recovery takeover remains available from work view")
	missing_ui.board.zoom(1, missing_ui.board.view.viewport.get_center())
	t.check(not missing_ui._save_current() and missing_ui.slot_status[0] == "recovered" and not FileAccess.file_exists(missing_ui.store.path_for("f01")) and FileAccess.get_file_as_string(missing_ui.store.path_for("f01", ".bak")) == saved_backup, "N-02 normal view save cannot acknowledge recovered backup")
	var free_index: int = missing_ui.session.player.cells.find(-1)
	t.check(missing_ui.session.player.commit([{"index": free_index, "before": -1, "after": 1}]) and not missing_ui._save_current() and missing_ui.slot_status[0] == "recovered" and not FileAccess.file_exists(missing_ui.store.path_for("f01")), "N-02 confirmed cell cannot autosave before takeover")
	missing_ui.set_tool("hand")
	t.check(missing_ui.slot_status[0] == "recovered" and not FileAccess.file_exists(missing_ui.store.path_for("f01")), "N-02 tool save remains blocked")
	missing_ui._ask_repair()
	missing_ui.repair_dialog.confirmed.emit()
	t.check(missing_ui.store.load_slot(f01).status == "loaded" and missing_ui.status_label.text.is_empty(), "N-02 confirmed takeover permits saving")
	missing_ui.queue_free()
	await t.process_frame
	var f02: Dictionary = Definition.load_fixture("f02")
	var color_store: SaveStore = SaveStore.new(SaveStore.test_root_override)
	color_store.fail_step = "after_rotation"
	t.check(not color_store.write_slot(Session.new(f02), Session.new(f02).view_state).is_empty() and color_store.load_slot(f02).status == "recovered", "N-02 color fixture interrupted after rotation")
	var color_backup: String = FileAccess.get_file_as_string(color_store.path_for("f02", ".bak"))
	var color_ui: Main = load("res://main.tscn").instantiate()
	t.root.add_child(color_ui)
	await t.process_frame
	color_ui.select_puzzle(1)
	color_ui.board.active_color = 2
	color_ui.set_tool("fill")
	t.check(color_ui.slot_status[1] == "recovered" and not FileAccess.file_exists(color_store.path_for("f02")) and FileAccess.get_file_as_string(color_store.path_for("f02", ".bak")) == color_backup, "N-02 changed color cannot autosave before takeover")
	color_ui._ask_repair()
	color_ui.repair_dialog.confirmed.emit()
	t.check(color_store.load_slot(f02).status == "loaded" and int(color_store.load_slot(f02).data.view.active_color) == 2, "N-02 confirmed color-slot takeover saves changed color")
	color_ui.queue_free()
