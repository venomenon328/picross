"""Developer and frozen entry share the same windowed lifecycle."""
import sys

if len(sys.argv) == 3 and sys.argv[1] == "--worker":
    from .worker import main
    main(sys.argv[2])
else:
    from .desktop import main
    main()
