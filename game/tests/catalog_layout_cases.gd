extends RefCounted
## Small KL regression in the existing synthetic pages process; no captures.
const Card = preload("res://ui/catalog_card.gd")

static func rows(probe, count: int, expected_columns: int = 0) -> void:
	var album = probe.app.album
	probe.check(album.choices.size() == count, "KL only actual matching cards exist")
	probe.check(album.grid.get_child_count() == mini(12,count) and album.right_grid.get_child_count() == maxi(0,count-12), "KL canonical 12/12 ownership without placeholders")
	probe.check(album.grid.columns == album.right_grid.columns and album.grid.columns >= 1 and album.grid.columns <= 3, "KL common safe capacity on both halves")
	if expected_columns > 0: probe.check(album.grid.columns == expected_columns, "KL native reference capacity")
	var first: Card = album.choices[0]
	for half: Container in [album.grid, album.right_grid]:
		var scroller: ScrollContainer = half.get_parent()
		probe.check(half.size.x <= scroller.size.x and scroller.scroll_horizontal == 0, "KL no horizontal overflow")
		var line: Array[Rect2] = []
		var previous_y: float = -1
		var row_count: int = 0
		for column: Control in half.get_children():
			var card: Card = column.get_child(0)
			probe.check(card.size == first.size and card.size.x >= card.minimum_card_width(album.ui_scale), "KL equal complete card budgets on both halves")
			probe.check(card.get_global_rect() == column.get_global_rect(), "KL exact card and wrapper hit rectangles")
			if not line.is_empty() and column.position.y != previous_y:
				centred(probe, half, line)
				line.clear()
				row_count += 1
			line.append(column.get_rect())
			previous_y = column.position.y
		if not line.is_empty():
			centred(probe, half, line)
			row_count += 1
		probe.check(row_count == ceili(half.get_child_count()/float(half.columns)), "KL expected logical row count")

static func centred(probe, half: Container, line: Array[Rect2]) -> void:
	probe.check(absf((line[0].position.x+line[-1].end.x)-half.content_width) <= 2, "KL each occupied row has symmetric horizontal margins")
	for index: int in range(1,line.size()):
		probe.check(line[index].position.x >= line[index-1].end.x+roundi(12*probe.app.ui_scale)-1, "KL distinct nonoverlapping card targets")

static func run(probe) -> void:
	var app = probe.app
	var album = app.album
	var original: Dictionary = album.items.duplicate()
	var ids: Array = original.keys()
	var saved: Dictionary = probe.save_bytes()
	album.choose_sort("size")
	# Full and partial rows in both reference capacities, including right-only
	# tails of one, eleven and twelve. Membership is independent of the reflow.
	for spec: Array in [[2560,1440,1.0,3],[1920,1080,1.0,2]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		for count: int in [1,2,5,11,12,13,23,24]:
			album.items.clear()
			for id: String in ids.slice(0,count): album.items[id] = original[id]
			album._render(0)
			await probe.frames()
			rows(probe,count,spec[3])
			probe.check(Array(album.visible_ids) == ids.slice(0,count), "KL reflow preserves canonical IDs")
	# Height, UI and aspect fallbacks use real projected paper, never a width
	# switch. Existing KE cases separately bind the measured column boundary.
	for spec: Array in [[2560,1440,1.25],[1920,1200,1.0],[1920,1200,1.25],[1280,720,1.0],[1280,720,1.25]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await probe.frames()
		rows(probe,24)
	# Positive, different offsets survive same-capacity resize and a scale
	# roundtrip when still inside the new ranges. Reflow keeps the controls.
	probe.surface.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	await probe.frames()
	album.selected_id = ids[13]
	album.scroll.scroll_vertical = 70
	album.right_scroll.scroll_vertical = 140
	var controls: Array = album.choices.duplicate()
	for spec: Array in [[1920,1200,1.0],[1920,1080,1.25],[1920,1080,1.0]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await probe.frames()
		probe.check(album.positions() == Vector2i(70,140) and album.selected_id == ids[13], "KL resize and UI roundtrip retain selection and both independent offsets")
		probe.check(album.choices == controls, "KL reflow retains live controls and ID callbacks")
	probe.check(probe.save_bytes() == saved, "KL layout never writes puzzle saves")
	# Actual pointer opening from the right half and return use the same ID
	# callbacks after reflow. Reset cancellation must keep the bound target.
	album.ensure_control_visible(album.choices[13])
	await probe.frames()
	var pair: Vector2i = album.positions()
	probe.click(album.choices[13])
	await probe.frames()
	probe.check(app.work.visible and app.session.definition.id == ids[13], "KL right-half pointer opens its stable ID")
	app.show_album()
	await probe.frames()
	probe.check(album.positions() == pair and album.selected_id == ids[13], "KL right-half return restores selection and both offsets")
	album.ensure_control_visible(album.reset_buttons[ids[12]])
	await probe.frames()
	probe.click(album.reset_buttons[ids[12]])
	await probe.frames()
	probe.check(app.reset_dialog.visible and app.reset_id == ids[12], "KL right-half reset has its own precise bound hitbox")
	probe.click(app.reset_dialog.get_cancel_button())
	await probe.frames()
	album.selected_id = ""
	album.items = original
	album._render(0)
	await probe.frames()
