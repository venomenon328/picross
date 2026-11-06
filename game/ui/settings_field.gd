extends HBoxContainer
## One aligned label/choice/help row, confined to the settings page.
const Help = preload("res://ui/settings_help.gd")
const Text = preload("res://ui/ui_text.gd")
const Buttons = preload("res://ui/book_button.gd")
var caption: Label
var choice: OptionButton
var help: Button

func configure(app: Control, title: String, selector: OptionButton, explanation: String = "") -> void:
	name = selector.name+"-field"
	caption = app.label(title,16)
	caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(caption)
	choice = selector
	choice.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(choice)
	if not explanation.is_empty():
		help = Help.new()
		help.text = "?"
		help.action_id = str(name)+"/help"
		help.tooltip_text = explanation
		help.accessibility_name = title+" erklären"
		help.focus_mode = Control.FOCUS_ALL
		help.paper_transparent = true
		add_child(help)
	choice.get_popup().about_to_popup.connect(func() -> void: Buttons.dismiss_all(get_tree()))
	choice.get_popup().popup_hide.connect(func() -> void: Buttons.dismiss_all(get_tree()))

func set_columns(label_width: float, scale_value: float) -> void:
	add_theme_constant_override("separation",roundi(10*scale_value))
	caption.custom_minimum_size.x = label_width
	choice.ui_scale = scale_value
	choice.custom_minimum_size.y = 44*scale_value
	if help == null: return
	help.ui_scale = scale_value
	help.custom_minimum_size = Vector2.ONE*44*scale_value
	help.add_theme_font_override("font",Text.small_font(Text.small_size(scale_value)))
	help.add_theme_font_size_override("font_size",Text.small_size(scale_value))
