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

class Moai:
    def __init__(self) -> None:
        self.moai = MOAI
        self.big_moai = BIG_MOAI

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
            else:
                moai_says_table.add_row(self.big_moai, word_panel)
        else:
            moai_says_table.add_row(word_panel)

        console.print(moai_says_table)
