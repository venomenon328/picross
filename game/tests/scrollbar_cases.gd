extends RefCounted
## Small SBR regression inside catalog/pages. No new renderer or captures.
const Ink = preload("res://ui/scrollbar_style.gd")

static func viewport_rect(probe, control: Control) -> Rect2:
	var rect: Rect2 = control.get_global_rect()
	if control.get_window() != probe.root: rect.position += Vector2(control.get_window().position)
	return rect

static func bars(node: Node) -> Array[ScrollBar]:
	var result: Array[ScrollBar] = []
	if node is ScrollBar: result.append(node)
	for child: Node in node.get_children(true): result.append_array(bars(child))
	return result

static func theme(probe, bar: ScrollBar, u: float) -> void:
	for name: String in ["scroll","scroll_focus","grabber","grabber_highlight","grabber_pressed"]:
		var style: StyleBox = bar.get_theme_stylebox(name)
		probe.check(style.get_script() == Ink and style.ui_scale == u,"SBR shared scaled StyleBox: "+str(bar.get_path())+"/"+name)
	for prefix: String in ["increment","decrement"]:
		var images: Array[PackedByteArray] = []
		for suffix: String in ["","_highlight","_pressed"]:
			var image: Image = bar.get_theme_icon(prefix+suffix).get_image()
			var n: int = roundi(22*u)
			probe.check(image.get_size() == Vector2i(n,n),"SBR native arrow hit dimensions match track")
			# Closed light triangle has ink in its interior; a recoloured
			# chevron has an empty centre. Backing is graphite, never paper.
			probe.check(image.get_pixel(n/2,n/2).r > 0.8 and image.get_pixel(1,1).r < 0.6,"SBR light solid triangle on graphite backing")
			images.append(image.get_data())
		probe.check(images[0] != images[1] and images[0] != images[2],"SBR distinct native hover and pressed icons")

static func motion(probe, p: Vector2, held: bool = false) -> void:
	var event := InputEventMouseMotion.new()
	event.position = p
	event.button_mask = MOUSE_BUTTON_MASK_LEFT if held else 0
	probe.surface.push_input(event,true)

static func button(probe, p: Vector2, down: bool) -> void:
	var event := InputEventMouseButton.new()
	event.position = p
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = down
	probe.surface.push_input(event,true)

