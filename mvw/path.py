from platformdirs import user_config_dir, user_data_dir, user_pictures_dir
from pathlib import Path

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

