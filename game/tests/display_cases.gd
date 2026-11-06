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
	func settle(_selection: Dictionary) -> void: pass

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
	r.check(r.app.display_settings == null and r.app.ui_scale_choice.item_count == 2 and r.app.view_choice.item_count == 2,"N02: common non-native settings work without physical display controls")
	r.check(r.app.ui_scale_choice.get_parent().help == null and r.app.view_choice.get_parent().help != null,"N03: common non-native UI has only the view help")
	var panel := Settings.new()
	r.app.display_group.add_child(panel)
	r.app.display_group.move_child(panel,0)
	r.app.display_settings = panel
	panel.configure(r.app,control)
	r.check(panel.size_choice.disabled and panel.size_choice.text == "1280 × 720 (Desktop)" and control.active.preset == "1920x1080","ANZ N01: desktop in disabled size field without changing remembered preset")
	r.check(panel.feedback.visible and panel.save_current.visible,"ANZ N01: temporary fallback keeps its explanation and explicit acceptance")
	control.request("borderless",control.active.preset)
	settle(control)
	control.confirm()
	r.check(not panel.feedback.visible and not panel.save_current.visible,"ANZ N01: successful acceptance leaves no permanent success text")
	control.request("window","1280x720")
	settle(control)
	control.cancel()
	settle(control)
	r.check(panel.feedback.visible,"ANZ N01: rollback feedback is not suppressed")
	backend.geometry = Server.new().geometry
	control.request("window","1920x1080")
	settle(control)
	control.confirm()
	r.check(panel.size_choice.text == "1920 × 1080" and not panel.size_choice.disabled,"ANZ N01: window field restores preset after fullscreen label")
	storage.fail_write = true
	control.request("borderless",control.active.preset)
	settle(control)
	control.confirm()
	settle(control)
	r.check(panel.feedback.visible and panel.feedback.text.contains("nicht gespeichert"),"ANZ N01: storage error remains visible after failed acceptance")
	storage.fail_write = false
	r.app.show_information("settings")
	for size: Vector2i in [Vector2i(1920,1080),Vector2i(1280,720)]:
		r.surface.size = size
		r.app.size = Vector2(size)
		for scale: float in [1.0,1.25]:
			r.app.return_to_work()
			r.app.set_ui_scale(scale)
			await r.frames()
			var catalog_font: Font = r.app.title.get_theme_font("font")
			var catalog_size: int = r.app.title.get_theme_font_size("font_size")
			r.check(r.app.album.visible and r.app.title.is_visible_in_tree() and catalog_font.resource_path == "res://art/drawing/BaksoDaging-Regular.ttf","N03: reference is the actual visible catalog title")
			r.app.show_information("settings")
			await r.frames()
			var groups: Array = [r.app.settings_panel.get_node("display-options"),r.app.settings_panel.get_node("puzzle-options")]
			r.check(groups[0].heading.text == "Anzeige" and groups[1].heading.text == "Rätselansicht" and r.app.settings_panel.get_child_count() == 3,"N02: exactly two framed settings groups")
			r.check(r.app.settings_title.get_theme_font("font") == catalog_font and catalog_size == roundi(28*scale) and r.app.settings_title.get_theme_font_size("font_size") == catalog_size,"N03: settings matches active Bakso catalog resource and size")
			for group: Control in groups:
				var font: FontVariation = group.heading.get_theme_font("font")
				r.check(font.base_font == r.app.TITLE_FONT and font.variation_opentype == {"wght":600.0} and group.heading.get_theme_font_size("font_size") == roundi(20*scale),"N03: separate Fraunces 600/20 group role preserved")
			var column: Rect2 = r.app.settings_panel.get_global_rect()
			var scroll: Rect2 = r.app.info_scroll.get_global_rect()
			r.check(column.size.x <= 640*scale+1 and column.size.x <= scroll.size.x and absf(column.get_center().x-scroll.get_center().x) < 10*scale and r.app.info_scroll.get_h_scroll_bar().max_value <= scroll.size.x,"N02: compact groups centred in safe left paper without horizontal scrolling "+str(column)+" / "+str(scroll)+" / max="+str(r.app.info_scroll.get_h_scroll_bar().max_value))
			var last_x: float = -1
			var help_count: int = 0
			for field: Control in r.app.settings_fields:
				var choice: OptionButton = field.choice
				var help: Button = field.help
				r.check(field.caption.global_position.x < choice.global_position.x and absf(field.caption.get_global_rect().get_center().y-choice.get_global_rect().get_center().y) < 1 and choice.size.y >= 44*scale,"N03: inline label and HZ choice "+str(field.name))
				if field.caption.text in ["Fenstergröße","Rätselansicht"]:
					help_count += 1
					r.check(help != null and help.global_position.x >= choice.get_global_rect().end.x and absf(help.get_global_rect().end.x-field.get_global_rect().end.x) < 1 and help.size.x >= 44*scale and help.size.y >= 44*scale and help.focus_mode == Control.FOCUS_ALL and not help.tooltip_text.is_empty(),"N03: independent help at safe row edge "+str(field.name))
				else:
					r.check(help == null and field.get_child_count() == 2 and absf(choice.get_global_rect().end.x-field.get_global_rect().end.x) < 1,"N03: no help/focus placeholder; dropdown fills released width and gap "+str(field.name))
				r.check(last_x < 0 or absf(choice.global_position.x-last_x)<1,"N02: common measured columns")
				last_x = choice.global_position.x
				r.check(column.grow(1).encloses(field.get_global_rect()),"N02: complete row inside frame")
			r.check(help_count == 2,"N03: exactly two field help buttons")
			r.check(r.app.ui_scale_choice.item_count == 2 and r.app.ui_scale_choice.get_item_text(0) == "100 %" and r.app.ui_scale_choice.get_item_text(1) == "125 %" and r.app.ui_scale_choice.selected == (1 if scale == 1.25 else 0),"N02: UI dropdown matches session scale")
			r.check(not r.app.board.has_method("reset_clue_pan") and r.app.settings_panel.find_children("exit-options","",true,false).is_empty(),"N02: manual reset command and settings exit removed")
			var tip_help: Button = panel.size_choice.get_parent().help
			r.check(tip_help.tooltip_text.contains("Desktopauflösung") and not tip_help.disabled and r.app.view_choice.get_parent().help.tooltip_text.contains("kleinere Zellen"),"N02: complete explanations on separate question marks")
			r.app.info_scroll.ensure_control_visible(r.app.animation_toggle)
			await r.frames()
			r.check(scroll.grow(1).encloses(r.app.animation_toggle.get_global_rect()),"N02: bottom setting reachable by vertical scroll")
			r.app.info_scroll.ensure_control_visible(tip_help)
			tip_help.grab_focus()
			await r.frames()
			r.check(is_instance_valid(tip_help.focus_tip) and Rect2(Vector2.ZERO,Vector2(size)).encloses(tip_help.focus_tip.get_global_rect()),"N02: focus opens styled help inside viewport")
			r.app.ui_scale_choice.grab_focus()
			await r.frames()
			r.check(not is_instance_valid(tip_help.focus_tip),"N02: focus exit dismisses help")
			r.app.info_scroll.scroll_vertical = 0
			await r.frames()
			r.click(panel.mode_choice)
			await r.frames()
			var popup: PopupMenu = panel.mode_choice.get_popup()
			r.check(popup.visible and Rect2i(Vector2i.ZERO,size).encloses(Rect2i(popup.position,popup.size)),"ANZ N01: opened mode popup fits viewport")
			r.app.show_information("help")
			await r.frames()
			r.check(not popup.visible,"ANZ N01: help transition dismisses popup")
			r.app.show_information("settings")
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
	r.app.display_settings = null
	panel.free()
	control.free()
	DirAccess.remove_absolute(path)
	DirAccess.remove_absolute(path+".bak")
	DirAccess.remove_absolute(blocked)
	r.surface.size = Vector2i(1920,1080)
	r.app.size = Vector2(1920,1080)
	r.app.set_ui_scale(1.0)
	r.app.return_to_work()
