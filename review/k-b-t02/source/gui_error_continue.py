from gui_steps import *
from gui_sizes import scale
scale(0)
# Continue after the safe click guard rejected an offscreen UI125 card.
source=(w/'gui_finish.py').read_text(encoding='utf-8')
start=source.index("win.click_rect(card('pz-test-kat2-003')")
root=w/'gui/profile/appdata/Godot/app_userdata/picross · P1/p1'
tmp=root/'recent-puzzle.json.tmp';old=(root/'recent-puzzle.json').read_bytes()
exec(source[start:])
