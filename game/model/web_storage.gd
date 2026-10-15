extends RefCounted
## Acknowledges the pinned engine's IDBFS transactions; SaveStore remains authoritative.
static func changed() -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.picrossStorage.changed()", true)

static func view_changed() -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.picrossStorage.viewChanged()", true)

static func finished(slot: String, error: String) -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.picrossStorage.finished(" + JSON.stringify(slot) + "," + JSON.stringify(error) + ")", true)
