"""Resource paths shared by the current rating/date readers.

Raster revisions are separate editor_change operations. There is no production
package update or historical update recovery entry point.
"""
from .catalog_io import safe as path_in
from .current_content import notice_path
