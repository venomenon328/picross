extends RefCounted
## B-A-N04 targeted native evidence; no fourth copy of the full UI matrix.
var p: SceneTree
var rows: Dictionary = {"counts":[],"scroll":[],"boundaries":[],"clips":[]}

func pair() -> Array:
	var c = p.study.app.album
	return [c.scroll.scroll_vertical,c.right_scroll.scroll_vertical]

func record(label: String, before: Array) -> void:
	rows.scroll.append({"case":label,"before":before,"after":pair()})

func wheel(half: ScrollContainer, down: bool = true) -> void:
	var point: Vector2 = half.get_global_rect().get_center()
	p.button(true,point,MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP)
	p.button(false,point,MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP)
	await p.frames(1)

func drag(half: ScrollContainer) -> void:
	var bar: VScrollBar = half.get_v_scroll_bar()
	var rect: Rect2 = bar.get_global_rect()
	var point := Vector2(rect.get_center().x,rect.position.y+rect.size.y*bar.page/bar.max_value/2)
	p.button(true,point)
	var move := InputEventMouseMotion.new()
	move.position = point+Vector2(0,72)
	move.relative = Vector2(0,72)
	move.button_mask = MOUSE_BUTTON_MASK_LEFT
	p.root.push_input(move,true)
	p.button(false,move.position)
	await p.frames(1)

