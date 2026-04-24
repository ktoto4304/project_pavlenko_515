import asyncio
import os
import time
from collections.abc import Iterator

from decorators import handle_db_errors

from .concurent_executor import ConcurrentProcessor
from .config import get_config
from .data import AsyncSource, Data, Source
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
        self.async_sources: list[AsyncSource] = []

    def add_async_source(self, source: AsyncSource) -> None:
        """Добавляет асинхронный источник данных."""
        self.async_sources.append(source)

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
        """Запускает приложение синхронно и возвращает результат и время выполнения."""
        self._setup_web_source()
        print("СБОР ДАННЫХ ИЗ ИСТОЧНИКОВ")

        start_collect = time.time()

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

        collect_time = time.time() - start_collect
        print(f"Время сбора данных: {collect_time:.4f} сек")

        print("ЗАПУСК ОБРАБОТКИ ДАННЫХ ЧЕРЕЗ СТРАТЕГИИ")
        start_process = time.time()
        result = list(self.strategy.process(iter(all_data)))
        process_time = time.time() - start_process

        print(f"\nОбработано записей: {len(result)}")
        print(f"Время обработки: {process_time:.4f} сек")
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО")

        return result, collect_time + process_time
    def run_with_delay(self) -> tuple[list[Data], float]:
        import time
        self._setup_web_source()
        start = time.perf_counter()
        all_data = []
        for source in self.sources:
            for data in source.get_data():
                time.sleep(0.15)
                all_data.append(data)
        collect_time = time.perf_counter() - start
        print(f"Сбор с задержками: {len(all_data)} записей за {collect_time:.4f} сек")
        start_process = time.perf_counter()
        result = list(self.strategy.process(iter(all_data)))
        process_time = time.perf_counter() - start_process
        total = collect_time + process_time
        print(f"Обработка: {process_time:.4f} сек")
        print(f"Общее время (sync с задержками): {total:.4f} сек")
        return result, total

    async def run_async(self) -> tuple[list[Data], float]:
        """Асинхронный запуск приложения."""
        print("АСИНХРОННЫЙ ЗАПУСК ПРИЛОЖЕНИЯ")
        self._setup_web_source()
        print("-" * 40)

        start_collect = time.perf_counter()
        async_tasks = []

        for source in self.async_sources:
            print(f"Запуск асинхронного сбора из источника: {source.name}")
            async_tasks.append(self._collect_async_source(source))
        for source in self.sources:
            print(f"Запуск синхронного сбора (в потоке) из источника: {source.name}")
            async_tasks.append(self._collect_sync_source_in_thread(source))
        all_results = await asyncio.gather(*async_tasks)
        all_data = []
        for data_list in all_results:
            all_data.extend(data_list)
        collect_time = time.perf_counter() - start_collect
        print(f"\nВсего собрано данных: {len(all_data)} записей")
        print(f"Время асинхронного сбора: {collect_time:.4f} сек")
        print("\nАСИНХРОННАЯ ОБРАБОТКА ДАННЫХ")
        start_process = time.perf_counter()
        async def data_generator():
            for item in all_data:
                yield item
        result = await self.strategy.process_async(data_generator())
        process_time = time.perf_counter() - start_process
        print(f"\nОбработано записей: {len(result)}")
        print(f"Время асинхронной обработки: {process_time:.4f} сек")
        total_time = collect_time + process_time
        print(f"Общее время выполнения: {total_time:.4f} сек")
        print("\nПРИЛОЖЕНИЕ УСПЕШНО ЗАВЕРШЕНО (async)")
        return result, total_time

    async def _collect_async_source(self, source: AsyncSource) -> list[Data]:
        """Собирает все данные из асинхронного источника."""
        data_list = []
        async for data in source.get_data_async():
            data_list.append(data)
        print(f"  Источник '{source.name}': собрано {len(data_list)} записей")
        return data_list

    async def _collect_sync_source_in_thread(self, source: Source) -> list[Data]:
        """
        Запускает синхронный сбор данных в отдельном потоке,
        чтобы не блокировать event loop.
        """
        loop = asyncio.get_running_loop()

        def sync_collect():
            return list(source.get_data())

        data_list = await loop.run_in_executor(None, sync_collect)
        print(f"  Источник '{source.name}': собрано {len(data_list)} записей")
        return data_list


