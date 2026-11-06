extends RefCounted
## Pure geometry policy; all measures use the native server's client coordinates.
const Preference = preload("res://model/display_preference.gd")

static func available(context: Dictionary) -> Array[String]:
	var result: Array[String] = []
	for preset: String in Preference.PRESETS:
		var outer: Vector2i = Preference.pixels(preset) + context.decorations
		if outer.x <= context.usable.size.x and outer.y <= context.usable.size.y:
			result.append(preset)
	return result

static func resolve(selection: Dictionary, context: Dictionary) -> Dictionary:
	if selection.mode != "window": return selection.duplicate()
	var choices: Array[String] = available(context)
	if selection.preset in choices: return selection.duplicate()
	var fallback: String = ""
	var limit: Vector2i = Preference.pixels(selection.preset).min(Vector2i(1920,1080))
	for preset: String in choices:
		var size: Vector2i = Preference.pixels(preset)
		if size.x <= limit.x and size.y <= limit.y: fallback = preset
	if fallback.is_empty():
		return {"mode": "borderless", "preset": selection.preset}
	return {"mode": "window", "preset": fallback}

static func position(context: Dictionary, client: Vector2i, current: Vector2i) -> Vector2i:
	var usable: Rect2i = context.usable
	var offset: Vector2i = context.offset
	var maximum: Vector2i = usable.end - client - context.decorations + offset
	return current.clamp(usable.position + offset, maximum.max(usable.position + offset))
