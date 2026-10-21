extends RefCounted
## Theme resources only: native controls retain all input and selection behavior.
const Paper = preload("res://ui/book_style.gd")
const Text = preload("res://ui/ui_text.gd")
const INK = Color("293e3d")
static var textures: Dictionary = {}

static func icon(id: String, scale: float, disabled: bool = false, tint: Color = INK) -> Texture2D:
	var key: String = "%s/%s/%s/%s" % [id,scale,disabled,tint.to_html()]
	if not textures.has(key):
		var source: Texture2D = load("res://art/book/"+id+".svg")
		var image: Image = source.get_image()
		image.convert(Image.FORMAT_RGBA8)
		var color: Color = Color("757970") if disabled else tint
		for y: int in range(image.get_height()):
			for x: int in range(image.get_width()):
				var pixel: Color = image.get_pixel(x,y)
				image.set_pixel(x,y,Color(color,color.a*pixel.a))
		image.resize(roundi(22*scale),roundi(22*scale),Image.INTERPOLATE_LANCZOS)
		textures[key] = ImageTexture.create_from_image(image)
	return textures[key]

static func styles(target: Theme, type: String, id: String, u: float) -> void:
	if type == "Button":
		# AcceptDialog reapplies these when laying out its native buttons.
		target.set_constant("buttons_min_width","AcceptDialog",roundi(44*u))
		target.set_constant("buttons_min_height","AcceptDialog",roundi(44*u))
	for state: String in ["normal","hover","pressed","hover_pressed","disabled","focus"]:
		var color: Color = Color("e9e2d4") if state == "disabled" else Color("c5d6cd") if state in ["pressed","hover_pressed"] else Color("e0ece6") if state == "hover" else Color("fffaf0")
		var style = Paper.make(id,u,color)
		if state == "focus":
			style.focus = true
			style.paper = Color.TRANSPARENT
			style.ink = INK
		style.content_margin_left = 10*u
		# OptionButton itself reserves its arrow and h_separation in addition to
		# the style margins. Reserving the arrow twice crowds long categories.
		style.content_margin_right = 10*u
		style.content_margin_top = 5*u
		style.content_margin_bottom = 5*u
		target.set_stylebox(state,type,style)
		if state != "focus":
			target.set_color("font_color" if state == "normal" else "font_"+state+"_color",type,Color("757970") if state == "disabled" else INK)

static func popup_theme(id: String, u: float, font: Font) -> Theme:
	var result := Theme.new()
	result.default_font = font
	result.default_font_size = Text.small_size(u)
	var panel = Paper.make(id,u)
	panel.opaque_bounds = true
	panel.set_content_margin_all(9*u)
	result.set_stylebox("panel","PopupMenu",panel)
	var hover = Paper.make(id+"/row",u,Color("e0ece6"))
	# The native marker occupies the row's leading inset. Highlight its paper
	# without drawing an extra contour through the checkmark's reserved space.
	hover.ink = Color.TRANSPARENT
	result.set_stylebox("hover","PopupMenu",hover)
	for state: String in ["font_color","font_hover_color","font_accelerator_color"]:
		result.set_color(state,"PopupMenu",INK)
	result.set_color("font_disabled_color","PopupMenu",Color("757970"))
	result.set_constant("v_separation","PopupMenu",roundi(12*u))
	result.set_constant("h_separation","PopupMenu",roundi(8*u))
	for name: String in ["checked","radio_checked"]:
		result.set_icon(name,"PopupMenu",icon("check",u))
	for name: String in ["unchecked","radio_unchecked"]:
		result.set_icon(name,"PopupMenu",icon("check-empty",u))
	for name: String in ["checked_disabled","radio_checked_disabled"]:
		result.set_icon(name,"PopupMenu",icon("check",u,true))
	for name: String in ["unchecked_disabled","radio_unchecked_disabled"]:
		result.set_icon(name,"PopupMenu",icon("check-empty",u,true))
	for state: String in ["scroll","grabber","grabber_highlight","grabber_pressed"]:
		var color: Color = Color("e3dfcf") if state == "scroll" else Color("c5d6cd") if state == "grabber_highlight" else Color("8ca99a") if state == "grabber_pressed" else Color("b4c6b5")
		var bar = Paper.make(id+"/scroll",u,color)
		bar.selected = state == "grabber_pressed"
		bar.set_content_margin_all(7*u)
		result.set_stylebox(state,"VScrollBar",bar)
	for state: String in ["","_highlight","_pressed"]:
		var tint: Color = Color("376a60") if state == "_highlight" else Color("172c2a") if state == "_pressed" else INK
		result.set_icon("increment"+state,"VScrollBar",icon("chevron-down",u,false,tint))
		result.set_icon("decrement"+state,"VScrollBar",icon("chevron-up",u,false,tint))
	return result

static func checks(target: Theme, u: float) -> void:
	for name: String in ["checked","unchecked","checked_disabled","unchecked_disabled"]:
		target.set_icon(name,"CheckBox",icon("checkbox-checked" if name.begins_with("checked") else "checkbox-empty",u,name.ends_with("disabled")))
	target.set_color("checkbox_checked_color","CheckBox",Color.WHITE)
	target.set_color("checkbox_unchecked_color","CheckBox",Color.WHITE)
	var focus = Paper.make("checkbox-focus",u,Color.TRANSPARENT)
	focus.focus = true
	focus.ink = INK
	target.set_stylebox("focus","CheckBox",focus)
