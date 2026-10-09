extends "res://ui/board.gd"
## Transient cell presentation shared with the isolated study; never writes model state.
const PREVIEW_ALPHA: float = 0.56
const SET_SECONDS: float = 0.140
const REMOVE_SECONDS: float = 0.080
const MAX_STEP_US: int = 8000
const MAX_SPREAD_US: int = 120000
const Marks = preload("res://ui/pencil_marks.gd")
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
	view_changed.connect(clear_effects)
	set_process(false)
	visibility_changed.connect(func() -> void:
		if not is_visible_in_tree():
			clear_effects())

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
	# changes() is model/index ordered. Capture the final G1 direction before
	# finish() cancels the gesture; only this transient presentation is reversed.
	var direction: Vector2i = session.gesture.endpoint - session.gesture.start
	if direction.x < 0 or direction.y < 0:
		changes.reverse()
	var old_cursor: int = session.player.cursor
	super.pointer_release(point, over_board)
	preview.clear()
	if style != 0 and animations and not session.completed and session.player.cursor != old_cursor:
		var started: int = animation_clock.call()
		var count: int = 0
		for change: Dictionary in changes:
			if int(change.after) >= 0:
				count += 1
		var step_us: float = minf(MAX_STEP_US, float(MAX_SPREAD_US) / (count - 1)) if count > 1 else 0.0
		var ordinal: int = 0
		for change: Dictionary in changes:
			var removing: bool = int(change.after) < 0
			var offset: int = 0 if removing else roundi(ordinal * step_us)
			effects[int(change.index)] = {"start": started + offset, "after": int(change.after),
				"seconds": REMOVE_SECONDS if removing else SET_SECONDS}
			if not removing:
				ordinal += 1
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
	if session != null:
		sync_preview()
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
