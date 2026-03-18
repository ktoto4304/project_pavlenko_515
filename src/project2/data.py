import json
import os
import uuid
from abc import ABC, abstractmethod


class Data:
    """Класс Единицы памяти."""

    def __init__(self, name: str, seller_name: str, price: float,\
                  seller_id: int, source: str, note: str = "Нет примечаний") -> None:
        """Инициализирует объект данных о сырье."""
        if type(name) is not str or type(price) is not float or\
             type(seller_id) is not int or type(seller_name) is not str:
            raise TypeError()
        if price <= 0:
            raise ValueError()
        self._record_id: str = str(uuid.uuid4())[:8]
        self.note: str = note
        self.name: str = name
        self.price: float = price
        self.source: str = source
        self.seller = Sellerinfo(seller_name, seller_id)

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
        return f"Компания - {self._id}"

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
        return f"{self.name}: {self.price} (Продавец: {self.seller.get_name})"

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление объекта."""
        return (f"Record_ID = {self.record_id}\n"
        f"Data(name='{self.name}', price={self.price}, "
        f"seller_id='{self.seller.get_id}')")

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
            ["медь", "Норникель", 1, 8745.23, "Нет примечаний"],
            ["газ", "Газпром", 2, 4.87, "Срочная поставка"],
            ["золото", "Полюс", 3, 1956.50, "Высокое качество"],
            ["никель", "Норникель", 1, 17834.91, "Оптовая партия"],
            ["нефть", "Лукойл", 4, 78.45, "Сезонное предложение"],
            ["серебро", "Полюс", 3, 25.67, "Нет примечаний"],
            ["платина", "Норникель", 1, 1056.32, "Высокое качество"],
            ["алюминий", "Русал", 5, 2356.78, "Срочная поставка"],
            ["газ", "Газпром", 2, 5.23, "Оптовая партия"],
            ["медь", "Норникель", 1, 8912.34, "Нет примечаний"]
        ]
        data_list = []
        for i in raw_list:
            data_list.append(Data(i[0], i[1], i[3], i[2], "demo", i[4]))
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
                data_list.append(Data(i[0], i[1], i[3], i[2], "file", i[4]))
        return data_list
class Sellerinfo:
    """Информация о продавце."""
    def __init__(self,name: str, id: int) -> None:
        self._id = id
        self.name = name
    @property
    def get_name(self) -> str:
        """Возвращает наименование компании продавца."""
        return self.name
    @property
    def get_id(self) -> int:
        """Возвращает ID компании продавца."""
        return self._id
