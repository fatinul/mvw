from pathlib import Path
from rich.text import Text
from rich.align import Align

from .base import BaseRenderer
from asciify import asciify, UNICODE_BLOCKS
from mvw.config import ConfigManager

CHARSETS = {
        "minimal": " .,;:+*#@",
        "dots": "•",
        "blocks": UNICODE_BLOCKS,
        }

poster_width = float(ConfigManager().get_config("UI", "poster_width"))-1
poster_height = int(1.1 * poster_width)

class ASCIIRenderer(BaseRenderer):
    def __rich_console__(self, console, options):
        try:
            if not self.image_path.exists():
                self.failed = True
                return

            charset_name = ConfigManager().get_config("UI", "charset")
            charset = CHARSETS.get(charset_name)

            if charset is None:
                charset = CHARSETS["minimal"]

            result = asciify(
                image_path=str(self.image_path),
                width=int(poster_width),
                height=poster_height,
                edges_detection=False,
                charset=charset
            )

            yield Align.center(Text.from_ansi(result))
        except Exception:
            self.failed = True
