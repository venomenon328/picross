extends RefCounted
## Reads the bundled lossless import, never a duplicate raw production PNG.
## Browser image decoding occurs in one ordinary Worker, not Godot's synchronous
## threadless ResourceLoader fallback. Publication stays with the visit owner.
const SCRIPT_PATH: String = "res://web/background_loader.js"
const MAX_IMPORT_BYTES: int = 67108864
const MIPMAP_BYTES: int = 7077844
var bridge: JavaScriptObject
var path: String = ""
var initialization_error: String = ""

func _init() -> void:
	if not OS.has_feature("web"):
		initialization_error = "not_web_backend"
		return
	var script: FileAccess = FileAccess.open(SCRIPT_PATH, FileAccess.READ)
	if script == null or script.get_length() > 65536:
		initialization_error = "missing_web_decoder"
		return
	JavaScriptBridge.eval(script.get_as_text(), true)
	var factory: JavaScriptObject = JavaScriptBridge.get_interface("picrossBackgroundLoader")
	if factory == null:
		initialization_error = "web_bridge_unavailable"
		return
	bridge = factory.create()
	if bridge == null: initialization_error = "web_decoder_unavailable"

func start(resource_path: String) -> String:
	if not path.is_empty(): return "loader_busy"
	if bridge == null: return initialization_error
	var remap := ConfigFile.new()
	if remap.load(resource_path + ".import") != OK:
		return "missing_texture_import"
	var imported: Variant = remap.get_value("remap", "path", null)
	if remap.get_value("remap", "importer", "") != "texture" or remap.get_value("remap", "type", "") != "CompressedTexture2D" or not imported is String:
		return "invalid_texture_import"
	if not imported.begins_with("res://.godot/imported/") or not imported.ends_with(".ctex") or ".." in imported or "\\" in imported:
		return "invalid_texture_remap"
	var file: FileAccess = FileAccess.open(imported, FileAccess.READ)
	if file == null or file.get_length() < 56 or file.get_length() > MAX_IMPORT_BYTES:
		return "missing_or_oversized_texture_import"
	var bytes: PackedByteArray = file.get_buffer(file.get_length())
	if bytes.size() != file.get_length(): return "incomplete_texture_import"
	# PackedByteArray is not a supported outbound JavaScriptBridge argument in
	# pinned Godot 4.7.2. String conversion is explicit; atob runs in the worker.
	var error: String = bridge.start(Marshalls.raw_to_base64(bytes))
	if not error.is_empty(): return error
	path = resource_path
	return ""

func poll() -> Dictionary:
	if bridge == null or path.is_empty(): return {"status":"error", "error":"no_request"}
	var status: String = bridge.poll()
	if status == "pending": return {"status":"pending"}
	path = ""
	if status != "loaded": return {"status":"error", "error":str(bridge.error())}
	var buffer: JavaScriptObject = bridge.take()
	if buffer == null or not JavaScriptBridge.is_js_buffer(buffer):
		return {"status":"error", "error":"invalid_web_pixel_buffer"}
	var bytes: PackedByteArray = JavaScriptBridge.js_buffer_to_packed_byte_array(buffer)
	if bytes.size() != MIPMAP_BYTES: return {"status":"error", "error":"invalid_web_mipmap_bytes"}
	var image: Image = Image.create_from_data(2304, 576, true, Image.FORMAT_RGBA8, bytes)
	return {"status":"loaded", "texture":ImageTexture.create_from_image(image), "image":image}

func cancel() -> bool:
	if bridge != null and not path.is_empty(): bridge.cancel()
	path = ""
	return true

func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and bridge != null: bridge.close()
