extends "res://ui/main.gd"
## Developer-only corpus injection through the REGULAR scene/layout/input path.
const Catalog = preload("res://full_view_study/catalog.gd")
const CorpusStore = preload("res://full_view_study/save_store.gd")

func create_store() -> SaveStore:
	return CorpusStore.new(OS.get_user_data_dir().path_join("vs2-corpus-tests"))

func puzzle_definitions() -> Array[Dictionary]:
	return Catalog.definitions()

func validate_definition(data: Dictionary) -> String:
	return Catalog.validate(data)
