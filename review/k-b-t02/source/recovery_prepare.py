from pathlib import Path
import shutil,json
w=Path(__file__).parent;out=w/'gui-recovery';out.mkdir()
shutil.copytree(w/'gui/profile',out/'profile')
root=out/'profile/appdata/Godot/app_userdata/picross · P1/p1'
backup=json.loads((root/'saves/kat2_001.bak').read_text())
assert not backup['completed'] and backup['history']
(root/'saves/kat2_001.json').write_text('{invalid-primary',encoding='utf-8')
(root/'recent-puzzle.json').write_text(json.dumps(dict(format='picross-recent-puzzle-v1',id='pz-test-kat2-001',revision=2)),encoding='utf-8')
