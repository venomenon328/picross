extends RefCounted

## Selects a contiguous window of complete clue tokens. Progress 0 keeps the
## grid-near end, progress 1 keeps the outer beginning. Marker extents are part
## of the fit calculation, so neither markers nor tokens are clipped.
static func select_window(extents: Array[float], available: float, progress: float, marker_extent: float, gap: float) -> Dictionary:
	var count: int = extents.size()
	if count == 0:
		return {"start": 0, "end": 0, "prefix_hidden": false, "suffix_hidden": false, "used_extent": 0.0}
	var prefix: Array[float] = [0.0]
	for extent: float in extents:
		prefix.append(prefix[-1] + extent)
	var full_extent: float = prefix[count] + gap * maxi(0, count - 1)
	if full_extent <= available + 0.01:
		return {"start": 0, "end": count, "prefix_hidden": false, "suffix_hidden": false, "used_extent": full_extent}
	var position: float = clampf(progress, 0.0, 1.0)
	var focus: int = clampi(roundi((1.0 - position) * float(count - 1)), 0, count - 1)
	var best: Dictionary = {}
	var best_count: int = -1
	var best_distance: float = INF
	var end: int = count
	for start: int in range(focus, -1, -1):
		while end > focus + 1 and _used_extent(prefix, count, start, end, marker_extent, gap) > available + 0.01:
			end -= 1
		while end < count and _used_extent(prefix, count, start, end + 1, marker_extent, gap) <= available + 0.01:
			end += 1
		var used: float = _used_extent(prefix, count, start, end, marker_extent, gap)
		if used > available + 0.01:
			continue
		var visible_count: int = end - start
		var center: float = (float(start) + float(end - 1)) / 2.0
		var distance: float = absf(center - float(focus))
		var prefer: bool = visible_count > best_count or (visible_count == best_count and distance < best_distance - 0.01)
		if not prefer and visible_count == best_count and is_equal_approx(distance, best_distance):
			prefer = start > int(best.get("start", -1)) if position <= 0.5 else start < int(best.get("start", count))
		if prefer:
			best_count = visible_count
			best_distance = distance
			best = {"start": start, "end": end, "prefix_hidden": start > 0, "suffix_hidden": end < count, "used_extent": used}
	if not best.is_empty():
		return best
	# Supported P1 clue gutters always fit a token plus both markers. Keep a
	# deterministic atomic token for defensive callers instead of slicing text.
	var marker_count: int = int(focus > 0) + int(focus + 1 < count)
	return {"start": focus, "end": focus + 1, "prefix_hidden": focus > 0, "suffix_hidden": focus + 1 < count,
		"used_extent": extents[focus] + marker_extent * marker_count + gap * marker_count}

static func _used_extent(prefix: Array[float], count: int, start: int, end: int, marker_extent: float, gap: float) -> float:
	var prefix_hidden: bool = start > 0
	var suffix_hidden: bool = end < count
	var units: int = end - start + int(prefix_hidden) + int(suffix_hidden)
	return prefix[end] - prefix[start] + marker_extent * (int(prefix_hidden) + int(suffix_hidden)) + gap * maxi(0, units - 1)
