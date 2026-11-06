extends Node
## One transition at a time; only a verified explicit confirmation writes disk.
const Preference = preload("res://model/display_preference.gd")
const Policy = preload("res://model/display_policy.gd")
signal changed
var backend: RefCounted
var preference: RefCounted
var active: Dictionary = Preference.defaults()
var confirmed: Dictionary = {}
var saved: Dictionary = {}
var monitor: Dictionary = {}
var message: String = ""
var preview: bool = false
var applying: bool = false
var deadline: int = 0
var settle_deadline: int = 0
var settle_frames: int = 0
var fallback_stage: int = 0
var purpose: String = "start"
var poll_at: int = 0
var recovery_failed: bool = false
var last_second: int = -1

func start(server: RefCounted, storage: RefCounted) -> void:
	backend = server
	preference = storage
	saved = preference.load_selection()
	message = preference.error
	monitor = backend.context()
	_begin(saved,"start")

func seconds_left(now: int = Time.get_ticks_msec()) -> int:
	return maxi(0,ceili(float(deadline-now)/1000.0))

func _begin(selection: Dictionary, reason: String) -> void:
	purpose = reason
	applying = true
	settle_frames = 0
	settle_deadline = Time.get_ticks_msec()+1000
	active = backend.apply(selection)
	if active != selection:
		message = "Fenstergröße passt nicht in den Arbeitsbereich. Sichere Anzeige aktiv; gespeicherte Präferenz bleibt erhalten."
	changed.emit()

func request(mode: String, preset: String) -> void:
	if applying or preview or mode not in Preference.MODES or preset not in Preference.PRESETS: return
	if mode == "window" and preset not in Policy.available(backend.context()):
		message = "Diese Fenstergröße passt samt Rahmen nicht in den aktuellen Arbeitsbereich."
		changed.emit()
		return
	confirmed = active.duplicate()
	message = ""
	recovery_failed = false
	fallback_stage = 0
	_begin({"mode":mode,"preset":preset},"preview")

func matches() -> bool:
	var actual: Dictionary = backend.observed()
	if actual.mode != active.mode: return false
	if active.mode == "window":
		return actual.client == Preference.pixels(active.preset) and backend.context().usable.encloses(actual.outer)
	return actual.client == backend.context().desktop

func confirm() -> void:
	if not preview or applying: return
	if Time.get_ticks_msec() >= deadline:
		cancel()
		return
	if not matches():
		message = "Anzeige hat sich geändert. Vorherige Anzeige wird wiederhergestellt."
		cancel(false)
		return
	if not preference.save_selection(active):
		message = preference.error
		cancel(false)
		return
	saved = active.duplicate()
	confirmed = active.duplicate()
	preview = false
	message = "Anzeige gespeichert."
	changed.emit()

func cancel(clear_message: bool = true) -> void:
	if not preview: return
	preview = false
	if clear_message: message = "Vorherige Anzeige wiederhergestellt."
	fallback_stage = 0
	_begin(confirmed,"restore")

func _process(_delta: float) -> void:
	if backend == null: return
	advance(Time.get_ticks_msec())

func advance(now: int) -> void:
	if applying:
		settle_frames += 1
		if settle_frames < 3: return
		backend.settle(active)
		if matches():
			applying = false
			monitor = backend.context()
			if purpose == "preview":
				preview = true
				deadline = now+15000
			else: confirmed = active.duplicate()
			changed.emit()
		elif now >= settle_deadline:
			message = "Anzeigemodus nicht verfügbar. Sichere Anzeige wird wiederhergestellt."
			preview = false
			fallback_stage += 1
			# Prefer real borderless; if that fails, restore the prior working mode.
			if fallback_stage == 1:
				_begin({"mode":"borderless","preset":active.preset},"restore")
			elif fallback_stage == 2:
				_begin(confirmed if not confirmed.is_empty() else Preference.defaults(),"restore")
			else:
				# Keep retry available, and report observed state honestly in the UI.
				applying = false
				recovery_failed = true
				var actual: Dictionary = backend.observed()
				active.mode = actual.mode
				message = "Anzeige konnte nicht angewandt werden. Bitte eine andere Einstellung wählen."
				changed.emit()
		return
	if recovery_failed: return
	if preview:
		if now >= deadline: cancel()
		elif seconds_left(now) != last_second:
			last_second = seconds_left(now)
			changed.emit()
	if now < poll_at: return
	poll_at = now+500
	var actual: Dictionary = backend.observed()
	if actual.minimized: return # Alt-Tab alone neither accepts nor cancels.
	var current: Dictionary = backend.context()
	if current != monitor or not matches():
		monitor = current
		if preview:
			preview = false
			message = "Monitor oder Arbeitsbereich geändert. Vorherige Anzeige wird sicher wiederhergestellt."
			_begin(confirmed,"restore")
		else:
			_begin(active,"restore")
	else: backend.keep_visible(active)
