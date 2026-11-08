extends Control
## One transient help visit; editorial navigation never touches a game session.
const Example = preload("res://ui/help_example.gd")
const Examples = preload("res://ui/help_examples.gd")
const BookButton = preload("res://ui/help_chapter_button.gd")
const Text = preload("res://ui/ui_text.gd")
const TITLES = ["Spielprinzip","Farbige Rätsel","Bedienung","Lösungstipps"]
var app: Control
var chapter: int = 0
# A measured paragraph column, independent of the wider diagram area.
class CopyColumn extends Container:
	var maximum: float = 0
	func _get_minimum_size() -> Vector2:
		return Vector2(0,get_child(0).get_combined_minimum_size().y)
	func _notification(what: int) -> void:
		if what == NOTIFICATION_SORT_CHILDREN:
			fit_child_in_rect(get_child(0),Rect2(Vector2.ZERO,Vector2(minf(size.x,maximum),size.y)))

var navigation: Control
var scroll: ScrollContainer
var article: VBoxContainer
var copy_columns: Array[CopyColumn] = []
var compact: bool = false
var ui_scale: float = 1.0
var paragraph_width: float = 0
var layout_size := Vector2.ZERO
var layout_scale: float = 0
var reading_anchor: Dictionary = {}
var restore_frames: int = 0
var advances: Dictionary = {}
var buttons: Array[Button] = []
var chapters: Array[VBoxContainer] = []
var figures: Array[Control] = []
var icons: Array[TextureRect] = []

func configure(owner: Control) -> void:
	app = owner
	mouse_filter = MOUSE_FILTER_PASS
	size_flags_horizontal = SIZE_EXPAND_FILL
	navigation = Control.new()
	add_child(navigation)
	scroll = ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.mouse_force_pass_scroll_events = false
	scroll.follow_focus = true
	add_child(scroll)
	# Theme propagation updates native scrollbar minima after the scale call.
	scroll.get_v_scroll_bar().minimum_size_changed.connect(layout_content.call_deferred)
	article = VBoxContainer.new()
	article.size_flags_horizontal = SIZE_EXPAND_FILL
	scroll.add_child(article)
	for i: int in range(TITLES.size()):
		var button := BookButton.new()
		button.text = TITLES[i]
		button.action_id = "help/"+str(i)
		button.name = "chapter-"+str(i)
		button.paper_transparent = true
		button.size_flags_horizontal = SIZE_EXPAND_FILL
		button.focus_mode = FOCUS_ALL
		button.pressed.connect(choose.bind(i))
		navigation.add_child(button)
		buttons.append(button)
		var page := VBoxContainer.new()
		page.name = "help-chapter-"+str(i)
		page.size_flags_horizontal = SIZE_EXPAND_FILL
		article.add_child(page)
		chapters.append(page)
	principle()
	colors()
	operation()
	tips()
	choose(0)
	set_process(false)
	set_ui_scale(app.ui_scale)

func heading(text: String, fs: int = 22) -> Label:
	# Explicit information-heading role, including sizes below label()'s old
	# 26px threshold. No global change to settings or other text roles.
	var item: Label = app.label(text,26)
	item.add_theme_font_override("font",app.WORK_TITLE_FONT)
	item.set_meta("base_font",fs)
	item.set_meta("help_heading",true)
	item.add_theme_font_size_override("font_size",fs)
	item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return item

func paragraph(parent: Node, text: String) -> Label:
	var item: Label = app.label(text,20)
	item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	item.size_flags_horizontal = SIZE_EXPAND_FILL
	item.mouse_filter = MOUSE_FILTER_IGNORE
	var column := CopyColumn.new()
	column.size_flags_horizontal = SIZE_EXPAND_FILL
	column.mouse_filter = MOUSE_FILTER_IGNORE
	column.add_child(item)
	parent.add_child(column)
	copy_columns.append(column)
	return item

