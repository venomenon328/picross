extends "res://ui/chalkboard_board.gd"
## Labeled typography specimen, not a puzzle or a substitute for native clues.
const NUMBERS: Array[String] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "17", "40", "100"]

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), PAPER)
	draw_string(BODY_FONT, Vector2(18, 26), "Chalkboard · reguläre P1-Typografie" + " · künstliche Schriftmuster, keine Rätseldaten", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, INK)
	var font: Font = clue_font()
	for row: int in range(6):
		var fs: int = Fonts.pixel_size([16, 16, 16, 20, 12, 8][row])
		var status: int = row if row < 3 else 0
		var y: float = 72 + row * 55
		draw_string(BODY_FONT, Vector2(18, y), ["Normal", "Gesetzt", "Begrenzt", "UI 125 %", "Klein", "Minimum"][row], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, INK)
		for i: int in range(NUMBERS.size()):
			var color: Color = cell_color(i % 4 + 1)
			draw_clue_number(font, Vector2(118 + i * 41, y), NUMBERS[i], fs, color, status)
	draw_string(BODY_FONT, Vector2(18, 418), "C1-Kontur, 78 % bei gesetzten Hinweisen; gleiche Größe in allen Zuständen.", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, INK)
