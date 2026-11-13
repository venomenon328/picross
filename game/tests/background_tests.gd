extends SceneTree
## Small native.catalog contract probe. No production images, saves or captures.
const Registry = preload("res://model/content_registry.gd")
const Background = preload("res://book/puzzle_background.gd")
var checks: int = 0
var failures: Array[String] = []

class ControlledLoader extends RefCounted:
	var busy: bool = false
	var paths: Array[String] = []
	var result: Dictionary = {}
	var start_error: String = ""
	func start(path: String) -> String:
		if busy: return "unexpected_parallel_request"
		paths.append(path)
		if not start_error.is_empty(): return start_error
		busy = true
		return ""
	func poll() -> Dictionary:
		if result.is_empty(): return {"status":"pending"}
		var next: Dictionary = result
		result = {}
		busy = false
		return next
	func cancel() -> bool:
		return not busy
	func finish(texture: Texture2D) -> void:
		result = {"status":"loaded", "texture":texture}
	func fail() -> void:
		result = {"status":"error", "error":"controlled_decode_failure"}

func _init() -> void:
	call_deferred("run")

func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition: failures.append(label)

static func entry(identifier: String = "pz-background-a", status: String = "selected", revision: int = 1) -> Dictionary:
	return {
		"id":identifier, "key":"background_a", "save_slot":"background_a",
		"definition":"data/content/background_a.json", "reveal":"art/content/background_a.png",
		"category_id":"test", "visible":true, "added_at":null, "difficulty":null,
		"background":{"status":status, "image_revision":null if status == "legacy" else revision,
			"asset":{"file":"art/backgrounds/" + identifier + ".png", "sha256":"a".repeat(64), "bytes":1234} if status == "selected" else null}
	}

static func registry(item: Dictionary, version: int = 6) -> Dictionary:
	return {"format":"picross-runtime-registry-v%d" % version, "categories":[{"id":"test", "name":"Test", "order":1}], "entries":[item]}

func reader_cases() -> void:
	for status: String in ["selected", "none", "legacy"]:
		check(Registry.validate(registry(entry("pz-background-a", status))).is_empty(), "v6 accepts " + status)
	var difficulty: Dictionary = {"method":"picross-difficulty-0.4", "level":"L2", "assessment_type":"instrumented", "confidence":"medium", "plausible_range":["L2", "L2"], "r4_required":false}
	for version: int in range(2, 7):
		var item: Dictionary = entry()
		if version < 6: item.erase("background")
		if version < 4: item.erase("added_at")
		if version < 3: item.erase("difficulty")
		check(Registry.validate(registry(item, version)).is_empty(), "unchanged version shape %d" % version)
		if version < 6: check(Registry.background(item) == Registry.LEGACY_BACKGROUND, "old entry means legacy %d" % version)
		if version >= 3:
			item.difficulty = difficulty
			check(Registry.validate(registry(item, version)).is_empty() == (version >= 5), "v5 difficulty semantics %d" % version)
		if version < 6:
			item["background"] = Registry.LEGACY_BACKGROUND
			check(not Registry.validate(registry(item, version)).is_empty(), "old version rejects background field %d" % version)
	for field: String in entry():
		var item: Dictionary = entry()
		item.erase(field)
		check(not Registry.validate(registry(item)).is_empty(), "v6 missing entry field " + field)
	var extra: Dictionary = entry()
	extra["offset"] = 3
	check(not Registry.validate(registry(extra)).is_empty(), "v6 extra entry field")
	for value: Variant in [null, [], "legacy", {}, {"status":"none", "asset":null}, {"status":"legacy", "image_revision":null, "asset":null, "offset":0}]:
		var item: Dictionary = entry()
		item.background = value
		check(not Registry.validate(registry(item)).is_empty(), "closed background fields " + str(value))
	for status: Variant in ["unknown", null, 1, true]:
		var item: Dictionary = entry()
		item.background.status = status
		check(not Registry.validate(registry(item)).is_empty(), "invalid background status " + str(status))
	for status: String in ["none", "selected"]:
		for revision: Variant in [null, 0, -1, true, "1", 1.5, 1000001, INF, NAN]:
			var item: Dictionary = entry("pz-background-a", status)
			item.background.image_revision = revision
			check(not Registry.validate(registry(item)).is_empty(), "invalid revision " + status + "/" + str(revision))
	for status: String in ["legacy", "none"]:
		var item: Dictionary = entry("pz-background-a", status)
		item.background.asset = entry().background.asset
		check(not Registry.validate(registry(item)).is_empty(), "no asset for " + status)
	var nonnull_legacy: Dictionary = entry("pz-background-a", "legacy")
	nonnull_legacy.background.image_revision = 1
	check(not Registry.validate(registry(nonnull_legacy)).is_empty(), "legacy revision must be null")
	for asset: Variant in [null, {}, [], "art/backgrounds/pz-background-a.png", {"file":"art/backgrounds/pz-background-a.png", "bytes":1234}, {"file":"art/backgrounds/pz-background-a.png", "bytes":1234, "sha256":"a".repeat(64), "extra":true}]:
		var item: Dictionary = entry()
		item.background.asset = asset
		check(not Registry.validate(registry(item)).is_empty(), "closed selected asset " + str(asset))
	for path: Variant in [null, true, 1, "art/backgrounds/other.png", "art/backgrounds/../pz-background-a.png", "res://art/backgrounds/pz-background-a.png", "/art/backgrounds/pz-background-a.png", "art\\backgrounds\\pz-background-a.png", "art/backgrounds/PZ-background-a.png", "art/backgrounds/pz-background-a.png "]:
		var item: Dictionary = entry()
		item.background.asset.file = path
		check(not Registry.validate(registry(item)).is_empty(), "reject path alias " + str(path))
	for identifier: String in ["pz-", "PZ-a", "pz-A", "pz-a/b", "pz-" + "a".repeat(61), "pz-_a"]:
		check(not Registry.validate(registry(entry(identifier))).is_empty(), "reject v6 puzzle ID " + identifier)
	for digest: Variant in [null, 1, "a".repeat(63), "A".repeat(64), "g".repeat(64)]:
		var item: Dictionary = entry()
		item.background.asset.sha256 = digest
		check(not Registry.validate(registry(item)).is_empty(), "reject digest " + str(digest))
	for count: Variant in [null, true, -1, 1.5, "2", 67108865, INF]:
		var item: Dictionary = entry()
		item.background.asset.bytes = count
		check(not Registry.validate(registry(item)).is_empty(), "reject ref byte count " + str(count))
	for count: int in [0, 67108864]:
		var item: Dictionary = entry()
		item.background.asset.bytes = count
		item.background.image_revision = 1000000
		check(Registry.validate(registry(item)).is_empty(), "existing Ref/revision bound " + str(count))
	var raw: String = JSON.stringify(registry(entry()))
	check(Registry.validate(JSON.parse_string(raw)).is_empty() and Registry.unique_keys(raw), "actual JSON numeric representation")
	check(not Registry.unique_keys('{"background":{"status":"none","status":"selected"}}'), "duplicate nested JSON key rejected")

