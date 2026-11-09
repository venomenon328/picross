extends SceneTree
func _initialize() -> void:
	var paths: Array = JSON.parse_string(OS.get_environment("RZ_PACK_PATHS"))
	var destination: String = OS.get_environment("RZ_PACK_EXTRACT")
	DirAccess.make_dir_recursive_absolute(destination)
	var rows: Array = []
	for path: String in paths:
		var config := ConfigFile.new()
		if config.load(path+".import") != OK: quit(5); return
		var imported: String = config.get_value("remap","path","")
		var data: PackedByteArray = FileAccess.get_file_as_bytes(imported)
		if data.is_empty(): quit(6); return
		var target: String = destination.path_join(path.get_file()+".ctex")
		var file := FileAccess.open(target,FileAccess.WRITE)
		file.store_buffer(data)
		file.close()
		rows.append({"source":path,"packed_import":imported,"file":target.get_file(),"bytes":data.size()})
	var file := FileAccess.open(destination.path_join("mapping.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(rows,"\t"))
	file.close()
	quit()
