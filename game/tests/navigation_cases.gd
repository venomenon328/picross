extends RefCounted
## NAV-A: small real-control checks inside existing catalog processes.
const ButtonInk = preload("res://ui/book_button.gd")

static func inventory(r: SceneTree) -> void:
	var count: int = 0
	for node: Node in r.app.find_children("*","Button",true,false):
		if not node is ButtonInk: continue
		var button: ButtonInk = node
		if not ((button.text.is_empty() and (button.image != null or button.swatch.a > 0)) or button.text == "?"): continue
		count += 1
		r.check(not button.tooltip_text.strip_edges().is_empty() and not button.accessibility_name.strip_edges().is_empty(),"NAV-A: icon tooltip/name defined, including disabled: "+button.action_id)
		if button.action_id.begins_with("color-"):
			var caption: String = "Farbe %s wählen · aktiviert Füllen" % button.action_id.trim_prefix("color-")
			r.check(button.tooltip_text == caption and button.accessibility_name == caption,"NAV-A: dynamic colour function/name")
		elif button.action_id in ["fill","erase","undo","redo","minus","plus","help","menu","reset"]:
			var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
			r.check(button.tooltip_text == icons[button.action_id][1],"NAV-A: current shared icon function: "+button.action_id)
	# Catalog controls are detached into the page, so traverse the actual app.
	r.check(count >= 12,"NAV-A: actual runtime icon inventory traversed")
	for card: Control in r.app.album.choices:
		r.check(card.tooltip_text.is_empty() and card.difficulty.tooltip_text.is_empty(),"NAV-A: passive card/difficulty stay without tooltip")

static func geometry(r: SceneTree) -> void:
	var app: Control = r.app
	var album: Control = app.album
	var u: float = app.ui_scale
	var viewport := Rect2(Vector2.ZERO,app.size)
	r.check(album.quit_button.text.is_empty() and album.quit_button.image != null and album.quit_button.size == Vector2.ONE*44*u and album.quit_button.tooltip_text == "Beenden" and album.quit_button.accessibility_name == "Beenden","NAV-A: owner-requested hand-drawn quit X has exact tooltip/name and target")
	var prior: Rect2
	for button: Control in [album.quit_button,album.settings_button,album.help_button]:
		var box: Rect2 = button.get_global_rect()
		r.check(viewport.encloses(box) and box.size.x >= 44*u and box.size.y >= 44*u,"NAV-A: fixed catalog header hit target")
		r.check(box.position.y < album.summary.global_position.y and not box.intersects(album.notice_area.get_global_rect()) and not box.intersects(app.recent_panel.get_global_rect()),"NAV-A: header clear of count, retry and full recent panel")
		if prior.has_area(): r.check(prior.end.x < box.position.x,"NAV-A: quit, gear, help in order")
		prior = box
	var left: Rect2 = app.book.projected_paper(false,-1)
	var right: Rect2 = app.book.projected_paper(false,1)
	for button: Control in [album.previous_button,album.next_button]:
		var box: Rect2 = button.get_global_rect()
		r.check(button.text.is_empty() and button.image != null and box.size == Vector2.ONE*44*u,"NAV-A: pagination is arrow-only with exact hit size")
		r.check(viewport.encloses(box) and box.position.y >= album.scroll.get_global_rect().end.y,"NAV-A: pagination outside card clips")
		r.check(box.end.x < left.end.x-left.size.x*0.075 or box.position.x > right.position.x+right.size.x*0.075,"NAV-A: pagination clears fold")
		r.check(button.tooltip_text == ("Vorherige Seite" if button == album.previous_button else "Nächste Seite") and button.accessibility_name == button.tooltip_text,"NAV-A: exact pagination tooltip/name")
	r.check(absf(album.previous_button.global_position.x-album.global_position.x)<1 and absf(album.next_button.get_global_rect().end.x-album.get_global_rect().end.x)<1,"NAV-A: arrows at opposite spread corners")
	r.check(album.page_label.is_visible_in_tree() and album.page_label.global_position.x > album.previous_button.get_global_rect().end.x and album.page_label.get_global_rect().end.x < left.end.x-left.size.x*0.075,"NAV-A: separate page text after left arrow and before fold")

