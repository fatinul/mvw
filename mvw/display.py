import re
from typing import Dict
from pathlib import Path
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.ansi import AnsiDecoder
from rich import box

from .moai import Moai
from .config import ConfigManager
from .path import PathManager
from .theme import Palette

import os
import sys

#Tui poster generating 
from PIL import Image, ImageEnhance
import numpy as np

class TerminalImageRenderer:
    def __init__(self, image_path: Path, width: int):
        self.image_path = image_path
        self.width = width
        self.failed = False

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
            rgb_img = enhancer.enhance(2.5) # Increased for terminal clarity
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
            if new_width % 2 != 0: new_width -= 1
            if new_height % 2 != 0: new_height -= 1
            
            if new_width <= 0 or new_height <= 0:
                self.failed = True
                return

            # Resize - BILINEAR is often crisper than LANCZOS for pixel art/icons
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            arr = np.array(img, dtype=np.float32)

            quadrants = [' ', '▘', '▝', '▀', '▖', '▌', '▞', '▛', '▗', '▚', '▐', '▜', '▄', '▙', '▟', '█']
            output_lines = []

            for y in range(0, new_height, 2):
                line_parts = []
                for x in range(0, new_width, 2):
                    block = arr[y:y+2, x:x+2]
                    
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
                        fg_ansi = "" # Not needed for space
                        bg_ansi = "\033[49m" # Reset to terminal default
                    
                    elif num_opaque < 4:
                        # Case 2: Partially Transparent (Edges)
                        # Use the alpha mask to choose the quadrant shape
                        q_val = 0
                        if mask[0]: q_val += 1
                        if mask[1]: q_val += 2
                        if mask[2]: q_val += 4
                        if mask[3]: q_val += 8
                        
                        char = quadrants[q_val]
                        # Avg color of only the visible pixels
                        fg = np.mean(pixels_rgb[mask], axis=0).astype(int)
                        fg_ansi = f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m"
                        bg_ansi = "\033[49m" # Let terminal background show through

                    else:
                        # Case 3: Fully Opaque - Use your original K-Means logic
                        avg = np.mean(pixels_rgb, axis=0)
                        dists = np.sum((pixels_rgb - avg)**2, axis=1)
                        c1 = pixels_rgb[np.argmax(dists)]
                        c2 = avg

                        for _ in range(2):
                            d1 = np.sum((pixels_rgb - c1)**2, axis=1)
                            d2 = np.sum((pixels_rgb - c2)**2, axis=1)
                            m = d1 > d2
                            if np.any(~m): c1 = np.mean(pixels_rgb[~m], axis=0)
                            if np.any(m): c2 = np.mean(pixels_rgb[m], axis=0)
                        
                        d1 = np.sum((pixels_rgb - c1)**2, axis=1)
                        d2 = np.sum((pixels_rgb - c2)**2, axis=1)
                        m = d1 > d2

                        fg, bg = c2.astype(int), c1.astype(int)
                        q_val = 0
                        if m[0]: q_val += 1
                        if m[1]: q_val += 2
                        if m[2]: q_val += 4
                        if m[3]: q_val += 8
                        
                        char = quadrants[q_val]
                        fg_ansi = f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m"
                        bg_ansi = f"\033[48;2;{bg[0]};{bg[1]};{bg[2]}m"

                    line_parts.append(f"{fg_ansi}{bg_ansi}{char}")
                
                line_parts.append("\033[0m")
                output_lines.append("".join(line_parts))

            yield Text.from_ansi("\n".join(output_lines))

        except Exception:
            self.failed = True

console = Console(force_terminal=True, soft_wrap=True, color_system="truecolor", legacy_windows=False)
config_manager = ConfigManager()
path = PathManager()
moai = Moai()
palette = Palette(str(config_manager.get_config("UI", "theme")))

