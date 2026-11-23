extends RefCounted
## Pointer input through the real account dialogs with deterministic service replies.
const Session = preload("res://model/session.gd")
const Profile = preload("res://model/account_profile.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const ACCOUNT := "f0000001-0000-4000-8000-000000000001"
const DEVICE := "f0000002-0000-4000-8000-000000000002"
const OTHER := "f0000003-0000-4000-8000-000000000003"
const GENERATION := "f0000004-0000-4000-8000-000000000004"
const CANDIDATE := "f0000005-0000-4000-8000-000000000005"
const STAMP := "2026-11-23T12:00:00Z"

class Service extends "res://model/sync_transport.gd":
	var rows := {}
	var requests: Array[String] = []

	func send(_server: String, path: String, method: int, _raw: String, _identity: Dictionary) -> Dictionary:
		requests.append("%d %s" % [method,path])
		await get_tree().process_frame
		var found: bool = rows.has(path)
		return {"status":200 if found else 404,"generation":GENERATION,"retry_after":0,
			"body":rows.get(path,{"code":"not_found"}).duplicate(true)}

static func version(id: String, rev: int, raster: int, device: String, label: String, save: Variant) -> Dictionary:
	return {"puzzle_id":id,"definition_revision":raster,"kind":"reset" if save == null else "snapshot",
		"device_id":device,"device_name":label,"server_revision":float(rev),"updated_at":STAMP,
		"save":save,"validation":null if save == null else "progress_structure_checked"}

static func visible_window(parent: Window) -> AcceptDialog:
	for child: Node in parent.get_children():
		if child is AcceptDialog and child.visible: return child
	return null

static func label_text(parent: Node, label_name: String) -> String:
	var label := parent.find_child(label_name,true,false) as Label
	return label.text if label != null and label.is_visible_in_tree() else ""

static func capture(r: SceneTree, directory: String, name: String, scale: int) -> Dictionary:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(directory)
	var path := directory.path_join(name)
	var frame: Image = r.surface.get_texture().get_image()
	r.check(frame != null and frame.save_png(path) == OK,"B2 comparison rendered original "+name)
	var file := FileAccess.open(path,FileAccess.READ)
	return {"file":name,"width":r.surface.size.x,"height":r.surface.size.y,"ui_scale_percent":scale,
		"bytes":file.get_length() if file else 0,"sha256":FileAccess.get_sha256(path)}

static func run(r: SceneTree) -> void:
	var app: Control = r.app
	var client: Node = app.accounts
	var server := "https://comparison-test.invalid"
	var profile := Profile.new()
	if not profile.open(server,ACCOUNT,DEVICE,GENERATION,true):
		r.check(false,"B2 comparison isolated account profile opens")
		return
	var transport: Node = client.transport
	var fixture := Service.new()
	client.add_child(fixture)
	client.transport = fixture
	client.access.server = server
	client.bind(profile,{"server":server,"account_id":ACCOUNT,"device_id":DEVICE,"generation":GENERATION,
		"username":"vergleich-test","token":"","expires_at":"2027-01-01T12:00:00"})
	var slot: Session = app.sessions[0]
	var id: String = slot.definition.id
	var raster: int = slot.definition.revision
	var root := "/v1/puzzles/"+id
	slot.player.commit([{"index":0,"before":-1,"after":1}])
	r.check(profile.save(slot,slot.view_state)>0,"B2 comparison has actual local account progress")
	app.slot_status[0] = "loaded"
	var progress := Protocol.progress(profile._store.slot_snapshot(slot,slot.view_state))
	progress.cells[1] = 0
	var remote := version(id,9,raster,DEVICE,"Windows",progress)
	var candidate := version(id,6,raster,OTHER,"Windows",progress.duplicate(true))
	candidate.save.cells[2] = 1
	candidate.erase("server_revision")
	candidate.erase("updated_at")
	candidate.merge({"candidate_id":CANDIDATE,"base_server_revision":6.0,"created_at":STAMP})
	var past := version(id,7,raster-1,OTHER,"Reiselaptop mit besonders langem Namen für den Fassungsvergleich",null)
	fixture.rows = {root:remote,root+"/conflicts":{"items":[candidate],"next_cursor":null},
		root+"/history":{"items":[past],"next_cursor":null},root+"/conflicts/"+CANDIDATE:candidate,root+"/history/7":past}
	var local_version: int = profile.status().local
	var dialog: AcceptDialog = client.dialog
	var captures := []
	var review_directory := OS.get_environment("KAT2_SYNC_B2_REVIEW_DIR")
	for scale: int in [100,125]:
		r.surface.size = Vector2i(1920,1080) if scale == 100 else Vector2i(1280,720)
		app.set_ui_scale(float(scale)/100)
		await r.frames()
		if not app.information.visible: r.click(app.album.settings_button)
		await r.frames()
		var manage: Button = r.caption_button(app.information,"Konto verwalten")
		app.info_scroll.ensure_control_visible(manage)
		await r.frames()
		r.click(manage)
		await r.frames()
		r.check(dialog.visible,"B2 comparison account settings open by pointer")
		r.click(r.caption_button(dialog,"Konflikte und Versionen"))
		await r.frames()
		await r.frames()
		var listing := visible_window(dialog)
		r.check(listing != null,"B2 comparison list opens by pointer")
		if listing == null: return
		r.click(r.caption_button(listing,"Konflikt 1 vergleichen" if scale == 100 else "Version 7 vergleichen"))
		await r.frames()
		await r.frames()
		var comparison := visible_window(listing)
		r.check(comparison != null,"B2 comparison detail opens by pointer")
		if comparison == null: return
		var scroll := comparison.find_children("*","ScrollContainer",true,false)[0] as ScrollContainer
		for summary: String in ["LocalSummary","ServerSummary","ChoiceSummary"]:
			var label := comparison.find_child(summary,true,false) as Label
			r.check(label != null and scroll.get_global_rect().grow(1).encloses(label.get_global_rect()),"B2 all three summaries fit before choice at UI%d: %s" % [scale,summary])
		var local := label_text(comparison,"LocalSummary")
		var current := label_text(comparison,"ServerSummary")
		var selected := label_text(comparison,"ChoiceSummary")
		r.check(local.contains("1 ausgefüllt · 0 als leer markiert") and current.contains("Windows · Gerätekennung f0000002 · dieses Gerät") and current.contains("1 ausgefüllt · 1 als leer markiert"),"B2 comparison displays separate local and current server progress")
		r.check(not (local+current+selected).contains(str(slot.definition.reveal.name)) and profile.status().local == local_version,"B2 comparison contains no motive and never journals a choice by opening")
		if scale == 125:
			r.check(selected.contains("Reiselaptop") and selected.contains("inkompatibel") and selected.contains("Zurückgesetzt") and not comparison.find_children("*","Button",true,false).any(func(b: Button) -> bool: return b.text == "Diese Version wiederherstellen"),"B2 incompatible reset stays understandable and cannot be restored")
			if not review_directory.is_empty(): captures.append(await capture(r,review_directory,"history-reset-ui125.png",scale))
			r.click(comparison.get_ok_button())
			await r.frames()
			r.check(visible_window(listing) == null and profile.status().local == local_version,"B2 back leaves all choices untouched")
			fixture.rows[root] = version(id,9,raster,DEVICE,"Windows",null)
			r.click(r.caption_button(listing,"Konflikt 1 vergleichen"))
			await r.frames()
			await r.frames()
			comparison = visible_window(listing)
			r.check(comparison != null and label_text(comparison,"ServerSummary").contains("Zurückgesetzt"),"B2 current server reset displays as an empty stand")
			if comparison == null: return
			r.click(r.caption_button(comparison,"Kandidatenfassung verwerfen"))
			await r.frames()
			await r.frames()
			var journal: Dictionary = profile.status()
			var entry: Dictionary = journal.entries.get(str(local_version+1),{})
			r.check(journal.local == local_version+1 and entry.get("operation") == "discard" and entry.get("value") == CANDIDATE and entry.get("base_server_revision") == 9,"B2 explicit current comparison journals exactly the bound choice")
			r.click(dialog.get_ok_button())
			await r.frames()
		else:
			r.check(selected.contains("Windows · Gerätekennung f0000003") and selected.contains("2 ausgefüllt · 1 als leer markiert"),"B2 candidate shows distinct device and progress before a choice")
			if not review_directory.is_empty(): captures.append(await capture(r,review_directory,"conflict-ui100.png",scale))
			var discard: Button = r.caption_button(comparison,"Kandidatenfassung verwerfen")
			candidate.candidate_id = OTHER
			r.click(discard)
			await r.frames()
			await r.frames()
			r.check(comparison.visible and client.problem.contains("nicht mehr verfügbar") and profile.status().local == local_version,"B2 readback refuses the wrong candidate and preserves selection")
			candidate.candidate_id = CANDIDATE
			remote.server_revision = 10.0
			var reads: int = fixture.requests.size()
			r.click(discard)
			await r.frames()
			await r.frames()
			r.check(comparison.visible and fixture.requests.size() == reads+1 and client.problem.contains("Serverstand geändert") and profile.status().local == local_version,"B2 changed base stops before detail and preserves selection")
			remote.server_revision = 9.0
			r.click(comparison.get_ok_button())
			await r.frames()
			r.click(listing.get_ok_button())
			await r.frames()
			r.click(dialog.get_ok_button())
			await r.frames()
	if not review_directory.is_empty():
		var proof := {"source_head":OS.get_environment("P1_PREFLIGHT_SOURCE_COMMIT"),
			"base_commit":OS.get_environment("P1_BASE_COMMIT"),"tested_checkout":OS.get_environment("GITHUB_SHA"),
			"run_id":OS.get_environment("GITHUB_RUN_ID"),"run_attempt":OS.get_environment("GITHUB_RUN_ATTEMPT"),
			"engine":Engine.get_version_info().string,"os":OS.get_name(),"display":DisplayServer.get_name(),"captures":captures,
			"scenario":"Synthetic account service replies, actual pointer input in the native book viewport. Stale base and wrong candidate rejected without journal mutation; explicit discard uses the confirmed basis and identity."}
		var out: FileAccess = FileAccess.open(review_directory.path_join("interaction.json"),FileAccess.WRITE)
		if out: out.store_string(JSON.stringify(proof,"\t")+"\n")
		r.check(out != null,"B2 comparison interaction original written")
	client.bind(null,{})
	client.transport = transport
	fixture.queue_free()
