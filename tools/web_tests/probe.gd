extends "res://ui/main.gd"
## Read-only observability in the separate technical export; never in player bundles.
var probe_elapsed: float = 0.0

func _process(delta: float) -> void:
	probe_elapsed += delta
	if probe_elapsed < 0.1 or board == null: return
	probe_elapsed = 0.0
	var controls: Array[Dictionary] = []
	_probe_controls(self, controls)
	var slots: Array[Dictionary] = []
	for item: Session in sessions:
		slots.append(SaveStore.snapshot(item, item.view_state))
	var origin: Vector2 = board.global_position + board.view.origin
	var data: Dictionary = {"controls": controls, "slots": slots, "slot_status": slot_status,
		"album": album.visible, "work": work.visible, "ending": ending.visible, "information": information.visible,
		"id": session.definition.id, "cells": session.player.cells, "history": session.player.history,
		"cursor": session.player.cursor, "completed": session.completed, "view": board.capture_view(),
		"origin": [origin.x, origin.y], "cell_size": board.view.cell_size,
		"dimensions": [session.player.width, session.player.height], "gesture": session.gesture.active,
		"canvas": [size.x, size.y], "ui_scale": ui_scale,
		"viewport": [get_viewport_rect().size.x, get_viewport_rect().size.y],
		"root": ProjectSettings.globalize_path("user://p1/saves"),
		"rows": session.definition.rows, "columns": session.definition.columns,
		"row_steps": board.row_clue_steps, "column_steps": board.column_clue_steps,
		"row_capacity": board.clue_capacity("row"), "column_capacity": board.clue_capacity("column"),
		"row_area": _probe_rect(board.row_clue_area()), "column_area": _probe_rect(board.column_clue_area()),
		"minimum": minimum_message.visible, "fit": board.view.viewport.encloses(board.view.bounds())}
	JavaScriptBridge.eval("window.picrossProbe = " + JSON.stringify(data), true)

func _probe_rect(rect: Rect2) -> Array[float]:
	return [rect.position.x + board.global_position.x, rect.position.y + board.global_position.y, rect.size.x, rect.size.y]

func _probe_controls(node: Node, result: Array[Dictionary]) -> void:
	if node is BaseButton and node.is_visible_in_tree() and node.get_window().visible:
		var box: Rect2 = node.get_global_rect()
		if node.get_window() != get_tree().root:
			box.position += Vector2(node.get_window().position)
		result.append({"name": node.name, "text": node.text if node is Button else "", "tooltip": node.tooltip_text, "disabled": node.disabled,
			"dialog": node.get_window() != get_tree().root,
			"center": [box.get_center().x, box.get_center().y]})
	for child: Node in node.get_children(true):
		_probe_controls(child, result)
