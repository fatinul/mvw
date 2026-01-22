from pathlib import Path
from rich.text import Text

from .base import BaseRenderer

from PIL import Image
import numpy as np


class ASCIIRenderer(BaseRenderer):
    def __rich_console__(self, console, options):
        try:
            if not self.image_path.exists():
                self.failed = True
                return

            # Open image and convert to grayscale
            img = Image.open(self.image_path).convert("L")

            if img.width == 0 or img.height == 0:
                self.failed = True
                return

            # Calculate dimensions for ASCII art
            aspect_ratio = img.width / img.height
            new_width = self.width
            new_height = int(
                new_width / aspect_ratio / 2
            )  # Adjust for character aspect ratio

            if new_height < 1:
                new_height = 1

            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            arr = np.array(img, dtype=np.uint8)

            # ASCII characters from dark to light
            ascii_chars = "@#%*+=:-. "

            output_lines = []

            for y in range(new_height):
                line_chars = []
                for x in range(new_width):
                    pixel_value = arr[y, x]
                    # Map pixel value (0-255) to ASCII character index
                    char_index = int((pixel_value / 255) * (len(ascii_chars) - 1))
                    char = ascii_chars[
                        len(ascii_chars) - 1 - char_index
                    ]  # Reverse for proper mapping
                    line_chars.append(char)
                output_lines.append("".join(line_chars))

            yield Text("\n".join(output_lines))

        except Exception:
            self.failed = True
