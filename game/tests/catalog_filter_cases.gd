extends RefCounted
## K-A regression in the existing pages process, using only synthetic sessions.
const Filter = preload("res://model/catalog_filter.gd")
const Session = preload("res://model/session.gd")

static func apply(album, status: String = "all", mode: String = "all", lower: int = 0, upper: int = 0, width: String = "", height: String = "") -> void:
	album.apply_filters(status,mode,lower,upper,width,height)

static func rules(probe) -> void:
	var album = probe.app.album
	var originals: Dictionary = album.items.duplicate()
	var metadata: Dictionary = album.metadata.duplicate(true)
	var statuses: Dictionary = album.statuses.duplicate()
	var ids: Array = originals.keys()
	album.choose_sort("size")
	var saved: Dictionary = probe.save_bytes()
	var preference: PackedByteArray = FileAccess.get_file_as_bytes(album.preference.path)
	# Even IDs are solved. Odd IDs start fresh, then exercise cells, Redo and
	# recovered progress separately; invalid slots cannot acquire either status.
	for index: int in range(ids.size()):
		var item := Session.new(originals[ids[index]].definition)
		item.completed = index % 2 == 0
		if index % 3 == 0: item.definition.palette.append({"id":2,"color":"#b55848","symbol":"B"})
		album.items[ids[index]] = item
		album.statuses[ids[index]] = "loaded"
		var level: String = "L%d" % (index % 6)
		album.metadata[ids[index]].difficulty = null if index % 6 == 0 else {"method":"picross-difficulty-0.4","level":level,"assessment_type":"instrumented","confidence":"medium","plausible_range":[level,level],"r4_required":false}
	for index: int in [1,3,7]: album.items[ids[index]].player.commit([{"index":0,"before":-1,"after":1}])
	album.items[ids[3]].player.undo()
	album.statuses[ids[7]] = "recovered"
	for index: int in [5,8]: album.statuses[ids[index]] = "error"
	album.reset_filters()
	for spec: Array in [["all",54],["open",26],["new",23],["started",3],["solved",26]]:
		apply(album,spec[0])
		probe.check(album.filtered_ids.size() == spec[1],"K-A valid status " + spec[0])
	apply(album,"started")
	probe.check(Array(album.filtered_ids) == [ids[1],ids[3],ids[7]],"K-A cells, redo-only and recovered progress; invalid completed excluded")
	probe.check(album.notes[2].text == "Begonnen" and album.repair_buttons.has(ids[7]),"K-A recovered hit retains actual status and repair action")
	var repair_id: Array[String] = []
	var repair_callback := func(id: String) -> void: repair_id.append(id)
	album.repair_requested.connect(repair_callback)
	album.repair_buttons[ids[7]].pressed.emit()
	probe.check(repair_id == [ids[7]],"K-A recovery action retains canonical ID")
	album.repair_requested.disconnect(repair_callback)
	await probe.frames()
	probe.click(probe.app.repair_dialog.get_cancel_button())
	await probe.frames()
	for spec: Array in [["all",54],["mono",36],["color",18]]:
		apply(album,"all",spec[0])
		probe.check(album.filtered_ids.size() == spec[1],"K-A puzzle mode " + spec[0])
	for level: int in range(1,6):
		apply(album,"all","all",level,level)
		var expected: Array = []
		for index: int in range(level,54,6): expected.append(ids[index])
		probe.check(Array(album.filtered_ids) == expected,"K-A inclusive single difficulty L%d" % level)
	apply(album,"all","all",2,4)
	probe.check(album.filtered_ids.size() == 27,"K-A inclusive difficulty span")
	for span: Vector2i in [Vector2i(1,0),Vector2i(0,5)]:
		apply(album,"all","all",span.x,span.y)
		probe.check(album.filtered_ids.size() == 45,"K-A either difficulty boundary excludes only unrated")
	apply(album)
	probe.check(album.filtered_ids.size() == 54,"K-A no bounds includes unrated")
	apply(album,"all","all",0,0,"20","20")
	probe.check(album.filtered_ids.size() == 54,"K-A inclusive width and height")
	for limits: Array in [["19",""],["","19"],["19","20"]]:
		apply(album,"all","all",0,0,limits[0],limits[1])
		probe.check(album.filtered_ids.is_empty() and album.empty_message.text.contains("Filtern") and album.all_button.visible,"K-A independent/combined dimension boundaries and no hits")
	album.choose_category("voegel")
	apply(album,"new","mono",1,5,"20","20")
	probe.check(Array(album.filtered_ids) == [ids[49],ids[53]],"K-A all axes form one AND pipeline")
	var valid: Dictionary = album.filters.duplicate()
	var generation: int = album.generation
	for spec: Array in [["0",""],["51",""],["-1",""],["1.5",""],["20×30",""],["abc",""],["","0"],["","51"],["","1.5"]]:
		apply(album,"all","color",0,0,spec[0],spec[1])
		probe.check(album.filters == valid and album.generation == generation and album.filter_panel.error.visible,"K-A invalid bounds/input visibly rejected, last valid selection retained")
	# Mutual menu limits prevent contradictory UI choices. Programmatic or
	# stale selections additionally follow the endpoint changed most recently.
	album.open_filters()
	var panel = album.filter_panel
	panel.upper.select(4)
	panel.upper.item_selected.emit(4)
	for level: int in range(1,6):
		probe.check(panel.lower.is_item_disabled(level) == (level>4),"K-A maximum L4 offers minima L1-L4 only")
	panel.lower.select(5)
	panel.lower.item_selected.emit(5)
	probe.check(panel.upper.selected == 5 and not panel.error.visible,"K-A raised minimum adjusts maximum without error")
	panel.upper.select(2)
	panel.upper.item_selected.emit(2)
	probe.check(panel.lower.selected == 2 and panel.upper.selected == 2,"K-A lowered maximum adjusts minimum to equality")
	for level: int in range(1,6):
		probe.check(panel.upper.is_item_disabled(level) == (level<2),"K-A minimum L2 offers maxima L2-L5 only")
	panel.upper.select(0)
	panel.upper.item_selected.emit(0)
	probe.check(not panel.lower.is_item_disabled(5) and not panel.upper.is_item_disabled(0),"K-A independent unbounded endpoint stays selectable")
	panel.lower.select(0)
	panel.lower.item_selected.emit(0)
	probe.check(not panel.upper.is_item_disabled(1),"K-A removing both bounds restores full menus")
	panel.hide()
	for dimension: String in ["1","50",""]:
		probe.check(Filter.validate("","all","all",0,0,dimension,dimension).has("selection"),"K-A supported dimension boundary " + dimension)
	var size_limit: Dictionary = Filter.validate("","all","all",0,0,"20","30").selection
	probe.check(Filter.matches(size_limit,"","new",false,20,30,null) and not Filter.matches(size_limit,"","new",false,30,20,null),"K-A inclusive rectangle dimensions preserve orientation")
	var width_only: Dictionary = Filter.validate("","all","all",0,0,"20","").selection
	var height_only: Dictionary = Filter.validate("","all","all",0,0,"","20").selection
	probe.check(Filter.matches(width_only,"","new",false,20,50,null) and Filter.matches(height_only,"","new",false,50,20,null),"K-A either dimension independently unbounded")
	probe.check(probe.save_bytes() == saved and FileAccess.get_file_as_bytes(album.preference.path) == preference,"K-A all filter/draft/reset operations never write saves or preferences")
	album.items = originals
	album.metadata = metadata
	album.statuses = statuses
	album.reset_filters()
	album._render(0)
	await probe.frames()
	probe.catalog_case("k-a-filter-rules")

