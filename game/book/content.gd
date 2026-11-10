extends "res://ui/main.gd"
## Regular product lifecycle with the shared book presentation.
const Surface = preload("res://book/surface.gd")
const CatalogSpread = preload("res://book/catalog.gd")
const Information = preload("res://book/information.gd")
const ViewTitle = preload("res://ui/view_title.gd")
const Marginalia = preload("res://book/marginalia.gd")
const PuzzleBackground = preload("res://book/puzzle_background.gd")
signal opening_requested(id: String)
signal return_requested
signal catalog_shown
signal exit_requested
signal scale_changing
var resetting_ending: bool = false
var book: Node3D
var info: RefCounted
var presentation_locked: bool = false
var save_retry: BookButton
var catalog_title: ViewTitle
var recent_panel: BookButton
var recent_retry: BookButton
var recent_signature: String = ""
var marginalia: Marginalia
var puzzle_background: PuzzleBackground
var background_visit: int = 0
var background_binding: Dictionary = {}

func configure_catalog(_catalog: Control) -> void: pass

func _build() -> void:
	# Configure the replacement catalog before its first _ready(). Only the
	# study subclass installs an in-memory preference through this hook.
	var parent: Node = get_parent()
	parent.remove_child(self)
	laying_out = true
	super._build()
	laying_out = false
	catalog_title = ViewTitle.new()
	page.add_child(catalog_title)
	var catalog_fallback: Label = label("Rätselkatalog",28)
	catalog_fallback.add_theme_font_override("font",WORK_TITLE_FONT)
	catalog_title.configure("catalog",catalog_fallback)
	# Reuse the three existing right slots and their sidebar axis.
	album_button.free()
	actions.erase("nav-album")
	album_button = actions["nav-information"]
	album_button.pressed.disconnect(show_information.bind("settings"))
	album_button.pressed.connect(func() -> void: return_requested.emit())
	album_button.action_id = "nav-work"
	album_button.name = "catalog-return"
	album_button.image = load("res://art/book/nav-work.svg")
	album_button.tooltip_text = "Zurück zum Katalog"
	album_button.accessibility_name = "Zurück zum Katalog"
	for id: String in ["help","menu","nav-information"]: actions[id].reparent(page)
	var old_album: Control = album
	page.remove_child(old_album)
	old_album.free()
	album = CatalogSpread.new()
	page.add_child(album)
	album.opened.connect(select_by_id)
	album.reset_requested.connect(_ask_reset_id)
	album.repair_requested.connect(_ask_repair_id)
	album.information_requested.connect(show_information.bind("settings"))
	album.help_requested.connect(show_information.bind("help"))
	album.quit_requested.connect(leave_app)
	configure_catalog(album)
	var previous: Control = surface
	remove_child(previous)
	previous.free()
	surface = Surface.new()
	surface.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(surface)
	move_child(surface, 0)
	parent.add_child(self)
	for item: Node in find_children("*","Button",true,false):
		if item is BookButton: item.paper_transparent = true
		if item is BookChoice: item.paper_transparent = true
	save_retry = _text_button("Speichern erneut versuchen",_save_current)
	save_retry.paper_transparent = true
	page.add_child(save_retry)
	save_retry.hide()
	recent_panel = preload("res://ui/recent_panel.gd").new()
	page.add_child(recent_panel)
	recent_panel.pressed.connect(resume_recent)
	recent_panel.hide()
	recent_retry = _text_button("Fortsetzen-Merker: erneut versuchen",func() -> void: recent.retry())
	recent_retry.paper_transparent = true
	album.notices.add_child(recent_retry)
	recent_retry.hide()
	marginalia = Marginalia.new()
	page.add_child(marginalia)
	page.move_child(marginalia,0)
	puzzle_background = PuzzleBackground.new()
	page.add_child(puzzle_background)
	page.move_child(puzzle_background,0)
	puzzle_background.hide()

func _background_binding() -> Dictionary:
	if session == null: return {}
	var entry: Dictionary = Registry.by_id(str(session.definition.id))
	return {"id":str(session.definition.id),"background":entry.get("background",{"status":"legacy","image_revision":null,"asset":null})}

func begin_background_visit() -> void:
	if puzzle_background == null or session == null: return
	background_visit += 1
	background_binding = _background_binding()
	puzzle_background.begin_visit(Registry.by_id(str(session.definition.id)),background_visit)

