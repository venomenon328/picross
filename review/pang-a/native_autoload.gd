extends Node
## One-time PANG-A implementation evidence; never shipped or added to CI.
const Text = preload("res://ui/ui_text.gd")
var root: Window
var book: Node
var app: Control
var folder: String
var checks: int = 0
var failures: Array[String] = []
var measurements: Array = []
var captures: Array = []
var characters: Dictionary = {}

func _ready() -> void:
	load("res://model/save_store.gd").test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		print("PANG_FAIL ",message)

func settle(seconds: float = 0.15) -> void:
	await get_tree().create_timer(seconds).timeout
	while app.presentation_locked: await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame

func shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	check(image.save_png(folder.path_join(name+".png")) == OK,"save native original "+name)
	captures.append({"file":name+".png","viewport":root.size,"ui":app.ui_scale,"chapter":app.help_panel.chapter,"section":app.information_section})

func inventory(text: String, font: Font, fs: int) -> void:
	var line := TextLine.new()
	line.add_string(text,font,fs)
	var ts: TextServer = TextServerManager.get_primary_interface()
	for glyph: Dictionary in ts.shaped_text_get_glyphs(line.get_rid()):
		check(glyph.index > 0,"no missing current glyph: "+text)
	for symbol: String in text: characters[symbol] = true

func help_measure() -> void:
	var count := 0
	var lines := 0
	for label: Node in app.help_panel.find_children("*","Label",true,false):
		if not label.is_visible_in_tree(): continue
		var fs: int = label.get_theme_font_size("font_size")
		var font: Font = label.get_theme_font("font")
		inventory(label.text,font,fs)
		var heading: bool = label.has_meta("help_heading")
		check(font.get_font_name() == ("Fraunces" if heading else "Pangolin"),"actual help role "+label.text)
		check(fs == roundi(float(label.get_meta("base_font"))*app.ui_scale),"actual help text size")
		check(label.get_visible_line_count() == label.get_line_count(),"all help lines fit "+label.text)
		check(label.position.x >= 0 and label.size.x <= app.help_panel.size.x+1,"help paragraph within paper column")
		count += 1
		lines += label.get_line_count()
	var scroll: ScrollContainer = app.info.help_scroll
	scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
	await settle()
	var last: Control = app.help_panel.chapters[app.help_panel.chapter].get_children()[-1]
	check(last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1,"help chapter end reachable")
	measurements.append({"kind":"help","viewport":root.size,"ui":app.ui_scale,"chapter":app.help_panel.chapter,"labels":count,"lines":lines,"paper":scroll.get_global_rect(),"content":app.help_panel.size,"last_bottom":last.get_global_rect().end.y,"clip_end":scroll.get_global_rect().end.y})
	scroll.scroll_vertical = 0
	await settle()

func roles() -> void:
	check(app.theme.default_font.get_font_name() == "Pangolin","shared standard role")
	check(app.title.get_theme_font("font").get_font_name() == "Bakso Daging","catalog heading unchanged")
	for choice: OptionButton in [app.album.category_choice,app.album.sort_choice,app.view_choice,app.ui_scale_choice]:
		check(choice.get_theme_font("font").get_font_name() == "Pangolin" and choice.get_popup().get_theme_font("font").get_font_name() == "Pangolin","closed and open choice role")
	for card: Control in app.choices:
		for label: Label in [card.detail,card.dimensions,card.difficulty,card.leaf,card.note]:
			check(label.get_theme_font("font").get_font_name() == "Pangolin","actual small card role")
			inventory(label.text,label.get_theme_font("font"),label.get_theme_font_size("font_size"))
		check(card.size.x >= card.minimum_card_width(app.ui_scale),"full metadata minimum")
		check(card.image_area.size.y >= 112*app.ui_scale,"retained image budget")
		for label: Label in [card.dimensions,card.difficulty,card.leaf,card.note]:
			check(Text.label_width(label,label.text,label.get_theme_font_size("font_size")) <= label.size.x+1,"unabridged metadata fit "+label.text)
	measurements.append({"kind":"catalog","viewport":root.size,"ui":app.ui_scale,"minimum":app.choices[0].minimum_card_width(app.ui_scale),"card":app.choices[0].size})

