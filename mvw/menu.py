from iterfzf import iterfzf

# Should be run after selected in `mvw list`
class MenuManager:
    """Handle any features in the menu"""
    def __init__(self) -> None:
        self.features = {}

    def add_feature(self, label:str, func, *args, **kwargs):
        """Register a new feature in the menu"""
        self.features[label] = {
            "func": func,
            "args": args,
            "kwargs": kwargs,
        }

    def run(self, imdbid: str, prompt: str = "Select an option:"):
        """Display menu and execute"""
        options = list(self.features.keys())
        choice = iterfzf(
            options,
            prompt = f"{prompt} >",
            preview=f"mvw preview -i {imdbid}",
        )

        if choice and choice in self.features:
            data = self.features[choice]
            data["func"](*data["args"], **data["kwargs"])