func lifecycle_cases() -> void:
	var image: Image = Image.create(2304, 576, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.2, 0.2, 0.2, 0.5))
	image.generate_mipmaps()
	var texture: ImageTexture = ImageTexture.create_from_image(image)
	var ink = Background.new()
	var loader := ControlledLoader.new()
	ink.backend = loader
	check(ink.mouse_filter == Control.MOUSE_FILTER_IGNORE and ink.focus_mode == Control.FOCUS_NONE and ink.process_mode == Node.PROCESS_MODE_ALWAYS and ink.texture_filter == CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS, "passive independent processing and mipmap filter")
	var a: Dictionary = entry()
	var b: Dictionary = entry("pz-background-b")
	ink.begin_visit(a, 1)
	ink.begin_visit(a, 1)
	check(loader.paths.size() == 1 and ink.snapshot().active_requests == 1, "duplicate preparation is idempotent")
	loader.finish(texture)
	ink._process(0)
	check(ink.state == "ready" and ink.ready_texture == texture and ink.texture == null, "ready is not published early")
	ink.publish(999)
	check(not ink.frozen, "foreign publication token ignored")
	ink.publish(1)
	ink.begin_visit(a, 1)
	ink.publish(1)
	check(ink.state == "visible" and ink.texture == texture and loader.paths.size() == 1 and ink.snapshot().visible_token == 1, "prepare/settle share one frozen decision")
	var source := Node.new()
	var capture := Node.new()
	root.add_child(source)
	root.add_child(capture)
	source.add_child(ink)
	ink.reparent(capture)
	check(ink.state == "visible" and ink.snapshot().visible_token == 1 and ink.texture == texture, "page reparent into a capture preserves its published visit")
	ink.begin_visit(entry("pz-background-a", "none", 2), 2)
	ink.publish(2)
	check(ink.state == "none" and ink.texture == null and loader.paths.size() == 1, "none clears image without load or fallback")
	var legacy: Dictionary = a.duplicate(true)
	legacy.erase("background")
	ink.begin_visit(legacy, 3)
	ink.publish(3)
	check(ink.state == "legacy" and ink.texture == null and loader.paths.size() == 1, "legacy is separate and requests no puzzle image")
	ink.begin_visit(entry("pz-background-a", "standard", 3), 30)
	ink.publish(30)
	check(ink.state == "standard" and ink.texture == null and loader.paths.size() == 1 and ink.binding.image_revision == 3, "standard retains its preference without a puzzle image request")
	ink.begin_visit(a, 4)
	ink.publish(4)
	check(ink.state == "omitted" and ink.diagnostic == "not_ready_at_publication", "publication immediately freezes late omission")
	loader.finish(texture)
	ink._process(0)
	check(ink.state == "omitted" and ink.texture == null and not ink.snapshot().has_ready and ink.snapshot().active_requests == 0, "late result discarded without visible jump")
	ink.begin_visit(a, 5)
	loader.finish(texture)
	ink.publish(5)
	check(ink.state == "visible" and ink.snapshot().visible_token == 5, "actual revisit can retry")
	ink.begin_visit(a, 6)
	loader.fail()
	ink._process(0)
	ink.publish(6)
	check(ink.state == "omitted" and ink.diagnostic == "controlled_decode_failure" and ink.binding.status == "selected", "failure remains diagnostic selected omission")
	ink.begin_visit(a, 7)
	ink.begin_visit(b, 8)
	ink.begin_visit(a, 9)
	check(ink.snapshot().active_requests == 1 and ink.snapshot().stale_requests == 1 and ink.snapshot().queued and loader.paths.size() == 5, "A-B-A retains one stale and only latest metadata")
	loader.finish(texture)
	ink._process(0)
	check(ink.texture == null and ink.ready_texture == null and ink.snapshot().active_requests == 1 and not ink.snapshot().queued and loader.paths.size() == 6, "old A result cannot install into new A visit")
	loader.finish(texture)
	ink.publish(9)
	check(ink.snapshot().visible_token == 9, "latest A request publishes only for its own visit")
	ink.begin_visit(a, 10)
	var revision: Dictionary = entry("pz-background-a", "selected", 2)
	ink.begin_visit(revision, 11)
	loader.finish(texture)
	ink._process(0)
	check(ink.ready_texture == null and ink.request.image_revision == 2 and loader.paths[-1] == loader.paths[-2], "same path new revision waits for obsolete request to drain")
	loader.finish(texture)
	ink.publish(11)
	check(ink.snapshot().visible_revision == 2 and ink.snapshot().visible_token == 11, "same-path result bound to current revision")
	ink.begin_visit(a, 12)
	ink.leave()
	check(ink.binding.is_empty() and ink.texture == null and ink.ready_texture == null and not ink.snapshot().queued, "leave immediately drops visit and texture references")
	loader.finish(texture)
	ink._process(0)
	check(ink.state == "idle" and ink.snapshot().active_requests == 0 and ink.snapshot().peak_requests == 1, "stale request drains within fixed one-request bound")
	loader.start_error = "missing_texture"
	ink.begin_visit(a, 13)
	ink.publish(13)
	check(ink.state == "omitted" and ink.diagnostic == "missing_texture" and ink.binding.status == "selected", "missing file does not become none or legacy")
	loader.start_error = ""
	ink.begin_visit(a, 14)
	ink.begin_visit(b, 15)
	var before_publication: int = loader.paths.size()
	ink.publish(15)
	loader.finish(texture)
	ink._process(0)
	check(ink.state == "omitted" and ink.snapshot().active_requests == 0 and loader.paths.size() == before_publication, "late stale result never starts an already frozen queued visit")
	ink.begin_visit(a, 16)
	var small: Image = Image.create(64, 16, false, Image.FORMAT_RGBA8)
	small.generate_mipmaps()
	loader.finish(ImageTexture.create_from_image(small))
	ink.publish(16)
	check(ink.state == "omitted" and ink.diagnostic == "invalid_texture_dimensions", "wrong dimensions fail before publication")
	ink.begin_visit(a, 17)
	var no_mips: Image = image.duplicate()
	no_mips.clear_mipmaps()
	loader.finish(ImageTexture.create_from_image(no_mips))
	ink.publish(17)
	check(ink.state == "omitted" and ink.diagnostic == "invalid_texture_mipmaps", "missing imported mipmaps fail before publication")
	ink.begin_visit(a, 18)
	loader.result = {"status":"loaded", "texture":"not_a_texture"}
	ink.publish(18)
	check(ink.state == "omitted" and ink.diagnostic == "texture_load_failed", "wrong resource type fails before publication")
	var paper := Rect2(0, 0, 1600, 1800)
	ink.arrange(paper, Vector2(1600, 1200), 1.0)
	var original: Rect2 = ink.box
	ink.arrange(paper, Vector2(1600, 1200), 1.0)
	check(ink.box == original and is_equal_approx(original.size.x / original.size.y, 4.0) and original.end.y == 1176, "one deterministic 4:1 fit at bottom of visible paper")
	check(Background.placement(Rect2(0, 0, 20, 20), Vector2(20, 20), 1).size == Vector2.ZERO, "no negative fit on impossible paper")
	for scale: float in [1.0, 1.25]:
		for size: Vector2 in [Vector2(1280, 720), Vector2(1920, 1080), Vector2(2560, 1440), Vector2(3840, 2160)]:
			var placed: Rect2 = Background.placement(Rect2(Vector2.ZERO, size * Vector2(1, 1.5)), size, scale)
			check(placed.has_area() and is_equal_approx(placed.size.x / placed.size.y, 4.0) and placed.end.y <= size.y - 24 * scale, "common fit at " + str(size) + "/" + str(scale))
	ink.free()
	source.free()
	capture.free()

func run() -> void:
	reader_cases()
	lifecycle_cases()
	if failures.is_empty():
		print("BACKGROUND_TESTS_OK " + JSON.stringify({"checks":checks}))
		quit(0)
	else:
		for failure: String in failures: printerr("BACKGROUND_TEST_FAILED: " + failure)
		quit(1)
