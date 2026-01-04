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

MOAI = '''  ▁▁
 ▁▁▁│
┌┘└ ░▌   
╚═══╝'''

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
        self.moai = MOAI
        self.big_moai = BIG_MOAI
        self.no_moai = NO_MOAI

    def says(self, word: str, moai: str = "small") -> None:
        from .config import ConfigManager
        config_manager = ConfigManager()

        moai_says_table = Table.grid()
        moai_says_table.add_column(style="light_steel_blue3") 
        moai_says_table.add_column(vertical="middle") 
        word_panel = Panel(word, box=ROUNDED, border_style="light_steel_blue3")

        if config_manager.get_config("UI", "moai").lower() == "true":
            if moai == "small":
                moai_says_table.add_row(self.moai, word_panel)
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
