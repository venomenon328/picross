"""Actual PE MSI byte inspection; never installs."""
import argparse
from pathlib import Path
from tools.app_products import PE
from tools.production_workspace.verify_installer import verify

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--expected-commit",required=True)
    p.add_argument("--version",default="0.2.1")
    p.add_argument("--compare-build",action="store_true")
    p.add_argument("--wix-archive",type=Path)
    a=p.parse_args(); verify(a.build,a.output,a.expected_commit,a.wix_archive,a.compare_build,a.version,app=PE)