func publish_background_visit() -> void:
	if puzzle_background == null or session == null: return
	# Preparation and settlement publish the SAME visit. A restored source or
	# changed image binding instead begins a fresh visit and freezes it now.
	if background_binding.is_empty() or background_binding != _background_binding():
		begin_background_visit()
	puzzle_background.publish(background_visit)

func leave_background_visit() -> void:
	background_binding.clear()
	if puzzle_background != null:
		puzzle_background.leave()
		puzzle_background.hide()

func open_puzzle() -> void:
	# Freeze before super exposes the destination or lays it out in a capture.
	publish_background_visit()
	super.open_puzzle()

func _process(_delta: float) -> void:
	if recent_retry == null: return
	var message: String = recent.message()
	recent_retry.visible = not message.is_empty()
	recent_retry.tooltip_text = message
	# Both marker errors and retry are separate from save-slot diagnostics.
	# They remain reachable on returning to the catalog, without blocking work.
	if _refresh_recent_panel(): _layout_book()

func _refresh_recent_panel() -> bool:
	if recent_panel == null: return false
	var id: String = recent_id()
	recent_panel.visible = album.visible and not id.is_empty()
	recent_panel.disabled = presentation_locked or album.locked
	if not recent_panel.visible:
		recent_signature = ""
		return false
	var item: Session = sessions[int(session_indices[id])]
	var signature: String = id+"/"+str(item.definition.revision)+"/"+str(ui_scale)
	# Compare the owned cell snapshot, not just a hash or a mutable array alias.
	if recent_signature == signature and recent_panel.preview.cells == item.player.cells: return false
	recent_signature = signature
	recent_panel.present(item)
	return true

func resume_recent() -> void:
	if presentation_locked or album.locked or not album.visible: return
	super.resume_recent()

