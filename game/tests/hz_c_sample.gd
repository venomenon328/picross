extends Control
## Static synthetic 14/15 comparison using the actual production components.
const Text = preload("res://ui/ui_text.gd")
const Card = preload("res://ui/catalog_card.gd")
const Choice = preload("res://ui/book_choice.gd")
const ButtonInk = preload("res://ui/book_button.gd")
const Paper = preload("res://ui/book_style.gd")
var ui_scale: float = 1.0
var cards: Array[Control] = []

func _ready() -> void:
	var u: float = ui_scale
	var width := 0.0
	for base: int in [14,15]:
		var card := Card.new()
		card.small_text_size = base
		card.ui_scale = u
		card.action_id = "hzc-comparison"
		card.content_surface = true
		card.add_theme_stylebox_override("normal",Paper.make("card/hzc-comparison",u,Color("fff8e8")))
		add_child(card)
		card.configure("???", "TEST Größe Äpfel\nStraße – Wiese", "Blatt 01")
		card.set_metadata(50,40,false,null)
		card.note.text = "Begonnen"
		card.status_icon.kind = "Begonnen"
		card.layout_content()
		width = maxf(width,card.minimum_card_width(u)+16*u)
		cards.append(card)
	var y := 0.0
	for i: int in range(2):
		var fs: int = roundi((14+i)*u)
		var x: float = (width+24*u)*i
		var title := Label.new()
		title.text = "%d · korrigiert" % (14+i)
		title.add_theme_font_override("font",Text.font())
		title.add_theme_font_size_override("font_size",roundi(18*u))
		title.position = Vector2(x+4*u,0)
		add_child(title)
		var card = cards[i]
		card.position = Vector2(x,40*u)
		card.size.x = width
		card.layout_content()
		y = card.position.y+card.size.y+12*u
		var choice := Choice.new()
		choice.name = "comparison-%d" % i
		choice.ui_scale = u
		choice.position = Vector2(x,y)
		choice.size = Vector2(width,44*u)
		choice.add_item("Größe · Äpfel – Straße")
		choice.add_item("Sehr leicht")
		choice.add_item("Sehr schwer")
		add_child(choice)
		choice.add_theme_font_override("font",Text.small_font(fs))
		choice.add_theme_font_size_override("font_size",fs)
		choice.get_popup().theme.default_font = Text.small_font(fs)
		choice.get_popup().theme.default_font_size = fs
		var button := ButtonInk.new()
		button.action_id = "hzc-comparison-button"
		button.text = "Zurück · Größe ändern"
		button.ui_scale = u
		button.position = Vector2(x,y+56*u)
		button.size = Vector2(width,44*u)
		button.add_theme_font_override("font",Text.small_font(fs))
		button.add_theme_font_size_override("font_size",fs)
		add_child(button)
	size = Vector2(width*2+24*u,y+100*u)
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO,size),Color("eee8d5"))
