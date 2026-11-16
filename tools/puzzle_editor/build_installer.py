"""PE MSI, using the shared Windows builder and inspector."""
import argparse
from pathlib import Path
from tools.app_products import PE
from tools.production_workspace.build_installer import run

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--version",default="0.2.1")
    a=p.parse_args(); run(a.output.resolve(),version=a.version,app=PE)
