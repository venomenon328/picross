extends "res://ui/board.gd"
## Study-only presentation. No animation callback can write model state.
const NUMERAL_FONT = preload("res://art/book/Fraunces.ttf")
const PREVIEW_ALPHA: float = 0.56
const SET_SECONDS: float = 0.140
const REMOVE_SECONDS: float = 0.080
const Marks = preload("res://study/marks.gd")
var marks: Marks
var style: int = 1 # 0 current baseline, 1 ink, 2 pencil
var animations: bool = true
var effects: Dictionary = {}
var preview: Dictionary = {}
var ink_font: FontVariation
var pencil_font: FontVariation
var draw_times_us: Array[int] = []
var measure_draws: bool = false

func _ready() -> void:
	ink_font = make_font(750.0, 20.0)
	pencil_font = make_font(650.0, 70.0)
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

func make_font(weight: float, softness: float) -> FontVariation:
	var font: FontVariation = FontVariation.new()
	font.base_font = NUMERAL_FONT
	font.variation_opentype = {"wght": weight, "opsz": 9.0, "SOFT": softness, "WONK": 1.0}
	font.variation_transform = Transform2D(Vector2(0.86, 0), Vector2(0, 1), Vector2.ZERO)
	return font

func clue_font() -> Font:
	if style == 0 or ink_font == null:
		return super.clue_font()
	return ink_font if style == 1 else pencil_font

func clue_font_size() -> int:
	if style == 0:
		return super.clue_font_size()
	return mini(roundi(16 * ui_scale), maxi(8, floori(view.cell_size - 3)))

func set_style(value: int) -> void:
	cancel_gesture()
	style = clampi(value, 0, 2)
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
		var started: int = Time.get_ticks_usec()
		for change: Dictionary in changes:
			effects[int(change.index)] = {"start": started, "after": int(change.after),
				"seconds": REMOVE_SECONDS if int(change.after) < 0 else SET_SECONDS}
	set_process(not effects.is_empty())

func _process(_delta: float) -> void:
	var now: int = Time.get_ticks_usec()
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
