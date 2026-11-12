"""PyInstaller entry: failed application/Tk imports need a native error."""
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
