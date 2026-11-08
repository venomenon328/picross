extends RefCounted
const ViewTitle = preload("res://ui/view_title.gd")
## One instance of each regular settings/help control, two local clip regions.
var app: Control
var help_scroll: ScrollContainer
var right_return: Button
var section: String = "settings"
var settings_heading: ViewTitle
var help_heading: ViewTitle

func _init(owner: Control) -> void:
	app = owner
	var old: Node = app.settings_panel.get_parent()
	var centred := HBoxContainer.new()
	centred.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	centred.alignment = BoxContainer.ALIGNMENT_CENTER
	app.info_scroll.add_child(centred)
	app.settings_panel.reparent(centred)
	help_scroll = app.help_panel.scroll
	app.help_panel.reparent(app.information)
	old.free()
	for panel: Control in [app.settings_panel,app.help_panel]:
		panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		panel.show()
	for scroll: ScrollContainer in [app.info_scroll,help_scroll]:
		scroll.mouse_force_pass_scroll_events = false
	# One fixed group on whichever information page is visible. Reuse the
	# regular controls and callbacks, including their motion/flush guards.
	right_return = app.actions["nav-work"]
	for id: String in ["settings","help"]:
		var button: Button = app.information.get_node(id+"-access")
		button.text = ""
		button.image = load("res://art/book/"+("menu" if id == "settings" else "help")+".svg")
		button.action_id = "information-"+id
	settings_heading = ViewTitle.new()
	app.information.add_child(settings_heading)
	settings_heading.configure("settings",app.settings_title)
	help_heading = ViewTitle.new()
	app.information.add_child(help_heading)
	help_heading.configure("help",app.label("Hilfe",28))

func positions() -> Vector2i:
	return Vector2i(app.info_scroll.scroll_vertical,help_scroll.scroll_vertical)

func focus_navigation() -> void:
	var control: Control = app.ui_scale_choice if section == "settings" else app.information.get_node("settings-access")
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
	var caption: String = "Zurück zum Katalog" if app.information_origin == "album" else "Zurück zum Rätsel"
	var buttons: Array[Button] = [right_return,app.information.get_node("settings-access"),app.information.get_node("help-access")]
	for i: int in range(buttons.size()):
		var button: Button = buttons[i]
		var active: bool = i > 0 and section == ["","settings","help"][i]
		var name: String = "Einstellungen" if i == 1 else "Hilfe"
		button.text = ""
		button.tooltip_text = caption if i == 0 else name+(" (aktuelle Ansicht)" if active else " öffnen")
		button.accessibility_name = button.tooltip_text
		button.ui_scale = u
		button.selected = active
		button.show()
		button.custom_minimum_size = Vector2.ONE*hit
		app._place(button,Rect2(Vector2(edge-(160-i*58)*u,top),Vector2.ONE*hit))
	app.info_scroll.visible = left
	app.help_panel.visible = not left
	settings_heading.visible = left
	help_heading.visible = not left
	var heading: ViewTitle = settings_heading if left else help_heading
	# Protect navigation/feedback and useful scrolling before decorative size.
	# A percentage of the remaining paper scales down in the tight/error case.
	var title_top: float = top+hit+12*u
	var title_height: float = minf(176*u,(bottom-title_top-32*u)*0.27)
	app._place(heading,Rect2(Vector2(x,title_top),Vector2(edge-x,title_height)))
	heading.fallback.add_theme_font_size_override("font_size",roundi(28*u))
	var scroll: Control = app.info_scroll if left else app.help_panel
	var content_top: float = title_top+title_height+16*u
	app._place(scroll,Rect2(Vector2(x,content_top),Vector2(edge-x,maxf(1,bottom-content_top))))
	app._layout_settings(app.info_scroll.size.x)
	if not left: app.help_panel.layout_content()
	# ScrollContainer itself clamps each independent offset after reflow.
	if app.get_viewport().gui_get_focus_owner() != null:
		var focus: Control = app.get_viewport().gui_get_focus_owner()
		if not focus.is_visible_in_tree(): focus.release_focus()
