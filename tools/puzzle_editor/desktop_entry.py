"""PyInstaller entry, with no imports from the user's selected data checkout."""
import sys
if sys.argv[1:] == ["--catalog-svg-self-test"]:
    from tools.puzzle_production.catalog_profiles import svg_self_test
    svg_self_test()
    raise SystemExit(0)

from tools.puzzle_editor.worker import main as worker_main, loop as worker_loop
from tools.puzzle_editor.desktop import main as desktop_main

if len(sys.argv) == 3 and sys.argv[1] == "--worker":
    worker_main(sys.argv[2])
elif len(sys.argv) == 3 and sys.argv[1] == "--session":
    worker_loop(sys.argv[2])
else:
    desktop_main()
