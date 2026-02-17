
from decorators import handle_db_errors

from .data import Data, Source
from .generator import get_data
from .objectspace import DataProcessing


class Application:
    """Класс основного приложения."""

    def __init__(self) -> None:
        self.name: str = "Main_Application"
        self.sources: list[Source] = []
        self.data_proc: DataProcessing | None = None

    @handle_db_errors
    def get_started(self, source_name: str = "Неизвестно", source_type: str = "test", x: int = 0) -> Source:
        """Создает и возвращает новый источник данных с тестовыми данными."""
        new_source = Source(source_name, source_type)
        temp_list = get_data(x)
        for i in range(len(temp_list)):
            new_source.add_data(Data(
                temp_list[i][0],
                temp_list[i][1],
                temp_list[i][2],
                temp_list[i][3]
            ))
        self.sources.append(new_source)
        self.data_proc = DataProcessing("Основной обработчик")
        return new_source

    def add_source(self, source_obj: Source) -> None:
        """Добавляет существующий источник в список источников приложения."""
        self.sources.append(source_obj)

    def normalize(self, source_obj: Source) -> None:
        """Нормализует данные в указанном источнике."""
        self.data_proc.normalizing(source_obj)

    @handle_db_errors
    def filter(self, source_obj: Source, key: str, param1: str | float, param2: float | None = None) -> Source | None:
        """Фильтрует данные в источнике по заданному критерию."""
        if not source_obj.data:
            print("Фильтрация невозможна, источник пуст")
            return source_obj
        if key not in ["Category", "Price", "Seller"]:
            raise ValueError(f"Поле {key} не существует/нельзя провести фильтрацию")
        print(f"Записей до фильтрации: {len(source_obj.data)}")
        if key == "Category":
            return self.data_proc.filter_category(source_obj, param1)
        if key == "Price":
            if type(param1) is not float:
                raise TypeError("Ошибка фильтрации, неправильный тип данных")
            return self.data_proc.filter_price(source_obj, param1, param2)
        if key == "Seller":
            return self.data_proc.filter_seller(source_obj, param1)
        return None

    def run(self) -> None:
        """Запускает основной конвейер обработки данных."""
        source1 = self.get_started("Рынок энергоносителей", "demo", 1)
        source2 = self.get_started("Биржа металлов", "demo", 2)
        print(f"Первый источник: {source1.name}")
        print(f"Второй источник: {source2.name}")
        for i, source_obj in enumerate(self.sources):
            print(f"Источник {i+1}: {source_obj.name} ({len(source_obj.data)} записей)")
            print(f"Получено данных: {len(source_obj.return_data)} записей")

        print("НОРМАЛИЗАЦИЯ:")
        for source_obj in self.sources:
            print(f"{source_obj.name}:")
            self.normalize(source_obj)

        print("ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ:")
        categories = ["нефть", "газ", "золото", "медь"]
        for category in categories:
            print(f"\n  Категория '{category}':")
            for source_obj in self.sources:
                print(f"Источник: \"{source_obj.name}\"")
                self.filter(source_obj, "Category", category)

        print("ФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
        for source_obj in self.sources:
            print(f"Источник: \"{source_obj.name}\"")
            self.filter(source_obj, "Price", 1000.0, 5000.0)

        print("ОБЩАЯ СТАТИСТИКА:")
        for source_obj in self.sources:
            if source_obj.data:
                avg_price = self.data_proc.average_price(source_obj)
                print(f"  {source_obj.name}: средняя цена(д.е.) = {avg_price:.2f}")

        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
