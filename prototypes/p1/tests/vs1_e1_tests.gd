extends SceneTree
const Cases = preload("res://tests/vs1_e1_cases.gd")
const Session = preload("res://model/session.gd")
var checks: int = 0
var failures: int = 0
var board: Control

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		if failures < 20: printerr("VS1 E1 FAIL: ", message)

func run() -> void:
	var template: Dictionary = load("res://full_view_study/catalog.gd").definitions()[0]
	board = load("res://full_view_study/board.gd").new()
	board.session = Session.new(template)
	board.book_layout = true
	board.size = Vector2(1800,900)
	root.add_child(board)
	await process_frame
	for ui: float in [1.0,1.25]:
		board.ui_scale = ui
		for n: int in range(1,6):
			board.session = Session.new(Cases.fixture(template,n))
			for mode: String in ["G","V"]:
				board.mode = mode
				board.fit_all()
				check(board.reserve_slots == Vector2i(n,n), "actual max1–5 reserves no padded slots")
				check(board.book_inset == Vector2(n*26,n*18)*ui+Vector2(6,6), "short axis reserve precedes fit")
				check(is_equal_approx(board.view.cell_size,board.fit_ceiling), "fit reaches computed ceiling")
				Cases.drag_probe(board,check)
		var previous: Array = []
		for transposed: bool in [false,true]:
			for n: int in [5,6,7,25]:
				board.session = Session.new(Cases.fixture(template,n,true,transposed))
				board.mode = "G"
				board.fit_all()
				print("VS1_E1_RESERVE ui=",ui," max=",n," transpose=",transposed," actual=",board.reserve_slots," ceilings=",board.raw_fit)
				var actual: int = board.reserve_slots.y if transposed else board.reserve_slots.x
				check(actual == n if n <= 7 else actual >= 7 and actual < n, "5/6/7 full; long reserve passes actual marker/movement need")
				check((board.reserve_slots.x if transposed else board.reserve_slots.y) == 1, "long line leaves other axis actual short")
				# Six pixels outer gap plus the actual two-pixel frame stroke.
				var vertical: float = (board.size.y-board.book_inset.y-8)/board.session.player.height
				var horizontal: float = (board.size.x-board.book_inset.x-8)/board.session.player.width
				check(absf(board.raw_fit-minf(vertical,horizontal)) < 0.001, "both axis ceilings; width/height limiting axis")
				if transposed and not previous.is_empty():
					check(board.raw_fit <= previous[-1] + 0.001, "larger actual top reserve cannot enlarge fit")
				previous.append(board.raw_fit)
				Cases.drag_probe(board,check)
				board.requested_cell = 100.0
				board._layout()
				check(board.view.cell_size <= board.fit_ceiling, "restored excessive desired zoom capped")
				for direction: int in [-1,1]:
					for step: int in range(30):
						board.zoom(direction,board.view.viewport.get_center())
						check(board.view.cell_size <= board.fit_ceiling and board.view.viewport.grow(0.01).encloses(board.view.bounds().grow(1.0)), "all zoom paths keep complete grid frame")
				board.fit_all()
			previous.clear()
	# Existing long color cases, real multi-digit counts, both axes and states.
	for index: int in [3,5,7,9]:
		board.session = Session.new(load("res://full_view_study/catalog.gd").definitions()[index])
		board.mode = "G"
		board.fit_all()
		for status: int in range(3):
			for y: int in range(board.session.player.height):
				for x: int in range(board.session.player.width):
					var solution: int = board.session.definition.solution[y][x]
					board.session.player.cells[y*board.session.player.width+x] = -1 if status == 0 or (status == 1 and solution == 0) else solution
			board.sync_clue_completion(board.session.visible_cells())
			var reserve: Vector2i = board.reserve_slots
			Cases.drag_probe(board,check)
			board._layout()
			check(board.reserve_slots == reserve, "completion never changes reserve or fit")
	print("VS1_E1_TESTS_", "OK" if failures == 0 else "FAILED", " checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