func section(index: int, caption: String, text: String) -> void:
	chapters[index].add_child(heading(caption))
	paragraph(chapters[index],text)

func figure(parent: Node, key: String, caption: String = "") -> Control:
	var group := VBoxContainer.new()
	group.size_flags_horizontal = SIZE_EXPAND_FILL
	parent.add_child(group)
	if not caption.is_empty(): paragraph(group,caption)
	var item := Example.new()
	item.configure(key,Examples.all()[key])
	group.add_child(item)
	figures.append(item)
	return item

func legend(parent: Node, key: String, text: String) -> void:
	var row := HBoxContainer.new()
	row.size_flags_horizontal = SIZE_EXPAND_FILL
	parent.add_child(row)
	figure(row,key)
	# A fixed diagram plus a wrapping text column; never put the caption in
	# the diagram's numeric ink layer or invent a new cell meaning.
	row.get_child(0).size_flags_horizontal = SIZE_SHRINK_BEGIN
	paragraph(row,text)

func action(icon: String, input: String, effect: String) -> void:
	var row := HBoxContainer.new()
	row.size_flags_horizontal = SIZE_EXPAND_FILL
	chapters[2].add_child(row)
	var image := TextureRect.new()
	image.texture = load("res://art/book/"+icon+".svg")
	image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	image.modulate = BookButton.INK
	image.mouse_filter = MOUSE_FILTER_IGNORE
	row.add_child(image)
	icons.append(image)
	var copy := VBoxContainer.new()
	copy.size_flags_horizontal = SIZE_EXPAND_FILL
	row.add_child(copy)
	copy.add_child(heading(input,19))
	paragraph(copy,effect)

func principle() -> void:
	section(0,"Ein Bild aus Hinweisen","Ein Nonogramm ist ein Bildrätsel auf einem Raster. Finde heraus, welche Felder Farbe bekommen und welche leer bleiben. Die Zahlen am Rand heißen Hinweise. Du brauchst keine Bildvorlage: Zeilen und Spalten geben gemeinsam alle Füllungen vor.")
	section(0,"Zahlen werden zu Blöcken","Ein Block besteht aus direkt benachbarten gefüllten Feldern. Eine 3 verlangt genau drei davon. Lies die Hinweise einer Zeile von links nach rechts, die einer Spalte von oben nach unten. Ihre Reihenfolge gilt für die ganze Linie. Zwischen zwei Blöcken derselben Farbe bleibt mindestens ein Feld leer.")
	section(0,"Drei Feldzustände","Unbekannt heißt: Hier hast du noch nichts festgelegt. Eine Füllung trägt Farbe. Ein X bedeutet: Hier gehört keine Farbe hin. Radieren entfernt einen Eintrag und macht das Feld wieder unbekannt.")
	legend(chapters[0],"unknown","Unbekannt: freies Papier.")
	legend(chapters[0],"filled","Gefüllt: ein Feld des Bildes.")
	legend(chapters[0],"empty","Als leer markiert: ein X.")
	section(0,"Dein erster sicherer Zug","Sieben Felder und die Hinweise 3 3: Drei Füllungen, ein notwendiges Leerfeld und drei Füllungen brauchen die ganze Zeile. Es bleibt kein Platz zum Verschieben. Fülle die beiden Dreierblöcke und markiere das Feld dazwischen als leer.")
	figure(chapters[0],"e1","3 + 1 Leerfeld + 3 = 7 Felder")
	section(0,"Zeile und Spalte helfen einander","Jede Füllung gehört zugleich zu einer Zeile und einer Spalte. Prüfe nach einem sicheren Zug die kreuzenden Linien. Beide müssen passen. Dieses kleine Lehrbild zeigt, wie daraus weitere sichere Züge entstehen.")
	figure(chapters[0],"e2-cross","1. Die mittlere Zeile und Spalte haben jeweils den Hinweis 5. Beide sind fünf Felder lang und damit vollständig gefüllt.")
	figure(chapters[0],"e2-empty","2. Die äußeren Zeilen und Spalten verlangen jeweils nur einen Einerblock. Dieser ist durch das Kreuz schon gesetzt. Alle übrigen Felder dieser vier Linien sind leer.")
	figure(chapters[0],"e2-finish","3. In den beiden übrigen Zeilen passen die Dreierblöcke jetzt genau zwischen die leeren Randfelder. Fülle sie. Auch alle Spaltenhinweise passen: Das Lehrbild ist gelöst.")
	section(0,"Wann ist das Rätsel gelöst?","Alle richtigen Füllungen müssen in ihrer Farbe gesetzt sein, ohne zusätzliche Füllungen. Du musst den Hintergrund dafür nicht vollständig auskreuzen. Nach dem Abschluss erscheinen Motivname und Bild.")

