extends RefCounted
const Text = preload("res://ui/ui_text.gd")
const Capture = preload("res://tests/hz_native.gd")
const Keys = preload("res://tests/hz_b_native.gd")
const Sample = preload("res://tests/hz_c_sample.gd")

static func prefix_pixels(runner: Object, label: Label) -> PackedByteArray:
	await runner.frames()
	await RenderingServer.frame_post_draw
	var image: Image = runner.surface.get_texture().get_image()
	# Common first H, identical horizontal origin, independent of the rest of
	# the word. Native raster pixels prove baseline stability, not just boxes.
	var rect := Rect2i(label.global_position+Vector2(2*runner.app.ui_scale,0), Vector2(8*runner.app.ui_scale,label.size.y))
	var crop: Image = image.get_region(rect)
	var ink := 0
	for y: int in range(crop.get_height()):
		for x: int in range(crop.get_width()):
			var color: Color = crop.get_pixel(x,y)
			if color.r < 0.4 and color.g < 0.4 and color.b < 0.4: ink += 1
	runner.check(ink > 5,"HZ-C prefix oracle contains actual dark glyph pixels")
	return crop.get_data()

static func run(runner: Object) -> void:
	preload("res://tests/hz_c_cases.gd").run(runner)
	var app = runner.app
	app.show_album()
	var saves: Dictionary = runner.save_bytes()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1080,1.0]]:
		runner.surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await runner.frames()
		# The old string-width-minus-32 oracle misses the native arrow budget.
		# Ask an identical one-item native control for the complete minimum.
		var full_category := Sample.Choice.new()
		full_category.ui_scale = app.ui_scale
		full_category.add_item("Gemüse, Pilze & Kräuter (1)")
		full_category.hide()
		app.add_child(full_category)
		runner.check(app.album.category_choice.size.x >= full_category.get_minimum_size().x,"HZ-C closed category fits full usual name including native arrow and margins: %s >= %s at %s" % [app.album.category_choice.size.x,full_category.get_minimum_size().x,spec])
		full_category.free()
		var card = app.choices[0]
		var geometry: Array = [card.detail.position,card.image_area,card.label_area,card.leaf.get_rect(),card.note.get_rect()]
		var old_note: String = card.note.text
		var old_icon: String = card.status_icon.kind
		var old_category: String = card.detail.text
		var baseline := -1.0
		for value: String in ["Neu","Begonnen","Gelöst"]:
			card.note.text = value
			card.status_icon.kind = value
			card.detail.text = "TEST Äpfel" if value == "Neu" else "TEST Größe\nStraße – Wiese"
			card.layout_content()
			runner.check([card.detail.position,card.image_area,card.label_area,card.leaf.get_rect(),card.note.get_rect()] == geometry,"HZ-C fixed category start and footer rectangles across text changes")
			var fs: int = card.note.get_theme_font_size("font_size")
			var current: float = Text.line_baseline(card.note.get_theme_font("font"),fs,card.note.size.y)
			if baseline < 0: baseline = current
			runner.check(current == baseline,"HZ-C stable status baseline "+value)
			runner.check(card.detail.get_theme_font_size("font_size") == Text.small_size(app.ui_scale),"HZ-C categories share the small text role")
			runner.check(card.note.get_theme_font_size("font_size") == card.leaf.get_theme_font_size("font_size"),"HZ-C footer shares baseline and size; Blatt remains 15")
			await Capture.capture(runner,"c-status-%s-%d"%["gelost" if value == "Gelöst" else value.to_lower(),spec[0]],card.get_global_rect())
		card.note.text = old_note
		card.status_icon.kind = old_icon
		card.detail.text = old_category
		card.layout_content()
		# Native Label prefix images, with unchanged first glyph and different
		# descender/accent content after it. A word-wise correction fails here.
		var label := Label.new()
		label.position = Vector2(40,80)
		label.size = Vector2(400,44)*app.ui_scale
		label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		Text.small_label(label,Text.small_size(app.ui_scale),app.ui_scale)
		var ink_style: StyleBox = label.get_theme_stylebox("normal")
		var background := StyleBoxFlat.new()
		background.bg_color = Color("fffaf0")
		for side: Side in [SIDE_LEFT,SIDE_TOP,SIDE_RIGHT,SIDE_BOTTOM]:
			background.set_content_margin(side,ink_style.get_content_margin(side))
		label.add_theme_stylebox_override("normal",background)
		app.add_child(label)
		var prefix: PackedByteArray
		for word: String in ["H Neu","H Begonnen","H Gelöst","H Größe × … ←"]:
			label.text = word
			var pixels: PackedByteArray = await prefix_pixels(runner,label)
			if prefix.is_empty(): prefix = pixels
			runner.check(pixels == prefix,"HZ-C actual first-glyph raster baseline stable: "+word)
		label.free()
		var button := Sample.ButtonInk.new()
		button.position = Vector2(40,80)
		button.size = Vector2(400,44)*app.ui_scale
		button.ui_scale = app.ui_scale
		var button_font: Font = Text.small_font(Text.small_size(app.ui_scale))
		button.add_theme_font_override("font",button_font)
		button.add_theme_font_size_override("font_size",Text.small_size(app.ui_scale))
		app.add_child(button)
		var first_span := Vector2i(-1,-1)
		for word: String in ["H Neu","H Begonnen","H Gelöst","H Größe × … ←"]:
			button.text = word
			button.queue_redraw()
			await runner.frames()
			await RenderingServer.frame_post_draw
			var fs: int = Text.small_size(app.ui_scale)
			var word_ink: Rect2 = Text.ink(button_font,word,fs)
			var first_ink: Rect2 = Text.ink(button_font,"H",fs)
			var start_x: int = roundi(button.global_position.x+roundf((button.size.x-word_ink.size.x)/2-word_ink.position.x)+first_ink.position.x)
			var pixels: Image = runner.surface.get_texture().get_image()
			var span := Vector2i(-1,-1)
			for y: int in range(roundi(7*app.ui_scale),roundi(button.size.y-7*app.ui_scale)):
				for x: int in range(start_x,start_x+roundi(first_ink.size.x)):
					var pixel: Color = pixels.get_pixel(x,roundi(button.global_position.y)+y)
					if pixel.r < 0.4 and pixel.g < 0.4 and pixel.b < 0.4:
						if span.x < 0: span.x = y
						span.y = y
			if first_span.x < 0: first_span = span
			runner.check(span.x >= 0 and span == first_span,"HZ-C direct BookButton first-glyph pixel baseline stable: "+word)
		button.free()
		for choice: OptionButton in [app.album.category_choice,app.album.sort_choice]:
			runner.check(choice.get_theme_font_size("font_size") == Text.small_size(app.ui_scale),"HZ-C closed native choice size")
			runner.click(choice)
			runner.surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
			await runner.frames()
			var popup: PopupMenu = choice.get_popup()
			runner.check(popup.visible and popup.get_theme_font_size("font_size") == Text.small_size(app.ui_scale),"HZ-C native open menu has matching size")
			await Capture.capture(runner,"c-%s-%d"%[choice.name,spec[0]],Rect2(Vector2(popup.position),Vector2(popup.size)))
			await Keys.key(runner,KEY_ESCAPE)
			runner.check(not popup.visible,"HZ-C native menu Escape closes")
		app.show_information("settings")
		app.info_scroll.ensure_control_visible(app.view_choice)
		await runner.frames()
		runner.click(app.view_choice)
		await runner.frames()
		runner.check(app.view_choice.get_popup().visible,"HZ-C actual settings view popup opens")
		await Capture.capture(runner,"c-view-%d"%spec[0],Rect2(Vector2(app.view_choice.get_popup().position),Vector2(app.view_choice.get_popup().size)))
		await Keys.key(runner,KEY_ESCAPE)
		app.return_to_work()
		app.hide()
		var sample := Sample.new()
		sample.theme = app.theme
		sample.position = Vector2(24,24)
		sample.ui_scale = spec[2]
		runner.surface.add_child(sample)
		await runner.frames()
		await Capture.capture(runner,"c-comparison-%d"%spec[0],sample.get_global_rect())
		for sample_card: Control in sample.cards:
			runner.check(sample_card.image_area.size.y >= 112*app.ui_scale,"HZ-C comparison preserves original image budget at both sizes")
			var fs: int = roundi(sample_card.small_text_size*app.ui_scale)
			var before := TextLine.new()
			before.add_string("Hhx",Text.font(),fs)
			var fallback := TextLine.new()
			fallback.add_string("Hhx × ←",Text.font(),fs)
			var after := TextLine.new()
			after.add_string("Hhx",Text.small_font(fs),fs)
			runner.hzc_measurements.append({"surface":spec,"base_size":sample_card.small_text_size,"pixels":fs,"original_ascent":before.get_line_ascent(),"original_descent":before.get_line_descent(),"fallback_ascent":fallback.get_line_ascent(),"fallback_descent":fallback.get_line_descent(),"role_ascent":after.get_line_ascent(),"role_descent":after.get_line_descent(),"baseline_offset":Text.small_font(fs).baseline_offset,"body_ink":Text.ink(Text.small_font(fs),Text.BODY_SAMPLE,fs),"card_size":sample_card.size,"image_area":sample_card.image_area})
		sample.free()
		app.show()
	runner.check(runner.save_bytes() == saves,"HZ-C typography routes preserve isolated save bytes")
