extends RefCounted
const Capture = preload("res://tests/hz_native.gd")
const Paper = preload("res://ui/book_style.gd")
const ButtonInk = preload("res://ui/book_button.gd")

static func key(runner: Object, code: Key) -> void:
	for pressed: bool in [true,false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.pressed = pressed
		runner.surface.push_input(event,true)
	await runner.frames()

static func run(runner: Object) -> void:
	preload("res://tests/hz_b_cases.gd").run(runner)
	var app = runner.app
	var saves: Dictionary = runner.save_bytes()
	var ids: Array = app.album.filtered_ids.duplicate()
	app.show_album()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		runner.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await runner.frames()
		var card = app.choices[0]
		var rect := Rect2(Vector2.ZERO,card.size)
		var initial: Array = card.get_theme_stylebox("normal").contours(rect)
		for state: String in ["hover","pressed","disabled"]:
			runner.check(card.get_theme_stylebox(state).contours(rect) == initial,"HZ-B card states retain stable identity")
		card.grab_focus()
		await Capture.capture(runner,"b-card-%d"%spec[0],card.get_global_rect())
		# A changed order rebuilds nodes, but never changes their identity seed.
		var id: String = card.action_id
		app.album.reverse_sort()
		await runner.frames()
		for rebuilt: Control in app.choices:
			if rebuilt.action_id == id:
				runner.check(rebuilt.get_theme_stylebox("normal").contours(rect) == initial,"HZ-B sorting rebuild preserves card contour")
		app.album.reverse_sort()
		await runner.frames()
		var choice = app.album.sort_choice
		runner.click(choice)
		runner.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
		await runner.frames()
		runner.check(choice.get_popup().visible,"HZ-B sort popup opened by pointer")
		await Capture.capture(runner,"b-sort-%d"%spec[0],Rect2(Vector2(choice.get_popup().position),Vector2(choice.get_popup().size)))
		await key(runner,KEY_ESCAPE)
		runner.check(not choice.get_popup().visible,"HZ-B native Escape dismisses")
		runner.click(choice)
		await runner.frames()
		app.show_information("settings")
		await runner.frames()
		runner.check(not choice.get_popup().visible,"HZ-B view change retires old popup")
		var old_toggle: bool = app.animation_toggle.button_pressed
		app.info_scroll.ensure_control_visible(app.animation_toggle)
		await runner.frames()
		runner.click(app.animation_toggle)
		await runner.frames()
		runner.check(app.animation_toggle.button_pressed != old_toggle,"HZ-B native checkbox pointer toggles")
		app.animation_toggle.grab_focus()
		await key(runner,KEY_SPACE)
		runner.check(app.animation_toggle.button_pressed == old_toggle,"HZ-B native checkbox keyboard toggles")
		await Capture.capture(runner,"b-settings-%d"%spec[0],app.info_scroll.get_global_rect())
		app.info_scroll.ensure_control_visible(app.view_choice)
		await runner.frames()
		runner.click(app.view_choice)
		runner.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
		await runner.frames()
		await Capture.capture(runner,"b-view-%d"%spec[0],Rect2(Vector2(app.view_choice.get_popup().position),Vector2(app.view_choice.get_popup().size)))
		runner.check(app.view_choice.get_popup().is_item_checked(app.view_choice.selected),"HZ-B native selected view check")
		await key(runner,KEY_ESCAPE)
		app.return_to_work()
		await runner.frames()
		# Native-size contact sheet of the actual Button class and SVG resources.
		var panel := Panel.new()
		panel.position = Vector2(50,180)
		panel.size = Vector2(12*56,3*60)*app.ui_scale
		panel.add_theme_stylebox_override("panel",Paper.make("test-sheet",app.ui_scale))
		app.add_child(panel)
		var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
		var n := 0
		for icon: String in icons:
			var button := ButtonInk.new()
			button.action_id = icon
			button.image = load("res://art/book/"+icon+".svg")
			button.ui_scale = app.ui_scale
			button.position = Vector2(8+(n%12)*55,8+(n/12)*56)*app.ui_scale
			button.size = Vector2(44,44)*app.ui_scale
			panel.add_child(button)
			n += 1
		for state: int in range(5):
			var button := ButtonInk.new()
			button.action_id = "fill"
			button.image = load("res://art/book/fill.svg")
			button.ui_scale = app.ui_scale
			button.position = Vector2(8+state*55,120)*app.ui_scale
			button.size = Vector2(44,44)*app.ui_scale
			button.selected = state in [1,4]
			button.disabled = state == 2
			panel.add_child(button)
			if state == 3: button.grab_focus()
			if state == 4: button.set_pressed_no_signal(true)
		await Capture.capture(runner,"b-icons-%d"%spec[0],panel.get_global_rect())
		panel.free()
		app.show_album()
		await runner.frames()
		runner.click(app.album.category_choice)
		await runner.frames()
		runner.surface.size.x -= 1
		await runner.frames()
		runner.check(not app.album.category_choice.get_popup().visible,"HZ-B viewport resize retires popup")
		runner.surface.size.x += 1
	runner.check(app.album.filtered_ids == ids,"HZ-B sorting order restored")
	runner.check(runner.save_bytes() == saves,"HZ-B control-only navigation preserves synthetic puzzle saves")