func _layout_book(prepare_board: bool = false) -> void:
	super._layout_book(prepare_board)
	if album == null or surface == null or laying_out: return
	if info == null: return
	var material: Rect2 = surface.material_rect()
	var title_origin: Vector2 = material.position+Vector2(material.size.x*0.12,38*ui_scale)
	for id: String in ["help","menu","nav-information"]:
		actions[id].visible = work.visible or ending.visible
	if work.visible or ending.visible:
		var paper_top: float = book.projected_paper(true).position.y if book != null else 0.0
		title_origin.y = maxf(title_origin.y,paper_top+12*ui_scale)
		title.position = title_origin
		var axis: float = actions["menu"].position.x
		album_button.position.x = axis-58*ui_scale
		actions["help"].position.x = axis+58*ui_scale
		for id: String in ["help","menu","nav-information"]:
			# Five pixels clear the paper rim while preserving the independent
			# preview frame's alpha envelope below the 44-pixel hit targets.
			actions[id].position.y = maxf(actions["menu"].position.y,paper_top+5*ui_scale)
	layout_warning.position.x = maxf(layout_warning.position.x, title_origin.x)
	title.visible = work.visible or ending.visible
	if catalog_title != null: catalog_title.visible = album.visible
	if information.visible: info.layout()
	if save_retry != null:
		save_retry.visible = session != null and not slot_errors[sessions.find(session)].is_empty() and not work_repair_button.visible
		if album.visible:
			# Also reachable when a blocked slot is outside the current filter.
			if save_retry.get_parent() != album.notices: save_retry.reparent(album.notices)
			save_retry.custom_minimum_size.y = 44*ui_scale
		else:
			if save_retry.get_parent() != page: save_retry.reparent(page)
			_place(save_retry,Rect2(work_repair_button.position,Vector2(340,44)*ui_scale))
	if album.summary != null: album.summary.visible = album.visible and catalog_error.is_empty()
	if album.notice_area != null: album.notice_area.visible = album.visible
	# Layout also runs while processing is disabled for the book capture. Bind
	# the destination now, before its first rendered frame, rather than waiting
	# for _process (or any input) after the transition has settled.
	_refresh_recent_panel()
	if album.visible:
		# Projected paper is already in viewport pixels, including letterboxing.
		# Use that one coordinate system for heading, clip areas and both footers.
		var left_paper: Rect2 = book.projected_paper(false,-1)
		var right_paper: Rect2 = book.projected_paper(false,1)
		var inset: float = 18*ui_scale
		var margin: float = left_paper.position.x+inset
		var edge: float = right_paper.end.x-inset
		var curve: float = left_paper.size.x*0.075
		album.fold_gap = 2*(curve+12*ui_scale)
		var right_heading: float = right_paper.position.x+curve+inset
		var heading_top: float = maxf(left_paper.position.y+12*ui_scale,material.size.y*0.035+12*ui_scale)
		# A larger drawing follows available paper height, with a compact fallback.
		var title_height: float = maxf(128*ui_scale,clampf(left_paper.size.y*0.14,64*ui_scale,110*ui_scale))
		# Reserve a full retry target plus breathing room above the recent panel,
		# even with no error. Showing/scrolling notices must not move the catalog.
		# Navigation and count share the top edge. Only actual text height,
		# notices and the existing recent/title budget determine later rows.
		album._style_controls(album.navigation)
		var nav_width: float = album.navigation.get_combined_minimum_size().x
		var summary_width: float = maxf(1,edge-nav_width-14*ui_scale-right_heading)
		var summary_font: int = roundi(18*ui_scale)
		album.summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		album.summary.add_theme_font_size_override("font_size",summary_font)
		_place(album.summary,Rect2(Vector2(right_heading,heading_top),Vector2(summary_width,26*ui_scale)))
		var summary_height: float = maxf(26*ui_scale,album.summary.get_minimum_size().y)
		var notice_top: float = heading_top+summary_height+2*ui_scale
		var panel_top: float = notice_top+52*ui_scale
		var catalog_top: float = maxf(heading_top+title_height+28*ui_scale,panel_top+76*ui_scale)
		album.right_pager.vertical = false
		_place(album, Rect2(Vector2(margin,catalog_top),Vector2(edge-margin,left_paper.end.y-inset-catalog_top)))
		_place(catalog_title, Rect2(Vector2(margin,heading_top),Vector2(left_paper.end.x-curve-inset-margin,title_height)))
		catalog_title.fallback.add_theme_font_size_override("font_size",roundi(28*ui_scale))
		if album.summary != null:
			_place(album.summary,Rect2(Vector2(right_heading,heading_top),Vector2(summary_width,summary_height)))
		if album.navigation != null:
			_place(album.navigation,Rect2(Vector2(edge-nav_width,heading_top),Vector2(nav_width,44*ui_scale)))
		# Messages use the existing free heading area. Its fixed, scrollable
		# bounds never enter either page's card/control layout, even on failure.
		if recent_panel != null:
			recent_panel.ui_scale = ui_scale
			var available: float = edge-right_heading
			var panel_height: float = 68*ui_scale
			var panel_width: float = available/2 if recent_panel.fits(available/2,panel_height) else available
			_place(recent_panel,Rect2(Vector2(right_heading,panel_top),Vector2(panel_width,panel_height)))
			recent_panel.layout()
		# This scroller is detached from album, so its controls need the same
		# scaling pass explicitly (including both retry targets and long labels).
		album._style_controls(album.notice_area)
		var notice_width: float = summary_width if notice_top < heading_top+44*ui_scale else edge-right_heading
		_place(album.notice_area,Rect2(Vector2(right_heading,notice_top),Vector2(notice_width,48*ui_scale)))
		album._layout_cards()
	_layout_marginalia()

