"""PyInstaller entry: failed application/Tk imports need a native error."""
import sys
if sys.argv[1:] == ["--catalog-svg-self-test"]:
    from tools.puzzle_production.catalog_profiles import svg_self_test
    svg_self_test()
    raise SystemExit(0)

if __name__ == '__main__':
    try:
        from tools.production_workspace.desktop import main
        code = main()
    except Exception:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, 'Programmpaket unvollständig. Bitte den gesamten App-Ordner erneut entpacken.',
                                        'Picross · Start nicht möglich', 0x10)
        code = 2
    raise SystemExit(code)
