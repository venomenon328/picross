extends "res://book/main.gd"
## Technical export only. The real root and lifecycle construct the observer UI.
const Probe = preload("res://book/web_probe.gd")

func create_content() -> Content:
	return Probe.new()

func _process(delta: float) -> void:
	super._process(delta)
	# The UI is deliberately disabled while captured. Observe from the running
	# root so a browser cannot mistake a frozen old sample for settled controls.
	if app != null: app.observe(delta)
