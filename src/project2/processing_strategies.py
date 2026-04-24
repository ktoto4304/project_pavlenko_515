from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator

from .config import get_config
from .data import Data
from .objectspace import CommodityProcessing


class ProcessingStrategy(ABC):
    """Абстрактный базовый класс для всех стратегий обработки данных."""

    @abstractmethod
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        """Выполняет обработку данных согласно конкретной стратегии (синхронно)."""
        pass

    @abstractmethod
    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронная версия обработки данных."""
        pass


class NormalizationStrategy(ProcessingStrategy):
    """Стратегия нормализации данных."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        """Синхронная нормализация данных."""
        normalized_count = 0
        result_data = []

        for data, was_normalized in processor.normalizing(data_iterator):
            if was_normalized:
                normalized_count += 1
            result_data.append(data)

        if normalized_count == 0:
            print("Нормализация не требуется")
        else:
            print(f"Успешно нормализовано {normalized_count} объекта/ов")

        return iter(result_data)

    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронная нормализация данных."""
        print("  [НОРМАЛИЗАЦИЯ] Начало асинхронной нормализации...")
        normalized_count = 0
        result_data = []

        async for data in data_iterator:
            if data is None:
                continue

            original_name = data.name
            if not original_name or not isinstance(original_name, str):
                result_data.append(data)
                continue
            normalized_name = original_name.lower().strip()
            data.name = normalized_name

            if normalized_name != original_name:
                normalized_count += 1

            result_data.append(data)

        if normalized_count == 0:
            print("  [НОРМАЛИЗАЦИЯ] Нормализация не требуется")
        else:
            print(f"  [НОРМАЛИЗАЦИЯ] Успешно нормализовано {normalized_count} объекта/ов")

        return result_data


class FilterStrategy(ProcessingStrategy):
    """Стратегия фильтрации данных."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        """Синхронная фильтрация данных."""
        key = kwargs.get('key')
        param = kwargs.get('param')

        if not key or not param:
            raise ValueError("Не указаны ключ или параметр фильтрации")

        result = list(processor.filter(key, data_iterator, param))

        if not result:
            print(f"Записей по ключу \"{param}\"({key}) не найдено")
        else:
            print(f"Найдено {len(result)} записей по ключу \"{param}\"({key})")
            for item in result:
                print(item)

        return iter(result)

    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронная фильтрация данных."""
        key = kwargs.get('key')
        param = kwargs.get('param')

        if not key or not param:
            raise ValueError("Не указаны ключ или параметр фильтрации")
        all_data = []
        async for data in data_iterator:
            all_data.append(data)
        result = list(processor.filter(key, iter(all_data), param))

        if not result:
            print(f"  [ФИЛЬТРАЦИЯ] Записей по ключу \"{param}\"({key}) не найдено")
        else:
            print(f"  [ФИЛЬТРАЦИЯ] Найдено {len(result)} записей по ключу \"{param}\"({key})")
            for item in result:
                print(f"    {item}")

        return result


class StatisticsStrategy(ProcessingStrategy):
    """Стратегия расчета статистики."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        """Синхронный расчёт статистики."""
        print("ОБЩАЯ СТАТИСТИКА:")
        data_list = list(data_iterator)

        print(f"Количество записей: {len(data_list)}")

        source_name = {}
        for data in data_list:
            if data.source not in source_name:
                source_name[data.source] = 1
            else:
                source_name[data.source] += 1

        for source_type, count in source_name.items():
            print(f"Записей из источника типа {source_type}: {count}.")

        for info in kwargs.get("info", []):
            print(f"После фильтрации по \"{info[0]}({info[1]})\": {info[2]}")

        avg_price = processor.average_price(iter(data_list))
        print(f"Средняя цена продуктов: {avg_price:.2f}")

        return iter(data_list)

    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронный расчёт статистики."""
        print("  [СТАТИСТИКА] Расчёт статистики...")
        data_list = []
        async for data in data_iterator:
            data_list.append(data)

        print(f"  [СТАТИСТИКА] Количество записей: {len(data_list)}")

        source_name = {}
        for data in data_list:
            if data.source not in source_name:
                source_name[data.source] = 1
            else:
                source_name[data.source] += 1

        for source_type, count in source_name.items():
            print(f"  Записей из источника типа {source_type}: {count}")

        if data_list:
            avg_price = processor.average_price(iter(data_list))
            print(f"  Средняя цена продуктов: {avg_price:.2f}")

        return data_list


