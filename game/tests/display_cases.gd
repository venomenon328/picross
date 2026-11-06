extends RefCounted
## Cheap display regression in the existing catalog/information process.
const Preference = preload("res://model/display_preference.gd")
const Policy = preload("res://model/display_policy.gd")
const Controller = preload("res://ui/display_controller.gd")
const Settings = preload("res://ui/display_settings.gd")

class Server extends RefCounted:
	var geometry: Dictionary = {"screen":0,"desktop":Vector2i(2560,1440),"usable":Rect2i(0,0,2560,1400),"decorations":Vector2i(16,39),"offset":Vector2i(8,31),"dpi":96}
	var state: Dictionary = {"mode":"window","client":Vector2i(1920,1080),"outer":Rect2i(8,31,1936,1119),"minimized":false}
	var reject: String = ""
	func context() -> Dictionary: return geometry.duplicate()
	func observed() -> Dictionary: return state.duplicate()
	func apply(selection: Dictionary) -> Dictionary:
		var target: Dictionary = Policy.resolve(selection,geometry)
		if target.mode == reject: return target
		state.mode = target.mode
		state.client = Preference.pixels(target.preset) if target.mode == "window" else geometry.desktop
		state.outer = Rect2i(geometry.usable.position,state.client+geometry.decorations)
		return target
	func keep_visible(_selection: Dictionary) -> void: pass

static func settle(control: Controller) -> void:
	for i: int in range(3): control.advance(Time.get_ticks_msec())

