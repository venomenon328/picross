extends RefCounted
## Real delayed viewport tooltips; no direct calls to tooltip factories.
const ButtonType = preload("res://ui/book_button.gd")
const TipType = preload("res://ui/book_tooltip.gd")
var proof: SceneTree
var rows: Array = []
var delay: float

class OldButton extends ButtonType:
	func _make_custom_tooltip(for_text: String) -> Object:
		var tip := TipType.new()
		tip.configure(for_text,ui_scale,get_viewport_rect().size.x,get_theme_font("font"))
		tooltip_ref=weakref(tip)
		return tip
	func _draw() -> void:
		super._draw()
		if is_hovered(): draw_line(Vector2(9,8)*ui_scale,Vector2(18,8)*ui_scale,INK,1.5*ui_scale,true)

func move(point: Vector2) -> void:
	Input.warp_mouse(point)
	var event := InputEventMouseMotion.new()
	event.position = point
	proof.root.push_input(event,true)
	await proof.frames()

func current(control: Control) -> Control:
	var ref: WeakRef = control.get("tooltip_ref")
	if ref == null: return null
	var tip: Control = ref.get_ref()
	if tip == null or not tip.is_inside_tree() or not tip.get_window().visible: return null
	return tip

func hover(control: Control, label: String, expected: String, capture: bool = true) -> Control:
	var catalog = proof.study.app.album
	if catalog.visible and (catalog.scroll.is_ancestor_of(control) or catalog.right_scroll.is_ancestor_of(control)):
		catalog.ensure_control_visible(control)
		await proof.frames()
	await move(Vector2(2,proof.root.size.y/2))
	await move(control.get_global_rect().get_center())
	await proof.create_timer(delay+0.15).timeout
	await proof.frames()
	var tip: Control = current(control)
	var ok: bool = tip == null if expected.is_empty() else tip != null
	var row: Dictionary = {"case":label,"width":proof.root.size.x,"scale":proof.study.app.ui_scale,"caption":expected,"wait_seconds":delay+0.15,"visible":tip != null}
	if tip != null:
		var text: Label = tip.get_child(0)
		var rect := Rect2i(tip.get_window().position,tip.get_window().size)
		ok = ok and text.text == expected and rect.size.x >= text.get_combined_minimum_size().x
		ok = ok and text.size.y >= text.get_minimum_size().y and Rect2i(Vector2i.ZERO,proof.root.size).encloses(rect)
		row.merge({"popup":[rect.position.x,rect.position.y,rect.size.x,rect.size.y],"label":[text.size.x,text.size.y],"text":text.text})
	proof.check(ok,"delayed tooltip "+label+"/%d" % proof.root.size.x)
	rows.append(row)
	if capture: await proof.screenshot("tooltip-"+label+"-%d" % proof.root.size.x)
	return tip

func dismissed(control: Control, label: String) -> void:
	await proof.frames()
	proof.check(current(control) == null,"tooltip dismissed "+label)
	rows.append({"case":"dismiss-"+label,"visible":current(control) != null})

