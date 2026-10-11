extends "res://ui/chalkboard_board.gd"
## Regular full view: one selected renderer, no study lifecycle or persistence.
const ROW_SLOT: float = 24.0 # V1-A: same font, shared tighter horizontal pitch
const Scribble = preload("res://ui/scribble.gd")
const FRAME_MARGIN: float = 1.0 # 0.28 deviation + 0.82 half-width + 1 AA - 1.10 inward
var composition_shift: Vector2 = Vector2.ZERO
var untranslated_occupied: Rect2
var untranslated_grid: Rect2
var mode: String = "G"
var requested_cell: float = 24.0 # valid desired work step; actual cell size may be fit-limited
var fit_ceiling: float = 24.0
var raw_fit: float = 24.0
var max_hints: Vector2i = Vector2i.ONE
var reserve_slots: Vector2i = Vector2i.ONE
var minimum_slots: Vector2i = Vector2i.ONE
var horizontal_budget: float = 0.0
var horizontal_used: float = 0.0
var reserve_cache: Dictionary = {}
var ink_cache: Dictionary = {}
var layout_valid: bool = true
var glyph_risk: bool = false
var layout_key: String = ""
var layout_state: Array = []

func _ready() -> void:
	# Share immutable measurements for this process without retaining script/font
	# resources beyond the SceneTree's lifetime through static dictionaries.
	var tree: SceneTree = get_tree()
	if not tree.has_meta("full_view_measurements"):
		tree.set_meta("full_view_measurements", {"reserves":{},"ink":{}})
	var cache: Dictionary = tree.get_meta("full_view_measurements")
	reserve_cache = cache.reserves
	ink_cache = cache.ink
	super._ready()

func _layout() -> void:
	if session == null or size.x <= 1 or size.y <= 1:
		return
	var key: String = "%d/%s/%s/%s/%s/%s" % [session.get_instance_id(), size, ui_scale, mode, overview, requested_cell]
	if key == layout_key and layout_state == [view.cell_size, view.center, view.viewport]:
		return
	layout_key = key
	mode = "V" if mode == "V" else "G"
	hand = false
	overview = false
	max_hints = Vector2i.ONE
	for line: Array in session.definition.rows:
		max_hints.x = maxi(max_hints.x, line.size())
	for line: Array in session.definition.columns:
		max_hints.y = maxi(max_hints.y, line.size())
	minimum_slots = max_hints if mode == "V" else Vector2i(required_slots("row"), required_slots("column"))
	reserve_slots = minimum_slots
	book_inset = Vector2(minimum_slots) * Vector2(ROW_SLOT, 18) * ui_scale + Vector2(6, 6)
	var frame_space: Vector2 = Vector2.ONE * 2.0 * FRAME_MARGIN
	var available: Vector2 = size - book_inset - Vector2(6, 6) - frame_space
	raw_fit = minf(available.x / session.player.width, available.y / session.player.height)
	# The bound pen uses a two-pixel inset. Below four pixels even its interior
	# disappears: report failure rather than feeding negative rectangles to it.
	layout_valid = raw_fit > 4.0
	fit_ceiling = maxf(1.0, floorf(raw_fit * 100.0) / 100.0)
	view.cell_size = minf(requested_cell, fit_ceiling)
	layout_valid = layout_valid and view.cell_size > 4.0
	book_grid_size = Vector2(session.player.width, session.player.height) * view.cell_size
	# One-way allocation: the displayed capacity never feeds back into fit.
	horizontal_budget = maxf(0.0, available.x - book_grid_size.x)
	horizontal_used = 0.0
	if mode == "G" and layout_valid:
		var pitch: float = ROW_SLOT * ui_scale
		var offered: int = mini(max_hints.x, minimum_slots.x + floori((horizontal_budget + 0.000001) / pitch))
		for capacity: int in range(offered, minimum_slots.x, -1):
			if suitable_slots("row", capacity):
				reserve_slots.x = capacity
				break
		horizontal_used = (reserve_slots.x - minimum_slots.x) * pitch
		book_inset.x += horizontal_used
	composition_shift = Vector2.ZERO
	view.configure(Rect2(book_inset, book_grid_size + frame_space), Vector2i(session.player.width, session.player.height))
	view.center = Vector2(view.dimensions) / 2.0
	view.reframe()
	untranslated_grid = view.bounds()
	untranslated_occupied = composition_envelope()
	if layout_valid:
		# Only the remaining space is balanced. Fit and real hint capacity are
		# final already; never introduce slots or shrink the board for symmetry.
		var desired: Vector2 = size / 2.0 - untranslated_occupied.get_center()
		var room: Vector2 = (size - untranslated_occupied.end).max(Vector2.ZERO)
		composition_shift = desired.round().max(Vector2.ZERO).min(room.floor())
		book_inset += composition_shift
		view.configure(Rect2(book_inset, book_grid_size + frame_space), Vector2i(session.player.width, session.player.height))
		view.center = Vector2(view.dimensions) / 2.0
		view.reframe()
	layout_state = [view.cell_size, view.center, view.viewport]
	if marks != null:
		marks.visible = layout_valid
	# Conservative real ink/status extents, including multi-digit columns. This
	# fast warning complements the exhaustive measured overlap test in delivery.
	glyph_risk = false
	var fs: int = clue_font_size()
	for axis: String in ["row", "column"]:
		for line: Array in (session.definition.rows if axis == "row" else session.definition.columns):
			for clue: Dictionary in line:
				var box: Rect2 = glyph_box(clue_token(clue), Vector2.ZERO, fs)
				if (box.size.y if axis == "row" else box.size.x) > view.cell_size or (box.size.x if axis == "row" else box.size.y) > (ROW_SLOT if axis == "row" else 18.0) * ui_scale:
					glyph_risk = true
	ensure_clue_steps()
	normalize_clue_steps()
	cancel_gesture()

