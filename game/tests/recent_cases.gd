extends RefCounted
const Recent = preload("res://model/recent_puzzle.gd")

static func raw(path: String, text: String) -> void:
	var file := FileAccess.open(path,FileAccess.WRITE)
	file.store_string(text)
	file.close()

static func run(probe) -> void:
	var app = probe.app
	var path: String = app.store.root.path_join("recent-tests/recent-puzzle.json")
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var marker := Recent.new(path)
	marker.load_record()
	probe.check(marker.record.is_empty() and not FileAccess.file_exists(path),"K-B missing marker load has no write")
	var valid: String = '{"format":"picross-recent-puzzle-v1","id":"pz-test-kat2-001","revision":1}'
	for invalid: String in ["", "null", "[]", valid+"x", valid.replace('"revision":1','"revision":0'),valid.replace('"revision":1','"revision":1.5'),valid.replace('"revision":1','"revision":true'),valid.replace('"revision":1','"revision":"1"'),valid.replace('"revision":1','"revision":1,"x":2'),valid.replace('"revision":1','"id":"x"'),valid.replace('"revision":1','"i\\u0064":"x"'),valid.replace('v1','v2'),valid.replace('"revision":1','"revision":{}'),valid+" ".repeat(1024)]:
		raw(path,invalid)
		marker.load_record()
		probe.check(marker.record.is_empty() and FileAccess.get_file_as_string(path) == invalid,"K-B invalid bytes ignored without rewrite")
	probe.check(Recent.decode(valid.to_utf8_buffer()).revision == 1,"K-B exact format accepted")
	for bytes: PackedByteArray in [PackedByteArray([255]),PackedByteArray([192,128]),PackedByteArray([237,160,128]),PackedByteArray([244,144,128,128]),PackedByteArray([226,130])]:
		probe.check(Recent.decode(bytes).is_empty(),"K-B malformed/overlong/surrogate/out-of-range/truncated UTF-8 ignored")
	var first = app.Session.new(app.sessions[1].definition)
	var second = app.Session.new(app.sessions[3].definition)
	first.player.commit([{"index":0,"before":-1,"after":1}])
	second.player.commit([{"index":0,"before":-1,"after":0}])
	probe.check(marker.edited(first),"K-B real Windows atomic initial publication")
	var original: PackedByteArray = FileAccess.get_file_as_bytes(path)
	for step: String in ["open","after_temp","replace"]:
		marker.fail_step = step
		probe.check(not marker.edited(second) and FileAccess.get_file_as_bytes(path) == original,"K-B "+step+" keeps previous valid bytes")
		var restart := Recent.new(path)
		restart.load_record()
		probe.check(restart.record.id == first.definition.id,"K-B interrupted temp never becomes startup marker")
	marker.fail_step = ""
	probe.check(marker.retry() and marker.record.id == second.definition.id,"K-B explicit replacement retry publishes latest candidate")
	probe.check(marker.clear_matching(str(first.definition.id)) and marker.record.id == second.definition.id,"K-B foreign reset leaves marker")
	marker.fail_step = "delete"
	original = FileAccess.get_file_as_bytes(path)
	probe.check(not marker.clear_matching(str(second.definition.id)) and FileAccess.get_file_as_bytes(path) == original,"K-B failed deletion reported and old bytes retained")
	marker.fail_step = ""
	probe.check(marker.retry() and not FileAccess.file_exists(path),"K-B deletion retry")
	probe.check(marker.edited(first),"K-B marker restored")
	original = FileAccess.get_file_as_bytes(path)
	DirAccess.make_dir_absolute(path+".tmp")
	probe.check(not marker.edited(second) and FileAccess.get_file_as_bytes(path) == original,"K-B temporary directory rejected without touching prior bytes")
	DirAccess.remove_absolute(path+".tmp")
	probe.check(marker.clear_matching(str(second.definition.id)) and marker.record.id == first.definition.id,"K-B reset of unpublished candidate retains older valid marker")
	var items: Dictionary = {str(first.definition.id):first}
	var statuses: Dictionary = {str(first.definition.id):"loaded"}
	probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B canonical ID resolution")
	for status: String in ["recovered","backup_invalid"]:
		statuses[first.definition.id] = status
		probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B valid reconstructed progress retains recovery route")
	statuses[first.definition.id] = "error"
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B invalid slot hidden")
	statuses[first.definition.id] = "loaded"
	marker.record.revision += 1
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B stale revision hidden")
	marker.record.revision -= 1
	probe.check(marker.resolve({},statuses).is_empty(),"K-B hidden/deleted/foreign ID has no fallback")
	first.player.undo()
	probe.check(marker.resolve(items,statuses) == first.definition.id,"K-B redo-only remains begun")
	first.completed = true
	probe.check(marker.resolve(items,statuses).is_empty(),"K-B completion immediately hides offer")
	first.completed = false
	# Restore these synthetic sessions before exercising the actual app boundary.
	app.sessions[1] = app.Session.new(first.definition)
	app.sessions[3] = app.Session.new(second.definition)
	app.select_puzzle(1)
	await probe.frames()
	app.recent.clear_matching(app.recent.record.get("id",""))
	app._save_current()
	probe.check(app.recent.record.is_empty(),"K-B view-only save never marks")
	app.store.fail_step = "after_temp"
	app.session.gesture.begin(app.session.player,Vector2i.ZERO,1)
	app.session.finish()
	app._on_commit()
	probe.check(app.recent.record.is_empty() and app.pending_edits.has(app.session.definition.id),"K-B failed action save retains its reason")
	app.store.fail_step = ""
	probe.check(app._save_current() and app.recent_id() == app.session.definition.id and app.pending_edits.is_empty(),"K-B explicit save retry completes action reason")
	var id: String = app.recent_id()
	app._undo()
	probe.check(app.recent_id() == id and app.session.player.cursor == 0,"K-B real Undo updates begun redo-only marker")
	app._redo()
	probe.check(app.recent_id() == id and app.session.player.cursor == 1,"K-B real Redo updates marker")
	await freshness_layout(probe)
	app.show_album()
	app.album.apply_filters("solved","all",0,0,"","")
	await probe.frames()
	probe.check(not app.album.filtered_ids.has(id) and app.recent_panel.visible,"K-B recent offer independent of excluding filters")
	var positions: Vector2i = app.album.positions()
	var filters: Dictionary = app.album.filters.duplicate()
	probe.click(app.recent_panel)
	await probe.frames()
	probe.check(app.work.visible and app.session.definition.id == id,"K-B actual panel pointer opens canonical ID")
	probe.click(app.album_button)
	await probe.frames()
	probe.check(app.album.filters == filters and app.album.positions() == positions,"K-B return preserves filter and both scrolls")
	app._ask_reset_id(id)
	await probe.frames()
	probe.click(app.reset_dialog.get_ok_button())
	await probe.frames()
	probe.check(app.recent_id().is_empty() and not app.recent_panel.visible,"K-B reset removes marker and panel")
	app.album.reset_filters()
	await retry_layout(probe)
	probe.catalog_case("k-b-recent")

