extends RefCounted
## P1-only JSON boundary. A slot is identified by a bundled fixture, never a path.
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const ClueLayout = preload("res://ui/clue_layout.gd")
const IDS: Array[String] = ["f01", "f02", "f03"]
const ZOOMS: Array[int] = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 44, 48, 54, 60, 66, 72]
static var test_root_override: String = ""
var root: String
var fail_step: String = "" # Deterministic filesystem interruption hook for isolated tests.

func _init(path: String = "user://p1/saves") -> void:
	root = path.trim_suffix("/")

func path_for(id: String, suffix: String = ".json") -> String:
	if not id in IDS:
		return ""
	return root.path_join(id + suffix)

static func number(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value))

static func integer(value: Variant) -> bool:
	return number(value) and float(value) == floor(float(value))

static func keys(value: Dictionary, expected: Array[String]) -> bool:
	if value.size() != expected.size():
		return false
	for key: String in expected:
		if not value.has(key):
			return false
	return true

static func valid_cell(value: Variant, colors: Array[int]) -> bool:
	return integer(value) and (int(value) == -1 or int(value) == 0 or int(value) in colors)

static func solved(cells: Array, definition: Dictionary) -> bool:
	var width: int = int(definition.width)
	for y: int in range(int(definition.height)):
		for x: int in range(width):
			var expected: int = int(definition.solution[y][x])
			var actual: int = int(cells[y * width + x])
			if (expected > 0 and actual != expected) or (expected == 0 and actual > 0):
				return false
	return true

static func valid_reads(reads: Variant, lines: Array) -> bool:
	if not reads is Array or reads.size() != lines.size():
		return false
	for i: int in range(lines.size()):
		var read: Variant = reads[i]
		if not read is Dictionary or not read.get("anchor") is String:
			return false
		if read.anchor in [ClueLayout.GRID_END, ClueLayout.OUTER_START]:
			if not keys(read, ["anchor"]):
				return false
		elif read.anchor == ClueLayout.MIDDLE:
			var count: int = maxi(1, lines[i].size())
			if not keys(read, ["anchor", "start", "end"]) or not integer(read.start) or not integer(read.end):
				return false
			if int(read.start) <= 0 or int(read.end) >= count or int(read.start) >= int(read.end):
				return false
		else:
			return false
	return true

static func validate(data: Variant, definition: Dictionary) -> String:
	if not data is Dictionary or not keys(data, ["schema", "definition_id", "definition_revision", "width", "height", "cells", "history", "cursor", "undo_used", "completed", "view"]):
		return "Ungültiges Speicherschema."
	if not integer(data.schema) or int(data.schema) != 1:
		return "Unbekannte Speicherversion."
	if data.definition_id != definition.id or not integer(data.definition_revision) or int(data.definition_revision) != int(definition.revision):
		return "Definition oder Revision passt nicht."
	if not integer(data.width) or not integer(data.height) or int(data.width) != int(definition.width) or int(data.height) != int(definition.height):
		return "Matrixgröße passt nicht."
	var count: int = int(definition.width) * int(definition.height)
	var colors: Array[int] = []
	for entry: Dictionary in definition.palette:
		colors.append(int(entry.id))
	if not data.cells is Array or data.cells.size() != count:
		return "Matrixlänge passt nicht."
	for value: Variant in data.cells:
		if not valid_cell(value, colors):
			return "Ungültiger Zellwert."
	if not data.history is Array or not integer(data.cursor) or int(data.cursor) < 0 or int(data.cursor) > data.history.size():
		return "Ungültiger History-Cursor."
	if not data.undo_used is bool or (int(data.cursor) < data.history.size() and not data.undo_used):
		return "Ungültiges Undo-Merkmal."
	var replay: Array[int] = []
	replay.resize(count)
	replay.fill(-1)
	var at_cursor: Array[int] = replay.duplicate()
	for action_index: int in range(data.history.size()):
		var action: Variant = data.history[action_index]
		if not action is Array or action.is_empty():
			return "Leere History-Aktion."
		var seen: Dictionary = {}
		for change: Variant in action:
			if not change is Dictionary or not keys(change, ["index", "before", "after"]):
				return "Ungültiger History-Eintrag."
			if not integer(change.index) or int(change.index) < 0 or int(change.index) >= count or seen.has(int(change.index)):
				return "Ungültiger oder doppelter Zellenindex."
			if not valid_cell(change.before, colors) or not valid_cell(change.after, colors) or int(change.before) == int(change.after):
				return "Ungültige History-Werte."
			if replay[int(change.index)] != int(change.before):
				return "History-Replay widerspricht dem Vorzustand."
			seen[int(change.index)] = true
		for change: Dictionary in action:
			replay[int(change.index)] = int(change.after)
		if action_index + 1 == int(data.cursor):
			at_cursor = replay.duplicate()
	if int(data.cursor) == 0:
		at_cursor.fill(-1)
	for i: int in range(count):
		if at_cursor[i] != int(data.cells[i]):
			return "Matrix und History-Cursor widersprechen sich."
	if not data.completed is bool or data.completed != solved(data.cells, definition):
		return "Abschlussstatus widerspricht der Matrix."
	var view: Variant = data.view
	if not view is Dictionary or not keys(view, ["center", "zoom", "overview", "active_color", "tool", "row_clue_reads", "column_clue_reads"]):
		return "Ungültige Ansicht."
	if not view.center is Array or view.center.size() != 2 or not number(view.center[0]) or not number(view.center[1]):
		return "Ungültiger Rasterfokus."
	if float(view.center[0]) < 0.0 or float(view.center[0]) > float(definition.width) or float(view.center[1]) < 0.0 or float(view.center[1]) > float(definition.height):
		return "Rasterfokus außerhalb des Rätsels."
	if not view.overview is bool or not integer(view.zoom) or not int(view.zoom) in ZOOMS:
		return "Ungültiger Arbeitszoom."
	if not integer(view.active_color) or not int(view.active_color) in colors or not view.tool is String or not view.tool in ["fill", "erase", "hand"]:
		return "Ungültiges Werkzeug oder Farbe."
	if not valid_reads(view.row_clue_reads, definition.rows) or not valid_reads(view.column_clue_reads, definition.columns):
		return "Ungültige Hinweis-Leseposition."
	return ""

