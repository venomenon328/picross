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
			var heading: Control = app.info.settings_heading if section == "settings" else app.info.help_heading
			var scroll: ScrollContainer = app.info_scroll if section == "settings" else app.info.help_scroll
			var back: Control = app.actions["nav-work"] if section == "settings" else app.info.right_return
			var switch: Control = app.information.get_node("help-access" if section == "settings" else "settings-access")
			var viewport := Rect2(Vector2.ZERO,app.size)
			r.check(heading.is_visible_in_tree() and heading.texture != null and not heading.fallback.visible,"BTI: imported image replaces text "+section)
			r.check(heading.accessibility_name == ("Hilfe" if section == "help" else "Einstellungen"),"BTI: exact semantic information title")
			r.check(absf(heading.get_global_rect().get_center().x-scroll.get_global_rect().get_center().x) < 1,"BTI: fixed title centres on same safe paper as content")
			r.check(heading.get_global_rect().end.y < scroll.get_global_rect().position.y and scroll.get_global_rect().end.y < back.get_global_rect().position.y,"BTI: title, scroll and bottom navigation do not overlap")
			for button: Control in [back,switch]:
				r.check(viewport.encloses(button.get_global_rect()) and button.size.x >= 44*config.z and button.size.y >= 44*config.z,"BTI: visible bottom hit target")
			r.check(not back.get_global_rect().intersects(switch.get_global_rect()),"BTI: independent bottom actions")
			var fixed_title: Rect2 = heading.get_global_rect()
			var fixed_back: Rect2 = back.get_global_rect()
			scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
			await r.frames()
			r.check(heading.get_global_rect() == fixed_title and back.get_global_rect() == fixed_back,"BTI: scrolling preserves fixed title/navigation")
			var last: Control = app.animation_toggle if section == "settings" else app.help_panel.chapters[app.help_panel.chapter].get_children()[-1]
			r.check(last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1,"BTI: content end reachable")
			scroll.scroll_vertical = 0
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