static func range_input(probe, scroller: ScrollContainer) -> void:
	# A changed information header reflows the article. Its finite reading-
	# anchor restore must finish before testing new user scroll commands.
	if scroller == probe.app.info.help_scroll:
		for frame: int in range(12):
			if probe.app.help_panel.restore_frames <= 0: break
			await probe.process_frame
		probe.check(probe.app.help_panel.restore_frames <= 0,"SBR article reflow settled before pointer range test")
	var bar: VScrollBar = scroller.get_v_scroll_bar()
	var limit: float = bar.max_value-bar.page
	probe.check(bar.is_visible_in_tree() and limit > 0,"SBR real overflowing native scroll range: "+str(scroller.get_path())+" limit="+str(limit))
	var rect: Rect2 = viewport_rect(probe,bar)
	var arrow: float = bar.get_theme_icon("increment").get_height()
	var top := Vector2(rect.get_center().x,rect.position.y+arrow*0.5)
	var bottom := Vector2(rect.get_center().x,rect.end.y-arrow*0.5)
	for ratio: float in [0.0,0.5,1.0]:
		bar.value = limit*ratio
		var before: float = bar.value
		probe.click_at(bottom)
		await probe.frames()
		probe.check(bar.value > before if ratio < 1 else bar.value == limit,"SBR native increment at start/middle/end")
		bar.value = before
		probe.click_at(top)
		await probe.frames()
		probe.check(bar.value < before if ratio > 0 else bar.value == 0,"SBR native decrement at start/middle/end")
	# Native track paging and thumb dragging; geometry from the documented
	# StyleBox margins and range, with no replacement input controller.
	for ratio: float in [0.0,0.5,1.0]:
		bar.value = limit*ratio
		var before: float = bar.value
		probe.click_at(Vector2(rect.get_center().x,rect.end.y-arrow-5))
		await probe.create_timer(0.3).timeout
		probe.check(bar.value > before if ratio < 1 else bar.value == limit,"SBR native track down at start/middle/end")
		bar.value = before
		probe.click_at(Vector2(rect.get_center().x,rect.position.y+arrow+5))
		await probe.create_timer(0.3).timeout
		probe.check(bar.value < before if ratio > 0 else bar.value == 0,"SBR native track up at start/middle/end")
	bar.value = 0
	var thumb_min: float = bar.get_theme_stylebox("grabber").get_minimum_size().y
	var track_margin: float = bar.get_theme_stylebox("scroll").get_minimum_size().y
	var area: float = rect.size.y-2*arrow-track_margin-thumb_min
	var thumb_size: float = bar.page/(bar.max_value-bar.min_value)*area+thumb_min
	for route: Vector2 in [Vector2(0,0.5),Vector2(0.5,1),Vector2(1,0)]:
		bar.value = limit*route.x
		var start := Vector2(rect.get_center().x,rect.position.y+arrow+track_margin*0.5+thumb_size*0.5+area*bar.value/(bar.max_value-bar.min_value))
		motion(probe,start)
		button(probe,start,true)
		var delta: float = area*limit/(bar.max_value-bar.min_value)*(route.y-route.x)
		motion(probe,start+Vector2(0,delta),true)
		button(probe,start+Vector2(0,delta),false)
		probe.check(absf(bar.value-limit*route.y) <= 2,"SBR native thumb from start/middle/end reaches middle/end/start")
	for ratio: float in [0.0,0.5,1.0]:
		bar.value = limit*ratio
		var before: float = bar.value
		probe.click_at(viewport_rect(probe,scroller).get_center(),MOUSE_BUTTON_WHEEL_DOWN)
		await probe.frames()
		probe.check(bar.value > before if ratio < 1 else bar.value == limit,"SBR wheel down over content at start/middle/end")
		bar.value = before
		probe.click_at(viewport_rect(probe,scroller).get_center(),MOUSE_BUTTON_WHEEL_UP)
		await probe.frames()
		probe.check(bar.value < before if ratio > 0 else bar.value == 0,"SBR wheel up over content at start/middle/end")
	bar.value = 0

