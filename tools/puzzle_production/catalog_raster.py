"""Separate current editor operation; no production package or migration route."""
from .editor_change import plan, apply, detail as view
from .content_registry import recover
from .editor_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
