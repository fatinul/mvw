from pathlib import Path
from rich.text import Text

from .base import BaseRenderer

# Tui poster generating
from PIL import Image, ImageEnhance
import numpy as np


class PixelRenderer(BaseRenderer):
    def __rich_console__(self, console, options):
        try:
            if not self.image_path.exists():
                self.failed = True
                return

            # Open as RGBA to catch transparency
            img = Image.open(self.image_path).convert("RGBA")

            if img.width == 0 or img.height == 0:
                self.failed = True
                return

            # Enhance only the RGB content to prevent edge artifacts
            r, g, b, a = img.split()
            rgb_img = Image.merge("RGB", (r, g, b))

            enhancer = ImageEnhance.Sharpness(rgb_img)
            rgb_img = enhancer.enhance(2.5)  # Increased for terminal clarity
            enhancer = ImageEnhance.Contrast(rgb_img)
            rgb_img = enhancer.enhance(1.2)

            # Re-merge with Alpha
            img = Image.merge("RGBA", (*rgb_img.split(), a))

            # Calculate Dimensions
            target_width = self.width * 2
            effective_img_aspect = (img.width / img.height) * 2.3
            new_width = target_width
            new_height = int(target_width / effective_img_aspect)

            # Ensure even dimensions for 2x2 blocks
            if new_width % 2 != 0:
                new_width -= 1
            if new_height % 2 != 0:
                new_height -= 1

            if new_width <= 0 or new_height <= 0:
                self.failed = True
                return

            # Resize - BILINEAR is often crisper than LANCZOS for pixel art/icons
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            arr = np.array(img, dtype=np.float32)

            quadrants = [
                " ",
                "▘",
                "▝",
                "▀",
                "▖",
                "▌",
                "▞",
                "▛",
                "▗",
                "▚",
                "▐",
                "▜",
                "▄",
                "▙",
                "▟",
                "█",
            ]
            output_lines = []

            for y in range(0, new_height, 2):
                line_parts = []
                for x in range(0, new_width, 2):
                    block = arr[y : y + 2, x : x + 2]

                    # Flatten block into 4 pixels
                    pixels_rgba = block.reshape(-1, 4)
                    pixels_rgb = pixels_rgba[:, :3]
                    pixels_a = pixels_rgba[:, 3]

                    # Create a mask for opaque pixels (threshold 128)
                    mask = pixels_a > 128
                    num_opaque = np.sum(mask)

                    if num_opaque == 0:
                        # Case 1: Fully Transparent
                        char = " "
                        fg_ansi = ""  # Not needed for space
                        bg_ansi = "\033[49m"  # Reset to terminal default

                    elif num_opaque < 4:
                        # Case 2: Partially Transparent (Edges)
                        # Use the alpha mask to choose the quadrant shape
                        q_val = 0
                        if mask[0]:
                            q_val += 1
                        if mask[1]:
                            q_val += 2
                        if mask[2]:
                            q_val += 4
                        if mask[3]:
                            q_val += 8

                        char = quadrants[q_val]
                        # Avg color of only the visible pixels
                        fg = np.mean(pixels_rgb[mask], axis=0).astype(int)
                        fg_ansi = f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m"
                        bg_ansi = "\033[49m"  # Let terminal background show through

                    else:
                        # Case 3: Fully Opaque - Use your original K-Means logic
                        avg = np.mean(pixels_rgb, axis=0)
                        dists = np.sum((pixels_rgb - avg) ** 2, axis=1)
                        c1 = pixels_rgb[np.argmax(dists)]
                        c2 = avg

                        for _ in range(2):
                            d1 = np.sum((pixels_rgb - c1) ** 2, axis=1)
                            d2 = np.sum((pixels_rgb - c2) ** 2, axis=1)
                            m = d1 > d2
                            if np.any(~m):
                                c1 = np.mean(pixels_rgb[~m], axis=0)
                            if np.any(m):
                                c2 = np.mean(pixels_rgb[m], axis=0)

                        d1 = np.sum((pixels_rgb - c1) ** 2, axis=1)
                        d2 = np.sum((pixels_rgb - c2) ** 2, axis=1)
                        m = d1 > d2

                        fg, bg = c2.astype(int), c1.astype(int)
                        q_val = 0
                        if m[0]:
                            q_val += 1
                        if m[1]:
                            q_val += 2
                        if m[2]:
                            q_val += 4
                        if m[3]:
                            q_val += 8

                        char = quadrants[q_val]
                        fg_ansi = f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m"
                        bg_ansi = f"\033[48;2;{bg[0]};{bg[1]};{bg[2]}m"

                    line_parts.append(f"{fg_ansi}{bg_ansi}{char}")

                line_parts.append("\033[0m")
                output_lines.append("".join(line_parts))

            yield Text.from_ansi("\n".join(output_lines))

        except Exception:
            self.failed = True
