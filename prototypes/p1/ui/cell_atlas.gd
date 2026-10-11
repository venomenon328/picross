extends RefCounted
## PERF-B runtime mapping, identical to the bound pencil-atlas-1 A contract.
const VERSION = "pencil-atlas-1"
const VARIANTS = 16
const FRAMES = 24
const DURATION_US = 210000
const PADDING = 2

static func variant(puzzle_id: String, revision: int, cell: Vector2i) -> int:
	var identity: String = "%s\n%s\n%d\n%d\n%d" % [VERSION, puzzle_id, revision, cell.x, cell.y]
	return identity.sha256_text().substr(0, 8).hex_to_int() % VARIANTS

static func frame(elapsed_us: int) -> int:
	return clampi(floori(float(maxi(0, elapsed_us)) * (FRAMES - 1) / DURATION_US), 0, FRAMES - 1)

static func level(cell_size: float) -> String:
	return "small" if cell_size < 18.0 else ("medium" if cell_size <= 36.0 else "large")

static func pixels(lod: String) -> int:
	return {"small": 32, "medium": 64, "large": 96}[lod]

static func logical(lod: String) -> float:
	return {"small": 16.0, "medium": 24.0, "large": 72.0}[lod]

static func region(lod: String, selected: int, time_frame: int) -> Rect2:
	var pitch: int = pixels(lod) + PADDING * 2
	return Rect2(time_frame * pitch + PADDING, selected * pitch + PADDING, pixels(lod), pixels(lod))

static func mapped_box(cell: Rect2, lod: String) -> Rect2:
	# Map the source's safe inner box to the actual cell inset of two pixels.
	# The full transparent frame follows from that mapping; padding never scales
	# away the prescribed cell gap. X stays in normalized logical cell space.
	var scale: float = (cell.size.x - 4.0) / (logical(lod) - 4.0)
	return Rect2(cell.position + Vector2.ONE * (2.0 - 2.0 * scale), Vector2.ONE * logical(lod) * scale)
