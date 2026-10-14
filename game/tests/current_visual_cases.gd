extends RefCounted
## Representative current layouts: tight/high UI, normal, large/high UI.
## Scope approved in #116; this is a coverage choice, not a runtime budget.
const CONFIGURATIONS: Array = [
	[Vector2i(1280, 720), 1.25],
	[Vector2i(1920, 1080), 1.0],
	[Vector2i(2560, 1440), 1.25],
]
