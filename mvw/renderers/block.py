from pathlib import Path
from rich_pixels import Pixels

from .base import BaseRenderer
from mvw.config import ConfigManager

poster_width = int(ConfigManager().get_config("UI", "poster_width"))
poster_height = int(1.2 * poster_width)

class BlockRenderer(BaseRenderer):
    def __rich_console__(self, console, options):
        try:
            if not self.image_path.exists():
                self.failed = True
                return

            # Use rich_pixels.Pixels for block-based rendering
            pixels = Pixels.from_image_path(
                path=str(self.image_path),
                resize=[poster_width, poster_height] # pyright: ignore
            )
            yield pixels

        except Exception:
            self.failed = True
