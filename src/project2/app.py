import os
from collections.abc import Iterator

from decorators import handle_db_errors

from .config import get_config
from .data import Data, Source
from .processing_strategies import ProcessingStrategy
from .web_parsing.parsfactory import create_web_parser


class Application:
    """Класс основного приложения."""
    def __init__(self, sources: list[Source], strategy: ProcessingStrategy) -> None:
        self.name = "Main_Application"
        self.sources = sources
        self.strategy = strategy
        self.config = get_config()

    def _setup_web_source(self) -> None:
        """Настраивает веб-источник (внутренний метод)."""
        print("ИНИЦИАЛИЗАЦИЯ ВЕБ-ПАРСЕРА")
        if os.path.exists(self.config.web_source_path):
            print(f"Файл {self.config.web_source_path} уже существует")
            from .sourcefactory import create_source
            web_source = create_source("file", {
                "filename": self.config.web_source_path,
                "name": self.config.web_source_name})
            self.sources.append(web_source)
            return
        parser = create_web_parser(
            self.config.web_parser_type,
            api_key=self.config.alpha_vantage_api_key,
            source_name=self.config.web_source_name)
        if parser:
            data = parser.fetch_data()
            if data and parser.save_to_file(self.config.web_source_path):
                print(f"Данные сохранены в {self.config.web_source_path}")
                from .sourcefactory import create_source
                web_source = create_source("file", {
                    "filename": self.config.web_source_path,
                    "name": self.config.web_source_name})
                self.sources.append(web_source)

    @handle_db_errors
    def show_source_stats(self, source: Source, data_iterator: Iterator[Data]) -> list[Data]:
        """Выводит статистику по отдельному источнику."""
        print(f"Имя источника: {source.name}")
        data_list = list(data_iterator)
        print(f"Количество записей: {len(data_list)}, тип источника: {source.type}")
        for data in data_list:
            print(data)
        return data_list

    @handle_db_errors
    def process_with_strategy(self, data_iterator: Iterator[Data], **kwargs) -> Iterator[Data]:
        """Применяет стратегию к данным."""
        return self.strategy.process(data_iterator, **kwargs)

    @handle_db_errors
    def run(self) -> None:
        """Запускает конвейер обработки."""
        self._setup_web_source()
        all_data = []
        for source in self.sources:
            source_iterator = source.get_data()
            source_data = self.show_source_stats(source, source_iterator)
            all_data.extend(source_data)
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
