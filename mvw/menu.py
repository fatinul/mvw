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

    def run(self, prompt: str = "Select an option:"):
        """Display menu and execute"""
        options = list(self.features.keys())
        choice = iterfzf(
            options,
            prompt = f"{prompt} >"
        )

        if choice and choice in self.features:
            data = self.features[choice]
            data["func"](*data["args"], **data["kwargs"])

if __name__ == "__main__":
    manager = MenuManager()

    def func1(name:str):
        print(f"Test, it works, the label = {name}")

    manager.add_feature("Test", func1, name="moai")
    manager.run()
