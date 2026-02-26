
from abc import ABC, abstractmethod
from collections.abc import Callable

from decorators import handle_db_errors

from .data import Data


class DataProcessing(ABC):
    """Класс обработчика данных."""

    @abstractmethod
    def normalizing(self, data_info: list[Data]) -> list[Data]:
        """Нормализация информации."""
        pass

    @abstractmethod
    def filter_registration(self,key:str,func: Callable) -> None:
        """Добавляет новый ключ фильтрации."""
        pass

    @abstractmethod
    def filter(self, key: str,source_data: list[Data], param: str) -> list[Data] | None:
        """Основная функция фильтрации информации."""
        pass

    @abstractmethod
    def filter_category(self, data_info: list[Data], category: str) -> list[Data]:
        """Фильтрует записи по указанной категориям."""
        pass

    @abstractmethod
    def filter_price(self, data_info: list[Data], param: str) -> list[Data]:
        """Фильтрует записи по диапазону цен."""
        pass

    @abstractmethod
    def filter_seller(self, data_info: list[Data], seller: str) -> list[Data]:
        """Фильтрует записи по указанному продавцу."""
        pass
    @abstractmethod
    def average_price(self, data_info: list[Data]) -> float:
        """Вычисляет среднюю цену всех записей."""
        pass
    @abstractmethod
    def word_counter(self, data: Data) -> int:
        """Подсчитывает количество слов в названии."""
        pass
class CommodityProcessing(DataProcessing):
    """Класс обработчика данных о сырье."""
    def __init__(self, name: str = "Обработчик") -> None:
        """Инициализирует обработчик данных с указанным именем."""
        self.name: str = name
        self._filters = {}
    @handle_db_errors
    def normalizing(self, data_info: list[Data]) -> list[Data]:
        """Нормализует названия сырья, приводя к нижнему регистру и удаляя пробелы."""
        _normalized_count = 0
        to_delete: list[int] = []
        for i in range(len(data_info)):
            original_name = data_info[i].name
            if not original_name or not original_name.strip():
                to_delete.append(i)
            data_info[i].name = data_info[i].name.lower().strip()
            if data_info[i].name != original_name:
                _normalized_count += 1
        for i in reversed(to_delete):
            data_info.pop(i)
        data_info.append(_normalized_count)
        return data_info
    @handle_db_errors
    def filter_registration(self,key:str,func: Callable) -> None:
        """Добавляет новый ключ фильтрации."""
        self._filters[key] = func
        return
    @handle_db_errors
    def filter(self, key: str,source_data: list[Data], param: str) -> list[Data] | None:
        """Основная функция фильтрации информации."""
        if key not in self._filters.keys():
            raise ValueError(f"Поле {key} не существует/нельзя провести фильтрацию")
        return self._filters[key](source_data,param)
    @handle_db_errors
    def filter_category(self, data_info: list[Data], category: str) -> list[Data]:
        """Фильтрует записи по указанной категории сырья."""
        result = []
        for i in range(len(data_info)):
            if data_info[i].name == category:
                result.append(data_info[i])
        return result
    @handle_db_errors
    def filter_price(self, data_info: list[Data], param: str) -> list[Data]:
        """Фильтрует записи по диапазону цен."""
        result = []
        price_range = param.split("-")
        min_price,max_price = float(price_range[0]),float(price_range[1])
        for i in range(len(data_info)):
            if min_price <= data_info[i].price <= max_price:
                result.append(data_info[i])
        return result
    @handle_db_errors
    def filter_seller(self, data_info: list[Data], seller: int) -> list[Data]:
        """Фильтрует записи по указанному продавцу."""
        result = []
        for i in range(len(data_info)):
            if data_info[i].seller.get_name == seller:
                result.append(data_info[i])
        return result
    def average_price(self, data_info: list[Data]) -> float:
        """Вычисляет среднюю цену всех записей."""
        total = 0.0
        count = 0
        for i in range(len(data_info)):
            total += data_info[i].price
            count += 1
        return total / count if count > 0 else 0.0
    def word_counter(self, data: Data) -> int:
        """Подсчитывает количество слов в названии сырья."""
        splitted = data.name.split(" ")
        return len(splitted)
