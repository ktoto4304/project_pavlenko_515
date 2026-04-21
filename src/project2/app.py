import os
from collections.abc import Iterator

from decorators import handle_db_errors

from .concurent_executor import ConcurrentProcessor
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
        self.concurrent_processor = ConcurrentProcessor(mode=self.config.execution_mode)

    def _setup_web_source(self) -> None:
        """Настраивает веб-источник (внутренний метод)."""
        if self.config.test_mode:
            print("ТЕСТОВЫЙ РЕЖИМ: веб-источник пропущен")
            return

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
        """Выводит статистику по отдельному источнику и возвращает данные."""
        print(f"Имя источника: {source.name}")
        data_list = list(data_iterator)
        print(f"Количество записей: {len(data_list)}, тип источника: {source.type}")
        if not self.config.test_mode:
            for data in data_list:
                print(data)
        return data_list

    def _process_chunk(self, chunk: list[Data]) -> list[Data]:
        if not chunk:
            return []
        return list(self.strategy.process(iter(chunk)))

    @staticmethod
    def _identity_data(data_chunk: list) -> list:
        """Статический метод для передачи данных (picklable для процессов)."""
        return data_chunk

    def run(self) -> tuple[list[Data], float]:
        """Запускает приложение и возвращает результат и время выполнения."""
        self._setup_web_source()
        print("СБОР ДАННЫХ ИЗ ИСТОЧНИКОВ")

        start_collect = __import__('time').time()

        if self.config.execution_mode == "sequential":
            all_data = []
            for source in self.sources:
                source_iterator = source.get_data()
                source_data = self.show_source_stats(source, source_iterator)
                all_data.extend(source_data)
        else:
            source_chunks = []
            for source in self.sources:
                source_chunks.append(list(source.get_data()))

            collected = self.concurrent_processor.process_chunks(source_chunks, self._identity_data)

            all_data = []
            for item in collected:
                if isinstance(item, list):
                    all_data.extend(item)
                else:
                    all_data.append(item)

            print(f"\nВсего собрано данных: {len(all_data)} записей")

        collect_time = __import__('time').time() - start_collect
        print(f"Время сбора данных: {collect_time:.4f} сек")

        print("ЗАПУСК ОБРАБОТКИ ДАННЫХ ЧЕРЕЗ СТРАТЕГИИ")
        start_process = __import__('time').time()
        result = list(self.strategy.process(iter(all_data)))
        process_time = __import__('time').time() - start_process

        print(f"\nОбработано записей: {len(result)}")
        print(f"Время обработки: {process_time:.4f} сек")
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")

        return result, collect_time + process_time
