import asyncio
import json
import os
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
        
import time
from decorators import handle_db_errors


class Data:
    """Класс Единицы памяти."""

    def __init__(self, name: str, seller_name: str, price: float,
                 seller_id: int, source: str, note: str = "Нет примечаний") -> None:
        """Инициализирует объект данных о сырье."""
        if type(name) is not str or type(price) is not float or \
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


class Sellerinfo:
    """Информация о продавце."""
    def __init__(self, name: str, id: int) -> None:
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


class Source(ABC):
    """Класс источника."""

    def __init__(self, name: str, source_type: str) -> None:
        """Инициализирует источник данных."""
        self.name: str = name
        self.type: str = source_type

    @abstractmethod
    def get_data(self) -> Iterator[Data]:
        """Получает данные из источника и возвращает итератор объектов Data."""
        pass


class AsyncSource(ABC):
    """Абстрактный асинхронный источник данных."""

    def __init__(self, name: str, source_type: str) -> None:
        """Инициализирует асинхронный источник данных."""
        self.name: str = name
        self.type: str = source_type

    @abstractmethod
    async def get_data_async(self) -> AsyncIterator[Data]:
        """Асинхронно выдаёт объекты Data."""
        pass


class DemoSource(Source):
    """Демо-источник с данными прямо в коде."""

    def __init__(self, name: str = "Неизвестно") -> None:
        """Инициализирует источник данных demo."""
        super().__init__(name, "demo")

    def get_data(self) -> Iterator[Data]:
        """Генерирует объекты Data по одному."""
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

        for item in raw_list:
            yield Data(item[0], item[1], item[3], item[2], "demo", item[4])


class AsyncDemoSource(AsyncSource):
    """Асинхронный демо-источник с имитацией сетевой задержки."""

    def __init__(self, name: str = "Неизвестно", delay: float = 0.1) -> None:
        """Инициализирует асинхронный демо-источник."""
        super().__init__(name, "async_demo")
        self.delay = delay
        self._raw = [
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

    async def get_data_async(self) -> AsyncIterator[Data]:
        """Асинхронно генерирует данные с имитацией задержки."""
        for i, item in enumerate(self._raw, 1):
            await asyncio.sleep(self.delay)
            data = Data(item[0], item[1], item[3], item[2], "async_demo", item[4])
            yield data


class FileSource(Source):
    """Файловый источник, читающий данные из JSON-файла построчно."""

    def __init__(self, filename: str, name: str = "Неизвестно") -> None:
        """Инициализирует файловый источник данных."""
        super().__init__(name, "file")
        self.path = os.path.abspath(filename)

    @handle_db_errors
    def get_data(self) -> Iterator[Data]:
        """Генерирует объекты Data из файла по одному."""
        with open(self.path, encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if isinstance(item, dict):
                    name = item.get("name", "")
                    seller = item.get("seller", "")
                    price = float(item.get("price", 0))
                    seller_id = int(item.get("seller_id", 0))
                    note = item.get("note", "Нет примечаний")
                elif isinstance(item, list):
                    name, seller, seller_id, price, note = item
                else:
                    print(f"Строка {line_num}: Неподдерживаемый формат")
                    continue
                yield Data(name, seller, price, seller_id, "file", note)


class AsyncFileSource(AsyncSource):
    """Асинхронный файловый источник с имитацией I/O задержек."""

    def __init__(self, filename: str, name: str = "Неизвестно", delay: float = 0.2) -> None:
        """Инициализирует асинхронный файловый источник."""
        super().__init__(name, "async_file")
        self.path = os.path.abspath(filename)
        self.delay = delay
        self._lines = []

    def _load_lines(self) -> None:
        """Загружает все строки из файла."""
        if not os.path.exists(self.path):
            print(f"[{self.name}] Файл {self.path} не найден")
            return

        with open(self.path, encoding='utf-8') as f:
            self._lines = [line.strip() for line in f if line.strip()]

    async def get_data_async(self) -> AsyncIterator[Data]:
        """Асинхронно читает данные из файла с имитацией I/O."""
        loop = asyncio.get_running_loop()
        self._lines = []
        await loop.run_in_executor(None, self._load_lines)

        total = len(self._lines)

        for i, line in enumerate(self._lines, 1):
            await asyncio.sleep(self.delay)

            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    name = item.get("name", "")
                    seller = item.get("seller", "")
                    price = float(item.get("price", 0))
                    seller_id = int(item.get("seller_id", 0))
                    note = item.get("note", "Нет примечаний")
                elif isinstance(item, list):
                    name, seller, seller_id, price, note = item
                else:
                    print(f"[{self.name}] Строка {i}: Неподдерживаемый формат")
                    continue

                data = Data(name, seller, price, seller_id, "async_file", note)
                yield data

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"[{self.name}] Ошибка в строке {i}: {e}")
                continue

        print(f"[{self.name}] Чтение файла завершено")


class DemoSyncWithDelay(DemoSource):
    def __init__(self, name: str = "Неизвестно", delay: float = 0.1):
        super().__init__(name)
        self.delay = delay
    
    def get_data(self):
        for item in self._raw:
            time.sleep(self.delay)
            yield Data(item[0], item[1], item[3], item[2], "demo", item[4])


class FileSyncWithDelay(FileSource):
    def __init__(self, filename: str, name: str = "Неизвестно", delay: float = 0.2):
        super().__init__(filename, name)
        self.delay = delay
    
    def get_data(self):
        with open(self.path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                time.sleep(self.delay)
                item = json.loads(line)
                yield Data(item["name"], item["seller"], float(item["price"]), int(item["seller_id"]), "file", item.get("note", ""))