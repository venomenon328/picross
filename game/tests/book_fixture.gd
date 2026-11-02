extends "res://book/main.gd"
## Focused native component cases settle the real presentation synchronously.
## Unaccelerated input/motion/lifecycle proofs use main.tscn without this fixture.
const Product = preload("res://book/main.gd")
var content_script: Script

class ImmediateContent extends "res://book/content.gd":
	func finish_navigation() -> void:
		book.interrupt("focus")
		# These component cases own no physical held button. Real release-barrier
		# assertions live in the unmodified product-root integration/Windows runs.
		book.held_buttons = 0
		book.release_barrier = false
		album.locked = false
		process_mode = Node.PROCESS_MODE_INHERIT
	func select_puzzle(index: int) -> void:
		if not album.visible: show_album()
		super.select_puzzle(index)
		finish_navigation()
	func open_puzzle() -> void:
		super.open_puzzle()
		if not presentation_locked and (work.visible or ending.visible):
			book.state = book.State.WORK
			book.selected_id = str(session.definition.id)
			book.page_identity(book.paper_material,"work/"+book.selected_id)
			book._pose(1)
	func show_information(section: String = "settings") -> void:
		super.show_information(section)
		finish_navigation()
	func return_to_work() -> void:
		super.return_to_work()
		finish_navigation()

func create_content() -> Content:
	return content_script.new() if content_script != null else ImmediateContent.new()

func request_open(id: String) -> bool:
	var accepted: bool = super.request_open(id)
	if accepted: app.finish_navigation()
	return accepted

func request_return() -> bool:
	var accepted: bool = super.request_return()
	if accepted: app.finish_navigation()
	return accepted

func request_page(target: int) -> bool:
	var accepted: bool = super.request_page(target)
	if accepted: app.finish_navigation()
	return accepted

static func attach(parent: Node, custom_content: Script = null) -> Content:
	var instance = load("res://main.tscn").instantiate()
	assert(instance.get_script() == Product,"Native probe must enter the regular book scene")
	instance.set_script(load("res://tests/book_fixture.gd"))
	instance.content_script = custom_content
	parent.add_child(instance)
	return instance.app

static func dispose(ui: Node, deferred: bool = false) -> void:
	var target: Node = ui.book if ui is Content and ui.book != null else ui
	if deferred: target.queue_free()
	else: target.free()
