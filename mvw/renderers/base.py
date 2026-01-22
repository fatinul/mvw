from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Any


class BaseRenderer(ABC):
    def __init__(self, image_path: Path, width: int):
        self.image_path = image_path
        self.width = width
        self.failed = False

    @abstractmethod
    def __rich_console__(self, console: Any, options: Any) -> Iterator[Any]:
        pass