func shared_clue_slot_extent(axis: String, font: Font, fs: int) -> float:
	return ROW_SLOT * ui_scale if book_layout and axis == "row" else super.shared_clue_slot_extent(axis, font, fs)

func row_clue_area() -> Rect2:
	var area: Rect2 = super.row_clue_area()
	area.position.x += composition_shift.x
	area.size.x -= composition_shift.x
	return area

func column_clue_area() -> Rect2:
	var area: Rect2 = super.column_clue_area()
	area.position.y += composition_shift.y
	area.size.y -= composition_shift.y
	return area

func composition_envelope() -> Rect2:
	# State-independent ink/status envelope. Complete lines use actual glyphs,
	# never empty slots. Overflow can bring whole glyphs to the clipping edge
	# during continuous reading, so its full travel area belongs to the block.
	var result: Rect2 = view.bounds().grow(FRAME_MARGIN)
	var fs: int = clue_font_size()
	for axis: String in ["row", "column"]:
		var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
		var capacity: int = clue_capacity(axis)
		var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
		for index: int in range(lines.size()):
			var entries: Array = clue_entries(lines[index])
			if entries.size() > capacity:
				result = result.merge(area)
				continue
			var layout: Dictionary = ClueLayout.select_window(entries.size(), capacity, 0)
			layout.slot_extent = shared_clue_slot_extent(axis, clue_font(), fs)
			var cross: float = (view.origin.y if axis == "row" else view.origin.x) + (index + 0.5) * view.cell_size
			for unit: Dictionary in layout.units:
				var text: String = str(entries[int(unit.index)].text)
				var width: float = clue_text_font(clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				var along: float = clue_slot_center(axis, area, layout, int(unit.slot))
				var baseline: Vector2 = Vector2(along-width/2.0, cross+clue_baseline_offset(fs)) if axis == "row" else Vector2(cross-width/2.0, along+clue_baseline_offset(fs))
				result = result.merge(glyph_box(text, baseline, fs))
	return result

func set_mode(value: String) -> void:
	value = "G" if value == "R" else value
	if not value in ["G", "V"]:
		return
	cancel_gesture()
	mode = value
	hand = false
	viewport_layout_requested.emit()
	_layout()
	view_changed.emit()

func navigation_target(point: Vector2) -> String:
	if mode == "G" and layout_valid:
		var target: String = super.navigation_target(point)
		if target in ["row", "column"]:
			var index: int = navigation_line(point, target)
			if index >= 0 and int(clue_layout(target, index).max_offset) > 0:
				return target
	return ""

func navigate_to(_normalized: Vector2) -> void:
	pass

func zoom(direction: int, anchor: Vector2) -> void:
	if session.gesture.active or not layout_valid:
		return
	var step: float = next_zoom_step(view.cell_size, direction)
	if direction < 0 and step >= view.cell_size:
		return
	if is_equal_approx(minf(step, fit_ceiling), view.cell_size):
		return
	overview = false
	requested_cell = step
	_layout()
	view_changed.emit()

func capture_view() -> Dictionary:
	var state: Dictionary = super.capture_view()
	# Schema 1 stores the user's valid work step, never a calculated fractional fit.
	state.zoom = roundi(requested_cell)
	state.overview = false
	state.tool = "erase" if eraser else "fill"
	state.center = [session.player.width / 2.0, session.player.height / 2.0]
	return state

func restore_view(state: Dictionary) -> void:
	# SaveStore validates the ENTIRE legacy save before this presentation mapping.
	var normalized: Dictionary = state.duplicate(true)
	normalized.tool = "fill" if normalized.get("tool") == "hand" else normalized.get("tool", "fill")
	normalized.overview = false
	normalized.center = [session.player.width / 2.0, session.player.height / 2.0]
	requested_cell = float(state.zoom)
	super.restore_view(normalized)
	_layout()

func _gui_input(event: InputEvent) -> void:
	if layout_valid:
		super._gui_input(event)

func pointer_press(point: Vector2, button: MouseButton) -> void:
	if layout_valid:
		super.pointer_press(point, button)

func _draw() -> void:
	if not layout_valid:
		if marks != null:
			marks.hide()
		draw_string(BODY_FONT, Vector2(12, 36), "Zu wenig Platz für Raster und Hinweise.", HORIZONTAL_ALIGNMENT_LEFT, size.x-24, 18, INK)
		draw_string(BODY_FONT, Vector2(12, 62), "Fenster vergrößern oder UI / Rätselansicht in Einstellungen ändern.", HORIZONTAL_ALIGNMENT_LEFT, size.x-24, 16, INK)
		return
	super._draw()
	if marks != null:
		marks.visible = layout_valid

func grid_stroke(start: Vector2, end: Vector2, axis: String, index: int) -> Dictionary:
	var horizontal: bool = axis == "row"
	var limit: int = session.player.height if horizontal else session.player.width
	var outer: bool = index == 0 or index == limit
	var detail: float = clampf((view.cell_size-4.0)/20.0,0.0,1.0)
	var identity: String = "%s/%s/%s/%d" % [session.definition.id,session.definition.revision,axis,index]
	var major: bool = outer or index % 5 == 0
	var width: float = (1.4 + 0.24 * (Scribble.unit(identity,0)+1.0)/2.0) if major else (0.7 + 0.2 * (Scribble.unit(identity,0)+1.0)/2.0)
	# Endpoints meet on the same inset rectangle. Interior logical boundaries
	# stay fixed; only their ink deviates within the existing two-pixel gap.
	var along: Vector2 = Vector2.RIGHT if horizontal else Vector2.DOWN
	start += along * 1.10
	end -= along * 1.10
	if outer:
		var inward: Vector2 = (Vector2.DOWN if horizontal else Vector2.RIGHT) * (1.10 if index == 0 else -1.10)
		start += inward
		end += inward
	var line: Dictionary = Scribble.stroke(start,end,identity,0.28*detail,width,maxi(2,ceili(start.distance_to(end)/24.0)))
	line.color = INK if major else Color("b5b6ab")
	return line

func draw_grid_line(start: Vector2, end: Vector2, axis: String, index: int) -> void:
	var line: Dictionary = grid_stroke(start,end,axis,index)
	Scribble.paint(self,line,line.color)

func clue_capacity(axis: String, _available_override: float = -1.0) -> int:
	return reserve_slots.x if axis == "row" else reserve_slots.y

# Full glyph + C1/AA + status-strike bounds in the moving direction. Status
# never reduces the geometry; the reserve is stable while solving or zooming.
func token_ink(text: String, axis: String, fs: int) -> Vector2:
	var key: String = "%s/%s/%d/%s" % [text, axis, fs, ui_scale]
	if ink_cache.has(key):
		return ink_cache[key]
	var width: float = clue_text_font(clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box: Rect2 = glyph_box(text, Vector2(-width / 2.0, clue_baseline_offset(fs)), fs)
	var result: Vector2 = Vector2(-box.position.x, box.end.x) if axis == "row" else Vector2(-box.position.y, box.end.y)
	ink_cache[key] = result
	return result

func sequence_units(entries: Array, capacity: int, origin_slot: int, shift: float, axis: String, fs: int, low: float, high: float, ink_bound: Vector2 = Vector2(-1,-1)) -> Dictionary:
	var pitch: float = (ROW_SLOT if axis == "row" else 18.0) * ui_scale
	var origin: float = high - capacity * pitch
	var candidates: Array[Dictionary] = []
	if ink_bound.x < 0:
		ink_bound = Vector2.ZERO
		for entry: Dictionary in entries:
			ink_bound = ink_bound.max(token_ink(str(entry.text),axis,fs))
	# Exclude only centers whose measured maximum ink cannot intersect the area.
	# This keeps the exact whole-glyph oracle linear in visible capacity rather
	# than scanning a hundred hidden tokens at every continuous boundary.
	var base: float = origin + (origin_slot+0.5)*pitch + shift
	var first: int = maxi(0,floori((low-ink_bound.y-base)/pitch))
	var last: int = mini(entries.size(),ceili((high+ink_bound.x-base)/pitch)+1)
	for i: int in range(first,last):
		var center: float = origin + (origin_slot + i + 0.5) * pitch + shift
		var ink: Vector2 = token_ink(str(entries[i].text), axis, fs)
		if center - ink.x >= low and center + ink.y <= high:
			candidates.append({"kind": "token", "index": i, "center": center, "before": ink.x, "after": ink.y})
	var prefix: bool = candidates.is_empty() or int(candidates[0].index) > 0
	var suffix: bool = candidates.is_empty() or int(candidates[-1].index) < entries.size() - 1
	var marker: Vector2 = token_ink("…", axis, fs)
	var start: float = origin + 0.5 * pitch
	var finish: float = origin + (capacity - 0.5) * pitch
	var units: Array[Dictionary] = []
	if prefix:
		units.append({"kind": "prefix", "index": -1, "center": start})
	for unit: Dictionary in candidates:
		if prefix and unit.center - unit.before < start + marker.y:
			continue
		if suffix and unit.center + unit.after > finish - marker.x:
			continue
		units.append(unit)
	if suffix:
		units.append({"kind": "suffix", "index": -1, "center": finish})
	return {"units": units, "prefix_hidden": prefix, "suffix_hidden": suffix}

# Visibility changes only at these glyph/area/marker boundaries. Testing both
# sides and each open interval proves the entire continuous drag, not samples.
func sequence_transitions(entries: Array, capacity: int, axis: String, fs: int) -> Array[float]:
	var pitch: float = (ROW_SLOT if axis == "row" else 18.0) * ui_scale
	var high: float = capacity * pitch + 6.0
	var maximum: float = (entries.size() - capacity + 1) * pitch
	var start: float = 6.0 + pitch * 0.5
	var finish: float = high - pitch * 0.5
	var marker: Vector2 = token_ink("…", axis, fs)
	var boundaries: Dictionary = {0.0: true, maximum: true}
	for i: int in range(entries.size()):
		var center: float = 6.0 + (capacity - entries.size() + i + 0.5) * pitch
		var ink: Vector2 = token_ink(str(entries[i].text), axis, fs)
		for boundary: float in [ink.x - center, high - ink.y - center, start + marker.y + ink.x - center, start - marker.x - ink.y - center, finish + marker.y + ink.x - center, finish - marker.x - ink.y - center]:
			if boundary > 0.0 and boundary < maximum:
				boundaries[boundary] = true
	var points: Array = boundaries.keys()
	points.sort()
	var result: Array[float] = []
	for i: int in range(points.size()):
		result.append(points[i])
		if i > 0:
			result.append((points[i-1] + points[i]) / 2.0)
	return result

func required_slots(axis: String) -> int:
	var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
	var key: String = "%s/%s/%s/%s" % [JSON.stringify(lines), axis, ui_scale, ROW_SLOT]
	if reserve_cache.has(key):
		return int(reserve_cache[key])
	var maximum: int = max_hints.x if axis == "row" else max_hints.y
	var chosen: int = maximum
	for capacity: int in range(mini(maximum, 5), maximum + 1):
		if suitable_slots(axis, capacity):
			chosen = capacity
			break
	reserve_cache[key] = chosen
	return chosen

func suitable_slots(axis: String, capacity: int) -> bool:
	var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
	var minimum_key: String = "%s/%s/%s/%s" % [JSON.stringify(lines),axis,ui_scale,ROW_SLOT]
	if reserve_cache.has(minimum_key) and capacity >= int(reserve_cache[minimum_key]):
		# Increasing capacity moves the prefix marker outward, keeps the suffix
		# edge fixed and shortens the shift interval. Every previously whole
		# token remains whole; a proven minimum therefore proves all supersets.
		return true
	var key: String = "safe/%s/%s/%s/%d/%s" % [JSON.stringify(lines), axis, ui_scale, capacity, ROW_SLOT]
	if reserve_cache.has(key):
		return bool(reserve_cache[key])
	var suitable: bool = true
	var seen: Dictionary = {}
	for line: Array in lines:
		if line.size() <= capacity:
			continue
		var entries: Array = clue_entries(line)
		# Ink bounds depend on tokens, not color or row identity. Large stress
		# sheets repeat the same sequence on many lines; prove it once.
		var tokens: String = str(entries.map(func(entry: Dictionary) -> String: return entry.text))
		if seen.has(tokens):
			continue
		seen[tokens] = true
		for fs: int in range(Fonts.pixel_size(8), Fonts.pixel_size(roundi(14 * ui_scale)) + 1):
			var ink_bound: Vector2 = Vector2.ZERO
			for entry: Dictionary in entries:
				ink_bound = ink_bound.max(token_ink(str(entry.text),axis,fs))
			for shift: float in sequence_transitions(entries, capacity, axis, fs):
				var drawn: Array = sequence_units(entries, capacity, capacity - entries.size(), shift, axis, fs, 0.0, capacity * (ROW_SLOT if axis == "row" else 18.0) * ui_scale + 6.0, ink_bound).units
				if drawn.filter(func(unit: Dictionary) -> bool: return unit.kind == "token").size() < mini(5, line.size()):
					suitable = false
					break
			if not suitable: break
		if not suitable: break
	reserve_cache[key] = suitable
	return suitable

func visual_hint_units(axis: String, index: int) -> Dictionary:
	var layout: Dictionary = visible_clue_layout(axis, index)
	if is_zero_approx(float(layout.visual_shift)):
		return super.visual_hint_units(axis, index)
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	return sequence_units(layout.entries, int(layout.slot_count), int(layout.token_slot) - int(layout.start), float(layout.visual_shift), axis, clue_font_size(), area.position.x if axis == "row" else area.position.y, area.end.x if axis == "row" else area.end.y)

func _draw_row_hint(index: int, py: float, font: Font, fs: int) -> void:
	draw_hint_units("row", index, py, font, fs)

func _draw_column_hint(index: int, px: float, font: Font, fs: int) -> void:
	draw_hint_units("column", index, px, font, fs)

func draw_hint_units(axis: String, index: int, cross: float, font: Font, fs: int) -> void:
	var layout: Dictionary = visible_clue_layout(axis, index)
	for unit: Dictionary in visual_hint_units(axis, index).units:
		var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
		var color: Color = ACCENT if unit.kind != "token" else Color(layout.entries[int(unit.index)].color)
		var width: float = clue_text_font(font, text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var baseline: Vector2 = Vector2(float(unit.center) - width/2.0, cross + clue_baseline_offset(fs)) if axis == "row" else Vector2(cross - width/2.0, float(unit.center) + clue_baseline_offset(fs))
		draw_clue_number(font, baseline, text, fs, color, clue_status(axis, index, int(unit.index)))

func glyph_box(text: String, baseline: Vector2, fs: int) -> Rect2:
	var font: Font = clue_text_font(clue_font(), text)
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var result: Rect2
	var advance: float = 0.0
	var first: bool = true
	for c: String in text:
		var glyph: int = ts.font_get_glyph_index(rid, fs, c.unicode_at(0), 0)
		var box: Rect2 = Rect2(baseline + Vector2(advance, 0) + ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph), ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph))
		result = box if first else result.merge(box)
		first = false
		advance += font.get_string_size(c, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# Bound C1/AA and all three statuses, independent of current completion state.
	var width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	result = result.merge(Rect2(baseline - Vector2(0, fs * 0.32 + 1), Vector2(width, 2)))
	return result.grow(maxf(0.5, ui_scale / 4.0))
