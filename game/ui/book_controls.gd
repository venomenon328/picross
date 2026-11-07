extends RefCounted
## Theme resources only: native controls retain all input and selection behavior.
const Paper = preload("res://ui/book_style.gd")
const Text = preload("res://ui/ui_text.gd")
const ScrollInk = preload("res://ui/scrollbar_style.gd")
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
	scrollbars(result,u)
	return result

static func scroll_arrow(id: String, u: float, state: String) -> Texture2D:
	var key: String = "scroll/%s/%s/%s" % [id,u,state]
	if not textures.has(key):
		# Native ScrollBar draws its two icons outside the track StyleBox.
		# Their own graphite backing keeps the light triangles legible there.
		var mark: Image = icon(id,u,false,Color("fffdf5") if state == "hover" else Color("e5e1d7") if state == "pressed" else Color("f3f0e7")).get_image()
		var image := Image.create(mark.get_width(),mark.get_height(),false,Image.FORMAT_RGBA8)
		image.fill(Color("777570") if state == "hover" else Color("494a47") if state == "pressed" else ScrollInk.TRACK)
		image.blend_rect(mark,Rect2i(Vector2i.ZERO,mark.get_size()),Vector2i.ZERO)
		textures[key] = ImageTexture.create_from_image(image)
	return textures[key]

static func scrollbars(target: Theme, u: float) -> void:
	# One family for inherited/dynamic ScrollContainers and explicit PopupMenu
	# themes, including the horizontal fallback. No input handler is installed.
	for type: String in ["VScrollBar","HScrollBar"]:
		var horizontal: bool = type == "HScrollBar"
		for name: String in ["scroll","scroll_focus","grabber","grabber_highlight","grabber_pressed"]:
			var state: String = "focus" if name == "scroll_focus" else "hover" if name.ends_with("highlight") else "pressed" if name.ends_with("pressed") else "normal"
			target.set_stylebox(name,type,ScrollInk.make(u,horizontal,name.begins_with("grabber"),state))
		for suffix: String in ["","_highlight","_pressed"]:
			var state: String = "hover" if suffix == "_highlight" else "pressed" if suffix == "_pressed" else "normal"
			target.set_icon("decrement"+suffix,type,scroll_arrow("scroll-left" if horizontal else "scroll-up",u,state))
			target.set_icon("increment"+suffix,type,scroll_arrow("scroll-right" if horizontal else "scroll-down",u,state))
		# The drawing's own inset exposes the track; no extra native gutter.
		for name: String in (["padding_top","padding_bottom"] if horizontal else ["padding_left","padding_right"]):
			target.set_constant(name,type,0)

static func scroll_steps(node: Node, u: float) -> void:
	# ScrollContainer's internal bars default to step=0. Now that their native
	# arrow buttons are visible, give them a useful native custom_step without
	# quantising drag/wheel values or handling any events ourselves.
	if node is ScrollBar: node.custom_step = roundi(32*u)
	for child: Node in node.get_children(true): scroll_steps(child,u)

static func checks(target: Theme, u: float) -> void:
	for name: String in ["checked","unchecked","checked_disabled","unchecked_disabled"]:
		target.set_icon(name,"CheckBox",icon("checkbox-checked" if name.begins_with("checked") else "checkbox-empty",u,name.ends_with("disabled")))
	target.set_color("checkbox_checked_color","CheckBox",Color.WHITE)
	target.set_color("checkbox_unchecked_color","CheckBox",Color.WHITE)
	var focus = Paper.make("checkbox-focus",u,Color.TRANSPARENT)
	focus.focus = true
	focus.ink = INK
	target.set_stylebox("focus","CheckBox",focus)
