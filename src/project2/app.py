
from decorators import handle_db_errors

from .data import Data, Source
from .objectspace import DataProcessing


class Application:
    """Класс основного приложения."""

    def __init__(self, sources: list[Source], data_proc: DataProcessing) -> None:
        """Инициализирует приложение со списком источников и обработчиком."""
        self.name: str = "Main_Application"
        self.sources: list[Source] = sources
        self.data_proc: DataProcessing = data_proc
        self.data: list[Data] = []
        self.filter_info: list[list[str | int]] = []

    @handle_db_errors
    def show_source_stats(self, source: Source) -> None:
        """Выводит статистику по отдельному источнику."""
        print(f"Имя источника: {source.name}")
        data = source.get_data()
        print(f"Количество записей: {len(data)}, тип источника: {source.type}")
        for i in data:
            print(i)

    @handle_db_errors
    def show_general_stats(self) -> None:
        """Выводит общую статистику по всем данным."""
        print(f"Количество записей: {len(self.data)}")
        demo_counter = 0
        file_counter = 0
        for i in self.data:
            if i.source == "demo":
                demo_counter += 1
            if i.source == "file":
                file_counter += 1
        print(f"Записей из источника типа demo: {demo_counter}. Из источника типа file: {file_counter}")
        for i in self.filter_info:
            print(f"После фильтрации по \"{i[0]}({i[1]})\": {i[2]}")
        avg_price = self.data_proc.average_price(self.data)
        print(f"Средняя цена продуктов: {avg_price}")

    @handle_db_errors
    def normalize(self) -> None:
        """Нормализует данные в указанном источнике."""
        self.data = self.data_proc.normalizing(self.data)

    @handle_db_errors
    def filter(self, key: str, param1: str | float, param2: float | None = None) -> list[Data] | None:
        """Фильтрует данные в источнике по заданному критерию."""
        source_data = self.data
        if not source_data:
            print("Фильтрация невозможна, источник пуст")
            return self.data
        if key not in ["Category", "Price", "Seller"]:
            raise ValueError(f"Поле {key} не существует/нельзя провести фильтрацию")
        print(f"Записей до фильтрации: {len(source_data)}")
        if key == "Category":
            result = self.data_proc.filter_category(source_data, param1)
            self.filter_info.append([key, param1, len(result)])
            for i in result:
                print(i)
        if key == "Price":
            if type(param1) is not float:
                raise TypeError("Ошибка фильтрации, неправильный тип данных")
            result = self.data_proc.filter_price(source_data, param1, param2)
            self.filter_info.append([key, f"{param1}-{param2}", len(result)])
            for i in result:
                print(i)
        if key == "Seller":
            result = self.data_proc.filter_seller(source_data, param1)
            self.filter_info.append([key, param1, len(result)])
            for i in result:
                print(i)
        return None

    @handle_db_errors
    def run(self) -> None:
        """Запускает основной конвейер обработки данных."""
        for i in self.sources:
            temp_data = i.get_data()
            for j in temp_data:
                self.data.append(j)
            self.show_source_stats(i)
        print("НОРМАЛИЗАЦИЯ:")
        self.normalize()
        print("ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ:")
        categories = ["нефть", "газ", "золото", "медь"]
        for category in categories:
            print(f"\n  Категория '{category}':")
            self.filter("Category", category)
        print("ФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
        self.filter("Price", 1000.0, 5000.0)
        print("ФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
        self.filter("Seller", "Лукойл")
        print("ОБЩАЯ СТАТИСТИКА:")
        self.show_general_stats()
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
