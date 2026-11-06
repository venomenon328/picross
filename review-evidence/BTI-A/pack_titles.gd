extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var manifest = JSON.parse_string(FileAccess.get_file_as_string("res://art/drawing/view_titles/manifest.json"))
	assert(manifest.assets.size() == 3)
	assert(FileAccess.get_file_as_string("res://art/drawing/view_titles/NOTICE.txt").contains("BTI-C-1"))
	var names: Array = []
	for entry: Dictionary in manifest.assets:
		var texture: Texture2D = load("res://art/drawing/view_titles/"+entry.file)
		assert(texture != null and texture.get_width() == entry.width and texture.get_height() == entry.height)
		var pixels: Image = texture.get_image()
		assert(pixels.has_mipmaps() and pixels.detect_alpha() != Image.ALPHA_NONE)
		names.append(entry.title)
	var Heading = load("res://ui/view_title.gd")
	assert(Heading.TITLES.values() == ["Rätselkatalog","Hilfe","Einstellungen"])
	print("BTI_PACK_OK ",names," imported RGBA/mipmaps and manifest/notice in actual PCK")
	quit()
