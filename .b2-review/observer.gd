extends Node
## Read-only geometry and progress for an isolated technical build.
var elapsed := 0.0
var last := ""
func _process(delta: float) -> void:
	elapsed += delta
	if elapsed < 0.25: return
	elapsed = 0
	var book = get_tree().current_scene
	if book == null or not "app" in book or not is_instance_valid(book.app): return
	var app = book.app
	if not app.is_inside_tree() or app.accounts == null: return
	var dlg = app.accounts.dialog
	var points := {}
	point(points,"settings",app.album.settings_button)
	point(points,"retry",app.account_retry)
	point(points,"recent-retry",app.recent_retry)
	point(points,"help",app.album.help_button)
	point(points,"back",app.album_button)
	point(points,"undo",app.undo_button)
	point(points,"redo",app.redo_button)
	point(points,"scale",app.ui_scale_choice)
	var menu: PopupMenu = app.ui_scale_choice.get_popup()
	if menu.visible:
		var last_item := Vector2(menu.position)+Vector2(menu.size)*Vector2(0.5,0.75)
		points["scale125"] = [last_item.x,last_item.y]
	if app.info: point(points,"info-back",app.info.right_return)
	for b in app.settings_panel.find_children("*","Button",true,false):
		if b.text == "Konto verwalten": point(points,"manage",b)
	if dlg.visible:
		point(points,"username",dlg.username)
		point(points,"password",dlg.password)
		for b in dlg.find_children("*","Button",true,false):
			if b.text in ["Anmelden","Abmelden"]: point(points,b.text,b)
			if b.text.ends_with(" lokal öffnen"): point(points,"open-local",b)
	var ids := []
	for card in app.album.choices:
		if is_instance_valid(card) and card.is_visible_in_tree() and app.album.scroll.get_global_rect().intersects(card.get_global_rect()):
			point(points,"puzzle/"+card.action_id,card)
			ids.append(card.action_id)
	var st := {"points":points,"locked":app.presentation_locked,"hover":[app.board.hover.x,app.board.hover.y] if app.board else [],"state":int(book.state),"status":app.account_status.text,"ids":ids,"scale":app.ui_scale,
		"size":[app.size.x,app.size.y],"busy":app.accounts.transport_busy or app.accounts.changing,
		"ready":app.accounts.inventory_ready,"profile":app.account_profile != null,
		"confirmed":app.account_profile.flush_confirmed() if app.account_profile else false,
		"font":app.account_status.get_theme_font("font").get_font_name(),"font_size":app.account_status.get_theme_font_size("font_size"),
		"status_rect":rect(app.account_status.get_global_rect()),"summary_rect":rect(app.album.summary.get_global_rect())}
	if app.session != null:
		st.id = app.session.definition.id
		st.cursor = app.session.player.cursor
		st.history = app.session.player.history.size()
		st.baseline = app.session.account_baseline.get("cells",[]).slice(0,5)
		st.cells = app.session.player.cells.slice(0,5)
		if app.work.visible and app.board.layout_valid and not app.presentation_locked:
			for i in range(3):
				var pixel: Vector2 = app.board.get_global_transform() * app.board.view.cell_rect(Vector2i(i,0)).get_center()
				points["cell"+str(i)] = [pixel.x,pixel.y]
	if not OS.has_feature("web"):
		var request := OS.get_environment("B2_OBSERVATION")+".png.request"
		if FileAccess.file_exists(request):
			get_viewport().get_texture().get_image().save_png(request.trim_suffix(".request"))
			DirAccess.remove_absolute(request)
	if dlg.visible:
		st.name_length = dlg.username.text.length()
		st.password_length = dlg.password.text.length()
	st.release_barrier = book.release_barrier
	st.transport = app.accounts.transport_busy
	st.changing = app.accounts.changing
	st.http_nodes = app.accounts.transport.get_child_count()
	st.active_device_sequence = app.accounts.profile._state.get("sequence") if app.accounts.profile else null
	var raw := JSON.stringify(st)
	if raw == last: return
	last = raw
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.b2Observation="+raw,true)
	else:
		var dest := OS.get_environment("B2_OBSERVATION")
		if dest != "":
			var file := FileAccess.open(dest,FileAccess.WRITE)
			if file: file.store_string(raw)

func rect(box: Rect2) -> Array: return [box.position.x,box.position.y,box.size.x,box.size.y]
func point(items: Dictionary, key: String, item: Control) -> void:
	if item == null or not item.is_visible_in_tree(): return
	var pos := item.get_global_rect().get_center()
	var win := item.get_window()
	if win != get_tree().root:
		if not win.visible: return
		pos += Vector2(win.position)
	items[key] = [pos.x,pos.y]
