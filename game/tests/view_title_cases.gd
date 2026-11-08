extends RefCounted
const Text = preload("res://ui/ui_text.gd")
## Cheap layout/resource regression in the existing catalog/information process.
static func run(r: SceneTree) -> void:
	var app: Control = r.app
	for heading: Control in [app.catalog_title,app.info.help_heading,app.info.settings_heading]:
		var source: Image = heading.texture.get_image()
		r.check(source != null and source.has_mipmaps() and source.detect_alpha() != Image.ALPHA_NONE,"BTI: local imported RGBA title with mipmaps "+heading.role)
		var rect: Rect2 = heading.image_rect()
		r.check(absf(rect.size.x/rect.size.y-float(source.get_width())/source.get_height()) < 0.001,"BTI: whole original stays proportional "+heading.role)
	for config: Vector3 in [Vector3(1280,720,1),Vector3(1280,720,1.25),Vector3(1920,1080,1),Vector3(1920,1080,1.25),Vector3(2560,1440,1),Vector3(2560,1440,1.25),Vector3(1920,1200,1.25)]:
		r.surface.size = Vector2i(config.x,config.y)
		app.size = Vector2(config.x,config.y)
		app.set_ui_scale(config.z)
		app.return_to_work()
		await r.frames()
		var catalog: Control = app.catalog_title
		r.check(catalog.visible and not app.title.visible and catalog.accessibility_name == "Rätselkatalog","BTI: single semantic catalog image title")
		var paper: Rect2 = app.book.projected_paper(false,-1)
		var safe_center: float = paper.get_center().x-paper.size.x*0.075/2
		r.check(absf(catalog.get_global_rect().get_center().x-safe_center) < 1,"BTI: catalog centred on safe left paper")
		r.check(catalog.get_global_rect().end.y <= app.album.get_global_rect().position.y,"BTI: catalog title outside card scrolls")
		for title: Control in [app.catalog_title,app.info.help_heading,app.info.settings_heading]:
			var image: Rect2 = title.image_rect()
			var optical: Rect2 = title.ink_rect()
			r.check(Rect2(Vector2.ZERO,title.size).encloses(image),"BTI-C: entire original including weak alpha fits "+title.role)
			r.check(optical.get_center().distance_to(title.size/2) < 0.01,"BTI-C: meaningful ink centred "+title.role)
		for section: String in ["settings","help"]:
			app.show_information(section)
			await r.frames()
			await r.frames()
			var heading: Control = app.info.settings_heading if section == "settings" else app.info.help_heading
			var scroll: ScrollContainer = app.info_scroll if section == "settings" else app.info.help_scroll
			var back: Control = app.actions["nav-work"] if section == "settings" else app.info.right_return
			var switch: Control = app.information.get_node("help-access" if section == "settings" else "settings-access")
			var viewport := Rect2(Vector2.ZERO,app.size)
			r.check(heading.is_visible_in_tree() and heading.texture != null and not heading.fallback.visible,"BTI: imported image replaces text "+section)
			r.check(heading.accessibility_name == ("Hilfe" if section == "help" else "Einstellungen"),"BTI: exact semantic information title")
			r.check(absf(heading.get_global_rect().get_center().x-(app.info_scroll if section == "settings" else app.help_panel).get_global_rect().get_center().x) < 1,"BTI: fixed title centres on same safe paper as content")
			r.check(is_equal_approx(back.global_position.y,heading.global_position.y) and heading.get_global_rect().end.y < scroll.get_global_rect().position.y,"BTI: title shares navigation top edge without added vertical row")
			var image_box := Rect2(heading.global_position+heading.image_rect().position,heading.image_rect().size)
			for button: Control in [back,app.information.get_node("settings-access"),app.information.get_node("help-access")]:
				r.check(not image_box.intersects(button.get_global_rect()),"BTI: whole original title clears the lateral symbol group")
			for button: Control in [back,switch]:
				r.check(viewport.encloses(button.get_global_rect()) and button.size.x >= 44*config.z and button.size.y >= 44*config.z,"BTI: visible top hit target")
			r.check(not back.get_global_rect().intersects(switch.get_global_rect()),"BTI: independent top actions")
			await preload("res://tests/navigation_cases.gd").information(r)
			var fixed_title: Rect2 = heading.get_global_rect()
			var fixed_back: Rect2 = back.get_global_rect()
			scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
			await r.frames()
			r.check(heading.get_global_rect() == fixed_title and back.get_global_rect() == fixed_back,"BTI: scrolling preserves fixed title/navigation")
			var last: Control = app.animation_toggle if section == "settings" else app.help_panel.chapters[app.help_panel.chapter].get_children()[-1]
			r.check(last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1,"BTI: content end reachable")
			scroll.scroll_vertical = 0
			if section == "help": await help_register(r,config.z)
	# Inspect the actual help labels in the existing information process.
	app.show_information("help")
	for scale: float in [1.0,1.25]:
		app.set_ui_scale(scale)
		await r.frames()
		var sizes: Dictionary = {22: 0, 19: 0}
		var corrected := false
		var clue_copy := false
		for chapter: VBoxContainer in app.help_panel.chapters:
			var chapter_headings := 0
			for node: Node in chapter.find_children("*","Label",true,false):
				var label: Label = node
				var base: int = int(label.get_meta("base_font"))
				if label.has_meta("help_heading"):
					chapter_headings += 1
					r.check(base in [19,22] and label.get_theme_font("font") == app.WORK_TITLE_FONT,"HIL-TYPO: actual heading uses shared Bakso")
					if base in sizes: sizes[base] += 1
				else:
					r.check(label.get_theme_font("font") == Text.font(),"HIL-TYPO: normal copy retains Pangolin")
				if label.text == "Unbekannt heißt: Hier hast du noch nichts festgelegt. Eine Füllung trägt Farbe. Ein X bedeutet: Hier gehört keine Farbe hin. Radieren entfernt einen Eintrag und macht das Feld wieder unbekannt.": corrected = true
				if label.text.contains("Gleich blasse Zahl mit handschriftlichem X:"): clue_copy = true
				r.check(label.get_theme_font_size("font_size") == roundi(base*scale),"HIL-TYPO: base font scales")
			r.check(chapter_headings > 0,"HIL-TYPO: headings in each chapter")
		r.check(sizes[22] > 0 and sizes[19] > 0 and corrected and clue_copy,"HIL-TYPO: both roles and exact copy")
	# A tighter measured paper region exercises wrapping of the same controls,
	# without adding an unsupported physical-window preset.
	var panel: Control = app.help_panel
	var prior: Vector2 = panel.size
	var figure_width: float = 0
	for figure: Control in panel.figures: figure_width = maxf(figure_width,figure.get_combined_minimum_size().x)
	panel.size.x = figure_width+120*app.ui_scale
	panel.layout_content()
	await r.frames()
	await r.frames()
	r.check(panel.compact and panel.buttons[3].position.y > panel.buttons[0].position.y,"HIL-REG: measured tighter paper wraps compact register")
	for button: Control in panel.buttons:
		r.check(panel.get_global_rect().encloses(button.get_global_rect()) and not button.get_global_rect().intersects(panel.scroll.get_global_rect()),"HIL-REG: wrapped entries remain complete above article")
	panel.size = prior
	panel.layout_content()
	# Missing files do not create an empty heading or hard preload failure.
	for heading: Control in [app.catalog_title,app.info.help_heading,app.info.settings_heading]:
		heading.load_art("res://art/drawing/view_titles/missing.png")
		r.check(heading.texture == null and heading.fallback.visible and heading.fallback.text == heading.TITLES[heading.role] and heading.fallback.get_theme_font_size("font_size") >= 28,"BTI: missing resource selects exact readable local fallback "+heading.role)
		heading.load_art("res://art/drawing/view_titles/"+heading.role+".png")
		r.check(heading.texture != null and not heading.fallback.visible,"BTI: restored resource removes duplicate text")
	r.surface.size = Vector2i(1920,1080)
	app.size = Vector2(1920,1080)
	app.set_ui_scale(1.0)
	app.return_to_work()