static func run(r: SceneTree) -> void:
	var context: Dictionary = Server.new().context()
	r.check(Policy.available(context) == ["1280x720","1366x768","1600x900","1920x1080","1920x1200"],"ANZ: actual decorations and taskbar filter presets")
	context.usable = Rect2i(0,0,3840,2120)
	r.check("3840x2160" not in Policy.available(context),"ANZ: 4K decorated client does not fit a 4K desktop")
	context.usable = Rect2i(0,0,2560,1560)
	r.check("1920x1200" in Policy.available(context) and "2560x1600" not in Policy.available(context),"ANZ: 16:10 presets use usable height")
	context.usable = Rect2i(-1920,40,1920,1040)
	r.check(Policy.resolve(Preference.defaults(),context) == {"mode":"window","preset":"1600x900"},"ANZ: largest fitting default below 1080p")
	r.check(Policy.position(context,Vector2i(1600,900),Vector2i(8000,-9000)) == Vector2i(-1608,71),"ANZ: nonzero/negative monitor coordinates clamp whole decoration")
	context.usable = Rect2i(0,0,1280,680)
	r.check(Policy.resolve(Preference.defaults(),context).mode == "borderless","ANZ: 720p desktop needs real borderless fallback")
	context.usable = Rect2i(0,0,1920,1040)
	context.decorations = Vector2i(24,60)
	r.check(Policy.resolve(Preference.defaults(),context).preset == "1600x900","ANZ: DPI-scaled measured frame is counted")
	var path: String = r.app.store.root.path_join("display-test.json")
	var storage = Preference.new(path)
	r.check(storage.load_selection() == Preference.defaults(),"ANZ: missing preference uses safe default")
	var valid: Dictionary = {"mode":"exclusive","preset":"2560x1600"}
	r.check(storage.save_selection(valid) and storage.load_selection() == valid,"ANZ: closed, validated preference roundtrip")
	var original: PackedByteArray = FileAccess.get_file_as_bytes(path)
	storage.fail_write = true
	r.check(not storage.save_selection(Preference.defaults()) and FileAccess.get_file_as_bytes(path) == original and not storage.error.is_empty(),"ANZ: failed write preserves previous valid bytes")
	storage.fail_write = false
	storage.fail_replace = true
	r.check(not storage.save_selection(Preference.defaults()) and FileAccess.get_file_as_bytes(path) == original,"ANZ: publication failure after rotation restores previous valid primary")
	storage.fail_replace = false
	r.check(DirAccess.rename_absolute(path,path+".bak") == OK and storage.load_selection() == valid,"ANZ: interrupted replacement gap recovers confirmed backup")
	DirAccess.rename_absolute(path+".bak",path)
	# Real rename failure, after writing a valid temporary file.
	var blocked: String = path+"-directory"
	DirAccess.make_dir_recursive_absolute(blocked)
	var blocked_storage = Preference.new(blocked)
	r.check(not blocked_storage.save_selection(valid) and DirAccess.dir_exists_absolute(blocked) and not FileAccess.file_exists(blocked+".tmp"),"ANZ: real replacement error leaves target and removes candidate")
	var raw: String = JSON.stringify({"format":Preference.FORMAT,"mode":"window","preset":"1920x1080"})
	for corrupt: String in ["{", "[]", raw.replace("v1","v2"), raw.replace("1920x1080","1921x1080"), raw.replace("window","maximized"), raw.replace("\"window\"","true"), raw.insert(1,'"mode":"window",'),raw.insert(1,'"mo\\u0064e":"window",'),raw.insert(1,'"other":0,'),raw.replace("}",",}")]:
		r.check(Preference.decode(corrupt).is_empty(),"ANZ: reject corrupt/foreign/duplicate preference: "+corrupt)
	var file := FileAccess.open(path,FileAccess.WRITE)
	file.store_string("bad preference")
	file.close()
	r.check(storage.load_selection() == Preference.defaults() and not storage.error.is_empty(),"ANZ: invalid file gives visible safe default")
	var backend := Server.new()
	var control := Controller.new()
	r.root.add_child(control)
	control.set_process(false)
	control.start(backend,storage)
	settle(control)
	r.check(control.active == Preference.defaults() and not control.applying,"ANZ: initial mode is verified")
	r.check(storage.save_selection(control.active),"ANZ: seed confirmed on disk")
	original = FileAccess.get_file_as_bytes(path)
	control.request("exclusive","1920x1080")
	settle(control)
	r.check(control.preview and backend.state.mode == "exclusive" and control.seconds_left(control.deadline-15000) == 15,"ANZ: exclusive preview with exactly 15 seconds")
	control.request("window","1280x720")
	r.check(control.active.mode == "exclusive" and FileAccess.get_file_as_bytes(path) == original,"ANZ: chained preview refused and crash-before-confirm leaves disk unchanged")
	backend.state.minimized = true
	control.advance(control.deadline-1000)
	r.check(control.preview and FileAccess.get_file_as_bytes(path) == original,"ANZ: Alt-Tab/minimize neither confirms nor cancels preview")
	backend.state.minimized = false
	control.advance(control.deadline)
	settle(control)
	r.check(not control.preview and control.active.mode == "window" and control.active.preset == "1920x1080","ANZ: timeout returns previous mode and preset")
	control.request("borderless","1920x1080")
	settle(control)
	control.confirm()
	r.check(storage.load_selection().mode == "borderless" and not control.preview,"ANZ: explicit accepted fullscreen persisted")
	control.request("window","1280x720")
	settle(control)
	control.cancel()
	settle(control)
	r.check(control.active.mode == "borderless" and control.active.preset == "1920x1080","ANZ: cancel restores last confirmed fullscreen and window preset")
	storage.fail_write = true
	control.request("window","1600x900")
	settle(control)
	control.confirm()
	settle(control)
	r.check(control.active.mode == "borderless" and control.message.contains("nicht gespeichert") and storage.load_selection().mode == "borderless","ANZ: failed acceptance rolls back with honest error")
	storage.fail_write = false
	backend.reject = "exclusive"
	control.request("exclusive","1920x1080")
	control.advance(control.settle_deadline+1)
	control.advance(control.settle_deadline+1)
	control.advance(control.settle_deadline+1)
	settle(control)
	r.check(control.active.mode == "borderless" and not control.preview and control.message.contains("nicht verfügbar"),"ANZ: unsupported exclusive falls back honestly without saving")
	backend.reject = ""
	control.request("window","1920x1080")
	settle(control)
	control.confirm()
	var saved_bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	backend.geometry.usable = Rect2i(0,0,1280,680)
	backend.geometry.desktop = Vector2i(1280,720)
	control.poll_at = 0
	control.advance(Time.get_ticks_msec())
	settle(control)
	r.check(control.active.mode == "borderless" and FileAccess.get_file_as_bytes(path) == saved_bytes,"ANZ: monitor fallback remains transient and visible")
	var panel := Settings.new()
	r.app.settings_panel.add_child(panel)
	panel.configure(r.app,control)
	r.check(panel.size_choice.disabled and panel.resolution.text.contains("1280 × 720"),"ANZ: fullscreen size disabled; observed resolution shown")
	control.request("borderless",control.active.preset)
	settle(control)
	for size: Vector2i in [Vector2i(1280,720),Vector2i(3840,2160),Vector2i(1920,1200)]:
		r.surface.size = size
		r.app.size = Vector2(size)
		for scale: float in [1.0,1.25]:
			r.app.set_ui_scale(scale)
			await r.frames()
			panel.layout_card()
			var safe: Rect2 = Rect2(Vector2.ZERO,Vector2(size))
			r.check(safe.encloses(panel.card.get_global_rect()) and panel.accept.custom_minimum_size.y == 44*scale,"ANZ: safe confirmation and HZ targets "+str(size)+" UI "+str(scale))
	control.cancel()
	settle(control)
	panel.free()
	control.free()
	DirAccess.remove_absolute(path)
	DirAccess.remove_absolute(path+".bak")
	DirAccess.remove_absolute(blocked)
	r.surface.size = Vector2i(1920,1080)
	r.app.size = Vector2(1920,1080)
	r.app.set_ui_scale(1.0)
