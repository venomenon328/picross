"""Fixed PE adapter for the shared release state machine; never a client updater."""
from tools.app_products import PE
from tools.production_workspace.release_channel import main

if __name__ == "__main__":
    main(app=PE)