static func snapshot(session: Session, view: Dictionary) -> Dictionary:
	return {"schema": 1, "definition_id": session.definition.id, "definition_revision": session.definition.revision,
		"width": session.player.width, "height": session.player.height, "cells": session.player.cells.duplicate(),
		"history": session.player.history.duplicate(true), "cursor": session.player.cursor,
		"undo_used": session.player.undo_used, "completed": session.completed, "view": view.duplicate(true)}

static func apply(data: Dictionary, session: Session) -> void:
	session.gesture.cancel()
	session.player.cells.clear()
	for value: Variant in data.cells:
		session.player.cells.append(int(value))
	session.player.history.clear()
	for action: Array in data.history:
		var restored: Array[Dictionary] = []
		for change: Dictionary in action:
			restored.append({"index": int(change.index), "before": int(change.before), "after": int(change.after)})
		session.player.history.append(restored)
	session.player.cursor = int(data.cursor)
	session.player.undo_used = data.undo_used
	session.completed = data.completed
	session.view_state = data.view.duplicate(true)

func _parse(path: String, definition: Dictionary) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"status": "missing"}
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"status": "invalid", "error": "Datei nicht lesbar."}
	var raw: String = file.get_as_text()
	file.close()
	var parser: JSON = JSON.new()
	if parser.parse(raw) != OK:
		return {"status": "invalid", "error": "JSON beschädigt."}
	var error: String = validate(parser.data, definition)
	return {"status": "valid", "data": parser.data} if error.is_empty() else {"status": "invalid", "error": error}

func load_slot(definition: Dictionary) -> Dictionary:
	var id: String = str(definition.id).to_lower().replace("-", "")
	if not id in IDS:
		return {"status": "error", "error": "Unbekanntes Fixture."}
	var primary: Dictionary = _parse(path_for(id), definition)
	var backup: Dictionary = _parse(path_for(id, ".bak"), definition)
	if primary.status == "valid":
		if backup.status == "invalid":
			return {"status": "backup_invalid", "data": primary.data, "error": "Primärstand geladen; Backup beschädigt und Speichern bis zur bewussten Erneuerung gesperrt."}
		return {"status": "loaded", "data": primary.data}
	if backup.status == "valid":
		return {"status": "recovered", "data": backup.data, "error": "Primärstand fehlt oder ist ungültig; gültiges Backup geladen."}
	if primary.status == "missing" and backup.status == "missing":
		return {"status": "fresh"}
	return {"status": "error", "error": "Gespeicherte Daten unlesbar oder inkompatibel; kein gültiges Backup. Arbeitsstand bewusst zurücksetzen."}

