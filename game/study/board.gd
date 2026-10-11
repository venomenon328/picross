extends "res://ui/drawing_board.gd"
## Only the study exposes font and historical cell-style comparisons.
const CHALKBOARD_ROW_SLOT: float = 26.0
const Fonts = preload("res://study/fonts.gd")
var font_choice: int = 2

func clue_font() -> Font:
	return Fonts.selected(font_choice)

func clue_text_font(font: Font, text: String) -> Font:
	return Fonts.REFERENCE if font_choice > 0 and not text.is_valid_int() else font

func clue_font_size() -> int:
	return mini(Fonts.pixel_size(font_choice, super.clue_font_size()), maxi(Fonts.pixel_size(font_choice, 8), floori(view.cell_size - 4)))

func shared_clue_slot_extent(axis: String, font: Font, fs: int) -> float:
	if book_layout and axis == "row" and font_choice == 2:
		return CHALKBOARD_ROW_SLOT * ui_scale
	return super.shared_clue_slot_extent(axis, font, fs)

func clue_tooltip_font_size() -> int:
	return Fonts.pixel_size(font_choice, super.clue_tooltip_font_size())

func clue_baseline_offset(fs: int) -> float:
	if font_choice == 0:
		return super.clue_baseline_offset(fs)
	var bounds: Vector2 = Fonts.ink_vertical(font_choice, fs)
	return -(bounds.x + bounds.y) / 2.0

func clue_vertical_extents(fs: int) -> Vector2:
	if font_choice == 0:
		return super.clue_vertical_extents(fs)
	var bounds: Vector2 = Fonts.ink_vertical(font_choice, fs)
	return Vector2(-bounds.x - clue_baseline_offset(fs), bounds.y + clue_baseline_offset(fs))

func set_font_choice(value: int) -> void:
	font_choice = clampi(value, 0, 2)
	row_slot_extent_cache.clear()
	queue_redraw()
