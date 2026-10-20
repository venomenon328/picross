extends RefCounted
## Synthetic native HZ-A layout evidence; no production registry or save corpus.
const Text = preload("res://ui/ui_text.gd")
const Glyphs = preload("res://tests/hz_cases.gd")
const Registry = preload("res://model/content_registry.gd")

static func capture(runner: Object, name: String, rect: Rect2) -> void:
	await runner.frames()
	await RenderingServer.frame_post_draw
	var image: Image = runner.surface.get_texture().get_image()
	var bounds := Rect2i(rect.intersection(Rect2(Vector2.ZERO, Vector2(image.get_size()))))
	var filename := "hz-" + name + ".png"
	runner.check(image.get_region(bounds).save_png(runner.output.path_join(filename)) == OK, "HZ native crop " + name)

static func run(runner: Object) -> void:
	Glyphs.run(runner)
	var app = runner.app
	var original: Dictionary = Registry.cached.duplicate(true)
	var saved: Dictionary = runner.save_bytes()
	var long_name: String = ("TEST Größe Äpfel Straße „Wiese“ – ").repeat(5).left(128)
	Registry.cached.categories[0].name = long_name
	while Registry.cached.categories.size() < 256:
		var n: int = Registry.cached.categories.size()
		Registry.cached.categories.append({"id":"hz-test-%03d" % n,"name":long_name.left(120)+" %03d" % n,"order":n+1})
	runner.check(Registry.validate(Registry.cached).is_empty(), "HZ synthetic 256 categories / 128-character name accepted by unchanged validator")
	app.show_album()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		runner.surface.size = Vector2i(spec[0], spec[1])
		app.set_ui_scale(spec[2])
		await runner.frames()
		runner.check(app.theme.default_font == Text.font(), "HZ standard text is Tidy Hand")
		runner.check(app.title.get_theme_font("font") == app.WORK_TITLE_FONT, "HZ catalog heading retains original Bakso resource")
		for card: Control in app.choices:
			for label: Label in [card.dimensions,card.difficulty,card.leaf,card.note]:
				runner.check(Text.label_width(label,label.text,label.get_theme_font_size("font_size")) <= label.size.x, "HZ complete metadata including style margins")
				runner.check(Text.label_height(label,label.get_theme_font_size("font_size")) <= label.size.y, "HZ measured line height fits")
			runner.check(card.image_area.size.y >= 112*app.ui_scale and card.reset.size.x >= 44*app.ui_scale, "HZ image and reset budgets preserved")
		for number: int in range(1,51):
			var label: Label = app.choices[0].dimensions
			runner.check(Text.label_width(label,"%d × %d" % [number,number],label.get_theme_font_size("font_size")) <= label.size.x, "HZ every legal dimension fits")
		await capture(runner,"catalog-%d" % spec[0],app.album.get_global_rect())
		runner.click(app.album.category_choice)
		runner.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
		await runner.frames()
		var popup: PopupMenu = app.album.category_choice.get_popup()
		runner.check(popup.visible and popup.item_count == 257, "HZ real category popup includes All and 256 categories")
		runner.check(Rect2(Vector2.ZERO,Vector2(runner.surface.size)).encloses(Rect2(Vector2(popup.position),Vector2(popup.size))), "HZ popup stays in client")
		runner.check(popup.get_theme_font("font").get_font_name() == "Tidy Hand", "HZ native popup inherits standard text")
		await capture(runner,"menu-%d" % spec[0],Rect2(Vector2(popup.position),Vector2(popup.size)))
		var full: String = popup.get_item_tooltip(1)
		runner.check(full.replace("\n","") == popup.get_item_text(1) and full.contains("\n"), "HZ tooltip retains all 128 name characters and count")
		for line: String in full.split("\n"):
			runner.check(Text.width(Text.font(),line,roundi(14*app.ui_scale)) <= 420*app.ui_scale + 2, "HZ long category tooltip measured line fits")
		for y: int in range(4, mini(150,popup.size.y),4):
			var motion := InputEventMouseMotion.new()
			motion.position = Vector2(popup.position)+Vector2(80,y)
			motion.global_position = motion.position
			motion.relative = Vector2(0,4)
			motion.velocity = Vector2(0,240)
			runner.surface.push_input(motion,true)
			if popup.get_focused_item() == 1: break
		runner.check(popup.get_focused_item() == 1, "HZ long category reached by actual hover")
		await runner.create_timer(0.8).timeout
		await capture(runner,"category-tooltip-%d" % spec[0],Rect2(Vector2.ZERO,Vector2(runner.surface.size)))
		popup.hide()
		await runner.frames()
		await runner.choose("hz-test-255")
		runner.check(app.album.choices.is_empty(), "HZ last synthetic category reachable by real wheel and pointer")
		await capture(runner,"selection-%d" % spec[0],app.album.category_choice.get_global_rect())
		await runner.choose("")
		app.show_information("help")
		await runner.frames()
		var help: Label = app.help_panel.get_child(1)
		runner.check(help.get_theme_font("font") == Text.font() and help.get_line_count() > 10, "HZ help uses wrapped standard text")
		app.info_scroll.scroll_vertical = 100000
		await runner.frames()
		runner.check(app.info_scroll.scroll_vertical > 0 or app.help_panel.size.y <= app.info_scroll.size.y, "HZ complete help fits or remains scrollable")
		await capture(runner,"help-%d" % spec[0],app.info_scroll.get_global_rect())
		app.return_to_work()
		app.reset_dialog.dialog_text = long_name + "\nNur dieses Blatt vollständig zurücksetzen?"
		app._popup_dialog(app.reset_dialog)
		await runner.frames()
		runner.check(app.reset_dialog.get_label().get_theme_font("font") == Text.font(), "HZ native dialog body uses Tidy Hand")
		runner.check(app.reset_dialog.get_theme_font("title_font", "Window") == app.BODY_FONT, "HZ native dialog heading retained")
		runner.check(app.reset_dialog.size.x <= runner.surface.size.x and app.reset_dialog.size.y <= runner.surface.size.y, "HZ wrapped long dialog fits client")
		await capture(runner,"dialog-%d" % spec[0],Rect2(Vector2(app.reset_dialog.position),Vector2(app.reset_dialog.size)))
		runner.click(app.reset_dialog.get_cancel_button())
		await runner.frames()
		runner.check(not app.reset_dialog.visible, "HZ dialog cancel works with real pointer")
	Registry.cached = original
	app.show_album()
	runner.check(runner.save_bytes() == saved, "HZ text/layout navigation preserves synthetic save bytes")
