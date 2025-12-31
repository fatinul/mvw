from rich.terminal_theme import TerminalTheme

class Palette:
    def __init__(self, theme_str: str) -> None:
        self.theme : TerminalTheme
        self.theme = self._get_theme(theme_str)

        self.style = self.get_style()



    def _get_theme(self, theme: str) -> TerminalTheme:
        """Returns the TerminalTheme based on string"""
        themes = {
            "gruvbox": Palette.GRUVBOX,
            "catppuccin" : Palette.CATPPUCCIN,
            "nord" : Palette.NORD
        }
        return themes.get(theme.lower(), Palette.GRUVBOX)

    def get_style(self) -> dict:
        """Get the color rgb for the items in review post"""
        return {
            "background": f"rgb({self.theme.background_color[0]},{self.theme.background_color[1]},{self.theme.background_color[2]})",
            "review_text": f"rgb({self.theme.foreground_color[0]},{self.theme.foreground_color[1]},{self.theme.foreground_color[2]})",
            "poster_border": f"rgb({self.theme.ansi_colors[7][0]},{self.theme.ansi_colors[7][1]},{self.theme.ansi_colors[7][2]})",
            "movie_data": f"rgb({self.theme.ansi_colors[2][0]},{self.theme.ansi_colors[2][1]},{self.theme.ansi_colors[2][2]})",
            "imdb_data": f"rgb({self.theme.ansi_colors[3][0]},{self.theme.ansi_colors[3][1]},{self.theme.ansi_colors[3][2]})",
            "stats_data": f"rgb({self.theme.ansi_colors[1][0]},{self.theme.ansi_colors[1][1]},{self.theme.ansi_colors[1][2]})",
            "text": f"rgb({self.theme.ansi_colors[7][0]},{self.theme.ansi_colors[7][1]},{self.theme.ansi_colors[7][2]})",
        }

    # Gruvbox Dark
    GRUVBOX = TerminalTheme(
        background=(60, 56, 54),
        foreground=(235, 219, 178),
        normal=[
            (40, 40, 40), (204, 36, 29), (152,186,85), (215, 153, 33), # black, red, green, yellow
            (69, 133, 136), (177, 98, 134), (104, 157, 106), (168,153, 132) # blue, purple, light green, gray
        ],
        bright=[
            (146, 131, 116), (251,73,52), (184, 187, 38), (250, 189, 47),
            (131, 165, 152), (211, 134, 155), (142, 192, 124), (235, 219, 178)
        ]
    )

    # Catppuccin (Mocha)
    CATPPUCCIN = TerminalTheme(
        background=(30, 30, 46),
        foreground=(205, 214, 244),
        normal=[
            (69, 71, 90), (243, 139, 168), (166, 227, 161), (249, 226, 175),
            (137, 180, 250), (245, 194, 231), (148, 226, 213), (186, 194, 222)
        ]
    )

    # Nord
    NORD = TerminalTheme(
        background=(43, 50, 62),    # nord0: Polar Night
        foreground=(216, 222, 233), # nord4: Snow Storm
        normal=[
            (59, 66, 82),    # Black (nord1)
            (191, 97, 106),  # Red (nord11)
            (163, 190, 140), # Green (nord14)
            (235, 203, 139), # Yellow (nord13)
            (129, 161, 193), # Blue (nord10)
            (180, 142, 173), # Magenta (nord15)
            (136, 192, 208), # Cyan (nord8)
            (229, 233, 240)  # White (nord5)
        ]
    )