class CompositeStrategy(ProcessingStrategy):
    """Композитная стратегия обработки данных."""

    def __init__(self, strategies: list[ProcessingStrategy]):
        self.strategies = strategies
        self.processor = CommodityProcessing()
        self.config = get_config()

        self.processor.filter_registration("Category", self.processor.filter_category)
        self.processor.filter_registration("Price", self.processor.filter_price)
        self.processor.filter_registration("Seller", self.processor.filter_seller)

    def process(self, data_iterator: Iterator[Data], **kwargs) -> Iterator[Data]:
        """Синхронная композитная обработка."""
        all_data = list(data_iterator)

        if not all_data:
            print("Нет данных для обработки")
            return iter([])

        filter_info = []

        for strategy in self.strategies:
            if isinstance(strategy, FilterStrategy):
                print("ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ:")
                for category in self.config.categories:
                    print(f"\n  Категория '{category}':")
                    filtered = list(strategy.process(
                        iter(all_data), self.processor, key="Category", param=category))
                    filter_info.append(["Category", category, len(filtered)])

                print("\nФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
                price_filtered = list(strategy.process(
                    iter(all_data), self.processor, key="Price", param=self.config.price_range))
                filter_info.append(["Price", self.config.price_range, len(price_filtered)])

                print("\nФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
                seller_filtered = list(strategy.process(
                    iter(all_data), self.processor, key="Seller", param=self.config.seller))
                filter_info.append(["Seller", self.config.seller, len(seller_filtered)])

            elif isinstance(strategy, NormalizationStrategy):
                print("\nНОРМАЛИЗАЦИЯ:")
                normalized_data = list(strategy.process(iter(all_data), self.processor))
                if normalized_data:
                    all_data = normalized_data

            elif isinstance(strategy, StatisticsStrategy):
                all_data = list(strategy.process(iter(all_data), self.processor, info=filter_info))

        return iter(all_data)

    async def process_async(self, data_iterator: AsyncIterator[Data], **kwargs) -> list[Data]:
        """Асинхронная композитная обработка."""
        all_data = []
        async for data in data_iterator:
            all_data.append(data)

        if not all_data:
            print("Нет данных для обработки")
            return []

        filter_info = []

        for strategy in self.strategies:
            if isinstance(strategy, NormalizationStrategy):
                print("\n[АСИНХРОННАЯ ОБРАБОТКА] НОРМАЛИЗАЦИЯ:")
                all_data = await strategy.process_async(
                    self._async_iter(all_data), self.processor)

            elif isinstance(strategy, FilterStrategy):
                print("\n[АСИНХРОННАЯ ОБРАБОТКА] ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ:")
                for category in self.config.categories:
                    print(f"\n  Категория '{category}':")
                    filtered = await strategy.process_async(
                        self._async_iter(all_data), self.processor,
                        key="Category", param=category)
                    filter_info.append(["Category", category, len(filtered)])

                print("\n[АСИНХРОННАЯ ОБРАБОТКА] ФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
                price_filtered = await strategy.process_async(
                    self._async_iter(all_data), self.processor,
                    key="Price", param=self.config.price_range)
                filter_info.append(["Price", self.config.price_range, len(price_filtered)])

                print("\n[АСИНХРОННАЯ ОБРАБОТКА] ФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
                seller_filtered = await strategy.process_async(
                    self._async_iter(all_data), self.processor,
                    key="Seller", param=self.config.seller)
                filter_info.append(["Seller", self.config.seller, len(seller_filtered)])

            elif isinstance(strategy, StatisticsStrategy):
                print("\n[АСИНХРОННАЯ ОБРАБОТКА] СТАТИСТИКА:")
                all_data = await strategy.process_async(
                    self._async_iter(all_data), self.processor, info=filter_info)

        return all_data

    async def _async_iter(self, data_list: list[Data]) -> AsyncIterator[Data]:
        """Вспомогательный метод: превращает список в асинхронный итератор."""
        for data in data_list:
            yield data