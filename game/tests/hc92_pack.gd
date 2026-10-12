extends SceneTree
## External probe loaded against --main-pack, without a source project overlay.
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var font: FontFile = load("res://art/drawing/DelightCoffee-Regular.ttf")
	var digest: HashingContext = HashingContext.new()
	digest.start(HashingContext.HASH_SHA256)
	digest.update(font.data)
	var hash: String = digest.finish().hex_encode()
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var digits: Array = []
	var ok: bool = hash=="4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23" and font.get_font_name()=="Delight Coffee"
	for digit: String in "0123456789":
		var glyph: int = ts.font_get_glyph_index(rid,24,digit.unicode_at(0),0)
		digits.append({"digit":digit,"glyph_index":glyph,"rid_family":ts.font_get_name(rid)})
		ok = ok and glyph>0 and ts.font_get_name(rid)=="Delight Coffee"
	var notices: Dictionary = {}
	for name: String in ["More Info.txt","Read Me.pdf"]:
		var path: String = "res://art/drawing/delight-coffee/"+name
		ok = ok and FileAccess.file_exists(path)
		notices[name] = FileAccess.get_sha256(path)
	var board = load("res://ui/full_view_board.gd").new()
	ok = ok and board.clue_font().get_font_name()=="Delight Coffee" and board.clue_font().fallbacks.is_empty() and not board.clue_font().allow_system_fallback
	board.free()
	var report: Dictionary = {"success":ok,"font_sha256":hash,"digits":digits,"notices":notices,"source_project_overlay":false}
	FileAccess.open(OS.get_environment("HC92_OUTPUT").path_join("hc92-pack.json"),FileAccess.WRITE).store_string(JSON.stringify(report)+"\n")
	print("HC92_PACK_", "OK" if ok else "FAILED")
	quit(0 if ok else 1)
