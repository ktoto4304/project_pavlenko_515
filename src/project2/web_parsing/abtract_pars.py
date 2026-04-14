from abc import ABC, abstractmethod
from typing import Any


class WebParser(ABC):
    """Абстрактный класс для всех веб-парсеров."""
    @abstractmethod
    def fetch_data(self) -> list[dict[str, Any]] | None:
        """Получает данные из веб-источника."""
        pass

    @abstractmethod
    def save_to_file(self, filename: str) -> bool:
        """Сохраняет полученные данные в файл."""
        pass