static func information(r: SceneTree) -> void:
	var app: Control = r.app
	var section: String = app.info.section
	var back: Control = app.actions["nav-work"]
	var settings: Control = app.information.get_node("settings-access")
	var help: Control = app.information.get_node("help-access")
	var active: Control = settings if section == "settings" else help
	var other: Control = help if section == "settings" else settings
	r.check(settings.selected == (section == "settings") and help.selected == (section == "help"),"NAV-A: active information location marked by underline")
	r.check(active.tooltip_text == ("Einstellungen" if section == "settings" else "Hilfe")+" (aktuelle Ansicht)" and active.accessibility_name == active.tooltip_text,"NAV-A: active location named")
	r.check(other.tooltip_text == ("Hilfe öffnen" if section == "settings" else "Einstellungen öffnen") and other.accessibility_name == other.tooltip_text,"NAV-A: opposite destination named")
	var expected: String = "Zurück zum Katalog" if app.information_origin == "album" else "Zurück zum Rätsel"
	r.check(back.tooltip_text == expected and back.accessibility_name == expected,"NAV-A: return names actual visit origin")
	var prior: Rect2
	for button: Control in [back,settings,help]:
		var box: Rect2 = button.get_global_rect()
		r.check(button.is_visible_in_tree() and button.text.is_empty() and box.size == Vector2.ONE*44*app.ui_scale,"NAV-A: full icon group on either information page")
		if prior.has_area(): r.check(box.position.x > prior.end.x and box.position.y == prior.position.y,"NAV-A: back, gear, help in one fixed row")
		prior = box
	var positions: Vector2i = app.info.positions()
	var chapter: int = app.help_panel.chapter
	var generation: int = app.book.generation
	r.click(active)
	await r.frames()
	r.check(app.book.generation == generation and app.info.positions() == positions and app.help_panel.chapter == chapter and app.info.section == section,"NAV-A: active location click changes no section, reading or animation")
	inventory(r)

static func catalog(r: SceneTree) -> void:
	var app: Control = r.app
	var album: Control = app.album
	for config: Vector3 in [Vector3(1280,720,1),Vector3(1280,720,1.25),Vector3(1920,1080,1),Vector3(2560,1440,1.25)]:
		r.surface.size = Vector2i(config.x,config.y)
		app.size = Vector2(config.x,config.y)
		app.set_ui_scale(config.z)
		await r.frames()
		geometry(r)
		inventory(r)
	album.choose_category("gebaeude-bauwerke")
	album.choose_sort("size")
	await r.frames()

	r.check(album.previous_button.disabled and not album.next_button.disabled,"NAV-A: first filtered spread boundary")
	r.click(album.next_button)
	await r.frames()
	r.check(album.page_index == 1 and not album.previous_button.disabled and album.next_button.disabled,"NAV-A: last filtered spread boundary")
	album.scroll.scroll_vertical = 95
	album.right_scroll.scroll_vertical = 145
	await r.frames()
	var positions: Vector2i = album.positions()
	album.selected_id = album.visible_ids[1]
	var selected: String = album.selected_id
	var filters: Dictionary = album.filters.duplicate()
	var order: Array = [album.preference.criterion,album.preference.direction]
	r.click(album.help_button)
	await r.frames()
	app.help_panel.choose(2)
	app.info.help_scroll.scroll_vertical = 250
	await r.frames()
	var help_position: int = app.info.help_scroll.scroll_vertical
	r.click(app.information.get_node("settings-access"))
	await r.frames()
	app.info_scroll.scroll_vertical = 80
	await r.frames()
	var settings_position: int = app.info_scroll.scroll_vertical
	r.click(app.information.get_node("help-access"))
	await r.frames()
	r.check(app.help_panel.chapter == 2 and app.info.help_scroll.scroll_vertical == help_position,"NAV-A: help chapter and reading survive settings pan")
	r.click(app.information.get_node("settings-access"))
	await r.frames()
	r.check(app.info_scroll.scroll_vertical == settings_position,"NAV-A: independent settings reading survives pan")
	r.click(app.actions["nav-work"])
	await r.frames()
	r.check(album.visible and album.page_index == 1 and album.positions() == positions and album.selected_id == selected and album.filters == filters and [album.preference.criterion,album.preference.direction] == order,"NAV-A: catalog-help-settings-back restores entire filtered spread context")
	album.choose_category("voegel")
	await r.frames()
	r.check(album.page_label.text == "Seite 1 von 1" and album.previous_button.disabled and album.next_button.disabled and album.previous_button.is_visible_in_tree() and album.next_button.is_visible_in_tree(),"NAV-A: single filtered spread keeps both inactive arrows and count")
	album.reset_filters()
	r.surface.size = Vector2i(1920,1080)
	app.size = Vector2(1920,1080)
	app.set_ui_scale(1.0)
	await r.frames()

static func work(r: SceneTree) -> void:
	var app: Control = r.app
	app.return_to_work()
	await r.frames()
	r.click(app.choices[0])
	await r.frames()
	r.click_at(app.board.global_position+app.board.view.cell_rect(Vector2i.ZERO).get_center())
	app._flush_current()
	var id: String = str(app.session.definition.id)
	var cells: Array = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	var cursor: int = app.session.player.cursor
	var saved: Dictionary = r.save_bytes()
	r.click(app.actions["help"])
	await r.frames()
	r.check(app.info.section == "help" and app.information_origin == "work","NAV-A: work opens help with work origin")
	r.click(app.information.get_node("settings-access"))
	await r.frames()
	await information(r)
	r.click(app.actions["nav-work"])
	await r.frames()
	r.check(app.work.visible and str(app.session.definition.id) == id and app.session.player.cells == cells and app.session.player.history == history and app.session.player.cursor == cursor and r.save_bytes() == saved,"NAV-A: work-help-settings-back restores same durable work")
	r.click(app.album_button)
	await r.frames()
	r.check(app.album.visible and app.album.selected_id == id,"NAV-A: own work arrow still restores bound catalog")
