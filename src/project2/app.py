
from decorators import handle_db_errors

from .data import Source
from .objectspace import DataProcessing


class Application:
    """Класс основного приложения."""

    def __init__(self, sources: list[Source], data_proc: DataProcessing) -> None:
        """Инициализирует приложение со списком источников и обработчиком."""
        self.name = "Main_Application"
        self.sources = sources
        self.data_proc = data_proc
        self.data = []
        self.filter_info = []

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
        source_name = {}
        for i in self.data:
            if i.source not in source_name.keys():
                source_name[i.source] = 1
            else:
                source_name[i.source] += 1
        for i in source_name.keys():
            print(f"Записей из источника типа {i}: {source_name[i]}.")
        for i in self.filter_info:
            print(f"После фильтрации по \"{i[0]}({i[1]})\": {i[2]}")
        avg_price = self.data_proc.average_price(self.data)
        print(f"Средняя цена продуктов: {avg_price}")

    @handle_db_errors
    def normalize(self) -> None:
        """Нормализует данные в указанном источнике."""
        if not self.data:
            print("Нормализация не требуется, источник пуст")
            return
        new_data = self.data_proc.normalizing(self.data)
        normilized_count = new_data[-1]
        if normilized_count == 0:
            print("Нормализация не требуется")
        else:
            print(f"Успешно нормализовано {normilized_count} объекта/ов")
        self.data = new_data[0:len(new_data)-2]
        return

    @handle_db_errors
    def filter(self, key: str, param:str) -> None:
        """Фильтрует данные в источнике по заданному критерию."""
        source_data = self.data
        if not source_data:
            print("Фильтрация невозможна, источник пуст")
            return
        result = self.data_proc.filter(key,source_data,param)
        self.filter_info.append([key, param, len(result)])
        if not result:
            print(f"Записей по ключу \"{param}\"({key}) не найдено")
        else:
            print(f"Найдено {len(result)} записей по ключу \"{param}\"({key})")
        for i in result:
            print(i)

        return

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
        self.data_proc.filter_registration("Category", self.data_proc.filter_category)
        self.data_proc.filter_registration("Price", self.data_proc.filter_price)
        self.data_proc.filter_registration("Seller", self.data_proc.filter_seller)
        categories = ["нефть", "газ", "золото", "медь"]
        for category in categories:
            print(f"\n  Категория '{category}':")
            self.filter("Category", category)
        print("ФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
        self.filter("Price", "1000.0-5000.0")
        print("ФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
        self.filter("Seller", "Лукойл")
        print("ОБЩАЯ СТАТИСТИКА:")
        self.show_general_stats()
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
