extends SceneTree
## External probe runs against the actual separate Windows PCK, never source fallbacks.
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
var failures: int = 0

func digest(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()

func backgrounds() -> void:
	# Inspect actual remaps and decoded mipmaps, not source-PNG hashes against
	# unrelated compressed bytes. Expected source bindings arrive outside the PCK.
	var expected: Dictionary = {}
	var expected_path: String = OS.get_environment("HP_BACKGROUND_EXPECTED")
	if not expected_path.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(expected_path))
		check(parsed is Dictionary, "PCK external background inventory is readable")
		if parsed is Dictionary: expected = parsed
		check(expected.get("registry_sha256", "") == digest(FileAccess.get_file_as_bytes(Registry.PATH)), "PCK background inventory binds actual runtime bytes")
	var expected_rows: Dictionary = {}
	for row: Dictionary in expected.get("assets", []): expected_rows[row.id] = row
	var wanted: Array[String] = []
	var wanted_imports: Array[String] = []
	var reports: Array[Dictionary] = []
	for entry: Dictionary in Registry.entries():
		var background: Dictionary = Registry.background(entry)
		if background.status != "selected": continue
		var path: String = "res://" + str(background.asset.file)
		var notice: String = path.get_basename() + ".txt"
		wanted.append(path.get_file())
		wanted.append(notice.get_file())
		check(FileAccess.file_exists(path + ".import"), "PCK background import remap " + entry.id)
		check(FileAccess.file_exists(notice), "PCK background notice " + entry.id)
		check(not FileAccess.file_exists(path), "PCK does not duplicate raw background PNG " + entry.id)
		var config := ConfigFile.new()
		if config.load(path + ".import") != OK:
			check(false, "PCK readable background remap " + entry.id)
			continue
		var imported: String = str(config.get_value("remap", "path", ""))
		var canonical: String = "res://.godot/imported/" + path.get_file() + "-" + path.md5_text() + ".ctex"
		wanted_imports.append(canonical.get_file())
		check(config.get_value("remap", "importer", "") == "texture" and config.get_value("remap", "type", "") == "CompressedTexture2D" and imported == canonical, "PCK background texture import " + entry.id)
		check(FileAccess.file_exists(imported), "PCK background imported bytes " + entry.id)
		var resource: Resource = ResourceLoader.load(path, "Texture2D", ResourceLoader.CACHE_MODE_IGNORE)
		if not resource is Texture2D:
			check(false, "PCK background texture load " + entry.id)
			continue
		var texture: Texture2D = resource as Texture2D
		var decoded: Image = texture.get_image()
		if decoded == null:
			check(false, "PCK background decoded pixels " + entry.id)
			continue
		check(texture.get_size() == Vector2(2304,576) and decoded.get_size() == Vector2i(2304,576), "PCK background PNG2304 dimensions " + entry.id)
		var imported_bytes: PackedByteArray = FileAccess.get_file_as_bytes(imported)
		check(imported_bytes.size() >= 52 and decoded.get_format() == imported_bytes.decode_u32(48) and decoded.get_format() in [Image.FORMAT_LA8, Image.FORMAT_RGBA8], "PCK background format matches actual imported LA8/RGBA8 " + entry.id)
		check(decoded.has_mipmaps() and decoded.get_mipmap_count() == 11, "PCK background full mipmaps " + entry.id)
		# Canonical RGBA is solely the measured decoder view. The source PNG and
		# compressed texture are unchanged, including native grayscale-alpha.
		decoded.convert(Image.FORMAT_RGBA8)
		var total_bytes: int = decoded.get_data().size()
		var mipmaps: int = decoded.get_mipmap_count()
		decoded.clear_mipmaps()
		var base: PackedByteArray = decoded.get_data()
		var row: Dictionary = {"id":entry.id, "image_revision":background.image_revision, "asset":background.asset,
			"remap":imported, "imported_bytes":imported_bytes.size(),
			"base_rgba_sha256":digest(base), "decoded_base_bytes":base.size(),
			"decoded_with_mips_bytes":total_bytes, "mipmap_count":mipmaps,
			"notice_sha256":digest(FileAccess.get_file_as_bytes(notice))}
		if not expected_path.is_empty():
			check(expected_rows.has(entry.id), "PCK selected background matches external inventory " + entry.id)
			if expected_rows.has(entry.id):
				var source: Dictionary = expected_rows[entry.id]
				check(source.asset == background.asset and source.image_revision == background.image_revision and source.notice.sha256 == row.notice_sha256 and int(source.notice.bytes) == FileAccess.get_file_as_bytes(notice).size(), "PCK background/notice source binding " + entry.id)
				if source.has("rgba_sha256"):
					check(source.rgba_sha256 == row.base_rgba_sha256, "PCK background lossless base RGBA " + entry.id)
		reports.append(row)
	var actual: Array[String] = []
	var directory := DirAccess.open("res://art/backgrounds")
	if directory != null:
		check(directory.get_directories().is_empty(), "PCK background namespace has no authoring subdirectories")
		for name: String in directory.get_files():
			actual.append(name.trim_suffix(".import") if name.ends_with(".png.import") else name)
	wanted.sort()
	actual.sort()
	check(actual == wanted, "PCK exact selected background/notice inventory")
	var actual_imports: Array[String] = []
	var imported_directory := DirAccess.open("res://.godot/imported")
	if imported_directory != null:
		for name: String in imported_directory.get_files():
			if not name.ends_with(".ctex") or not ".png-" in name: continue
			var source_name: String = name.get_slice(".png-",0) + ".png"
			var source_path: String = "res://art/backgrounds/" + source_name
			if name == source_name + "-" + source_path.md5_text() + ".ctex": actual_imports.append(name)
	wanted_imports.sort()
	actual_imports.sort()
	check(actual_imports == wanted_imports, "PCK exact selected background import inventory")
	if not expected_path.is_empty(): check(reports.size() == expected_rows.size(), "PCK exact background source selection")
	var web: bool = OS.get_environment("HP_BACKGROUND_PACK_TARGET") == "web"
	check(FileAccess.file_exists("res://web/background_loader.js") == web, "PCK platform-specific background decoder")
	check(not FileAccess.file_exists("res://web/shell.html") and not FileAccess.file_exists("res://web/storage.js"), "PCK excludes external Web delivery files")
	var output: String = OS.get_environment("HP_BACKGROUND_REPORT")
	if not output.is_empty():
		var file := FileAccess.open(output, FileAccess.WRITE)
		check(file != null, "PCK background report destination")
		if file != null: file.store_string(JSON.stringify({"format":"picross-background-pack-v1", "target":"web" if web else "windows", "images":reports, "inventory":actual, "imported_inventory":actual_imports}, "\t") + "\n")

