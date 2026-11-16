"""Portable PE image using the same pinned/audited builder as the MSI."""
import argparse
from pathlib import Path
from tools.app_products import PE
from tools.production_workspace.build_windows import build as shared_build

def build(output, *, version="0.2.1"):
    return shared_build(output, version=version, app=PE)

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--version", default="0.2.1")
    a=p.parse_args(); build(a.output, version=a.version)
