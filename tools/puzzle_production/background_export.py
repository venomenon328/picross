"""Background variants use the same current exporter as every other input."""
from .integration_input import export as export_background, Input


def verify_background_export(directory):
    value=Input(directory)
    return value.value, {"status":"valid","id":value.entry["id"]}
