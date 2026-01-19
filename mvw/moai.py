from rich.box import ROUNDED
from rich.panel import Panel
from rich.table import Table
from rich.console import Console


console = Console()

BIG_MOAI = '''  ╓╌╌─╗
 ╔▁▁▁░╚╗
 ╛▟▲▘ ▒║ 
╭╒╼╾╮░╓
╚─────╝
  MOAI'''

# The base shape with placeholders for the "mood"
MOAI_BASE = '''  ▁▁ 
 │▁▁▁{icon}
▐  ░└┐
 ╚═{mouth}╝  '''

MOODS = {
    "normal": {"mouth": "══", "icon": " ", "color": "light_steel_blue3"},
    "info":   {"mouth": "ᗜ ", "icon": "(i) ", "color": "sky_blue1"},
    "error":  {"mouth": "△═", "icon": "❗", "color": "indian_red"},
    "sad":    {"mouth": "︿", "icon": "💧", "color": "dim light_steel_blue3"},
    "fun":    {"mouth": "⛛ ", "icon": "✦𓈒", "color": "green"},
    "nerd":   {"mouth": "3═", "icon": "👆", "color": "yellow"}
}

NO_MOAI = ''''''

TITLE = '''
   __  ______  __      ___     __
  /  |/  /| | / /      | | /| / /
 / /|_/ / | |/ /       | |/ |/ / 
/_/  /_/o |___/ie revie|__/|__/ 
         -- ...- .--
'''

class Moai:
    def __init__(self) -> None:
        self.moai = MOAI_BASE
        self.big_moai = BIG_MOAI
        self.no_moai = NO_MOAI

    def says(self, word: str, moai: str = "small", type: str = "normal") -> None:
        from .config import ConfigManager
        config_manager = ConfigManager()

        mood = MOODS.get(type, MOODS["normal"])
        current_moai_ascii = self.moai.format(mouth=mood["mouth"], icon=mood["icon"])
        moai_says_table = Table.grid()
        # Use the mood color for the Moai and the border
        moai_says_table.add_column(style=mood["color"]) 
        moai_says_table.add_column(vertical="middle") 
        word_panel = Panel(word, box=ROUNDED, border_style=mood["color"])

        if config_manager.get_config("UI", "moai").lower() == "true":
            if moai == "small":
                moai_says_table.add_row(current_moai_ascii, word_panel)
            elif moai == "no":
                moai_says_table.add_row(word_panel)
            else:
                moai_says_table.add_row(self.big_moai, word_panel)
        else:
            moai_says_table.add_row(word_panel)

        console.print(moai_says_table)

    def title(self):
        # console.print(f"[light_steel_blue3 bold]{TITLE}[/]")
        moai_lines = BIG_MOAI.splitlines()
        title_lines = TITLE.splitlines()

        max_height = max(len(moai_lines), len(title_lines))

        for i in range(max_height):
            left = moai_lines[i] if i < len(moai_lines) else ""
            right = title_lines[i] if i < len(title_lines) else ""
            console.print(f"         [light_steel_blue3]{left.ljust(9)}{right}[/]")

if __name__ == "__main__":
    Moai().says(f"Hi normal", type="normal")
    Moai().says(f"Hi error", type="error")
    Moai().says(f"Hi info", type="info")
    Moai().says(f"Hi sad", type="sad")
    Moai().says(f"Hi fun", type="fun")
    Moai().says(f"Hi nerd", type="nerd")
