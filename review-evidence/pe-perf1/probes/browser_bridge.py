from pathlib import Path
import sys,os
Path(__file__).with_name('native-session-private.txt').write_text(sys.argv[1],encoding='utf-8')
os.startfile(sys.argv[1])