func colors() -> void:
	section(1,"Die Zahl zählt, die Farbe färbt","Die Hinweiszahl bestimmt die Blocklänge, die Hinweisfarbe die Farbe der Felder. Auch hier bleibt die Reihenfolge verbindlich. Wähle vor dem Füllen das passende Farbfeld rechts neben dem Raster.")
	section(1,"Gleiche Farbe braucht Abstand","Aufeinanderfolgende Blöcke derselben Farbe benötigen mindestens ein Leerfeld. Bei sechs Feldern bleibt für 3 Rot und 2 Rot genau diese Belegung:")
	figure(chapters[1],"e4-same","Drei rote Felder · ein Leerfeld · zwei rote Felder")
	section(1,"Andere Farben dürfen sich berühren","Verschiedenfarbige Blöcke dürfen direkt aneinandergrenzen, müssen es aber nicht. Die Hinweise 3 Rot und 2 Blau erlauben zum Beispiel beide folgenden Belegungen. Das sind mögliche Lagen, keine vollständige Aufzählung und noch keine eindeutige Gesamtlösung.")
	figure(chapters[1],"e4-touch","Ohne Abstand: Rot 1–3, Blau 4–5, Feld 6 leer.")
	figure(chapters[1],"e4-gap","Mit Abstand: Rot 1–3, Feld 4 leer, Blau 5–6.")
	paragraph(chapters[1],"Die kreuzenden Zeilen und Spalten entscheiden mit, welche Lage im ganzen Rätsel passt. Ein Farbwechsel allein verlangt kein X.")