class DisplayManager:
    def __init__(self, movie, poster_path) -> None:
        self.movie = movie
        self.poster_path = poster_path
        self.poster_width = int(config_manager.get_config("UI", "poster_width"))
        self.info_width = 100

    def display_all_color_theme(self, palette: Palette):
        console.print(str(config_manager.get_config("UI", "theme")))
        console.print(f"[{palette.style.get('background')}]BACKGROUND[/]")
        console.print(f"[{palette.style.get('text')}]TEXT[/]")
        console.print(f"[{palette.style.get('poster_border')}]POSTER_BORDER[/]")
        console.print(f"[{palette.style.get('movie_data')}]MOVIE_DATA[/]")
        console.print(f"[{palette.style.get('imdb_data')}]IMDB_DATA[/]")
        console.print(f"[{palette.style.get('stats_data')}]STATS_DATA[/]")
        console.print(f"[{palette.style.get('review_text')}]REVIEW_TEXT[/]")

    def display_movie_info(self, star: float = 0.0, review_text: str = "Your review will show here."):
        """The Movie Review Card"""
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except AttributeError:
                os.system('chcp 65001')
        
        reviewer_name = config_manager.get_config("USER", "name")
        suffix = "'s" if reviewer_name else ""

        try:
            current_term_width = console.width
            poster_panel = self.poster_panel()

            review_header = Text.from_markup(f"[{str(palette.style.get('review_text', 'cyan'))} bold]󰭹 {reviewer_name.upper()}{suffix} REVIEW :[/] [{str(palette.style.get('imdb_gold', 'yellow'))}]{self.iconize_star(float(star))}[/]")
            review = Text.from_markup(review_text if review_text != None else "Seems like something [italic]happened[/], Sorry for the inconvenience.", overflow="fold", justify="left", style=str(palette.style.get('text', 'white')))
            gap = Text.from_markup(" ")

            review_group = Group(gap, review_header, review)

            spacing = Text(" ")

            if config_manager.get_config("UI", "review") == "true":
                right_group = Group(spacing, self.movie_group(), self.imdb_group(), self.stats_group(), review_group)
            else:
                right_group = Group(spacing, self.movie_group(), self.imdb_group(), self.stats_group())

            if current_term_width < 70:
                main_layout = Group(Align.center(poster_panel), Text(" "), right_group)
            else:
                body_table = Table.grid(padding=(0, 2))
                body_table.add_column(width=self.poster_width + 2)
                body_table.add_column()
                body_table.add_row(poster_panel, right_group)

                main_group = Table.grid(expand=True)
                main_group.add_row(body_table)

                main_layout = Panel(main_group, box=box.SIMPLE_HEAD, width=100)

            full_panel = Panel(main_layout, box=box.SIMPLE_HEAD, width=min(100, current_term_width))
            console.print(full_panel)
        except KeyError:
            moai.says(f"[yellow]x Ermm.. actually TV Shows are currently not supported[/]", type="nerd")
            os.abort()
        except Exception:
            print(f"The terminal preview is not supported")

    def save_display_movie_info(self):
        """Save a screenshot of the user's review"""
        import subprocess
        title_raw = self.movie['title']
        year = self.movie['year']
        title_clean = re.sub(r'[^\w\s.-]', '_', title_raw)
        svg_path = path.screenshot_dir / f"{title_clean} ({year}).svg"

        try:
            command = ["mvw", "preview", "-t", self.movie['title']]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')

            console = Console(force_terminal=True, soft_wrap=True, color_system="truecolor", legacy_windows=False, record=True, width=100)
            decoder = AnsiDecoder()
            lines = list(decoder.decode(result.stdout))

            for line in lines:
                console.print(line)

            # Add nerfont support
            svg_code_format = '''<svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Generated with Rich https://www.textualize.io -->
    <style>

    @font-face {{
        font-family: "FiraCode Nerd Font";
        src: local("FiraCode Nerd Font"),
                local("FiraCodeNF-Regular"),
                url("https://cdn.jsdelivr.net/gh/ryanoasis/nerd-fonts@v3.1.1/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf") format("truetype");
        font-style: normal;
        font-weight: 400;
    }}
    @font-face {{
        font-family: "FiraCode Nerd Font";
        src: local("FiraCode Nerd Font Bold"),
                local("FiraCodeNF-Bold"),
                url("https://cdn.jsdelivr.net/gh/ryanoasis/nerd-fonts@v3.1.1/patched-fonts/FiraCode/Bold/FiraCodeNerdFont-Bold.ttf") format("truetype");
        font-style: bold;
        font-weight: 700;
    }}

    .{unique_id}-matrix {{
        font-family: "FiraCode Nerd Font", "Symbols Nerd Font", monospace;
        font-size: {char_height}px;
        line-height: {line_height}px;
        font-variant-east-asian: full-width;
    }}

    .{unique_id}-title {{
        font-size: 18px;
        font-weight: bold;
        font-family: arial;
    }}

    {styles}
    </style>

    <defs>
    <clipPath id="{unique_id}-clip-terminal">
      <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
    </clipPath>
    {lines}
    </defs>

    {chrome}
    <g transform="translate({terminal_x}, {terminal_y})" clip-path="url(#{unique_id}-clip-terminal)">
    {backgrounds}
    <g class="{unique_id}-matrix">
    {matrix}
    </g>
    </g>
</svg>
'''

            console.save_svg(str(svg_path), title=f"MVW (MoVie revieW) 🗿", theme=palette.theme, code_format=svg_code_format)
            moai.says(f"[green]✓ {self.movie['title']} ({svg_path}) [italic]saved[/italic] successfully[/]\n            [dim]Note that it was in [yellow]`svg`[/yellow] so prefered to use [italic]browser[/italic] to view[/]", type="fun")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Screenshot error ({e}) occured.[/]", type="error")

    def iconize_star(self, star: float):
        star = max(0, min(5, star))
        full_star = int(star)
        has_half_star = (star - full_star) >= 0.5
        empty_star = 5 - full_star - (1 if has_half_star else 0)

        STAR = " "
        HALF = " "
        EMPTY = " "

        return (STAR * full_star) + (HALF if has_half_star else "") + (EMPTY * empty_star)

    def movie_group(self) -> Group: 
        movie_table = Table.grid(expand=False)
        movie_table.add_column(style=str(palette.style.get('movie_data', 'cyan')))
        movie_table.add_column(style=str(palette.style.get('text', 'white')))

        movie_header = Text.from_markup(f"[{str(palette.style.get('movie_data', 'cyan'))} bold]󰿎 MOVIE : [/][{str(palette.style.get('review_text', 'white'))}]{self.movie['title']} ({self.movie['year']})", style="bold")
        movie_table.add_row("├  : ", str(self.movie['director']))
        movie_table.add_row("├  : ", str(self.movie['language']))
        movie_table.add_row("├  : ", str(self.movie['rated']))
        movie_table.add_row("├ 󰔚 : ", str(self.movie['runtime']))
        movie_table.add_row("├  : ", str(self.movie['released']))
        movie_table.add_row("└ 󰴂 : ", str(self.movie['genre']))

        return Group(
            movie_header,
            movie_table
        )

    def imdb_group(self) -> Group:
        imdb_table = Table.grid(expand=False)
        imdb_table.add_column(style=str(palette.style.get('imdb_data', 'yellow')))
        imdb_table.add_column(style=str(palette.style.get('text', 'white')), justify="left")

        imdb_header = Text.from_markup(f"[bold {str(palette.style.get('imdb_data', 'yellow'))}]󰈚 IMDB : [/bold {str(palette.style.get('imdb_data', 'yellow'))}][{str(palette.style.get('review_text', 'white'))}]{self.movie['imdbid']}", style="bold")
        imdb_rating = f"{self.movie['imdbrating']}/10 ({self.movie['imdbvotes']})"
        imdb_table.add_row("└  : ", imdb_rating)

        return Group(
            imdb_header,
            imdb_table
        )

    def stats_group(self) -> Group:
        stats_table = Table.grid(expand=False)
        stats_table.add_column(style=str(palette.style.get('stats_data', 'indian_red')))
        stats_table.add_column(style=str(palette.style.get('text', 'white')), justify="left")

        stats_header = Text.from_markup(f"[bold {str(palette.style.get('stats_data', 'indian_red'))}]  STATS : [/bold {str(palette.style.get('stats_data', 'indian_red'))}][{str(palette.style.get('review_text', 'white'))}]{self.movie['boxoffice']}", style="bold")

        stats: Dict = self.extract_awards(str(self.movie['awards']))

        if stats['oscars'] > 0:
            stats_table.add_row("├ 󰙍 : ", f"Won {stats['oscars']} Oscars")

        stats_table.add_row("├ 󰴥 : ", f"Got {stats['nominations']} Nominations")
        stats_table.add_row("└  : ", f"Won {stats['wins']} Awards")

        return Group(
            stats_header,
            stats_table
        )

    def extract_awards(self, text: str) -> Dict:
        oscar_match = re.search(r'(\d+)\s*Oscar', text, re.IGNORECASE)
        wins_match = re.search(r'(\d+)\s*win', text, re.IGNORECASE)
        nom_match = re.search(r'(\d+)\s*nomination', text, re.IGNORECASE)

        return {
            "oscars": int(oscar_match.group(1)) if oscar_match else 0,
            "wins": int(wins_match.group(1)) if wins_match else 0,
            "nominations": int(nom_match.group(1)) if nom_match else 0
        }

    def poster_panel(self) -> Panel:
        panel_kwargs = {
            "width": self.poster_width + 4,
            "subtitle": str(self.movie['title']),
            "expand": True,
            "style": str(palette.style.get('poster_border', ''))
        }

        if config_manager.get_config("UI", "poster_border") != "true":
            panel_kwargs.update({
                "box": box.SIMPLE_HEAD,
                "subtitle": "",
            })

        def placeholder_panel() -> Panel:
            placeholder_text = Align.center(
                Text("No Poster", style=str(palette.style.get('text', 'white'))),
                vertical="middle",
                height=16
            )
            return Panel(placeholder_text, **panel_kwargs)

        poster_path = str(self.poster_path or "").strip()
        if not poster_path or poster_path == "N/A":
            return placeholder_panel()

        poster_file = Path(poster_path)
        if not poster_file.is_file():
            return placeholder_panel()

        try:
            renderer = TerminalImageRenderer(poster_file, self.poster_width)
            test_panel = Panel(renderer, **panel_kwargs)

            if renderer.failed:
                return placeholder_panel()
            return test_panel
        except Exception:
            return placeholder_panel()
