import json
import os
import uuid
from abc import ABC, abstractmethod


class Data:
    """Класс Единицы памяти."""

    def __init__(self, name: str, price: float, seller: str, source: str, note: str = "Нет примечаний") -> None:
        """Инициализирует объект данных о сырье."""
        if type(name) is not str or type(price) is not float or type(seller) is not str:
            raise TypeError()
        if price <= 0:
            raise ValueError()
        self.record_id: str = str(uuid.uuid4())[:8]
        self.note: str = note
        self.name: str = name
        self.price: float = price
        self.id: str = seller
        self.source: str = source

    @property
    def name_display(self) -> str:
        """Возвращает отформатированное название сырья."""
        return f"Тип сырья - {self.name}"

    @property
    def price_display(self) -> str:
        """Возвращает отформатированную цену."""
        return f"Цена за единицу объема - {self.price}"

    @property
    def seller_display(self) -> str:
        """Возвращает отформатированную информацию о продавце."""
        return f"Компания - {self.id}"

    @property
    def record_display(self) -> str:
        """Возвращает отформатированный ID записи."""
        return f"ID записи - {self.record_id}"

    @property
    def note_display(self) -> str:
        """Возвращает отформатированное примечание."""
        if self.note == "Нет примечаний":
            return "Нет примечаний"
        return f"Примечание - {self.note}"

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{self.name}: {self.price} (Продавец: {self.id})"

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление объекта."""
        return f"Record_ID = {self.record_id}, Data(name='{self.name}', price={self.price}, seller_id='{self.id}')"

    def __lt__(self, second: 'Data') -> bool:
        """Меньше (<) - по ценe."""
        if not isinstance(second, Data):
            return NotImplemented
        return self.price < second.price
    def __le__(self, second: 'Data') -> bool:
        """Меньше или равно (<=) - по цене."""
        if not isinstance(second, Data):
            return NotImplemented
        return self.price <= second.price
    def __gt__(self, second: 'Data') -> bool:
        """Больше (>) - по цене."""
        if not isinstance(second, Data):
            return NotImplemented
        return self.price > second.price
    def __ge__(self, second: 'Data') -> bool:
        """Больше или равно (>=) - по цене."""
        if not isinstance(second, Data):
            return NotImplemented
        return self.price >= second.price
    def __eq__(self, second: 'Data') -> bool:
        """Равно (=) - по уникальному ID."""
        if not isinstance(second, Data):
            return NotImplemented
        return self.id == second.id



class Source(ABC):
    """Класс источника."""

    def __init__(self, name: str, source_type: str) -> None:
        """Инициализирует источник данных."""
        self.name: str = name
        self.type: str = source_type

    @abstractmethod
    def get_data(self) -> list[Data]:
        """Получает данные из источника и возвращает список объектов Data."""
        pass


class DemoSource(Source):
    """Демо-источник с данными прямо в коде."""

    def __init__(self, name: str = "Неизвестно") -> None:
        """Инициализирует источник данных demo."""
        super().__init__(name, "demo")

    def get_data(self) -> list[Data]:
        raw_list = [
            ["медь", 8745.23, "Норникель", "Нет примечаний"],
            ["газ", 4.87, "Газпром", "Срочная поставка"],
            ["золото", 1956.50, "Полюс", "Высокое качество"],
            ["никель", 17834.91, "Норникель", "Оптовая партия"],
            ["нефть", 78.45, "Лукойл", "Сезонное предложение"],
            ["серебро", 25.67, "Полюс", "Нет примечаний"],
            ["платина", 1056.32, "Норникель", "Высокое качество"],
            ["алюминий", 2356.78, "Русал", "Срочная поставка"],
            ["газ", 5.23, "Газпром", "Оптовая партия"],
            ["медь", 8912.34, "Норникель", "Нет примечаний"]
        ]
        data_list = []
        for i in raw_list:
            data_list.append(Data(i[0], i[1], i[2], "demo", i[3]))
        return data_list


class FileSource(Source):
    """Файловый источник, читающий данные из JSON-файла."""

    def __init__(self, filename: str, name: str = "Неизвестно") -> None:
        """Инициализирует файловый источник данных."""
        super().__init__(name, "file")
        self.path = os.path.abspath(filename)

    def get_data(self) -> list[Data]:
        data_list = []
        with open(self.path, encoding='utf-8') as f:
            raw_list = json.load(f)
            for i in raw_list:
                data_list.append(Data(i[0], i[1], i[2], "file", i[3]))
        return data_list