static func pixel(probe, index: int, filled: bool) -> void:
	await probe.frames()
	await RenderingServer.frame_post_draw
	var preview = probe.app.recent_panel.preview
	var step: float = preview.image_rect().size.x/preview.width
	var point: Vector2 = preview.global_position+Vector2(index%preview.width+0.5,index/preview.width+0.5)*step
	var actual: Color = probe.surface.get_texture().get_image().get_pixelv(Vector2i(point))
	var expected: Color = Color(probe.app.session.definition.palette[0].color) if filled else Color("faf6ec")
	probe.check(absf(actual.r-expected.r)+absf(actual.g-expected.g)+absf(actual.b-expected.b) < 0.03,"RF-A own miniature pixel before any hover (filled=%s)" % filled)

static func freshness_layout(probe) -> void:
	var app = probe.app
	# This is the real catalog destination path during disabled capture. No
	# _process, pointer movement, focus change or second refresh may bind it.
	app.session.player.commit([{"index":84,"before":-1,"after":1}])
	app._on_commit()
	app.process_mode = Node.PROCESS_MODE_DISABLED
	app.present_album()
	probe.check(app.recent_panel.preview.cells == app.session.player.cells,"RF-A destination binds synchronously with processing disabled")
	await pixel(probe,84,true)
	app.process_mode = Node.PROCESS_MODE_INHERIT
	# Live update with the catalog left open, then Undo/Redo without mouse.
	app._undo()
	await pixel(probe,84,false)
	app._undo()
	await pixel(probe,84,false)
	probe.check(app.recent_panel.visible and app.session.player.cursor == 0 and not app.session.player.history.is_empty(),"RF-A valid empty redo-only miniature remains visible")
	app._redo()
	app._redo()
	await pixel(probe,84,true)
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[1920,1080,1.25],[2560,1440,1.0],[2560,1440,1.25],[1920,1200,1.25],[2560,1440,1.0]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await probe.frames()
		var panel = app.recent_panel
		# The count now shares the row with navigation; the panel still uses
		# the complete safe right-paper width, independently of that label.
		var paper: Rect2 = app.book.projected_paper(false,1)
		var safe_edge: float = paper.end.x-18*app.ui_scale
		var width: float = safe_edge-app.album.summary.position.x
		probe.check(absf(panel.size.x-width/2) < 0.01 or absf(panel.size.x-width) < 0.01,"RF-A box is exactly half or full projected heading width")
		if spec == [2560,1440,1.0]: probe.check(absf(panel.size.x-width/2) < 0.01,"RF-A 1440p UI100 half width")
		if spec == [1280,720,1.25]: probe.check(absf(panel.size.x-width) < 0.01,"RF-A narrow UI125 full width")
		probe.check(absf(panel.position.x-app.album.summary.position.x) < 0.01 and panel.get_rect().end.x <= safe_edge+0.01,"RF-A fixed left edge and safe right boundary")
		probe.check(panel.fits(panel.size.x,panel.size.y),"RF-A both shaped text lines and full miniature fit")
		var caption: Rect2 = panel.caption.get_global_rect()
		var detail: Rect2 = panel.detail.get_global_rect()
		var preview: Rect2 = panel.preview.get_global_rect()
		probe.check(absf(caption.position.x-panel.global_position.x-12*app.ui_scale) < 0.01 and absf((caption.position.y+detail.end.y)/2-panel.get_global_rect().get_center().y) < 0.01,"RF-A text group retains inset and vertical centre")
		probe.check(caption.end.x <= preview.position.x-8*app.ui_scale+0.01 and detail.end.x <= preview.position.x-8*app.ui_scale+0.01 and preview.size == Vector2.ONE*56*app.ui_scale,"RF-A no overlap or miniature shrink")
		probe.check(absf(app.album.sort_choice.global_position.y-panel.get_global_rect().end.y-8*app.ui_scale) < 0.1,"RF-A unchanged eight UI gap to sorting/filter")
		preload("res://tests/navigation_cases.gd").geometry(probe)
		await pixel(probe,84,true)
	# A fit-derived boundary, same geometry, and scale roundtrip: no arbitrary
	# screen-size breakpoint and no intermediate width during the fallback.
	var panel = app.recent_panel
	var original: Vector2 = panel.size
	var original_position: Vector2 = panel.position
	var text_width: float = maxf(panel.caption.get_theme_font("font").get_string_size(panel.caption.text,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x,panel.detail.get_theme_font("font").get_string_size(panel.detail.text,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x)
	var boundary: float = text_width+panel.caption.get_theme_stylebox("normal").get_minimum_size().x+84
	for width: float in [boundary-2,boundary+2,boundary-2]:
		probe.check(panel.fits(width,68) == (width > boundary),"RF-A shaped text fit switches directly at measured boundary")
	probe.check(panel.size == original and panel.position == original_position,"RF-A fit measurement does not mutate control geometry")
	app.select_puzzle(3)
	await probe.frames()
	app.session.player.commit([{"index":84,"before":-1,"after":1}])
	app._on_commit()
	app.show_album()
	await pixel(probe,84,true)
	probe.check(app.recent_panel.preview.style_identity == str(app.session.definition.id)+"/recent","RF-A another recent ID binds before hover")
	# Return to the first ID for the existing filter/navigation/reset cases.
	app.select_puzzle(1)
	await probe.frames()
	app._undo()
	app._redo()

static func retry_layout(probe) -> void:
	# B-01: exercise clipping and actual edge hits, not just the Button minimum.
	# Stay in the existing pages process; no captures or extra history process.
	var app = probe.app
	var album = app.album
	var hits: Array[int] = [0,0]
	app.recent_retry.pressed.connect(func() -> void: hits[0] += 1)
	app.save_retry.pressed.connect(func() -> void: hits[1] += 1)
	for spec: Array in [[1280,720,1.0],[1280,720,1.25],[1920,1080,1.0],[1920,1080,1.25]]:
		probe.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await probe.frames()
		app._layout_book()
		await probe.frames()
		var fixed: Array = [album.get_global_rect(),album.sort_choice.get_global_rect(),album.filter_button.get_global_rect(),app.recent_panel.get_global_rect(),album.scroll.get_global_rect(),album.right_scroll.get_global_rect()]
		app.recent.fail_step = "open"
		var candidate = app.Session.new(app.sessions[3].definition)
		candidate.player.commit([{"index":0,"before":-1,"after":1}])
		app.recent.edited(candidate)
		app.store.fail_step = "after_temp"
		app.session.gesture.begin(app.session.player,Vector2i.ZERO,1)
		app.session.finish()
		app._on_commit()
		album.feedback.text = "Synthetischer langer Speicherfehler. ".repeat(60)
		album.feedback.show()
		await probe.frames()
		var area: Rect2 = album.notice_area.get_global_rect()
		probe.check(area.position.y >= album.summary.get_global_rect().end.y and area.end.y <= app.recent_panel.position.y,"B-01 notices remain between summary and recent panel")
		for index: int in range(2):
			var button: Button = app.recent_retry if index == 0 else app.save_retry
			album.notice_area.ensure_control_visible(button)
			await probe.frames()
			var target: Rect2 = button.get_global_rect()
			probe.check(button.is_visible_in_tree() and area.grow(0.001).encloses(target) and target.size.x >= 44*app.ui_scale and target.size.y >= 44*app.ui_scale,"B-01 full retry target survives ScrollContainer clipping")
			var before: int = hits[index]
			for point: Vector2 in [target.position+Vector2.ONE,target.position+Vector2(target.size.x-1,1),target.end-Vector2.ONE,target.position+Vector2(1,target.size.y-1),target.get_center()]:
				probe.click_at(point)
				await probe.frames()
			probe.check(hits[index] == before+5,"B-01 retry receives all four corner and centre pointer clicks")
		probe.check(album.notice_area.get_v_scroll_bar().max_value > area.size.y,"B-01 long errors scroll separately")
		probe.check(fixed == [album.get_global_rect(),album.sort_choice.get_global_rect(),album.filter_button.get_global_rect(),app.recent_panel.get_global_rect(),album.scroll.get_global_rect(),album.right_scroll.get_global_rect()],"B-01 errors and scrolling never move catalog controls or recent panel")
		app.store.fail_step = ""
		app._save_current()
		app.recent.fail_step = ""
		app.recent.retry()
		album.feedback.hide()
		await probe.frames()
