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
                
            img = Image.open(self.image_path).convert("RGB")
            
            if img.width == 0 or img.height == 0:
                self.failed = True
                return
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)

            target_width = self.width * 2
            effective_img_aspect = img.width / img.height * 2.3
            new_width = target_width
            new_height = int(target_width / effective_img_aspect)

            if new_width % 2 != 0: new_width -= 1
            if new_height % 2 != 0: new_height -= 1
            
            if new_width <= 0 or new_height <= 0:
                self.failed = True
                return

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            arr = np.array(img, dtype=np.float32)

            quadrants = [' ', '▘', '▝', '▀', '▖', '▌', '▞', '▛', '▗', '▚', '▐', '▜', '▄', '▙', '▟', '█']
            output_lines = []

            for y in range(0, new_height, 2):
                line_parts = []
                for x in range(0, new_width, 2):
                    block = arr[y:y+2, x:x+2]
                    pixels = block.reshape(-1, 3)
                    
                    avg = np.mean(pixels, axis=0)
                    dists = np.sum((pixels - avg)**2, axis=1)
                    c1 = pixels[np.argmax(dists)]
                    c2 = avg
                    
                    for _ in range(2):
                        d1 = np.sum((pixels - c1)**2, axis=1)
                        d2 = np.sum((pixels - c2)**2, axis=1)
                        mask = d1 > d2
                        
                        if np.any(~mask): c1 = np.mean(pixels[~mask], axis=0)
                        if np.any(mask): c2 = np.mean(pixels[mask], axis=0)
                        
                    d1 = np.sum((pixels - c1)**2, axis=1)
                    d2 = np.sum((pixels - c2)**2, axis=1)
                    mask = d1 > d2
                    
                    if np.all(mask):
                        fg, bg = c2.astype(int), c2.astype(int)
                        char_idx = 15
                    elif np.all(~mask):
                        fg, bg = c1.astype(int), c1.astype(int)
                        char_idx = 15
                    else:
                        fg, bg = c2.astype(int), c1.astype(int)
                        q_val = 0
                        if mask[0]: q_val += 1
                        if mask[1]: q_val += 2
                        if mask[2]: q_val += 4
                        if mask[3]: q_val += 8
                        char_idx = q_val

                    char = quadrants[char_idx]
                    line_parts.append(f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m\033[48;2;{bg[0]};{bg[1]};{bg[2]}m{char}")
                
                line_parts.append("\033[0m")
                output_lines.append("".join(line_parts))
            
            yield Text.from_ansi("\n".join(output_lines))

        except Exception:
            self.failed = True

#_____


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
            moai.says(f"[indian_red]x Sorry, TV Shows are currently not supported[/]")
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

            console.save_svg(str(svg_path), title=f"MVW (MoVie revieW) 🗿", theme=palette.theme)
            moai.says(f"[green]✓ {self.movie['title']} ({svg_path}) [italic]saved[/italic] successfully[/]\nNote that it was in [yellow]`svg`[/] so prefered to use [italic]browser[/] to view")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Screenshot error ({e}) occured.[/]")

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
