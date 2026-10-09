extends "res://model/save_store.gd"
const Catalog = preload("res://full_view_study/catalog.gd")

func registered_ids() -> Array[String]:
	return Catalog.IDS
