extends RefCounted
## One native request at a time. The owner keeps only the latest desired visit.
## CACHE_MODE_IGNORE and draining before reuse prevent stale same-path revisions.
var path: String = ""

func start(resource_path: String) -> String:
	if not path.is_empty(): return "loader_busy"
	if not ResourceLoader.exists(resource_path, "Texture2D"):
		return "missing_texture"
	var error: Error = ResourceLoader.load_threaded_request(resource_path, "Texture2D", false, ResourceLoader.CACHE_MODE_IGNORE)
	if error != OK: return "request_failed_%d" % error
	path = resource_path
	return ""

func poll() -> Dictionary:
	if path.is_empty(): return {"status":"error", "error":"no_request"}
	var status: ResourceLoader.ThreadLoadStatus = ResourceLoader.load_threaded_get_status(path)
	if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		return {"status":"pending"}
	# get() is called only after a terminal status, never as a blocking wait.
	# The terminal read also releases ResourceLoader's user-request token.
	var result: Resource = ResourceLoader.load_threaded_get(path) if status != ResourceLoader.THREAD_LOAD_INVALID_RESOURCE else null
	path = ""
	if status != ResourceLoader.THREAD_LOAD_LOADED or not result is Texture2D:
		return {"status":"error", "error":"texture_load_failed"}
	return {"status":"loaded", "texture":result}

func cancel() -> bool:
	# Godot cannot cancel a started threaded resource request. The control keeps
	# polling this single stale operation, discards it, then serves the newest wish.
	return path.is_empty()
