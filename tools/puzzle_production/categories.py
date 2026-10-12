"""KAT-1 catalog metadata. Never part of puzzle, proof or save identity."""
import re

from .authoring_package import require
from .contract import exact_keys, integer, load_json

PATH = "content/categories.json"
FORMAT = "picross-categories-v1"
MAX_BYTES = 131072
MAX_CATEGORIES = 256
ID = re.compile(r"[a-z][a-z0-9-]{0,63}\Z", re.ASCII)


def validate(raw):
    exact_keys(raw, {"format", "categories"})
    require(raw["format"] == FORMAT, "Unsupported categories format")
    entries = raw["categories"]
    require(isinstance(entries, list) and len(entries) <= MAX_CATEGORIES,
            "Categories must be a list of at most 256 entries")
    ids, orders = set(), set()
    for entry in entries:
        exact_keys(entry, {"id", "name", "order"})
        identifier = entry["id"]
        require(isinstance(identifier, str) and ID.fullmatch(identifier), "Invalid category ID")
        require(identifier not in ids, "Duplicate category ID: " + identifier)
        ids.add(identifier)
        name = entry["name"]
        require(isinstance(name, str) and 1 <= len(name) <= 128 and name == name.strip()
                and all(ord(c) >= 32 and not 127 <= ord(c) <= 159 for c in name),
                "Category name must contain 1..128 printable characters")
        order = integer(entry["order"], 1, 10000, "category order")
        require(order not in orders, "Duplicate category order")
        orders.add(order)
    return raw


def load(path):
    return validate(load_json(path, MAX_BYTES))


def source_bytes(path):
    """Bound even the raw transaction snapshot and concurrent-change reads."""
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "Categories exceed 131072 byte limit")
    return data


def ordered(raw):
    return sorted(validate(raw)["categories"], key=lambda e: e["order"])


def lookup(raw, identifier):
    require(isinstance(identifier, str) and ID.fullmatch(identifier),
            "Exactly one explicit category_id is required")
    for entry in validate(raw)["categories"]:
        if entry["id"] == identifier:
            return entry
    require(False, "Unknown category_id: " + identifier)