static func run(probe) -> void:
	var app = probe.app
	var album = app.album
	var saved: Dictionary = probe.save_bytes()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1200,1.25],[1920,1080,1.0]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await probe.frames()
		for bar: ScrollBar in bars(app):
			# Hidden popup choices are restyled when their panel opens; they
			# deliberately retain the previous scale while not in use.
			if bar.is_visible_in_tree(): theme(probe,bar,app.ui_scale)
		for half: ScrollContainer in [album.scroll,album.right_scroll]:
			var bar: VScrollBar = half.get_v_scroll_bar()
			probe.check(is_equal_approx(bar.get_combined_minimum_size().x,roundi(22*app.ui_scale)),"SBR actual scaled gutter width")
			probe.check(is_equal_approx(album._available_card_width(half),half.size.x-bar.get_combined_minimum_size().x-2*app.ui_scale),"SBR measured gutter reserved even when hidden")
			probe.check(half.get_global_rect().encloses(bar.get_global_rect()),"SBR complete native bar stays inside half")
		probe.check(album.grid.columns == album.right_grid.columns and album.grid.get_child_count() == 12 and album.right_grid.get_child_count() == 12,"SBR symmetric 12/12 capacity")
	# Decoration is reproducible across redraw/state/size roundtrips. Its
	# bounded strokes include the AA envelope, unlike large-paper contours.
	var style = album.scroll.get_v_scroll_bar().get_theme_stylebox("scroll")
	for length: float in [48,600]:
		var rect := Rect2(0,0,22,length)
		var lines: Array = style.hatching(rect)
		probe.check(lines == style.hatching(rect) and lines.size() > 2,"SBR deterministic short/long hand hatch")
		probe.check(lines[0][0].y-lines[1][0].y != lines[1][0].y-lines[2][0].y,"SBR hatch spacing varies")
		for line: PackedVector2Array in lines:
			for p: Vector2 in line: probe.check(rect.grow(-1).has_point(p),"SBR hatch and AA bounded inside track")
		probe.check(style.outline(rect) == album.right_scroll.get_v_scroll_bar().get_theme_stylebox("scroll_focus").outline(rect),"SBR focus retains decorative geometry")
	await range_input(probe,album.scroll)
	await range_input(probe,album.right_scroll)
	probe.check(album.visible and not app.work.visible,"SBR scrollbar input never opens a card")
	album.scroll.scroll_vertical = 70
	album.right_scroll.scroll_vertical = 140
	probe.surface.size = Vector2i(1280,720)
	app.set_ui_scale(1.25)
	app.show_information("help")
	await probe.frames()
	# With the title back at the top, the short opening chapter can fit.
	# Exercise the scrollbar on the existing longer navigation chapter.
	app.help_panel.choose(2)
	await probe.frames()
	var help: ScrollContainer = app.info.help_scroll
	theme(probe,help.get_v_scroll_bar(),app.ui_scale)
	await range_input(probe,help)
	help.scroll_vertical = 100
	app._information_section("settings")
	await probe.frames()
	await range_input(probe,app.info_scroll)
	app.info_scroll.scroll_vertical = 40
	var pair: Vector2i = app.info.positions()
	app._information_section("help")
	await probe.frames()
	probe.check(app.info.positions() == pair,"SBR independent information positions survive pan")
	app.return_to_work()
	await probe.frames()
	probe.check(album.positions() == Vector2i(70,140),"SBR both catalog positions survive information visit")
	# Need-only visibility and no invisible bar target, using a real short
	# context (category with six entries). Returning resets/clamps natively.
	album.choose_category("voegel")
	probe.surface.size = Vector2i(2560,1440)
	app.set_ui_scale(1.0)
	await probe.frames()
	probe.check(not album.right_scroll.get_v_scroll_bar().visible,"SBR no bar without right-half content")
	album.choose_category("")
	probe.surface.size = Vector2i(1920,1080)
	await probe.frames()
	# Real embedded long PopupMenu: same explicit family, wheel and Escape
	# stay inside the native menu and cannot alter the selected category.
	var choice: OptionButton = album.category_choice
	var original: int = choice.selected
	var original_count: int = choice.item_count
	for index: int in range(60): choice.add_item("TEST ONLY lange Scrolloption %d" % index)
	probe.click(choice)
	probe.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
	await probe.frames()
	var popup: PopupMenu = choice.get_popup()
	probe.check(popup.visible,"SBR category popup opens")
	var overflow: ScrollContainer
	for bar: ScrollBar in bars(popup):
		theme(probe,bar,app.ui_scale)
		if bar is VScrollBar and bar.visible: overflow = bar.get_parent()
	probe.check(overflow != null,"SBR actual long popup exposes native scroll container")
	if overflow != null: await range_input(probe,overflow)
	probe.click_at(Vector2(popup.position)+Vector2(popup.size)*0.5,MOUSE_BUTTON_WHEEL_DOWN)
	var escape := InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	probe.surface.push_input(escape,true)
	await probe.frames()
	probe.check(not popup.visible and choice.selected == original and album.visible,"SBR popup Escape preserves selection without click-through")
	probe.click(choice)
	probe.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
	await probe.frames()
	probe.click_at(Vector2(popup.position)-Vector2(5,5))
	await probe.frames()
	probe.check(choice.selected == original and album.visible,"SBR popup outside click is isolated from cards")
	# Offscreen input has no OS focus server to close this embedded Window.
	# Actual desktop outside-close remains part of M01; hide only for cleanup.
	popup.hide()
	while choice.item_count > original_count: choice.remove_item(choice.item_count-1)
	probe.surface.size = Vector2i(1280,720)
	app.set_ui_scale(1.25)
	await probe.frames()
	album.open_filters()
	await probe.frames()
	# A long draft error forces the existing narrow panel's need-only path;
	# no production data or permanent UI text is added.
	album.filter_panel.error.text = "TEST ONLY langer Entwurfsfehler. ".repeat(100)
	album.filter_panel.error.show()
	album.filter_panel._fit_content()
	await probe.frames()
	for bar: ScrollBar in bars(album.filter_panel): theme(probe,bar,app.ui_scale)
	await range_input(probe,album.filter_panel.scroller)
	album.filter_panel.hide()
	probe.check(probe.save_bytes() == saved,"SBR style and scrolling never mutate saves")
	album.scroll.scroll_vertical = 0
	album.right_scroll.scroll_vertical = 0
	probe.surface.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	await probe.frames()
	probe.catalog_case("sbr-scrollbars")
