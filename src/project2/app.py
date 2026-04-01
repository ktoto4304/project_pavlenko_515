# app.py
from collections.abc import Iterator

from decorators import handle_db_errors

from .data import Data, Source
from .processing_strategies import ProcessingStrategy


class Application:
    """Класс основного приложения."""

    def __init__(self, sources: list[Source], strategy: ProcessingStrategy) -> None:
        """Инициализирует приложение со списком источников и обработчиком."""
        self.name = "Main_Application"
        self.sources = sources
        self.strategy = strategy

    @handle_db_errors
    def show_source_stats(self, source: Source, data_iterator: Iterator[Data]) -> list[Data]:
        """Выводит статистику по отдельному источнику и возвращает данные."""
        print(f"Имя источника: {source.name}")
        data_list = list(data_iterator)
        print(f"Количество записей: {len(data_list)}, тип источника: {source.type}")
        for data in data_list:
            print(data)

        return data_list

    @handle_db_errors
    def process_with_strategy(self, data_iterator: Iterator[Data], **kwargs) -> Iterator[Data]:
        """Применяет указанную стратегию к текущим данным."""
        return self.strategy.process(data_iterator, **kwargs)

    @handle_db_errors
    def run(self) -> None:
        """Запускает основной конвейер обработки данных."""
        all_data = []
        for source in self.sources:
            source_iterator = source.get_data()
            source_data = self.show_source_stats(source, source_iterator)
            all_data.extend(source_data)
        result = list(self.process_with_strategy(iter(all_data)))
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
