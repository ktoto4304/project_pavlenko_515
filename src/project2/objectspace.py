from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator

from decorators import handle_db_errors

from .data import Data


class DataProcessing(ABC):
    """Класс обработчика данных."""

    @abstractmethod
    def normalizing(self, data_iterator: Iterator[Data]) -> Iterator[tuple[Data, bool]]:
        """Нормализация информации. Возвращает итератор с кортежами."""
        pass

    @abstractmethod
    def filter_registration(self, key: str, func: Callable) -> None:
        """Добавляет новый ключ фильтрации."""
        pass

    @abstractmethod
    def filter(self, key: str, data_iterator: Iterator[Data], param: str) -> Iterator[Data]:
        """Основная функция фильтрации информации."""
        pass

    @abstractmethod
    def filter_category(self, data_iterator: Iterator[Data], category: str) -> Iterator[Data]:
        """Фильтрует записи по указанной категориям."""
        pass

    @abstractmethod
    def filter_price(self, data_iterator: Iterator[Data], param: str) -> Iterator[Data]:
        """Фильтрует записи по диапазону цен."""
        pass

    @abstractmethod
    def filter_seller(self, data_iterator: Iterator[Data], seller: str) -> Iterator[Data]:
        """Фильтрует записи по указанному продавцу."""
        pass

    @abstractmethod
    def average_price(self, data_iterator: Iterator[Data]) -> float:
        """Вычисляет среднюю цену всех записей."""
        pass


class CommodityProcessing(DataProcessing):
    """Класс обработчика данных о сырье."""
    def __init__(self, name: str = "Обработчик") -> None:
        """Инициализирует обработчик данных с указанным именем."""
        self.name: str = name
        self._filters = {}
    @handle_db_errors
    def normalizing(self, data_iterator: Iterator[Data]) -> Iterator[tuple[Data, bool]]:
        """Нормализует названия сырья, приводя к нижнему регистру и удаляя пробелы."""
        for data in data_iterator:
            if data is None:
                continue
            original_name = data.name
            if not original_name or not isinstance(original_name, str):
                yield data, False
                continue
            normalized_name = original_name.lower().strip()
            data.name = normalized_name
            was_normalized = (normalized_name != original_name)
            yield data, was_normalized
    @handle_db_errors
    def filter_registration(self, key: str, func: Callable) -> None:
        """Добавляет новый ключ фильтрации."""
        self._filters[key] = func
    @handle_db_errors
    def filter(self, key: str, data_iterator: Iterator[Data], param: str) -> Iterator[Data]:
        """Основная функция фильтрации информации."""
        if key not in self._filters:
            raise ValueError(f"Поле {key} не существует/нельзя провести фильтрацию")
        filter_func = self._filters[key]
        return filter_func(data_iterator, param)
    @handle_db_errors
    def filter_category(self, data_iterator: Iterator[Data], category: str) -> Iterator[Data]:
        """Фильтрует записи по указанной категории сырья."""
        for data in data_iterator:
            if data.name.lower().strip() == category.lower().strip():
                yield data
    @handle_db_errors
    def filter_price(self, data_iterator: Iterator[Data], param: str) -> Iterator[Data]:
        """Фильтрует записи по диапазону цен."""
        try:
            price_range = param.split("-")
            min_price, max_price = float(price_range[0]), float(price_range[1])
        except (ValueError, IndexError):
            print(f"Ошибка формата диапазона цен: {param}")
            return
        for data in data_iterator:
            if min_price <= data.price <= max_price:
                yield data
    @handle_db_errors
    def filter_seller(self, data_iterator: Iterator[Data], seller: str) -> Iterator[Data]:
        """Фильтрует записи по указанному продавцу."""
        for data in data_iterator:
            if data.seller.get_name == seller:
                yield data
    @handle_db_errors
    def average_price(self, data_iterator: Iterator[Data]) -> float:
        """Вычисляет среднюю цену всех записей."""
        total = 0.0
        count = 0
        for data in data_iterator:
            total += data.price
            count += 1
        return total / count