static func help_register(r: SceneTree, u: float) -> void:
	var app: Control = r.app
	var panel: Control = app.help_panel
	var scroll: ScrollContainer = panel.scroll
	var fixed: Array[Rect2] = []
	for i: int in range(4):
		var button: Button = panel.buttons[i]
		fixed.append(button.get_global_rect())
		r.check(button.text == panel.TITLES[i] and button.size.x >= 44*u and button.size.y >= 44*u,"HIL-REG: full measured chapter targets")
		r.check(not scroll.is_ancestor_of(button) and panel.get_global_rect().encloses(button.get_global_rect()),"HIL-REG: register outside article and inside paper")
		r.check(not button.get_global_rect().intersects(scroll.get_global_rect()),"HIL-REG: article never covers register")
		for j: int in range(i): r.check(not button.get_global_rect().intersects(fixed[j]),"HIL-REG: compact entries do not overlap")
	r.check(panel.compact == (r.surface.size.x == 1280 and u == 1.25),"HIL-REG: measured narrow fallback versus wide layout")
	for i: int in range(4):
		r.click(panel.buttons[i])
		await r.frames()
		r.check(panel.chapter == i and scroll.scroll_vertical == 0,"HIL-REG: pointer chapter selection resets article")
		panel.buttons[(i+1)%4].grab_focus()
		r.check(panel.buttons[i].selected and panel.buttons[(i+1)%4].has_focus() and not panel.buttons[(i+1)%4].selected,"HIL-REG: focus separate from active underline")
		var line: Dictionary = panel.buttons[i].underline()
		panel.buttons[i].queue_redraw()
		r.check(line == panel.buttons[i].underline(),"HIL-REG: deterministic active underline")
		# Use the native focused Button's existing accept route as well.
		var event := InputEventAction.new()
		event.action = "ui_accept"
		event.pressed = true
		r.surface.push_input(event,true)
		event = event.duplicate()
		event.pressed = false
		r.surface.push_input(event,true)
		await r.frames()
		r.check(panel.chapter == (i+1)%4,"HIL-REG: focused accept chooses chapter")
		panel.choose(i)
		await r.frames()
		scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
		await r.frames()
		for j: int in range(4): r.check(panel.buttons[j].get_global_rect() == fixed[j],"HIL-REG: entire register fixed at article end")
		var last: Control = panel.chapters[i].get_children()[-1]
		r.check(last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1,"HIL-REG: final copy reachable")
		for figure: Control in panel.figures:
			if figure.is_visible_in_tree(): r.check(figure.size.x <= scroll.size.x and figure.cell_size == 32*u,"HIL-REG: full passive diagrams fit")
		r.check(scroll.get_h_scroll_bar().max_value <= scroll.size.x+1,"HIL-REG: no horizontal scroll")
		for column: Control in panel.copy_columns:
			if column.is_visible_in_tree(): r.check(column.get_child(0).size.x <= panel.paragraph_width+1,"HIL-REG: measured prose width cap")
	panel.choose(2)
	await r.frames()
	scroll.scroll_vertical = 400
	await r.frames()
	var offset: int = scroll.scroll_vertical
	app._information_section("settings")
	await r.frames()
	app._information_section("help")
	await r.frames()
	r.check(panel.chapter == 2 and scroll.scroll_vertical == offset,"HIL-REG: settings preserves chapter and reading offset")
	# No new visit: scaling/reflow uses an article anchor, not raw old pixels.
	var other: float = 1.25 if u == 1.0 else 1.0
	app.set_ui_scale(other)
	await r.frames()
	await r.frames()
	app.set_ui_scale(u)
	await r.frames()
	await r.frames()
	r.check(panel.chapter == 2 and abs(scroll.scroll_vertical-offset) <= 2,"HIL-REG: UI roundtrip preserves reading anchor")