static func navigation(probe) -> void:
	var app = probe.app
	var album = app.album
	probe.surface.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	album.choose_sort("size")
	apply(album,"open")
	await probe.frames()
	var ids: Array[String] = album.filtered_ids.duplicate()
	probe.check(ids.size()>24,"K-A full open result exceeds one page")
	album.commit_page(0)
	await probe.frames()
	album.scroll.scroll_vertical = 70
	album.right_scroll.scroll_vertical = 140
	var pair: Vector2i = album.positions()
	var generation: int = album.generation
	apply(album,"open")
	await probe.frames()
	probe.check(album.positions() == pair and album.generation == generation,"K-A same filter is a true no-op for both scrolls and live cards")
	app.show_information()
	app.return_to_work()
	await probe.frames()
	probe.check(album.filters.status == "open" and album.positions() == pair,"K-A information return preserves both offsets and filters")
	album.ensure_control_visible(album.choices[13])
	await probe.frames()
	pair = album.positions()
	var id: String = album.visible_ids[13]
	probe.click(album.choices[13])
	await probe.frames()
	probe.check(app.session.definition.id == id and app.work.visible,"K-A filtered right-half card opens exact ID")
	app.show_album()
	await probe.frames()
	probe.check(album.filters.status == "open" and album.positions() == pair and album.selected_id == id,"K-A work return preserves applied filter, ID and both scrolls")
	apply(album,"new")
	await probe.frames()
	probe.check(album.page_index == 0 and album.positions() == Vector2i.ZERO,"K-A changed filter resets page and both scrolls")
	# A live completion and confirmed reset change membership before clamping.
	album.reset_filters()
	apply(album,"solved")
	await probe.frames()
	var solved_ids: Array[String] = album.filtered_ids.duplicate()
	album.commit_page(1)
	await probe.frames()
	var target: String = album.visible_ids[0]
	var foreign: Dictionary = probe.save_bytes(app.store.key_for_definition(target))
	probe.click(album.reset_buttons[target])
	await probe.frames()
	probe.check(app.reset_id == target,"K-A filtered reset dialog binds exact ID")
	apply(album,"new")
	probe.click(app.reset_dialog.get_ok_button())
	await probe.frames()
	probe.check(target in album.filtered_ids and probe.save_bytes(app.store.key_for_definition(target)) == foreign,"K-A confirmed reset refreshes current filter and preserves foreign slot bytes")
	apply(album,"solved")
	# Remove the remaining last-page membership through the live session source.
	for solved: String in solved_ids.slice(24): album.items[solved].completed = false
	album.page_index = 1
	album._render(99999)
	await probe.frames()
	probe.check(album.page_index == 0 and album.positions() == Vector2i.ZERO,"K-A removed last page clamps page and both offsets to top")
	for solved: String in solved_ids: album.items[solved].completed = solved != target
	album.reset_filters()
	apply(album,"new")
	await probe.frames()
	var opened: String = album.visible_ids[0]
	album.ensure_control_visible(album.choices[0])
	probe.click(album.choices[0])
	await probe.frames()
	# Use the existing completion helper/real Session gesture path and SaveStore.
	for row: int in range(app.session.player.height):
		for column: int in range(app.session.player.width):
			if app.session.definition.solution[row][column] > 0:
				app.session.gesture.begin(app.session.player,Vector2i(column,row),1)
				app.session.finish()
	probe.check(app.session.completed and app._save_current(),"K-A newly completed session and save succeed")
	app.show_album()
	await probe.frames()
	probe.check(not opened in album.filtered_ids,"K-A completion refreshes new filter on return")
	album.show_error(opened,"TEST ONLY write failed")
	apply(album,"all","all",0,0,"1","1")
	await probe.frames()
	probe.check(album.feedback.visible and album.feedback.text.contains("write failed") and album.filtered_ids.is_empty(),"K-A filtered-out save failure remains visible separately from no hits")
	var sort_pair: Array = [album.preference.criterion,album.preference.direction]
	album.reset_filters()
	await probe.frames()
	probe.check(album.filters == Filter.DEFAULTS and [album.preference.criterion,album.preference.direction] == sort_pair,"K-A reset neutralizes category and all axes, retains sort pair")
	album.errors[opened] = ""
	album._render(0)
	await probe.frames()
	probe.catalog_case("k-a-filter-navigation")
