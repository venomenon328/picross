"""Fixed PG release producer entry point."""
from tools.app_products import PG
from tools.production_workspace.release_channel import main

if __name__ == '__main__':
    main(app=PG)
