extends RefCounted
## Only the Windows main window reaches this backend. No OS video-mode writes.
const Policy = preload("res://model/display_policy.gd")
const Preference = preload("res://model/display_preference.gd")
const MODES: Dictionary = {"window": DisplayServer.WINDOW_MODE_WINDOWED, "borderless": DisplayServer.WINDOW_MODE_FULLSCREEN, "exclusive": DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN}
var window: Window
var decorations: Vector2i = Vector2i.ZERO
var offset: Vector2i = Vector2i.ZERO
var measured_dpi: int = 96

func _init(owner: Window) -> void:
	window = owner
	window.unresizable = true
	context()

func context() -> Dictionary:
	var screen: int = DisplayServer.window_get_current_screen()
	var dpi: int = maxi(1, DisplayServer.screen_get_dpi(screen))
	if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_WINDOWED:
		decorations = DisplayServer.window_get_size_with_decorations() - DisplayServer.window_get_size()
		offset = DisplayServer.window_get_position() - DisplayServer.window_get_position_with_decorations()
		measured_dpi = dpi
	var ratio: float = float(dpi) / measured_dpi
	return {"screen": screen, "desktop": DisplayServer.screen_get_size(screen), "usable": DisplayServer.screen_get_usable_rect(screen), "dpi": dpi, "decorations": Vector2i(Vector2(decorations)*ratio), "offset": Vector2i(Vector2(offset)*ratio)}

func observed() -> Dictionary:
	var mode: int = DisplayServer.window_get_mode()
	var name: String = "other"
	for key: String in MODES:
		if MODES[key] == mode: name = key
	return {"mode": name, "client": DisplayServer.window_get_size(), "minimized": mode == DisplayServer.WINDOW_MODE_MINIMIZED, "outer": Rect2i(DisplayServer.window_get_position_with_decorations(),DisplayServer.window_get_size_with_decorations())}

func apply(selection: Dictionary) -> Dictionary:
	window.unresizable = true
	# Switching back first obtains the actual decorated geometry on this monitor.
	if selection.mode == "window":
		window.mode = Window.MODE_WINDOWED
		window.borderless = false
	var current: Dictionary = context()
	var target: Dictionary = Policy.resolve(selection,current)
	window.mode = MODES[target.mode]
	if target.mode == "window":
		window.size = Preference.pixels(target.preset)
		window.position = Policy.position(current,window.size,window.position)
	return target

func keep_visible(selection: Dictionary) -> void:
	if selection.mode == "window":
		window.position = Policy.position(context(),window.size,window.position)
