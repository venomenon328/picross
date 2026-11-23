extends Node
const Recent = preload("res://model/recent_puzzle.gd")
const Registry = preload("res://model/content_registry.gd")

func send(server: String, path: String, method: int, raw: String, session: Dictionary) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = 30.0
	http.max_redirects = 0
	http.body_size_limit = 16 * 1024 * 1024
	add_child(http)
	var headers := PackedStringArray(["Content-Type: application/json"])
	if not session.is_empty():
		headers.append("Authorization: Bearer " + str(session.token))
		headers.append("X-Picross-Generation: " + str(session.generation))
	var result := {"status":0,"generation":"","retry_after":0,"body":{}}
	if http.request_raw(server+path,headers,method,raw.to_utf8_buffer()) == OK:
		var values: Array = await http.request_completed
		if values[0] == HTTPRequest.RESULT_SUCCESS:
			result.status = int(values[1])
			for header: String in values[2]:
				var field := header.get_slice(":",0).strip_edges().to_lower()
				var value := header.substr(header.find(":")+1).strip_edges()
				if field == "x-picross-generation": result.generation = value
				if field == "retry-after" and value.is_valid_int(): result.retry_after = maxi(0,int(value))
			var bytes: PackedByteArray = values[3]
			if Recent.valid_utf8(bytes):
				var content := bytes.get_string_from_utf8()
				if Registry.unique_keys(content):
					var body: Variant = JSON.parse_string(content)
					if body is Dictionary: result.body = body
	http.queue_free()
	return result
