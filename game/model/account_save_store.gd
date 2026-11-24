extends "res://model/save_store.gd"
## Account saves replay local history from the last accepted remote progress.
const ACCOUNT_FORMAT = "picross-account-save/v1"
const Protocol = preload("res://model/sync_protocol.gd")

static func validate_account(data: Variant, definition: Dictionary) -> String:
	if not data is Dictionary or not keys(data, ["format", "definition_id", "definition_revision", "width", "height", "baseline", "cells", "history", "cursor", "undo_used", "completed", "view"]):
		return "Ungültiges Kontospeicherformat."
	if data.format != ACCOUNT_FORMAT or not data.baseline is Dictionary or data.baseline.is_empty():
		return "Unbekannte Kontospeicherversion oder fehlende Empfangsbasis."
	return validate_state(data, definition, data.baseline)

func validate_slot(data: Variant, definition: Dictionary) -> String:
	if data is Dictionary and data.has("schema"):
		return validate(data, definition)
	return validate_account(data, definition)

func older_slot(data: Variant, definition: Dictionary) -> bool:
	if not data is Dictionary or not data.has("format"): return super.older_slot(data,definition)
	if not keys(data,["format","definition_id","definition_revision","width","height","baseline","cells","history","cursor","undo_used","completed","view"]): return false
	if data.format != ACCOUNT_FORMAT or data.definition_id != definition.id or not data.baseline is Dictionary or data.baseline.is_empty(): return false
	return SaveRevision.older_state(data,definition,self,data.baseline)

func slot_snapshot(session: Session, view: Dictionary) -> Dictionary:
	var data := snapshot(session, view)
	data.erase("schema")
	data.format = ACCOUNT_FORMAT
	data.baseline = session.account_baseline.duplicate(true)
	if data.baseline.is_empty():
		var empty: Array[int] = []
		empty.resize(session.player.width * session.player.height)
		empty.fill(-1)
		data.baseline = {"cells": empty, "undo_used": false, "completed": solved(empty, session.definition)}
	return data

func received(progress: Variant, session: Session) -> Dictionary:
	if not Protocol.valid_progress(progress, session.definition.id): return {}
	var data := slot_snapshot(session, session.view_state)
	if Protocol.progress(data) == progress:
		return data if validate_account(data, session.definition).is_empty() else {}
	for key: String in Protocol.PROGRESS_FIELDS:
		data[key] = progress[key]
	data.baseline = {"cells": progress.cells.duplicate(), "undo_used": progress.undo_used, "completed": progress.completed}
	data.history = []
	data.cursor = 0
	return data if validate_account(data, session.definition).is_empty() else {}
