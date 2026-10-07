extends "res://ui/board.gd"
## Study-only presentation. No animation callback can write model state.
const PREVIEW_ALPHA: float = 0.56
const SET_SECONDS: float = 0.140
const REMOVE_SECONDS: float = 0.080
const CHALKBOARD_ROW_SLOT: float = 26.0
const Marks = preload("res://study/marks.gd")
const Fonts = preload("res://study/fonts.gd")
var font_choice: int = 2 # Chalkboard selected by owner E3; other fonts remain comparison references.
var marks: Marks
var style: int = 2 # 0 historical regular baseline, 2 selected pencil
var animations: bool = true
var effects: Dictionary = {}
var preview: Dictionary = {}
var draw_times_us: Array[int] = []
var measure_draws: bool = false
var animation_clock: Callable = Time.get_ticks_usec

func _ready() -> void:
	marks = Marks.new()
	marks.board = self
	marks.show_behind_parent = true
	marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(marks)
	super._ready()
	set_process(false)
	visibility_changed.connect(func() -> void:
		if not is_visible_in_tree():
			clear_effects())

func clue_font() -> Font:
	return Fonts.selected(font_choice)

func clue_text_font(font: Font, text: String) -> Font:
	return Fonts.REFERENCE if font_choice > 0 and not text.is_valid_int() else font

func clue_font_size() -> int:
	return mini(Fonts.pixel_size(font_choice, super.clue_font_size()), maxi(Fonts.pixel_size(font_choice, 8), floori(view.cell_size - 4)))

func shared_clue_slot_extent(axis: String, font: Font, fs: int) -> float:
	if book_layout and axis == "row" and font_choice == 2:
		return CHALKBOARD_ROW_SLOT * ui_scale
	return super.shared_clue_slot_extent(axis, font, fs)

func clue_tooltip_font_size() -> int:
	return Fonts.pixel_size(font_choice, super.clue_tooltip_font_size())

func clue_baseline_offset(fs: int) -> float:
	if font_choice == 0:
		return super.clue_baseline_offset(fs)
	var bounds: Vector2 = Fonts.ink_vertical(font_choice, fs)
	return -(bounds.x + bounds.y) / 2.0

func clue_vertical_extents(fs: int) -> Vector2:
	if font_choice == 0:
		return super.clue_vertical_extents(fs)
	var bounds: Vector2 = Fonts.ink_vertical(font_choice, fs)
	return Vector2(-bounds.x - clue_baseline_offset(fs), bounds.y + clue_baseline_offset(fs))

func set_font_choice(value: int) -> void:
	font_choice = clampi(value, 0, 2)
	row_slot_extent_cache.clear()
	queue_redraw()

func set_style(value: int) -> void:
	cancel_gesture()
	style = 0 if value == 0 else 2
	row_slot_extent_cache.clear()
	queue_redraw()

func set_animations(enabled: bool) -> void:
	animations = enabled
	if not enabled:
		clear_effects()

func clear_effects() -> void:
	effects.clear()
	set_process(false)
	queue_redraw()

func cancel_gesture() -> void:
	clear_effects()
	preview.clear()
	super.cancel_gesture()

func sync_preview() -> void:
	preview.clear()
	for change: Dictionary in session.gesture.changes():
		preview[int(change.index)] = int(change.after)
		# Supersession is permanent, even if this new preview later retracts.
		effects.erase(int(change.index))
	set_process(not effects.is_empty())

func pointer_press(point: Vector2, button: MouseButton) -> void:
	super.pointer_press(point, button)
	sync_preview()

func pointer_move(point: Vector2, over_board: bool) -> void:
	super.pointer_move(point, over_board)
	sync_preview()

func pointer_release(point: Vector2, over_board: bool) -> void:
	if over_board:
		session.gesture.move(view.hit(point))
	sync_preview()
	var changes: Array = session.gesture.changes()
	var old_cursor: int = session.player.cursor
	super.pointer_release(point, over_board)
	preview.clear()
	if style != 0 and animations and not session.completed and session.player.cursor != old_cursor:
		var started: int = animation_clock.call()
		for change: Dictionary in changes:
			effects[int(change.index)] = {"start": started, "after": int(change.after),
				"seconds": REMOVE_SECONDS if int(change.after) < 0 else SET_SECONDS}
	set_process(not effects.is_empty())

func _process(_delta: float) -> void:
	var now: int = animation_clock.call()
	for index: int in effects.keys():
		var effect: Dictionary = effects[index]
		if float(now - int(effect.start)) / 1000000.0 >= float(effect.seconds):
			effects.erase(index)
	set_process(not effects.is_empty())
	# Only cell marks redraw. Clues, analysis, UI and miniature remain cached.
	if marks != null:
		marks.queue_redraw()

func _draw() -> void:
	super._draw()
	if marks != null:
		marks.visible = style != 0
		marks.queue_redraw()

func draw_active_bands(grid: Rect2, active: Vector2i) -> void:
	if style == 0:
		super.draw_active_bands(grid, active)

func draw_cell(box: Rect2, value: int, index: int) -> void:
	if style == 0:
		super.draw_cell(box, value, index)

func draw_preview() -> void:
	if style == 0:
		super.draw_preview()
