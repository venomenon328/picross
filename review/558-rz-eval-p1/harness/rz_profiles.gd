extends "E:/Zeuch/Coding/picross_codex/558-rz-eval-p1/temp/rz_probe.gd"

func run() -> void:
	output = OS.get_environment("RZ_OUTPUT")
	DirAccess.make_dir_recursive_absolute(output)
	root.size = Vector2i(1280,720)
	surface = SubViewport.new()
	surface.size = Vector2i(2560,1440)
	surface.own_world_3d = true
	surface.gui_embed_subwindows = true
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames()
	for id: String in ["pz-c71563f1b8c940de998afdd62f09","pz-9d08697a30c749258b742ac979de9def"]:
		for entry: Array in [["1536","png"],["2304","png"],["3072","png"],["2304","webp"],["2304","q85.webp"],["2304","la.png"],["2304","nomips.png"]]:
			app.rz_eval.profile = entry[0]
			app.rz_eval.extension = entry[1]
			app.rz_eval.texture_filter = Control.TEXTURE_FILTER_LINEAR if entry[1] == "nomips.png" else Control.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
			await open_id(id,0)
			var label: String = Drawing.PILOTS[id]+"-"+entry[0]+"-"+entry[1]
			await snapshot(label+"-1440")
			resource_record(label+"-1440")
			if Drawing.PILOTS[id] == "basilisk":
				surface.size = Vector2i(3840,2160)
				await frames()
				await snapshot(label+"-4k")
				resource_record(label+"-4k")
				surface.size = Vector2i(2560,1440)
				await frames()
			await close_id()
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"renderer":RenderingServer.get_video_adapter_name(),"records":records,"failures":failures},"\t"))
	file.close()
	print("RZ_PROFILES_DONE failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