func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		push_error(message)

func walk(path: String) -> void:
	var directory: DirAccess = DirAccess.open(path)
	check(directory != null,"PCK directory available")
	if directory == null: return
	for name: String in directory.get_directories():
		if name == ".godot": continue
		check(not name in ["tests","production","input","packages","full_view_study","study","perf_a"],"technical directory in PCK: "+path+name)
		walk(path.path_join(name))
	for name: String in directory.get_files():
		check(not "proof" in name and not name.ends_with(".zip") and not name in ["handoff.json","inventory.json","approval.json","derivation.json","inspection.json","categories.json"],"technical file in PCK: "+name)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	walk("res://")
	check(ProjectSettings.get_setting("application/config/name") == "picross · P1", "PCK unchanged application identity")
	check(ProjectSettings.get_setting("application/run/main_scene") == "res://main.tscn", "PCK regular startup scene")
	var scene: PackedScene = load("res://main.tscn")
	var root_entry: Node = scene.instantiate()
	check(root_entry is Node3D and root_entry.get_script().resource_path == "res://book/main.gd", "PCK regular book root, no hidden old entry")
	root_entry.free()
	for name: String in ["main.gd","content.gd","binding.gd","catalog.gd","information.gd","information_routes.gd","surface.gd","page.gdshader","material.gdshader","fold.gdshaderinc"]:
		check(ResourceLoader.exists("res://book/"+name), "PCK shared book dependency "+name)
	for name: String in ["web_probe.gd","web_root.gd","windows_observer.gd","fixtures.json","inputs.gd","verify.gd"]:
		check(not ResourceLoader.exists("res://book/"+name) and not FileAccess.file_exists("res://book/"+name), "PCK excludes technical book input "+name)
	for name: String in ["paper","leather","table"]:
		var material: Texture2D = load("res://book/"+name+".png")
		var provenance: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://book/"+name+".json"))
		check(material != null and material.get_width() == provenance.size[0] and material.get_height() == provenance.size[1], "PCK imported material and rights "+name)
	for name: String in ["help_panel","help_example","help_examples"]:
		check(ResourceLoader.exists("res://ui/"+name+".gd"),"PCK passive help dependency "+name)
	var examples = load("res://ui/help_examples.gd")
	check(examples.all().size() == 16,"PCK complete passive teaching diagrams")
	var ids: Array[String] = Registry.catalog_ids()
	# Fixed shared KB resources, independent of the growing puzzle catalog.
	var book_manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/manifest.json"))
	var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
	check(icons.size() == 28 and icons.has("quit") and icons.has("checkbox-checked") and icons.has("reset"), "PCK active HZ-B/SBR icon inventory")
	check(book_manifest.has("hz_icon_source") and FileAccess.file_exists("res://art/book/HZ-B-284-NOTICE.txt"), "PCK HZ-B provenance")
	for name: String in icons:
		var texture: Texture2D = load("res://art/book/"+name+".svg")
		check(texture != null and texture.get_size() == Vector2(26,26), "PCK imported KB icon available "+name)
		var bound: bool = false
		for entry: Dictionary in book_manifest.files:
			if entry.file == name+".svg": bound = true
		check(bound, "PCK icon bound to resource manifest "+name)
	# SBR resources must resolve from the actual Windows/Web pack as well as
	# the source theme. The external probe itself is never shipped.
	var controls = load("res://ui/book_controls.gd")
	var scrollbar_theme := Theme.new()
	controls.scrollbars(scrollbar_theme,1.25)
	for type: String in ["VScrollBar","HScrollBar"]:
		var style: StyleBox = scrollbar_theme.get_stylebox("grabber",type)
		check(style.get_script().resource_path == "res://ui/scrollbar_style.gd" and style.ui_scale == 1.25,"PCK shared SBR StyleBox "+type)
		for direction: String in ["increment","decrement"]:
			check(scrollbar_theme.get_icon(direction,type).get_size() == Vector2(28,28),"PCK imported SBR triangle "+type+direction)
	check(FileAccess.file_exists("res://art/book/KB-168-NOTICE.txt"), "PCK KB icon provenance notice")
	# Actual exported font bytes/role, with controlled local fallbacks.
	var ui_text = load("res://ui/ui_text.gd")
	var normal: FontFile = ui_text.font()
	check(normal.data == ui_text.SOURCE.data and not normal.allow_system_fallback, "PCK HZ original Pangolin/local role")
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(normal.data)
	check(hash.finish().hex_encode() == "a48db64eadc589c2e9f14a4ba79eed82a438c7f620f929dd19e352c20b2a922e", "PCK HZ Pangolin bytes")
	check(normal.fallbacks.size() == 1 and normal.fallbacks[0].get_font_name() == "IBM Plex Sans" and not normal.fallbacks[0].allow_system_fallback, "PCK HZ bundled fallback")
	check(FileAccess.file_exists("res://art/drawing/pangolin/NOTICE.txt"), "PCK PANG provenance")
	hash.start(HashingContext.HASH_SHA256)
	hash.update(FileAccess.get_file_as_bytes("res://art/drawing/pangolin/OFL.txt"))
	check(hash.finish().hex_encode() == "414e35e9875605ea0dfe549a6bdad6d1f1f3d5427c97af2060213adb6709484c", "PCK PANG original OFL bytes")
	check(not ResourceLoader.exists("res://art/drawing/TidyHand.ttf") and not FileAccess.file_exists("res://art/drawing/tidy-hand/NOTICE.txt"), "PCK excludes inactive historical Tidy Hand")
	check(Registry.load_error.is_empty(), "PCK registry/category format invalid")
	backgrounds()
	var categories: Array[Dictionary] = Registry.categories()
	check(not categories.is_empty(), "PCK categories projection missing")
	var category_ids: Array[String] = []
	for category: Dictionary in categories:
		category_ids.append(category.id)
	# Fixed runtime-contract samples; never extend this set when adding content.
	for key: String in ["t01", "t02", "t04", "t06", "t08", "t09", "pz-test-direct-mono", "pz-test-direct-color", "pz-test-repair-mono", "pz-test-repair-color"]:
		if not key in ids: continue
		var entry: Dictionary = Registry.by_key(key)
		check(entry.category_id in category_ids, "PCK category assignment missing " + key)
		check(not Definition.load_fixture(key).is_empty(),"PCK definition missing "+key)
		check(Definition.validate(Definition.load_fixture(key)).is_empty(),"PCK content invalid "+key)
		if key.begins_with("pz-"):
			check(FileAccess.file_exists("res://"+str(entry.reveal).get_basename()+".txt"),"PCK usage notice missing")
	check(ids.size() == int(OS.get_environment("ZA1_PACK_COUNT")),"PCK selection count")
	if failures == 0: print("CONTENT_PACK_OK count=",ids.size())
	quit(0 if failures == 0 else 4)
