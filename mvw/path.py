from platformdirs import user_config_dir, user_data_dir, user_pictures_dir
from pathlib import Path
from iterfzf import iterfzf
import os

APP_NAME = "mvw"

class PathManager:
    def __init__(self) -> None:
        self.config_dir = Path(user_config_dir(APP_NAME))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.user_conf_path = self.config_dir / "user.conf"

        self.data_dir = Path(user_data_dir(APP_NAME))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "metadata.db"

        self.poster_dir = self.data_dir / "posters"
        self.poster_dir.mkdir(parents=True, exist_ok=True)

        self.screenshot_dir = Path(user_pictures_dir())
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def image_picker(self):
        home = Path.home()
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

        def image_generator():
            for root, dirs, files in os.walk(home):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if Path(file).suffix.lower() in valid_extensions:
                        yield os.path.join(root, file)

        selected = iterfzf(image_generator(), header="Choose your image")
        return selected