func run(context: SceneTree) -> Array:
	proof=context
	delay=float(ProjectSettings.get_setting("gui/timers/tooltip_delay_sec",0.5))
	proof.check(delay >= 0.5,"native tooltip delay is not bypassed")
	for configuration: Array in proof.Current.CONFIGURATIONS:
		proof.root.size=configuration[0]
		proof.study.set_ui_scale(configuration[1])
		proof.study.app.show_album()
		await proof.frames(6)
		var catalog = proof.study.app.album
		var footer: Array = [catalog.next_button]
		for b: Node in catalog.find_children("*","Button",true,false):
			if b.text in ["Einstellungen / Info","Beenden"]: footer.append(b)
		proof.check(footer.size()==3,"three fully captioned footer controls %d" % proof.root.size.x)
		for index: int in range(footer.size()):
			await hover(footer[index],"footer-%d" % index,"")
		var next: Control=footer[0]
		next.tooltip_text=" \t\n "
		await hover(next,"whitespace","")
		next.tooltip_text=""
		var direction: Control=catalog.direction_button
		await hover(direction,"direction",direction.tooltip_text)
		var reset: Control=catalog.choices[1].reset
		await hover(reset,"reset",reset.tooltip_text)
		await dismissed(direction,"switch-%d" % proof.root.size.x)
		var mode: Control=catalog.choices[0].mode_tip
		await hover(mode,"mode",mode.tooltip_text)
		await move(Vector2(2,2))
		await dismissed(mode,"leave-%d" % proof.root.size.x)
		await hover(direction,"click-before",direction.tooltip_text,false)
		var point: Vector2=direction.get_global_rect().get_center()
		proof.button(true,point)
		proof.button(false,point)
		await dismissed(direction,"click-%d" % proof.root.size.x)
		await hover(direction,"caption-after-click",direction.tooltip_text)
		# Restore sort before later original fixture assertions.
		catalog.reverse_sort()
		await move(Vector2(2,2))
		proof.study.request_open("T-06")
		proof.study.interrupt("focus")
		await proof.frames(6)
		for id: String in ["fill","help"]:
			var control: Control=proof.study.app.actions[id]
			await hover(control,id,control.tooltip_text)
		# Long current caption at the right edge exercises wrapping and bounds.
		var help: Control=proof.study.app.actions.help
		var original: String=help.tooltip_text
		help.tooltip_text="Diese Hilfebeschreibung prüft die aktuelle mehrzeilige Beschriftung am rechten Fensterrand bei unveränderter UI-Skalierung."
		await hover(help,"wrapped-edge",help.tooltip_text)
		help.tooltip_text=original
		await move(Vector2(2,2))
		proof.study.app.show_album()
		await proof.frames()
	# Lifecycle at the existing 1920 configuration, separate from motion matrix.
	proof.root.size=Vector2i(1920,1080)
	proof.study.set_ui_scale(1.0)
	await proof.frames(6)
	for reason: String in ["resize","ui-scale","focus","motion-start"]:
		var direction: Control=proof.study.app.album.direction_button
		await hover(direction,"before-"+reason,direction.tooltip_text,false)
		if reason=="resize": proof.root.size+=Vector2i(8,0)
		elif reason=="ui-scale": proof.study.set_ui_scale(1.25)
		elif reason=="focus": proof.study.app._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		else: proof.study.request_page(1)
		await dismissed(direction,reason)
		if reason=="motion-start":
			while proof.study.state in [proof.Study.State.PREPARING,proof.Study.State.OPENING]: await proof.process_frame
			await proof.frames()
			await dismissed(direction,"motion-end-no-revival")
			await hover(direction,"after-motion",direction.tooltip_text)
		proof.root.size=Vector2i(1920,1080)
		proof.study.set_ui_scale(1.0)
		proof.study.app.album.commit_page(0)
		await proof.frames(6)
	await negative_controls()
	await move(Vector2(2,2))
	return rows

func negative_controls() -> void:
	# Restore both old defects in a test-only subclass, using native hover delay.
	var old := OldButton.new()
	old.theme=proof.study.app.theme
	old.text="Probe"
	old.action_id="n03-hover-counterexample"
	old.paper_transparent=true
	old.position=Vector2(20,20)
	old.size=Vector2(150,54)
	proof.root.add_child(old)
	await move(old.get_global_rect().get_center())
	await proof.create_timer(delay+0.15).timeout
	await proof.frames()
	var tip: Control=current(old)
	var empty_popup: bool=tip != null and tip.get_child(0).text.is_empty()
	proof.check(empty_popup,"negative empty tooltip reproduced by native hover")
	await proof.screenshot("tooltip-negative-empty")
	old.dismiss_tooltip()
	old.free()
	await proof.frames()
	# Native transparent capture, same control identity and pointer path.
	var viewport := SubViewport.new()
	viewport.size=Vector2i(160,64)
	viewport.transparent_bg=true
	viewport.disable_3d=true
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	proof.root.add_child(viewport)
	var counts: Array[int]=[]
	for legacy: bool in [false,true]:
		var control: Control=OldButton.new() if legacy else ButtonType.new()
		control.theme=proof.study.app.theme
		control.action_id="n03-hover-counterexample"
		control.text="Probe"
		control.paper_transparent=true
		control.size=Vector2(150,54)
		viewport.add_child(control)
		var motion := InputEventMouseMotion.new()
		motion.position=Vector2(70,25)
		viewport.push_input(motion,true)
		await proof.frames()
		var img: Image=viewport.get_texture().get_image()
		img.save_png(proof.output.path_join("hover-negative.png" if legacy else "hover-current.png"))
		var count: int=0
		for y: int in range(7,10):
			for x: int in range(10,18):
				if img.get_pixel(x,y).a>0.4: count+=1
		counts.append(count)
		control.free()
	proof.check(counts[0]==0 and counts[1]>=8,"negative detached hover stroke rejected")
	rows.append({"case":"negative-controls","empty_popup":empty_popup,"current_detached_pixels":counts[0],"legacy_detached_pixels":counts[1]})
	viewport.queue_free()