func operation() -> void:
	section(2,"Eintragen und korrigieren","Die Werkzeuge stehen rechts unter den Farben. Die Wirkung eines Strichs hängt von Werkzeug, Maustaste und Startfeld ab.")
	action("fill","Füllen · linke Maustaste","Klicke auf ein unbekanntes Feld, um die gewählte Farbe zu setzen. Ein Klick auf eine Füllung entfernt sie – auch bei einer anderen Farbe. Ein Klick auf ein X wandelt es in die gewählte Farbe um.")
	legend(chapters[2],"empty","Rechte Maustaste: Unbekannt wird X, X wird unbekannt, eine Füllung wird X. Ein X kennzeichnet leer; es radiert nicht auf unbekannt.")
	action("erase","Radieren · linke Maustaste","Wähle den Radierer und entferne Füllungen oder X. Die Felder sind danach unbekannt. Rechts gilt weiterhin die X-Regel.")
	section(2,"Gerade Linien ziehen","Halte die Maustaste gedrückt und ziehe. Ab der ersten eindeutigen Bewegung bleibt der Strich in einer Zeile oder Spalte. Zurückziehen verkürzt die Vorschau. Zurück auf dem tatsächlichen Startfeld kannst du die Richtung neu wählen. Loslassen übernimmt den angezeigten Strich als einen Schritt.")
	paragraph(chapters[2],"Startest du auf unbekannt, bleiben vorhandene Füllungen und X geschützt. Links auf X begonnen wandelt unbekannte Felder und X in Farbe; rechts auf einer Füllung begonnen wandelt unbekannte Felder und Füllungen in X. Links auf Füllung entfernt nur Füllungen, rechts auf X nur X. Starttyp, Modus und Farbe gelten für den ganzen Strich.")
	paragraph(chapters[2],"Die helle Vorschau zeigt nur die geplanten Änderungen. Begonnene Striche reichen auch über anderen Bedienelementen bis zum Rasterrand. Der Zähler am Zeiger zählt ab zwei Feldern die ganze Strichlänge, auch geschützte Felder.")
	section(2,"Abbrechen statt übernehmen","Escape oder die andere Maustaste verwirft den laufenden Strich. Nach dem Abbruch mit der anderen Taste lasse beide Tasten los und beginne neu. Auch ein Fokusverlust verwirft den Strich.")
	action("fill","Farbe wählen","Klicke auf ein Farbfeld in der Palette. Eckmarkierungen zeigen die Auswahl; der Tooltip nennt die Farbnummer. Die Farbwahl aktiviert Füllen, auch nach dem Radierer.")
	action("undo","Rückgängig","Der gebogene Rückpfeil nimmt den letzten ganzen Strich zurück, einschließlich seiner früheren Feldzustände.")
	action("redo","Wiederholen","Der gebogene Vorwärtspfeil stellt den zurückgenommenen Strich wieder her. Eine neue Bearbeitung nach Rückgängig ersetzt den bisherigen Wiederholungszweig.")
	action("minus","Verkleinern","Minus oder das Mausrad nach unten über dem Raster verkleinert die Darstellung.")
	action("plus","Vergrößern","Plus oder das Mausrad nach oben über dem Raster vergrößert bis zur Grenze, an der das ganze Raster sichtbar bleibt. Während eines Zellstrichs ist Zoom gesperrt.")
	section(2,"Lange Hinweise lesen","Ziehe eine gekürzte Zeilenfolge mit der linken Maustaste waagerecht, eine Spaltenfolge senkrecht. Nur die angefasste Folge bewegt sich und rastet beim Loslassen ein. Darüberfahren zeigt zusätzlich den vollständigen Hinweis. Vollständig passende Folgen lassen sich nicht verschieben.")
	action("menu","Einstellungen","Das Zahnrad oben rechts öffnet die Einstellungen auf der linken Informationsseite. Dort wählst du UI 100/125 % und die Rätselansicht. Die Gesamtansicht zeigt alle Hinweise und kann kleinere Zellen benötigen. Das Fragezeichen daneben öffnet die Hilfe. Ein Unterstrich markiert die aktuelle Ansicht; Hilfe und Einstellungen behalten während deines Besuchs ihre Lesestellen.")
	section(2,"Anzeigenlegende","Die Miniatur zeigt deine eigenen Füllungen einschließlich möglicher Fehler, keine korrigierte Lösung. X und unbekannte Felder erscheinen dort gleichermaßen neutral. Das Raster hebt zur Orientierung die Zeile und Spalte am Zeiger hervor; über Hinweisen nur deren eine Linie.")
	paragraph(chapters[2],"– bedeutet: Diese ganze Linie ist leer. … zeigt verborgene Hinweise auf der betreffenden Seite an.")
	paragraph(chapters[2],"Legende für „Erfüllte Hinweise markieren“: Die folgenden drei Zustände werden hier unabhängig vom aktuellen Schalter gezeigt. Sie beruhen nur auf deinen Einträgen und den Hinweisen der ganzen Linie. Sie bestätigen nicht die hinterlegte Lösung.")
	legend(chapters[2],"clue-open","Kräftige Zahl: noch nicht eindeutig erfüllt.")
	legend(chapters[2],"clue-filled","Blasse Zahl: ein anhand deiner Linienbelegung eindeutig vollständig gesetzter Block.")
	legend(chapters[2],"clue-closed","Gleich blasse Zahl mit handschriftlichem X: zusätzlich an beiden Enden abgegrenzt. Unmittelbares X, echter Rasterrand oder direkt andere Füllfarbe zählen; unbekannte Nachbarn nicht.")
	paragraph(chapters[2],"Ist „Erfüllte Hinweise markieren“ ausgeschaltet, erscheinen im Rätsel alle Hinweise normal. Der Schalter gilt für diese Sitzung.")
	action("nav-work","Zurück und später fortsetzen","Der linke Pfeil in der Gruppe oben rechts führt zum Katalog oder Rätsel, aus dem du die Hilfe geöffnet hast. Sein Tooltip nennt das Ziel. Der Pfeil im Rätselkopf führt zum Katalog. Dein Arbeitsstand mit Rückgängig/Wiederholen wird lokal gespeichert und beim erneuten Öffnen fortgesetzt. Im Katalog blättern die beiden unteren Pfeile die ganze Doppelseite; Beenden steht oben rechts links neben dem Zahnrad.")
	paragraph(chapters[2],"Speicherfehler bleiben sichtbar. Lasse die Anwendung dann offen und versuche die Speicherung erneut. Eine angebotene Backupübernahme braucht deine Bestätigung. Im Browser warte auf die bestätigte Sicherung, bevor du den Tab schließt.")

