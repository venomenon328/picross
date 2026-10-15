extends PanelContainer
## Native tooltip popup owns placement/lifetime; content has bounded, UI-scaled ink.
const Scribble = preload("res://ui/scribble.gd")
var ui_scale: float = 1.0

func configure(caption: String, scale_value: float, client_width: float, font: Font) -> void:
	ui_scale = scale_value
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var paper: StyleBoxFlat = StyleBoxFlat.new()
	paper.bg_color = Color("fffaf0")
	paper.set_content_margin_all(12 * ui_scale)
	add_theme_stylebox_override("panel", paper)
	var label: Label = Label.new()
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.text = caption
	label.add_theme_font_override("font", font)
	var fs: int = roundi(16 * ui_scale)
	label.add_theme_font_size_override("font_size", fs)
	label.add_theme_color_override("font_color", Color("293e3d"))
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = minf(font.get_multiline_string_size(caption,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x, minf(420*ui_scale,client_width-56*ui_scale))
	add_child(label)

func _draw() -> void:
	for line: Dictionary in Scribble.outline_strokes(Rect2(Vector2.ZERO,size).grow(-2*ui_scale),"book-tooltip",ui_scale):
		Scribble.paint(self,line,Color("6d624d"))
