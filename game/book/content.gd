extends "res://ui/main.gd"
## Regular product lifecycle with the shared book presentation.
const Surface = preload("res://book/surface.gd")
const CatalogSpread = preload("res://book/catalog.gd")
const Information = preload("res://book/information.gd")
const ViewTitle = preload("res://ui/view_title.gd")
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
	# Remove the old left tab completely. Reuse the three existing right slots;
	# the middle menu remains the unchanged sidebar axis in the base layout.
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
			if save_retry.get_parent() != album.left_page: save_retry.reparent(album.left_page)
			album.left_page.move_child(save_retry,1)
			save_retry.custom_minimum_size.y = 44*ui_scale
		else:
			if save_retry.get_parent() != page: save_retry.reparent(page)
			_place(save_retry,Rect2(work_repair_button.position,Vector2(340,44)*ui_scale))
	if album.summary != null: album.summary.visible = album.visible and catalog_error.is_empty()
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
		var catalog_top: float = heading_top+53*ui_scale
		var footer_width: float = album.right_pager.get_child(0).get_combined_minimum_size().x+album.next_button.get_combined_minimum_size().x+12*ui_scale
		album.right_pager.vertical = (edge-margin-album.fold_gap)/2 < footer_width
		_place(album, Rect2(Vector2(margin,catalog_top),Vector2(edge-margin,left_paper.end.y-inset-catalog_top)))
		_place(catalog_title, Rect2(Vector2(margin,heading_top),Vector2(left_paper.end.x-curve-inset-margin,45*ui_scale)))
		catalog_title.fallback.add_theme_font_size_override("font_size",roundi(28*ui_scale))
		if album.summary != null:
			_place(album.summary,Rect2(Vector2(right_heading,heading_top),Vector2(edge-right_heading,45*ui_scale)))
			album.summary.add_theme_font_size_override("font_size",roundi(18*ui_scale))
		album._layout_cards()

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