func tips() -> void:
	section(3,"1 · Vollständig bestimmte Linien","Beginne mit Linien, deren Blöcke samt notwendigen Abständen genau hineinpassen. Wie bei 3 3 in sieben Feldern steht dann jedes Feld fest. Auch eine 5 in fünf Feldern ist sofort vollständig bestimmt.")
	figure(chapters[3],"e1")
	section(3,"2 · Überlappungen finden","Eine 5 in sieben Feldern kann nicht beliebig ausweichen. Vergleiche die früheste und späteste mögliche Lage. Wo sich beide überdecken, muss jede zulässige Lage Farbe tragen.")
	figure(chapters[3],"e3-first","Mögliche Platzierung ganz links: Felder 1–5.")
	figure(chapters[3],"e3-last","Mögliche Platzierung ganz rechts: Felder 3–7.")
	figure(chapters[3],"e3-overlap","Sicher sind nur die mittleren Felder 3–5. Felder 1, 2, 6 und 7 bleiben unbekannt: Aus dieser Information allein folgt dort kein X.")
	section(3,"3 · Abgrenzen und kreuzend weiterarbeiten","Ist die Lage eines vollständigen Blocks sicher, markiere benachbarte Felder nur dann als leer, wenn die Hinweise es verlangen. Zwischen gleichfarbigen Blöcken ist Abstand nötig; bei einer anderen Farbe kann der nächste Block direkt anschließen.")
	paragraph(chapters[3],"Prüfe danach die kreuzenden Linien: Jede sichere Füllung und jedes sichere Leerfeld schränkt ihre Möglichkeiten ein. Wechsle zwischen Zeilen und Spalten, wie im kleinen Lehrbild unter Spielprinzip. So entsteht das Bild Schritt für Schritt, ohne Raten.")

func choose(index: int) -> void:
	chapter = index
	for i: int in range(chapters.size()):
		chapters[i].visible = i == index
		buttons[i].selected = i == index
	reading_anchor = {}
	restore_frames = 0
	set_process(false)
	scroll.scroll_vertical = 0

func begin_visit() -> void: choose(0)

func set_ui_scale(value: float) -> void:
	if value != ui_scale: remember_reading()
	ui_scale = value
	article.add_theme_constant_override("separation",roundi(20*value))
	for button: BookButton in buttons:
		button.ui_scale = value
		button.add_theme_font_size_override("font_size",roundi(20*value))
		button.custom_minimum_size = Vector2(44,44)*value
	for box: Node in find_children("*","BoxContainer",true,false):
		box.add_theme_constant_override("separation",roundi((12 if box is HBoxContainer else 8)*value))
	for page: VBoxContainer in chapters: page.add_theme_constant_override("separation",roundi(14*value))
	for item: Control in figures: item.set_ui_scale(value)
	for icon: TextureRect in icons: icon.custom_minimum_size = Vector2(44,44)*value

	layout_content()

