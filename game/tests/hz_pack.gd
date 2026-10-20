extends SceneTree
## External synthetic input against the actual downloaded PCK, original UI/fonts.
const Main = preload("res://ui/main.gd")
const Text = preload("res://ui/ui_text.gd")
var checks := 0
var failures: Array[String] = []
var output: String
var contour_hashes: Dictionary = {}

class TechnicalMain extends Main:
	var fixture_textures: Array[Texture2D] = []
	func puzzle_definitions() -> Array[Dictionary]:
		var input: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("HZ_PACK_INPUT")))
		# The regular export correctly excludes synthetic reveals. Supply only
		# these external fixture images in the resource cache; never replace a
		# packed UI/font/art resource or bypass Definition.validate().
		for path: String in input.images:
			assert(path.begins_with("res://art/fixtures/") and not ResourceLoader.exists(path))
			var image := Image.new()
			var error: Error = image.load_svg_from_string(input.images[path])
			assert(error == OK)
			var texture := ImageTexture.create_from_image(image)
			texture.take_over_path(path)
			fixture_textures.append(texture)
		Registry.cached = input.registry
		var result: Array[Dictionary] = []
		for data: Dictionary in input.definitions: result.append(data)
		return result

func _initialize() -> void: call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures.append(message); print("HZ_PACK_FAIL ",message)

func frames() -> void:
	await process_frame
	await process_frame
	await process_frame

func shot(name: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	check(root.get_texture().get_image().save_png(output.path_join(name+".png")) == OK,"actual PCK framebuffer "+name)

func run() -> void:
	output = OS.get_environment("HZ_PACK_OUTPUT")
	if output.is_empty(): quit(4); return
	root.gui_embed_subwindows = true
	var app := TechnicalMain.new()
	root.add_child(app)
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await frames()
	check(app.catalog_error.is_empty() and app.sessions.size() == 6,"actual PCK loads only six external synthetic fixtures: " + app.catalog_error)
	check(Text.font().data == Text.SOURCE.data and not Text.font().allow_system_fallback,"actual PCK original Tidy bytes and local fallback")
	check(FileAccess.file_exists("res://art/drawing/tidy-hand/NOTICE.txt"),"actual PCK includes author permission")
	var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
	check(icons.size() == 23 and FileAccess.file_exists("res://art/book/HZ-B-284-NOTICE.txt"),"actual PCK complete HZ-B family/provenance")
	for id: String in icons:
		var texture: Texture2D = load("res://art/book/"+id+".svg")
		check(texture != null and texture.get_size() == Vector2(26,26),"actual PCK imported icon "+id)
		check(texture.get_image().is_invisible() == (id == "check-empty"),"actual PCK visible ink "+id)
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1080,1.0]]:
		root.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await frames()
		check(app.theme.default_font.get_font_name() == "Tidy Hand" and app.title.get_theme_font("font") == app.WORK_TITLE_FONT,"actual PCK normal and heading roles across scale roundtrip")
		for card: Control in app.choices:
			for label: Label in [card.dimensions,card.difficulty,card.leaf,card.note]:
				check(Text.label_width(label,label.text,label.get_theme_font_size("font_size")) <= label.size.x,"actual PCK full metadata")
		await shot("catalog-%d" % spec[0])
		var contours: Array = app.choices[0].get_theme_stylebox("normal").contours(Rect2(Vector2.ZERO,app.choices[0].size))
		var hash := HashingContext.new()
		hash.start(HashingContext.HASH_SHA256)
		hash.update(var_to_bytes(contours))
		var fingerprint: String = hash.finish().hex_encode()
		var key: String = "%s/%s" % [spec[0],spec[2]]
		if contour_hashes.has(key): check(contour_hashes[key] == fingerprint,"actual PCK scale roundtrip contour bytes")
		contour_hashes[key] = fingerprint
		check(app.choices[0].get_theme_stylebox("normal").get_script().resource_path == "res://ui/book_style.gd","actual PCK uses HZ-B card contours")
		app.album.sort_choice.show_popup()
		await frames()
		check(app.album.sort_choice.get_popup().get_theme_stylebox("panel").get_script().resource_path == "res://ui/book_style.gd","actual PCK HZ-B native popup paper")
		await shot("controls-sort-%d" % spec[0])
		app.album.sort_choice.get_popup().hide()
		app.show_information("settings")
		await shot("controls-settings-%d" % spec[0])
		app.view_choice.show_popup()
		await shot("controls-view-%d" % spec[0])
		app.view_choice.get_popup().hide()
		app.return_to_work()
		app.select_puzzle(0)
		await frames()
		check(app.board.clue_font().data == app.FullViewBoard.Typography.SOURCE.data,"actual PCK original Delight clue bytes")
		await shot("work-%d" % spec[0])
		app.show_album()
		app.show_information("help")
		await frames()
		await shot("help-%d" % spec[0])
		app.return_to_work()
	# A synthetic glyph sheet supplements real controls; no generated font art.
	var panel := PanelContainer.new()
	panel.position = Vector2(100,200)
	var paper := StyleBoxFlat.new()
	paper.bg_color = Color("fffaf0")
	paper.set_content_margin_all(16)
	panel.add_theme_stylebox_override("panel",paper)
	var sample := Label.new()
	sample.text = "Tidy Hand · Größe Straße ÄÖÜ äöü ß\n× · … % „Anführungen“ – − ← → ↑ ↓\nNicht eingestuft · Sehr leicht · Sehr schwer\n20 × 20 · 40 × 40 · 50 × 50"
	sample.add_theme_font_override("font",Text.font())
	sample.add_theme_font_size_override("font_size",24)
	panel.add_child(sample)
	app.add_child(panel)
	await shot("glyphs")
	var report := {"test_only":true,"package":"HZ-B","contour_hashes":contour_hashes,"checks":checks,"failures":failures,"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"engine":Engine.get_version_info()}
	var file := FileAccess.open(output.path_join("pack.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n")
	file.close()
	app.free()
	print("HZ_PACK_OK ",checks)
	quit(0 if failures.is_empty() else 4)
