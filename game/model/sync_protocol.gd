extends RefCounted
## Closed v1 mutation vocabulary. Identity/generation are local bindings, never body fields.
const FORMAT = "picross-sync/v1"
const MAX_INTEGER = 9007199254740991
const SEQUENCE_ERRORS = ["sequence_reused", "sequence_stale", "sequence_gap"]

const PROGRESS_FORMAT = "picross-progress/v1"
const PROGRESS_FIELDS = ["definition_id","definition_revision","width","height","cells","undo_used","completed"]

static func matches(value: Variant, pattern: String) -> bool:
	if not value is String:
		return false
	var regex := RegEx.new()
	regex.compile(pattern)
	return regex.search(value) != null

static func uuid(value: Variant) -> bool:
	return matches(value, "\\A[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\\z")

static func count(value: Variant, minimum: int = 0) -> bool:
	return (value is int or value is float) and value >= minimum and value <= MAX_INTEGER and floor(value) == value

## Called only after SaveStore has validated the full local snapshot.
static func progress(snapshot: Dictionary) -> Dictionary:
	var result := {"format":PROGRESS_FORMAT}
	for key: String in PROGRESS_FIELDS:
		result[key] = snapshot[key]
	# Godot parses JSON numbers as floats. Canonicalize integral wire fields before hashing.
	for key: String in ["definition_revision","width","height"]:
		result[key] = int(result[key])
	var cells: Array[int] = []
	for cell: Variant in snapshot.cells:
		cells.append(int(cell))
	result.cells = cells
	return result

static func valid_progress(value: Variant, id: String) -> bool:
	if not value is Dictionary or value.size() != 8 or not value.has_all(PROGRESS_FIELDS) or value.get("format") != PROGRESS_FORMAT:
		return false
	if value.definition_id != id or not count(value.definition_revision,1):
		return false
	if not count(value.width,1) or value.width > 50 or not count(value.height,1) or value.height > 50:
		return false
	if not value.undo_used is bool or not value.completed is bool or not value.cells is Array or value.cells.size() != value.width * value.height:
		return false
	var colors := {}
	for cell: Variant in value.cells:
		if not count(cell,-1): return false
		if cell > 0: colors[int(cell)] = true
	return colors.size() <= 8

static func mutation(entry: Dictionary, sequence: int, base: int) -> Dictionary:
	if not count(sequence, 1) or not count(base):
		return {}
	var body := {"format":FORMAT, "request_seq":sequence, "base_server_revision":base, "operation":entry.operation}
	match entry.operation:
		"snapshot":
			if not valid_progress(entry.value,entry.id): return {}
			body.save = entry.value
		"reset":
			if not count(entry.value, 1): return {}
			body.definition_revision = entry.value
		"resolve", "discard":
			if not uuid(entry.value): return {}
			body.candidate_id = entry.value
		"restore":
			if not count(entry.value, 1): return {}
			body.history_revision = entry.value
		_:
			return {}
	return body

static func valid_reply(request: Dictionary, status: int, reply: Dictionary) -> bool:
	var body: Dictionary = JSON.parse_string(request.body)
	if reply.size() != 7 or not reply.has_all(["format","request_seq","outcome","server_revision","candidate_id","code","sequence_consumed"]):
		return false
	if reply.format != FORMAT or not count(reply.request_seq, 1) or reply.request_seq != body.request_seq or not count(reply.server_revision) or not reply.sequence_consumed is bool:
		return false
	if (status != 200 if reply.code == "ok" else status != 409):
		return false
	if reply.sequence_consumed == (reply.code in SEQUENCE_ERRORS):
		return false
	match reply.code:
		"ok":
			var candidate: Variant = body.get("candidate_id")
			var discard: bool = body.operation == "discard"
			return (reply.candidate_id == candidate and reply.outcome == ("discarded" if discard else "applied")
				and reply.server_revision == body.base_server_revision + (0 if discard else 1))
		"conflict_saved":
			return body.operation in ["snapshot","reset"] and reply.outcome == "conflict" and uuid(reply.candidate_id)
		"candidate_missing", "history_missing", "revision_conflict", "storage_limit", "conflict_limit", "sequence_reused", "sequence_stale", "sequence_gap":
			return reply.outcome == "rejected" and reply.candidate_id == null
	return false
