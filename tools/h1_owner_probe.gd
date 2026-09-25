extends SceneTree
## External, explicitly synthetic owner test. Run with the exported P1 executable.
## No SaveStore, no registered album fixture, no access to normal user saves.
const Board = preload("res://ui/board.gd")
const Session = preload("res://model/session.gd")
const Miniature = preload("res://ui/miniature.gd")
var board: Board
var mini: Miniature

func _initialize() -> void:
	call_deferred("build")

func build() -> void:
	root.size = Vector2i(1280, 720)
	root.title = "H1 · Isolierte Linienprobe · kein Produkträtsel"
	var page: VBoxContainer = VBoxContainer.new()
	page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(page)
	var note: Label = Label.new()
	note.text = "H1 · Künstliche Linien, keine Speicherung. Zeile 1: 3 5; Zeile 2: 3 3; Zeile 3: 10; Zeile 4: vier Farben.\nZeile 1/2: Spalten 9–11 füllen, dann X in 8 und 12. Zeile 1: X in 13–20 erzeugen Widerspruch."
	page.add_child(note)
	var tools: HBoxContainer = HBoxContainer.new()
	page.add_child(tools)
	var data: Dictionary = {"id": "H1-TEST", "width": 20, "height": 20, "rows": [], "columns": [], "solution": [], "reveal": {}, "palette": [
		{"id": 1, "color": "#343f42", "symbol": "A"}, {"id": 2, "color": "#cd613e", "symbol": "B"},
		{"id": 3, "color": "#e8b945", "symbol": "C"}, {"id": 4, "color": "#487e9b", "symbol": "D"}]}
	for i: int in range(20):
		data.rows.append([])
		data.columns.append([])
		var row: Array[int] = []
		row.resize(20)
		row.fill(0)
		data.solution.append(row)
	data.rows[0] = [{"length": 3, "color": 1}, {"length": 5, "color": 1}]
	data.rows[1] = [{"length": 3, "color": 1}, {"length": 3, "color": 1}]
	data.rows[2] = [{"length": 10, "color": 1}]
	data.rows[3] = [{"length": 3, "color": 1}, {"length": 3, "color": 2}, {"length": 3, "color": 3}, {"length": 3, "color": 4}]
	board = Board.new()
	board.session = Session.new(data)
	for i: int in range(4):
		var color: int = i + 1
		add_button(tools, "Farbe " + str(color), func() -> void: board.active_color = color; board.eraser = false)
	add_button(tools, "Radierer", func() -> void: board.eraser = true)
	add_button(tools, "Undo", func() -> void: board.session.undo(); refresh())
	add_button(tools, "Redo", func() -> void: board.session.redo(); refresh())
	add_button(tools, "Leeren", func() -> void: board.cancel_gesture(); board.session = Session.new(data); refresh())
	var toggle: CheckBox = CheckBox.new()
	toggle.text = "Erfüllte Hinweise markieren"
	toggle.button_pressed = true
	toggle.toggled.connect(func(value: bool) -> void: board.mark_completed_clues = value; refresh())
	tools.add_child(toggle)
	var work: HBoxContainer = HBoxContainer.new()
	work.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(work)
	board.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	work.add_child(board)
	mini = Miniature.new()
	mini.custom_minimum_size = Vector2(180, 180)
	mini.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	work.add_child(mini)
	board.edited.connect(refresh)
	refresh()
	if OS.get_cmdline_user_args().has("--h1-probe-smoke"):
		print("H1_OWNER_PROBE_OK")
		quit()

func refresh() -> void:
	# This deliberately inconsistent line worksheet has no completion/reveal mode.
	board.session.completed = false
	board.queue_redraw()
	mini.cells = board.session.visible_cells()
	mini.width = 20
	mini.height = 20
	mini.palette = board.session.definition.palette
	mini.queue_redraw()

func add_button(parent: Control, text: String, action: Callable) -> void:
	var button: Button = Button.new()
	button.text = text
	button.pressed.connect(action)
	parent.add_child(button)
