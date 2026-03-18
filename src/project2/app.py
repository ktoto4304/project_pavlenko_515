
from decorators import handle_db_errors

from .data import Data, Source
from .processing_strategies import (
    ProcessingStrategy,
)


class Application:
    """Класс основного приложения."""
    def __init__(self, sources: list[Source],strategy: ProcessingStrategy) -> None:
        """Инициализирует приложение со списком источников и обработчиком."""
        self.name = "Main_Application"
        self.sources = sources
        self.data = []
        self.filter_info = []
        self.strategy = strategy
    @handle_db_errors
    def show_source_stats(self, source: Source) -> None:
        """Выводит статистику по отдельному источнику."""
        print(f"Имя источника: {source.name}")
        data = source.get_data()
        print(f"Количество записей: {len(data)}, тип источника: {source.type}")
        for i in data:
            print(i)

    @handle_db_errors
    def process_with_strategy(self, strategy: ProcessingStrategy, **kwargs) -> list[Data]:
        """Применяет указанную стратегию к текущим данным."""
        return strategy.process(self.data, **kwargs)

    @handle_db_errors
    def run(self) -> None:
        """Запускает основной конвейер обработки данных."""
        for i in self.sources:
            temp_data = i.get_data()
            for j in temp_data:
                self.data.append(j)
            self.show_source_stats(i)
        self.process_with_strategy(self.strategy)
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
