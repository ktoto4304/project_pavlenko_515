from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator

from .config import get_config
from .data import Data
from .objectspace import CommodityProcessing


class ProcessingStrategy(ABC):
    """Абстрактный базовый класс для всех стратегий обработки данных."""

    @abstractmethod
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> list[Data]:
        """Выполняет синхронную обработку данных согласно стратегии."""
        pass

    @abstractmethod
    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Выполняет асинхронную обработку данных согласно стратегии."""
        pass


class NormalizationStrategy(ProcessingStrategy):
    """Стратегия нормализации данных."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> list[Data]:
        """Синхронная нормализация данных."""
        result_data = []
        for data, _ in processor.normalizing(data_iterator):
            result_data.append(data)
        return result_data

    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронная нормализация данных."""
        result_data = []
        async for data in data_iterator:
            if data is None:
                continue
            if not data.name or not isinstance(data.name, str):
                result_data.append(data)
                continue
            data.name = data.name.lower().strip()
            result_data.append(data)
        return result_data


class FilterStrategy(ProcessingStrategy):
    """Стратегия фильтрации данных."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> list[Data]:
        """Синхронная фильтрация данных."""
        key = kwargs.get('key')
        param = kwargs.get('param')
        if not key or not param:
            raise ValueError("Не указаны ключ или параметр фильтрации")
        return list(processor.filter(key, data_iterator, param))

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
        return list(processor.filter(key, iter(all_data), param))


class StatisticsStrategy(ProcessingStrategy):
    """Стратегия расчета статистики."""

    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> list[Data]:
        """Синхронный расчёт статистики."""
        return list(data_iterator)

    async def process_async(self, data_iterator: AsyncIterator[Data],
                            processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Асинхронный расчёт статистики."""
        data_list = []
        async for data in data_iterator:
            data_list.append(data)
        return data_list


class CompositeStrategy(ProcessingStrategy):
    """Композитная стратегия обработки данных."""

    def __init__(self, strategies: list[ProcessingStrategy]) -> None:
        """Инициализирует композитную стратегию."""
        self.strategies: list[ProcessingStrategy] = strategies
        self.processor: CommodityProcessing = CommodityProcessing()
        self.config = get_config()
        self.processor.filter_registration("Category", self.processor.filter_category)
        self.processor.filter_registration("Price", self.processor.filter_price)
        self.processor.filter_registration("Seller", self.processor.filter_seller)

    def process(self, data_iterator: Iterator[Data], **kwargs) -> list[Data]:
        """Синхронная композитная обработка."""
        all_data = list(data_iterator)
        if not all_data:
            return []
        for strategy in self.strategies:
            if isinstance(strategy, FilterStrategy):
                for category in self.config.categories:
                    strategy.process(iter(all_data), self.processor, key="Category", param=category)
                strategy.process(iter(all_data), self.processor, key="Price", param=self.config.price_range)
                strategy.process(iter(all_data), self.processor, key="Seller", param=self.config.seller)
            elif isinstance(strategy, NormalizationStrategy):
                all_data = strategy.process(iter(all_data), self.processor)
            elif isinstance(strategy, StatisticsStrategy):
                all_data = strategy.process(iter(all_data), self.processor)
        return all_data

    async def process_async(self, data_iterator: AsyncIterator[Data], **kwargs) -> list[Data]:
        """Асинхронная композитная обработка."""
        all_data = []
        async for data in data_iterator:
            all_data.append(data)
        if not all_data:
            return []
        for strategy in self.strategies:
            if isinstance(strategy, FilterStrategy):
                for category in self.config.categories:
                    await strategy.process_async(self._async_iter(all_data), self.processor,
                                                 key="Category", param=category)
                await strategy.process_async(self._async_iter(all_data), self.processor,
                                             key="Price", param=self.config.price_range)
                await strategy.process_async(self._async_iter(all_data), self.processor,
                                             key="Seller", param=self.config.seller)
            elif isinstance(strategy, NormalizationStrategy):
                all_data = await strategy.process_async(self._async_iter(all_data), self.processor)
            elif isinstance(strategy, StatisticsStrategy):
                all_data = await strategy.process_async(self._async_iter(all_data), self.processor)
        return all_data

    async def _async_iter(self, data_list: list[Data]) -> AsyncIterator[Data]:
        """Преобразует список в асинхронный итератор."""
        for data in data_list:
            yield data