func _absolute(path: String) -> String:
	return ProjectSettings.globalize_path(path) if path.begins_with("user://") else path

func write_slot(session: Session, view: Dictionary) -> String:
	var id: String = str(session.definition.id).to_lower().replace("-", "")
	if not id in IDS:
		return "Unbekanntes Fixture."
	var candidate: Dictionary = snapshot(session, view)
	var error: String = validate(candidate, session.definition)
	if not error.is_empty():
		return error
	var primary_path: String = path_for(id)
	var backup_path: String = path_for(id, ".bak")
	var temp_path: String = path_for(id, ".tmp")
	var previous: Dictionary = _parse(primary_path, session.definition)
	var backup: Dictionary = _parse(backup_path, session.definition)
	if previous.status == "invalid" or backup.status == "invalid":
		return "Vorhandene ungültige Daten werden nicht überschrieben."
	if DirAccess.make_dir_recursive_absolute(_absolute(root)) != OK:
		return "Speicherverzeichnis nicht erstellbar."
	var file: FileAccess = FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		return "Temporäre Datei nicht schreibbar."
	file.store_string(JSON.stringify(candidate) + "\n")
	file.flush()
	var write_error: Error = file.get_error()
	file.close()
	if write_error != OK:
		return "Temporäre Datei nicht vollständig geschrieben."
	if _parse(temp_path, session.definition).status != "valid":
		return "Temporäre Datei besteht Validierung nicht."
	if fail_step == "after_temp":
		return "Testabbruch nach Tempvalidierung."
	if previous.status == "valid":
		if FileAccess.file_exists(backup_path) and DirAccess.remove_absolute(_absolute(backup_path)) != OK:
			return "Altes Backup nicht entfernbar."
		if DirAccess.rename_absolute(_absolute(primary_path), _absolute(backup_path)) != OK:
			return "Primärstand nicht als Backup rotierbar."
	if fail_step == "after_rotation":
		return "Testabbruch nach Backuprotation."
	if DirAccess.rename_absolute(_absolute(temp_path), _absolute(primary_path)) != OK:
		return "Temporäre Datei nicht als Primärstand einsetzbar."
	return ""

func reset_slot(id: String) -> String:
	if not id in IDS:
		return "Unbekanntes Fixture."
	if fail_step == "reset":
		return "Testabbruch vor Reset."
	for suffix: String in [".json", ".bak", ".tmp"]:
		var path: String = path_for(id, suffix)
		if FileAccess.file_exists(path) and DirAccess.remove_absolute(_absolute(path)) != OK:
			return "Arbeitsstand konnte nicht vollständig entfernt werden."
	return ""

func repair_from_backup(definition: Dictionary) -> String:
	var id: String = str(definition.id).to_lower().replace("-", "")
	if not id in IDS:
		return "Unbekanntes Fixture."
	var backup: Dictionary = _parse(path_for(id, ".bak"), definition)
	if backup.status != "valid":
		return "Kein gültiges Backup vorhanden."
	var primary: Dictionary = _parse(path_for(id), definition)
	if primary.status == "valid":
		return ""
	var temp_path: String = path_for(id, ".tmp")
	var file: FileAccess = FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		return "Wiederherstellungsdatei nicht schreibbar."
	file.store_string(JSON.stringify(backup.data) + "\n")
	file.flush()
	var write_error: Error = file.get_error()
	file.close()
	if write_error != OK or _parse(temp_path, definition).status != "valid":
		return "Wiederherstellungsdatei ungültig."
	var primary_path: String = path_for(id)
	if FileAccess.file_exists(primary_path) and DirAccess.remove_absolute(_absolute(primary_path)) != OK:
		return "Beschädigter Primärstand nicht entfernbar."
	if DirAccess.rename_absolute(_absolute(temp_path), _absolute(primary_path)) != OK:
		return "Backup konnte nicht als Primärstand eingesetzt werden."
	return ""

func discard_invalid_backup(definition: Dictionary) -> String:
	var id: String = str(definition.id).to_lower().replace("-", "")
	if not id in IDS:
		return "Unbekanntes Fixture."
	if _parse(path_for(id), definition).status != "valid":
		return "Kein gültiger Primärstand vorhanden."
	var backup_path: String = path_for(id, ".bak")
	if _parse(backup_path, definition).status != "invalid":
		return "Backup ist nicht beschädigt."
	if DirAccess.remove_absolute(_absolute(backup_path)) != OK:
		return "Beschädigtes Backup nicht entfernbar."
	return ""
