"""PyInstaller entry, with no imports from the user's selected data checkout."""
import sys
from tools.puzzle_editor.worker import main as worker_main
from tools.puzzle_editor.desktop import main as desktop_main

if len(sys.argv) == 3 and sys.argv[1] == "--worker":
    worker_main(sys.argv[2])
else:
    desktop_main()