func _layout_marginalia() -> void:
	if marginalia == null or book == null: return
	if puzzle_background != null:
		puzzle_background.visible = work.visible
		puzzle_background.arrange(book.projected_paper(true),size,ui_scale)
	var key: String = ""
	var paper: Rect2
	var hard: Array[Rect2] = []
	var soft: Array[Rect2] = []
	var controls: Array[Control] = [status_label,layout_warning,work_repair_button,save_retry]
	if work.visible and session != null:
		var entry: Dictionary = Registry.by_id(str(session.definition.id))
		# selected (including omitted/failed loads) and explicit none never
		# borrow a Legacy category drawing. Help retains its existing pilot.
		if str(entry.get("background",{}).get("status","legacy")) != "legacy":
			marginalia.arrange("",Rect2(),size,ui_scale,hard,soft)
			return
		key = str(entry.get("category_id",""))
		# Unselected categories need no extra clue/font scan for absent artwork.
		if not Marginalia.ORIGINALS.has(key):
			marginalia.arrange(key,Rect2(),size,ui_scale,hard,soft)
			return
		paper = book.projected_paper(true)
		controls.append_array([title,coordinate,tools_scroll])
		for id: String in ["help","menu","nav-information"]: controls.append(actions[id])
		hard.append_array([surface.card,surface.palette])
		hard.append_array(surface.wells)
		if board.layout_valid:
			var ink: Rect2 = board.composition_envelope()
			ink.position += board.position
			soft.append(ink)
		else: key = ""
	elif information.visible and info.section == "help":
		key = "help"
		paper = book.projected_information(1)
		controls.append_array([info.help_heading,help_panel.navigation,info.right_return,information.get_node("settings-access"),information.get_node("help-access")])
		# ScrollContainer sorts its child scrollbar later. Its old rectangle can
		# still have the UI125 width after a UI100 reflow. Reserve the current
		# measured width on the already placed article, across every chapter.
		var scroll: Rect2 = help_panel.scroll.get_global_rect()
		var bar_width: float = help_panel.scroll.get_v_scroll_bar().get_combined_minimum_size().x
		hard.append(Rect2(Vector2(scroll.end.x-bar_width,scroll.position.y),Vector2(bar_width,scroll.size.y)))
		# Reserve a state-independent reading envelope: all chapters, diagrams
		# and tool-icon rows. Article scrolling never changes drawing placement.
		var width: float = help_panel.paragraph_width+56*ui_scale
		for figure: Control in help_panel.figures: width = maxf(width,figure.get_combined_minimum_size().x)
		var article: Rect2 = help_panel.scroll.get_global_rect()
		article.size.x = minf(article.size.x,width)
		soft.append(article)
	for control: Control in controls:
		if control != null and control.is_visible_in_tree(): hard.append(control.get_global_rect())
	marginalia.arrange(key,paper,size,ui_scale,hard,soft)

func select_puzzle(index: int) -> void:
	if resetting_ending:
		super.select_puzzle(index)
		return
	if index >= 0 and index < sessions.size(): opening_requested.emit(str(sessions[index].definition.id))

func _reset_selected() -> void:
	resetting_ending = reset_origin == "ending"
	super._reset_selected()
	resetting_ending = false

func activate(id: String) -> bool:
	return session_indices.has(id) and _activate_session(int(session_indices[id]))

func set_ui_scale(value: float) -> void:
	scale_changing.emit()
	super.set_ui_scale(value)
	if info != null: info.layout()

func _build_information() -> void:
	super._build_information()
	info = Information.new(self)

func show_information(section: String = "settings") -> void:
	if book != null: book.information_routes.request(section)

func _information_section(section: String) -> void:
	if info == null: information_section = section
	else: show_information(section)

func return_to_work() -> void:
	if book != null: book.information_routes.request_return()

func present_album() -> void:
	leave_background_visit()
	super.present_album()
	catalog_shown.emit()

func _schedule_view_save() -> void:
	if not presentation_locked: super._schedule_view_save()

func _save_action_visible() -> bool:
	return super._save_action_visible() or (save_retry != null and save_retry.visible)

func _update_status() -> void:
	var prior_status: bool = status_label != null and status_label.visible
	var prior_repair: bool = work_repair_button != null and work_repair_button.visible
	var prior_retry: bool = save_retry != null and save_retry.visible
	super._update_status()
	if session == null and status_label != null:
		status_label.hide()
		if work_repair_button != null: work_repair_button.hide()
	if save_retry != null:
		var visible_retry: bool = session != null and not slot_errors[sessions.find(session)].is_empty() and not work_repair_button.visible
		if prior_retry and not visible_retry and album.visible:
			# A successful catalog retry must clear both the summary feedback and
			# the card diagnosis without changing filter, page or either offset.
			album.present(sessions,slot_status,slot_errors,catalog_error,album.selected_id)
		var information_changed: bool = information.visible and (prior_status != status_label.visible or prior_repair != work_repair_button.visible)
		if save_retry.visible != visible_retry or information_changed:
			save_retry.visible = visible_retry
			_layout_book()

func leave_app() -> void: exit_requested.emit()

func quit_after_flush() -> void: super.leave_app()

func _web_lifecycle(arguments: Array) -> void:
	book.interrupt("leave")
	super._web_lifecycle(arguments)

func _notification(what: int) -> void:
	# The root owns the one close request, including asynchronous preparation.
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null: _cancel_interaction()
