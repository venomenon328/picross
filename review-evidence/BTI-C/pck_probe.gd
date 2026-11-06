extends SceneTree
var checks: int = 0
var failures: Array[String] = []
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var expected: String = OS.get_environment("BTI_SOURCE").path_join("game/art/drawing/view_titles")
	var prefix: String = "res://art/drawing/view_titles/"
	for name: String in ["NOTICE.txt","manifest.json","provenance.json"]:
		check(FileAccess.get_file_as_bytes(prefix+name) == FileAccess.get_file_as_bytes(expected.path_join(name)),"exact packaged "+name)
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(prefix+"manifest.json"))
	var records: Array = []
	for asset: Dictionary in manifest.assets:
		var texture: Texture2D = load(prefix+asset.file)
		check(texture != null,"title imported "+asset.file)
		var image: Image = texture.get_image()
		check(image.has_mipmaps() and image.detect_alpha() != Image.ALPHA_NONE,"alpha and mipmaps "+asset.file)
		image.clear_mipmaps();image.convert(Image.FORMAT_RGBA8)
		var source: Image = Image.load_from_file(expected.path_join(asset.file))
		source.convert(Image.FORMAT_RGBA8)
		check(source.get_size() == image.get_size(),"PNG dimensions preserved "+asset.file)
		check(FileAccess.get_sha256(expected.path_join(asset.file))==asset.sha256,"approved source hash "+asset.file)
		var a: PackedByteArray = image.get_data()
		var b: PackedByteArray = source.get_data()
		var same: bool = a.size()==b.size()
		var min_x: int = image.get_width()
		var min_y: int = image.get_height()
		var max_x: int = 0
		var max_y: int = 0
		for i: int in range(3,mini(a.size(),b.size()),4):
			if a[i] != b[i]: same=false
			if a[i] >= 16:
				var pixel: int = (i-3)/4
				var x: int = pixel%image.get_width()
				var y: int = pixel/image.get_width()
				min_x=mini(min_x,x);min_y=mini(min_y,y);max_x=maxi(max_x,x+1);max_y=maxi(max_y,y+1)
		check(same,"every alpha byte including weak edges preserved "+asset.file)
		var bounds: Array = asset.optical_bounds
		check(min_x==int(bounds[0]) and min_y==int(bounds[1]) and max_x==int(bounds[2]) and max_y==int(bounds[3]),"independent optical bounds "+asset.file)
		records.append({"file":asset.file,"source_sha256":asset.sha256,"width":image.get_width(),"height":image.get_height(),"every_alpha_byte_equal":same,"optical_bounds":[min_x,min_y,max_x,max_y+0]})
	# Exercise the packaged helper against missing resources, not a source-tree mock.
	var script: Script = load("res://ui/view_title.gd")
	for role: String in ["catalog","help","settings"]:
		var title: Control = script.new()
		root.add_child(title)
		var label := Label.new()
		label.add_theme_font_override("font",load("res://art/drawing/BaksoDaging-Regular.ttf"))
		title.configure(role,label)
		title.load_art("res://art/drawing/view_titles/missing.png")
		check(title.texture==null and label.visible and label.text==title.TITLES[role] and title.accessibility_name==label.text,"packaged missing-image fallback "+role)
		title.load_art(prefix+role+".png")
		check(title.texture!=null and not label.visible,"packaged image restored without duplicate "+role)
		title.free()
	var result: Dictionary = {"checks":checks,"failures":failures,"records":records,"pack":OS.get_environment("BTI_PACK")}
	var output := FileAccess.open(OS.get_environment("BTI_PCK_REPORT"),FileAccess.WRITE)
	output.store_string(JSON.stringify(result,"\t")+"\n");output.close()
	print("BTI_PCK_OK ",checks," ",failures)
	quit(0 if failures.is_empty() else 4)
