import asyncio
import os
import time
from collections.abc import Iterator

from decorators import handle_db_errors

from .concurent_executor import ConcurrentProcessor
from .config import get_config
from .data import AsyncSource, Data, Source
from .processing_strategies import ProcessingStrategy
from .task_manager import TaskManager
from .web_parsing.parsfactory import create_web_parser


class Application:
    """Класс основного приложения."""

    def __init__(self, sources: list[Source], strategy: ProcessingStrategy) -> None:
        """Инициализирует приложение с источниками и стратегией."""
        self.name: str = "Main_Application"
        self.sources: list[Source] = sources
        self.strategy: ProcessingStrategy = strategy
        self.config = get_config()
        self.concurrent_processor: ConcurrentProcessor = ConcurrentProcessor(
            mode=self.config.execution_mode)
        self.async_sources: list[AsyncSource] = []
        self.task_manager: TaskManager = TaskManager(max_workers=self.config.max_workers)

    def add_async_source(self, source: AsyncSource) -> None:
        """Добавляет асинхронный источник данных."""
        self.async_sources.append(source)

    def _setup_web_source(self) -> None:
        """Настраивает веб-источник."""
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

    def _print_results(self, data: list[Data], total_time: float) -> None:
        """Выводит результаты обработки и всех фильтраций."""
        if not data:
            print("Нет данных для вывода")
            return
        print("РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ")
        print("\nФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ")
        for category in self.config.categories:
            filtered = list(self.strategy.processor.filter_category(iter(data), category))
            print(f"\n  Категория '{category}': найдено {len(filtered)} записей")
            for item in filtered:
                print(f"    {item}")

        print(f"\nФИЛЬТРАЦИЯ ПО ЦЕНЕ ({self.config.price_range})")
        price_filtered = list(self.strategy.processor.filter_price(iter(data), self.config.price_range))
        print(f"  Найдено {len(price_filtered)} записей")
        for item in price_filtered:
            print(f"    {item}")
        print(f"\nФИЛЬТРАЦИЯ ПО ПРОДАВЦУ ({self.config.seller})")
        seller_filtered = list(self.strategy.processor.filter_seller(iter(data), self.config.seller))
        print(f"  Найдено {len(seller_filtered)} записей")
        for item in seller_filtered:
            print(f"    {item}")
        print("ОБЩАЯ СТАТИСТИКА")
        print(f"Обработано записей: {len(data)}")
        print(f"Общее время: {total_time:.4f} сек")
        categories: dict[str, int] = {}
        sellers: dict[str, int] = {}
        total_price: float = 0.0
        for item in data:
            categories[item.name] = categories.get(item.name, 0) + 1
            sellers[item.seller.get_name] = sellers.get(item.seller.get_name, 0) + 1
            total_price += item.price
        print(f"Категории: {categories}")
        print(f"Продавцы: {sellers}")
        print(f"Средняя цена: {total_price / len(data):.2f}")

    @handle_db_errors
    def show_source_stats(self, source: Source, data_iterator: Iterator[Data]) -> list[Data]:
        """Выводит статистику по отдельному источнику и возвращает данные."""
        print(f"Имя источника: {source.name}")
        data_list = list(data_iterator)
        print(f"Количество записей: {len(data_list)}, тип источника: {source.type}")
        return data_list

    @staticmethod
    def _identity_data(data_chunk: list) -> list:
        """Статический метод для передачи данных."""
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
        start_process = time.time()
        result = self.strategy.process(iter(all_data))
        process_time = time.time() - start_process
        total = collect_time + process_time
        self._print_results(result, total)
        return result, total

    def run_with_delay(self) -> tuple[list[Data], float]:
        """Синхронный запуск с задержками для сравнения с асинхронным."""
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
        result = self.strategy.process(iter(all_data))
        process_time = time.perf_counter() - start_process
        total = collect_time + process_time
        self._print_results(result, total)
        return result, total

    async def run_async(self) -> tuple[list[Data], float]:
        """Асинхронный запуск приложения."""
        self._setup_web_source()
        start = time.perf_counter()
        async_tasks = []
        for source in self.async_sources:
            async_tasks.append(self._collect_async_source(source))
        for source in self.sources:
            async_tasks.append(self._collect_sync_source_in_thread(source))
        all_results = await asyncio.gather(*async_tasks)
        all_data = []
        for data_list in all_results:
            all_data.extend(data_list)
        collect_time = time.perf_counter() - start
        print(f"Асинхронный сбор: {len(all_data)} записей за {collect_time:.4f} сек")
        start_process = time.perf_counter()
        async def gen():
            for item in all_data:
                yield item
        result = await self.strategy.process_async(gen())
        process_time = time.perf_counter() - start_process
        total = collect_time + process_time
        self._print_results(result, total)
        return result, total

    async def run_hybrid(self) -> tuple[list[Data], float]:
        """Гибридный запуск: асинхронный сбор + обработка через executor."""
        self._setup_web_source()
        start = time.perf_counter()
        async_tasks = []
        for source in self.async_sources:
            async_tasks.append(self._collect_async_source(source))
        for source in self.sources:
            async_tasks.append(self._collect_sync_source_in_thread(source))
        all_results = await asyncio.gather(*async_tasks)
        all_data = []
        for data_list in all_results:
            all_data.extend(data_list)
        collect_time = time.perf_counter() - start
        print(f"Асинхронный сбор: {len(all_data)} записей за {collect_time:.4f} сек")
        use_processes = self.config.hybrid_executor == "processes"
        start_process = time.perf_counter()
        result = await self.task_manager.process_with_executor(
            all_data, self.strategy, self.config.chunk_size, use_processes)
        process_time = time.perf_counter() - start_process
        total = collect_time + process_time
        executor_type = "процессов" if use_processes else "потоков"
        print(f"Гибридная обработка ({executor_type}): {process_time:.4f} сек")
        print(f"Общее время (hybrid): {total:.4f} сек")
        self._print_results(result, total)
        return result, total

    async def _collect_async_source(self, source: AsyncSource) -> list[Data]:
        """Собирает все данные из асинхронного источника."""
        data_list = []
        async for data in source.get_data_async():
            data_list.append(data)
        print(f"Источник '{source.name}': собрано {len(data_list)} записей")
        return data_list

    async def _collect_sync_source_in_thread(self, source: Source) -> list[Data]:
        """Запускает синхронный сбор данных в отдельном потоке."""
        loop = asyncio.get_running_loop()
        def sync_collect() -> list[Data]:
            return list(source.get_data())
        data_list = await loop.run_in_executor(None, sync_collect)
        print(f"Источник '{source.name}': собрано {len(data_list)} записей")
        return data_list
