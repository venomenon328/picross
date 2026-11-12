"""Developer fallback with the shared desktop instance/port/stop contract."""
from .desktop import main as desktop_main


def main(argv=None):
    return desktop_main(argv, console=True)


if __name__ == '__main__':
    raise SystemExit(main())
