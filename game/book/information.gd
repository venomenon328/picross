extends RefCounted
## One instance of each regular settings/help control, two local clip regions.
var app: Control
var help_scroll: ScrollContainer
var right_return: Button
var section: String = "settings"

func _init(owner: Control) -> void:
	app = owner
	var old: Node = app.settings_panel.get_parent()
	app.settings_panel.reparent(app.info_scroll)
	help_scroll = ScrollContainer.new()
	help_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	app.information.add_child(help_scroll)
	app.help_panel.reparent(help_scroll)
	old.free()
	for panel: Control in [app.settings_panel,app.help_panel]:
		panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		panel.show()
	for scroll: ScrollContainer in [app.info_scroll,help_scroll]:
		scroll.mouse_force_pass_scroll_events = false
	right_return = app._text_button("Zurück zum Katalog",app.return_to_work)
	right_return.name = "information-return"
	app.information.add_child(right_return)
	# Reuse the existing section shortcuts; each belongs to the opposite page.
	app.information.get_node("help-access").text = "Hilfe →"
	app.information.get_node("settings-access").text = "← Einstellungen"

func positions() -> Vector2i:
	return Vector2i(app.info_scroll.scroll_vertical,help_scroll.scroll_vertical)

func focus_navigation() -> void:
	var control: Control = app.ui_scale_button if section == "settings" else app.information.get_node("settings-access")
	control.focus_mode = Control.FOCUS_ALL
	control.grab_focus()

func present(value: String, fresh: bool = false) -> void:
	section = value
	app.information_section = value
	app.work.hide()
	app.ending.hide()
	app.album.hide()
	app.album.suspend()
	app.stress_label.hide()
	app.information.show()
	if fresh:
		app.info_scroll.scroll_vertical = 0
		help_scroll.scroll_vertical = 0
	app._layout_book()
	focus_navigation()

func layout() -> void:
	var u: float = app.ui_scale
	var left: bool = section == "settings"
	var paper: Rect2 = app.book.projected_information(-1 if left else 1)
	# Exclude the resting curve, paper perimeter and viewport bottom. The
	# near camera intentionally shows only the upper part of a physical leaf.
	var curve: float = paper.size.x*0.075
	var x: float = paper.position.x+(24*u if left else curve+24*u)
	var edge: float = paper.end.x-(curve+24*u if left else 24*u)
	var top: float = maxf(24*u,paper.position.y+20*u)
	var bottom: float = minf(app.book.get_viewport().size.y-24*u,paper.end.y-24*u)
	# Native save/recovery feedback belongs to the currently visible paper,
	# including the left settings page. Reserve it outside the scrolling text.
	if app.status_label.visible:
		bottom -= 124*u
		app._place(app.status_label,Rect2(Vector2(x,bottom+8*u),Vector2(edge-x,64*u)))
		app._place(app.work_repair_button,Rect2(Vector2(x,bottom+76*u),Vector2(340,44)*u))
	var hit: float = 44*u
	var back: Button = app.actions["nav-work"] if left else right_return
	var switch: Button = app.information.get_node("help-access" if left else "settings-access")
	var caption: String = "Zurück zum Katalog" if app.information_origin == "album" else "Zurück zum Rätsel"
	for button: Button in [app.actions["nav-work"],right_return]:
		button.text = caption
		button.tooltip_text = caption
		button.accessibility_name = caption
		button.ui_scale = u
		button.custom_minimum_size = Vector2(260,44)*u
	app.actions["nav-work"].visible = left
	right_return.visible = not left
	app.information.get_node("help-access").visible = left
	app.information.get_node("settings-access").visible = not left
	app.info_scroll.visible = left
	help_scroll.visible = not left
	app._place(back,Rect2(Vector2(x,top),Vector2(260*u,hit)))
	app._place(switch,Rect2(Vector2(edge-210*u,top),Vector2(210*u,hit)))
	var scroll: ScrollContainer = app.info_scroll if left else help_scroll
	app._place(scroll,Rect2(Vector2(x,top+hit+24*u),Vector2(edge-x,bottom-top-hit-24*u)))
	for panel: Control in [app.settings_panel,app.help_panel]:
		panel.add_theme_constant_override("separation",roundi(16*u))
		for child: Node in panel.get_children():
			if child is Label: child.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	# ScrollContainer itself clamps each independent offset after reflow.
	if app.get_viewport().gui_get_focus_owner() != null:
		var focus: Control = app.get_viewport().gui_get_focus_owner()
		if not focus.is_visible_in_tree(): focus.release_focus()