func run(proof: SceneTree) -> Dictionary:
	p = proof
	var app = p.study.app
	var c = app.album
	p.root.size = Vector2i(1920,1200)
	p.study.set_ui_scale(1.0)
	app.show_album()
	c.commit_page(0)
	await p.frames()
	# Small sets exercise the real pagination/render path, never copied fixtures.
	for count: int in [0,1,12,13,24,27]:
		c.present(app.sessions.slice(0,count),app.slot_status.slice(0,count),app.slot_errors.slice(0,count),"","")
		for page: int in range(maxi(1,ceili(count/24.0))):
			c.commit_page(page)
			await p.frames(1)
			var expected: Array = app.sessions.slice(page*24,mini(count,(page+1)*24)).map(func(s: RefCounted) -> String: return s.definition.id)
			var left: int = mini(12,expected.size())
			var right: int = maxi(0,expected.size()-12)
			p.check(c.visible_ids == expected and c.grid.get_child_count() == left and c.right_grid.get_child_count() == right,"N04 left-first %d/%d" % [count,page])
			for i: int in range(c.choices.size()):
				p.check((c.grid if i < 12 else c.right_grid).is_ancestor_of(c.choices[i]),"N04 stable half %d/%d/%d" % [count,page,i])
			rows.counts.append({"count":count,"page":page,"left":left,"right":right,"ids":c.visible_ids.duplicate()})
	app.show_album()
	c.commit_page(0)
	await p.frames()
	var before: Array = pair()
	await wheel(c.scroll)
	p.check(pair()[0] > before[0] and pair()[1] == before[1],"N04 wheel left owns offset")
	record("wheel-left",before)
	before = pair()
	await wheel(c.right_scroll)
	await wheel(c.right_scroll)
	p.check(pair()[0] == before[0] and pair()[1] > before[1] and pair()[0] != pair()[1],"N04 wheel right owns offset")
	record("wheel-right",before)
	# Thumb motion is a separate real input route from wheel input.
	for half: ScrollContainer in [c.scroll,c.right_scroll]:
		half.scroll_vertical = 0
		await p.frames(1)
		before = pair()
		await drag(half)
		var side: int = 0 if half == c.scroll else 1
		p.check(pair()[side] > before[side] and pair()[1-side] == before[1-side],"N04 scrollbar owns half %d" % side)
		record("bar-left" if side == 0 else "bar-right",before)
	before = pair()
	c.ensure_control_visible(c.choices[23])
	await p.frames(1)
	p.check(pair()[0] == before[0] and pair()[1] > before[1],"N04 ensure-visible right only")
	record("ensure-right",before)
	before = pair()
	await wheel(c.right_scroll)
	p.check(pair() == before,"N04 right range edge does not forward")
	record("right-edge",before)
	c.ensure_control_visible(c.choices[11])
	await p.frames(1)
	p.check(pair()[1] == before[1],"N04 ensure-visible left only")
	# A native click from each independently scrolled half, edit, return.
	for index: int in [14,2]:
		c.commit_page(0,91,173)
		await p.frames()
		c.ensure_control_visible(c.choices[index])
		await p.frames()
		before = pair()
		var id: String = c.visible_ids[index]
		var point: Vector2 = c.choices[index].get_global_rect().intersection((c.right_scroll if index >= 12 else c.scroll).get_global_rect()).get_center()
		p.button(true,point)
		p.button(false,point)
		p.check(p.study.selected_id == id and p.study.return_context.scroll == before[0] and p.study.return_context.right_scroll == before[1],"N04 click captures both before await %d" % index)
		p.study.interrupt("focus")
		await p.frames()
		var cell: Vector2 = app.board.global_position+app.board.view.origin+Vector2(7.5,7.5)*app.board.view.cell_size
		var cursor: int = app.session.player.cursor
		p.button(true,cell)
		p.button(false,cell)
		await p.frames()
		p.check(app.session.player.cursor == cursor+1,"N04 edited selected ID %d" % index)
		p.check(p.study.request_return(),"N04 return accepted %d" % index)
		p.study.interrupt("focus")
		await p.frames()
		p.check(pair() == before and app.session.definition.id == id and c.previews[index].cells == app.session.player.cells,"N04 return preserves both and progress %d" % index)
		record("return-right" if index >= 12 else "return-left",before)
	before = pair()
	app.show_album()
	await p.frames()
	p.check(pair() == before,"N04 redisplay preserves right property")
	c.choose_category(c.category_id)
	c.choose_sort(c.preference.criterion)
	await p.frames(1)
	p.check(pair() == before,"N04 filter sort no-op preserves both")
	record("no-op",before)
	for action: String in ["filter","sort","reverse"]:
		c.commit_page(0,91,173)
		await p.frames(1)
		if action == "filter": c.choose_category("technical")
		elif action == "sort": c.choose_sort("size")
		else: c.reverse_sort()
		await p.frames(1)
		p.check(c.page_index == 0 and pair() == [0,0],"N04 true change resets both "+action)
		rows.scroll.append({"case":"reset-"+action,"after":pair()})
	c.choose_category("")
	c.choose_sort("category")
	c.present(app.sessions.slice(0,12),app.slot_status.slice(0,12),app.slot_errors.slice(0,12),"","")
	c.commit_page(0)
	await p.frames()
	c.scroll.scroll_vertical = 80
	before = pair()
	await wheel(c.right_scroll)
	p.check(pair() == before and before == [80,0] and c.right_grid.get_child_count() == 0,"N04 empty right does not forward")
	record("empty-right",before)
	app.show_album()
	c.commit_page(0)
	await p.frames()
	await p.screenshot("catalog-1920x1200")
	await p.measure_ink(false)
	for half: ScrollContainer in [c.scroll,c.right_scroll]:
		var side: int = -1 if half == c.scroll else 1
		var paper: Rect2 = p.study.projected_paper(false,side)
		var safe: Rect2 = paper
		if side == 1: safe.position.x += paper.size.x*0.075
		safe.size.x -= paper.size.x*0.075
		var rect: Rect2 = half.get_global_rect()
		p.check(safe.encloses(rect.grow(8)),"N04 card clipping stays on flat paper %d" % side)
		rows.clips.append({"side":side,"rect":[rect.position.x,rect.position.y,rect.size.x,rect.size.y]})
	p.root.size = Vector2i(1280,720)
	p.study.set_ui_scale(1.25)
	await p.frames()
	c.scroll.scroll_vertical = 91
	c.right_scroll.scroll_vertical = int(c.right_scroll.get_v_scroll_bar().max_value)
	before = pair()
	p.root.size = Vector2i(1920,1200)
	p.study.set_ui_scale(1.0)
	await p.frames()
	var limit: int = int(c.right_scroll.get_v_scroll_bar().max_value-c.right_scroll.get_v_scroll_bar().page)
	p.check(pair()[0] == 91 and pair()[1] == limit and limit < before[1],"N04 resize clamps each half independently")
	rows.scroll.append({"case":"resize-clamp","before":before,"after":pair(),"right_limit":limit})
	# Neighboring ratios/UI125: cheap geometry, no duplicated tooltip suite.
	for configuration: Array in [[1920,1200,1.25],[1920,1192,1.0],[1920,1208,1.0],[1920,1088,1.0]]:
		c.scroll.scroll_vertical = 91
		c.right_scroll.scroll_vertical = 173
		p.root.size = Vector2i(configuration[0],configuration[1])
		p.study.set_ui_scale(configuration[2])
		await p.frames()
		var minimum: float = INF
		for control: Control in [app.title,c.summary,c.previous_button,c.next_button,c.category_choice,c.sort_choice,c.direction_button]:
			var side: int = -1 if control.get_global_rect().get_center().x < p.root.size.x/2.0 else 1
			var paper: Rect2 = p.study.projected_paper(false,side)
			var rect: Rect2 = control.get_global_rect().grow(3)
			minimum = minf(minimum,minf(rect.position.y-paper.position.y,paper.end.y-rect.end.y))
		var valid: bool = true
		for half: ScrollContainer in [c.scroll,c.right_scroll]:
			var bar: VScrollBar = half.get_v_scroll_bar()
			valid = valid and half.scroll_vertical >= 0 and half.scroll_vertical <= maxf(0,bar.max_value-bar.page)
		p.check(minimum >= 8 and valid and pair() == [91,173],"N04 boundary geometry %s" % [configuration])
		rows.boundaries.append({"width":configuration[0],"height":configuration[1],"scale":configuration[2],"margin":minimum,"offsets":pair()})
	p.root.size = Vector2i(1920,1200)
	p.study.set_ui_scale(1.0)
	c.commit_page(0,91,173)
	await p.frames()
	p.study.request_open("T-06")
	p.study.interrupt("focus")
	await p.frames()
	await p.screenshot("work-1920x1200")
	await p.measure_ink(true)
	p.check(p.study.request_return(),"N04 targeted return starts")
	while p.study.state == p.Study.State.PREPARING: await p.process_frame
	p.study.set_process(false)
	p.study._pose(1)
	await p.screenshot("return-handoff-texture-1920x1200")
	p.study._settle(true)
	p.study.set_process(true)
	await p.screenshot("return-handoff-direct-1920x1200")
	p.handoffs.append({"configuration":[p.root.size,1.0],"texture":"return-handoff-texture-1920x1200.png","direct":"return-handoff-direct-1920x1200.png"})
	c.commit_page(0)
	p.root.size = Vector2i(1920,1080)
	await p.frames()
	return rows