func remember_reading() -> void:
	if not reading_anchor.is_empty() or chapters.is_empty(): return
	var offset: float = scroll.scroll_vertical
	for item: Control in chapters[chapter].get_children():
		if item.position.y <= offset:
			reading_anchor = {"item":item,"fraction":(offset-item.position.y)/maxf(1,item.size.y)}

func layout_content() -> void:
	if scroll == null or size.x <= 0: return
	var changed: bool = size != layout_size or ui_scale != layout_scale
	if changed: remember_reading()
	var u: float = ui_scale
	var register_width: float = 44*u
	for button: Button in buttons:
		button.add_theme_font_override("font",Text.font())
		button.add_theme_font_size_override("font_size",roundi(20*u))
		register_width = maxf(register_width,Text.width(button.get_theme_font("font"),button.text,button.get_theme_font_size("font_size"))+24*u)
	# Average advance of the real copy at its actual font size, rather than
	# a window breakpoint or a fixed number of assumed monospace pixels.
	var fs: int = roundi(20*u)
	if not advances.has(fs):
		var sample: String = ""
		for column: CopyColumn in copy_columns: sample += column.get_child(0).text
		advances[fs] = Text.font().get_string_size(sample,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x/maxi(1,sample.length())
	var advance: float = advances[fs]
	# The upper target leaves room for word-boundary raggedness (usually
	# 60–75 actual characters). Two AA pixels separate register and article.
	paragraph_width = ceilf(75*advance)+4*u
	var diagram_width: float = 0
	for item: Control in figures: diagram_width = maxf(diagram_width,item.get_combined_minimum_size().x)
	var gutter: float = scroll.get_v_scroll_bar().get_combined_minimum_size().x+4*u
	compact = size.x < register_width+34*u+maxf(paragraph_width,diagram_width)+gutter
	var article_x: float = 0
	var article_y: float = 0
	if compact:
		var pen := Vector2.ZERO
		for button: Button in buttons:
			var width: float = maxf(44*u,Text.width(button.get_theme_font("font"),button.text,button.get_theme_font_size("font_size"))+24*u)
			if pen.x > 0 and pen.x+width > size.x:
				pen.x = 0
				pen.y += 48*u
			button.position = pen
			button.size = Vector2(width,44*u)
			pen.x += width+8*u
		article_y = pen.y+56*u
		navigation.size = Vector2(size.x,article_y-8*u)
	else:
		for i: int in range(buttons.size()):
			buttons[i].position = Vector2(0,i*52*u)
			buttons[i].size = Vector2(register_width,44*u)
		navigation.size = Vector2(register_width,4*52*u)
		article_x = register_width+34*u
	var target := Rect2(Vector2(article_x,article_y),Vector2(size.x-article_x,maxf(1,size.y-article_y)))
	if scroll.get_rect() != target and not changed:
		remember_reading()
		changed = true
	scroll.position = target.position
	scroll.size = target.size
	for column: CopyColumn in copy_columns:
		column.maximum = paragraph_width
		column.queue_sort()
	layout_size = size
	layout_scale = u
	if changed:
		restore_frames = 4
		set_process(true)

func _process(_delta: float) -> void:
	# Containers settle over several deferred sorts. Keep a semantic paragraph
	# anchor while width/font changes, including while the help page is hidden.
	if not reading_anchor.is_empty():
		var item: Control = reading_anchor.item
		scroll.scroll_vertical = roundi(item.position.y+reading_anchor.fraction*item.size.y)
	restore_frames -= 1
	if restore_frames <= 0:
		reading_anchor = {}
		set_process(false)
