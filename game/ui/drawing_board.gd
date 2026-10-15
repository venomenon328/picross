extends "res://ui/board.gd"
## Transient cell presentation shared with the isolated study; never writes model state.
const PREVIEW_ALPHA: float = 0.56
const SET_SECONDS: float = 0.210
const REMOVE_SECONDS: float = 0.120
const MAX_STEP_US: int = 12000
const MAX_SPREAD_US: int = 180000
const Marks = preload("res://ui/atlas_marks.gd")
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
		marks.tick()

func _draw() -> void:
	if session == null: return
	sync_preview()
	if marks != null:
		marks.visible = style != 0
		marks.sync()
	var began: int = Time.get_ticks_usec()
	if style == 0:
		super._draw()
		return
	# Grid and clues are above cached marks. No inherited all-cell draw loop.
	var grid: Rect2 = view.visible_bounds()
	var values: Array[int] = session.visible_cells()
	sync_clue_completion(values)
	var first: Vector2i = Vector2i(((grid.position-view.origin)/view.cell_size).floor()).max(Vector2i.ZERO)
	var last: Vector2i = Vector2i(((grid.end-view.origin)/view.cell_size).ceil()).min(view.dimensions)
	for x: int in range(first.x,last.x+1):
		var px: float = view.origin.x+x*view.cell_size
		if px >= view.viewport.position.x and px <= view.viewport.end.x:
			draw_grid_line(Vector2(px,grid.position.y),Vector2(px,grid.end.y),"column",x)
	for y: int in range(first.y,last.y+1):
		var py: float = view.origin.y+y*view.cell_size
		if py >= view.viewport.position.y and py <= view.viewport.end.y:
			draw_grid_line(Vector2(grid.position.x,py),Vector2(grid.end.x,py),"row",y)
	var saved_hover: Vector2i = hover
	hover = Vector2i(-1,-1) # bands belong to the independently updated cursor
	_draw_clues(first,last)
	hover = saved_hover
	_draw_clue_tooltip()
	_draw_gesture_counter()
	if measure_draws: draw_times_us.append(Time.get_ticks_usec()-began)

func _gui_input(event: InputEvent) -> void:
	if style != 0 and session != null and not session.completed and event is InputEventMouseMotion and not session.gesture.active and pan_button == MOUSE_BUTTON_NONE:
		hover = view.hit(event.position)
		if hover.x >= 0: pointed.emit(hover)
		update_clue_hover(event.position)
		if marks != null: marks.sync_cursor()
		return
	super._gui_input(event)

func clear_clue_hover() -> void:
	if clue_hover_axis.is_empty() and clue_hover_index == -1: return
	super.clear_clue_hover()

func set_clue_hover(axis: String, index: int) -> void:
	if clue_hover_axis == axis and clue_hover_index == index: return
	super.set_clue_hover(axis,index)

func clear_pointer_hover() -> void:
	clue_pointer_known = false
	if style == 0:
		super.clear_pointer_hover()
		return
	clear_clue_hover()
	if session != null and not session.gesture.active:
		hover = Vector2i(-1,-1)
		if marks != null: marks.sync_cursor()

func draw_active_bands(grid: Rect2, active: Vector2i) -> void:
	if style == 0:
		super.draw_active_bands(grid, active)

func draw_cell(box: Rect2, value: int, index: int) -> void:
	if style == 0:
		super.draw_cell(box, value, index)

func draw_preview() -> void:
	if style == 0:
		super.draw_preview()
