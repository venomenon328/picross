extends "res://model/save_store.gd"
const Catalog = preload("res://full_view_study/catalog.gd")

func registered_ids() -> Array[String]:
	return Catalog.IDS

func key_for_definition(id: String) -> String:
	return id.to_lower().replace("-", "")

func slot_for_key(id: String) -> String:
	return id