func run() -> void:
	folder = OS.get_environment("PANG_OUTPUT")
	root = get_tree().root
	root.gui_embed_subwindows = true
	load("res://model/save_store.gd").test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	book = get_tree().current_scene
	while book == null:
		await get_tree().process_frame
		book = get_tree().current_scene
	app = book.app
	await settle(0.8)
	for configuration: Array in [[1920,1080,1.0],[1280,720,1.25],[2560,1440,1.25]]:
		root.size = Vector2i(configuration[0],configuration[1])
		app.set_ui_scale(configuration[2])
		await settle()
		check(root.size == Vector2i(configuration[0],configuration[1]),"actual requested reference viewport")
		roles()
		if configuration[0] != 1280: await shot("catalog-%d-ui%d" % [root.size.x,roundi(app.ui_scale*100)])
		app.show_information("help")
		await settle(1.2)
		for chapter: int in range(4):
			app.help_panel.choose(chapter)
			await settle()
			await help_measure()
			if (configuration[0] == 1920 and chapter in [0,3]) or (configuration[0] == 1280 and chapter == 1) or (configuration[0] == 2560 and chapter == 2):
				await shot("help-%d-%d-ui%d" % [chapter,root.size.x,roundi(app.ui_scale*100)])
		app.show_information("settings")
		await settle(0.9)
		if configuration[0] == 1280:
			await shot("settings-1280-ui125")
			app.ui_scale_choice.show_popup()
			await settle()
			check(app.ui_scale_choice.get_popup().visible,"native choice popup open")
			await shot("dropdown-open-1280-ui125")
			app.ui_scale_choice.get_popup().hide()
		app.return_to_work()
		await settle(1.2)
	# UI100 -> 125 -> 100 retains the same role-specific baseline and advance.
	root.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	await settle()
	var before: float = Text.line_baseline(Text.small_font(15),15,44)
	app.set_ui_scale(1.25)
	await settle()
	app.set_ui_scale(1.0)
	await settle()
	check(before == Text.line_baseline(Text.small_font(15),15,44),"UI roundtrip baseline stable")
	# Real popup/menu contents with a maximum legal synthetic category caption.
	var choice: OptionButton = app.album.category_choice
	choice.add_item("TEST Äpfel, Straßen und ungewöhnliche Größen – "+"W".repeat(81))
	choice.set_item_tooltip(choice.item_count-1,choice.get_item_text(choice.item_count-1))
	choice.select(choice.item_count-1)
	await settle()
	await shot("dropdown-long-closed-1920-ui100")
	choice.show_popup()
	await settle()
	choice.get_popup().scroll_to_item(choice.item_count-1)
	await settle()
	await shot("dropdown-long-open-1920-ui100")
	choice.get_popup().hide()
	choice.remove_item(choice.item_count-1)
	choice.select(0)
	# Use the actual tooltip component, without OS pointer takeover.
	var tooltip = load("res://ui/book_tooltip.gd").new()
	tooltip.configure("Speichern erneut versuchen · Äpfel, Straße, Größen × 50 …\n„Backup übernehmen“ – nur dieses Blatt. ← → ↑ ↓",1.0,root.size.x,Text.font())
	app.add_child(tooltip)
	tooltip.position = Vector2(1250,80)
	await settle()
	check(tooltip.size.x <= 444,"bounded tooltip wrap")
	await shot("tooltip-1920-ui100")
	tooltip.queue_free()
	app.repair_dialog.dialog_text = "TEST: Der beschädigte oder fehlende Primärstand wird durch das gültige Backup ersetzt.\nÄpfel, Straße, Größen × 50 … „Übernehmen“ – ← → ↑ ↓"
	app._popup_dialog(app.repair_dialog)
	await settle()
	check(app.repair_dialog.get_label().get_theme_font("font").get_font_name() == "Pangolin","dialog content font")
	check(app.repair_dialog.get_theme_font("title_font","Window").get_font_name() == "IBM Plex Sans","dialog title preserved")
	await shot("recovery-dialog-1920-ui100")
	app.repair_dialog.hide()
	var report := {"source_head":OS.get_environment("PANG_HEAD"),"engine":Engine.get_version_info(),"os":OS.get_version(),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"checks":checks,"failures":failures,"measurements":measurements,"captures":captures,"current_characters":"".join(characters.keys())}
	var file := FileAccess.open(folder.path_join("native-text.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print("PANG_NATIVE_DONE ",checks," failures=",failures.size())
	get_tree().quit(0 if failures.is_empty() else 4)
