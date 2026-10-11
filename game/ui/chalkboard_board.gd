extends "res://ui/drawing_board.gd"
## The single selected regular presentation; no study controls or save override.
const CHALKBOARD_ROW_SLOT: float = 26.0
const Fonts = preload("res://ui/drawing_font.gd")

func clue_font() -> Font:
	return Fonts.selected()

func clue_text_font(font: Font, text: String) -> Font:
	return Fonts.REFERENCE if not text.is_valid_int() else font

func clue_font_size() -> int:
	return mini(Fonts.pixel_size(super.clue_font_size()), maxi(Fonts.pixel_size(8), floori(view.cell_size - 4)))

func shared_clue_slot_extent(axis: String, font: Font, fs: int) -> float:
	if book_layout and axis == "row":
		return CHALKBOARD_ROW_SLOT * ui_scale
	return super.shared_clue_slot_extent(axis, font, fs)

func clue_tooltip_font_size() -> int:
	return Fonts.pixel_size(super.clue_tooltip_font_size())

func clue_baseline_offset(fs: int) -> float:
	var bounds: Vector2 = Fonts.ink_vertical(fs)
	return -(bounds.x + bounds.y) / 2.0

func clue_vertical_extents(fs: int) -> Vector2:
	var bounds: Vector2 = Fonts.ink_vertical(fs)
	return Vector2(-bounds.x - clue_baseline_offset(fs), bounds.y + clue_baseline_offset(fs))
