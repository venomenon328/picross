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
		runner.check(choice.get_popup().get_theme_stylebox("panel").opaque_bounds,"HZ-B popup opaque through its outer padding")
		for step: int in range(choice.item_count+1):
			if choice.get_popup().get_focused_item() == 0: break
			await key(runner,KEY_DOWN)
		runner.check(choice.get_popup().get_focused_item() == 0,"HZ-B native keyboard highlights first row")
		await Capture.capture(runner,"b-sort-%d"%spec[0],Rect2(Vector2(choice.get_popup().position),Vector2(choice.get_popup().size)))
		var popup: PopupMenu = choice.get_popup()
		var pixels: Image = runner.surface.get_texture().get_image()
		for edge: Vector2i in [Vector2i(1,popup.size.y/2),Vector2i(popup.size.x-2,2)]:
			var pixel: Color = pixels.get_pixelv(popup.position+edge)
			var paper := Color("fffaf0")
			runner.check(absf(pixel.r-paper.r)+absf(pixel.g-paper.g)+absf(pixel.b-paper.b) < 0.012,"HZ-B native outer popup pixels are opaque paper")
		var panel_style: StyleBox = popup.get_theme_stylebox("panel")
		var marker_rect := Rect2i(Vector2(popup.position)+Vector2(panel_style.get_margin(SIDE_LEFT),panel_style.get_margin(SIDE_TOP)+3*app.ui_scale),
			Vector2(22*app.ui_scale,popup.get_theme_font("font").get_height(popup.get_theme_font_size("font"))))
		var brown_pixels := 0
		for y: int in range(marker_rect.position.y,marker_rect.end.y):
			for x: int in range(marker_rect.position.x,marker_rect.end.x):
				var pixel: Color = pixels.get_pixel(x,y)
				if pixel.r-pixel.g > 0.04 and pixel.g-pixel.b > 0.04: brown_pixels += 1
		runner.check(brown_pixels == 0,"HZ-B hovered row adds no frame ink in native selection-marker budget")
		await key(runner,KEY_ESCAPE)
		runner.check(not choice.get_popup().visible,"HZ-B native Escape dismisses")
		runner.click(choice)
		runner.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
		await runner.frames()
		for control: Node in choice.get_parent().get_children():
			if control is Button and control.text == "Einstellungen / Info":
				runner.click(control)
				break
		# An offscreen SubViewport has no parent Window focus-in/close request.
		# Check the input guard before delivering that native close notification.
		runner.check(app.album.visible and not app.information.visible,"HZ-B outside press does not activate underlying action")
		choice.get_popup().notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
		await runner.frames()
		runner.check(not choice.get_popup().visible and app.album.visible and not app.information.visible,"HZ-B outside click dismisses without activating underlying action")
		app.show_album()
		await runner.frames()
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
		app._popup_dialog(app.reset_dialog)
		await runner.frames()
		for action: Button in [app.reset_dialog.get_ok_button(),app.reset_dialog.get_cancel_button()]:
			runner.check(action.size.x >= 44*app.ui_scale and action.size.y >= 44*app.ui_scale,"HZ-B native dialog actions retain full minimum hits")
		await Capture.capture(runner,"b-dialog-%d"%spec[0],Rect2(Vector2(app.reset_dialog.position),Vector2(app.reset_dialog.size)))
		runner.click(app.reset_dialog.get_cancel_button())
		await runner.frames()
		runner.check(not app.reset_dialog.visible,"HZ-B native enlarged dialog cancel route")
		# Native-size contact sheet of the actual Button class and SVG resources.
		var panel := Panel.new()
		panel.position = Vector2(50,180)
		panel.size = Vector2(13*56,3*60)*app.ui_scale
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
		var bar := VScrollBar.new()
		bar.theme = preload("res://ui/book_controls.gd").popup_theme("test-scroll",app.ui_scale,app.theme.default_font)
		bar.position = Vector2(675,8)*app.ui_scale
		bar.size = Vector2(28,160)*app.ui_scale
		bar.page = 25
		panel.add_child(bar)
		await Capture.capture(runner,"b-icons-%d"%spec[0],panel.get_global_rect())
		var normal: Button = panel.get_child(23)
		var pressed: Button = panel.get_child(27)
		var motion := InputEventMouseMotion.new()
		motion.position = normal.get_global_rect().get_center()
		runner.surface.push_input(motion,true)
		await runner.frames()
		runner.check(normal.is_hovered(),"HZ-B actual pointer hover state")
		await Capture.capture(runner,"b-hover-%d"%spec[0],panel.get_global_rect())
		motion = InputEventMouseMotion.new()
		motion.position = pressed.get_global_rect().get_center()
		runner.surface.push_input(motion,true)
		var down := InputEventMouseButton.new()
		down.position = motion.position
		down.button_index = MOUSE_BUTTON_LEFT
		down.pressed = true
		runner.surface.push_input(down,true)
		await runner.frames()
		runner.check(pressed.is_pressed(),"HZ-B actual held pointer state")
		await Capture.capture(runner,"b-pressed-%d"%spec[0],panel.get_global_rect())
		down.pressed = false
		runner.surface.push_input(down,true)
		await runner.frames()
		var bar_rect := Rect2i(bar.get_global_rect())
		var normal_pixels: PackedByteArray = runner.surface.get_texture().get_image().get_region(bar_rect).get_data()
		motion = InputEventMouseMotion.new()
		motion.position = bar.global_position + Vector2(bar.size.x/2,
			bar.get_theme_icon("decrement").get_height()+bar.get_theme_stylebox("scroll").get_margin(SIDE_TOP)+bar.get_theme_stylebox("grabber").get_minimum_size().y/2)
		runner.surface.push_input(motion,true)
		await Capture.capture(runner,"b-scroll-hover-%d"%spec[0],panel.get_global_rect())
		var hover_pixels: PackedByteArray = runner.surface.get_texture().get_image().get_region(bar_rect).get_data()
		runner.check(hover_pixels != normal_pixels,"HZ-B native scrollbar pointer hover visibly differs")
		down = InputEventMouseButton.new()
		down.position = motion.position
		down.button_index = MOUSE_BUTTON_LEFT
		down.pressed = true
		runner.surface.push_input(down,true)
		await Capture.capture(runner,"b-scroll-pressed-%d"%spec[0],panel.get_global_rect())
		runner.check(runner.surface.get_texture().get_image().get_region(bar_rect).get_data() != hover_pixels,"HZ-B native held scrollbar visibly differs from hover")
		down.pressed = false
		runner.surface.push_input(down,true)
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
