extends SceneTree
func _initialize() -> void:
	var failures: Array = []
	var rows: Array = []
	var paths: Array = JSON.parse_string(OS.get_environment("RZ_PACK_PATHS"))
	var width: int = OS.get_environment("RZ_PACK_WIDTH").to_int()
	var mips: bool = OS.get_environment("RZ_PACK_MIPS") == "true"
	for path: String in paths:
		var times: Array = []
		var texture: Texture2D
		for i: int in range(3):
			texture = null
			var start: int = Time.get_ticks_usec()
			texture = ResourceLoader.load(path,"Texture2D",ResourceLoader.CACHE_MODE_IGNORE) as Texture2D
			times.append((Time.get_ticks_usec()-start)/1000.0)
		if texture == null:
			failures.append("missing packed texture "+path)
			continue
		var image: Image = texture.get_image()
		if texture.get_size() != Vector2(width,width/4) or image == null or image.has_mipmaps() != mips:
			failures.append("packed dimensions/mips mismatch "+path)
		rows.append({"path":path,"width":texture.get_width(),"height":texture.get_height(),"mipmaps":image.has_mipmaps() if image != null else false,"image_bytes":image.get_data_size() if image != null else 0,"load_ms":times})
	var file := FileAccess.open(OS.get_environment("RZ_PACK_OUTPUT"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"os":OS.get_name(),"executable":OS.get_executable_path(),"rows":rows,"failures":failures},"\t"))
	file.close()
	print("RZ_PACK_READ ",rows.size()," failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
