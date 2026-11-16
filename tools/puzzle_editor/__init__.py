"""Offline editor, using the existing catalog writers. Protocol PE v1."""
VERSION = "0.2.0"

# Version injection is a packaged resource, never an environment/data-checkout value.
import json
import sys
from pathlib import Path
if getattr(sys, "frozen", False):
    VERSION = json.loads(Path(__file__).with_name("build.json").read_text(encoding="utf-8"))["version"]
