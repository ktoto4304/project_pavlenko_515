from abc import ABC, abstractmethod
from typing import Any

from .config import get_config
from .data import Data
from .objectspace import CommodityProcessing


class ProcessingStrategy(ABC):
    """Абстрактный базовый класс для всех стратегий обработки данных."""
    @abstractmethod
    def process(self, data: list[Data], processor: CommodityProcessing, **kwargs) -> list[Data]:
        """Выполняет обработку данных согласно конкретной стратегии."""
        pass

class NormalizationStrategy(ProcessingStrategy):
    """Стратегия нормализации данных."""
    def process(self, data: list[Data], processor: CommodityProcessing, **kwargs) -> list[Data]:
        print("НОРМАЛИЗАЦИЯ:")
        if not data:
            print("Нормализация не требуется, источник пуст")
            return data
        new_data, normilized_count = processor.normalizing(data)
        if normilized_count == 0:
            print("Нормализация не требуется")
        else:
            print(f"Успешно нормализовано {normilized_count} объекта/ов")
        return new_data

class FilterStrategy(ProcessingStrategy):
    """Стратегия фильтрации данных."""
    def process(self, data: list[Data], processor: CommodityProcessing, **kwargs) -> list[Data]:
        key = kwargs['key']
        param = kwargs['param']
        source_data = data
        if not source_data:
            print("Фильтрация невозможна, источник пуст")
            return data
        result = processor.filter(key, data, param)
        if not result:
            print(f"Записей по ключу \"{param}\"({key}) не найдено")
        else:
            print(f"Найдено {len(result)} записей по ключу \"{param}\"({key})")
        for i in result:
            print(i)
        return result

class StatisticsStrategy(ProcessingStrategy):
    """Стратегия расчета статистики."""
    def process(self, data: list[Data], processor: CommodityProcessing, **kwargs) -> dict[str, Any]:
        print("ОБЩАЯ СТАТИСТИКА:")
        print(f"Количество записей: {len(data)}")
        source_name = {}
        for i in data:
            if i.source not in source_name.keys():
                source_name[i.source] = 1
            else:
                source_name[i.source] += 1
        for i in source_name.keys():
            print(f"Записей из источника типа {i}: {source_name[i]}.")
        for i in kwargs["info"]:
            print(f"После фильтрации по \"{i[0]}({i[1]})\": {i[2]}")
        avg_price = processor.average_price(data)
        print(f"Средняя цена продуктов: {avg_price}")
        return {}

class CompositeStrategy(ProcessingStrategy):
    """Композитная стратегия обработки данных."""
    def __init__(self, strategies: list[ProcessingStrategy]):
        self.strategies = strategies
        self.processor = CommodityProcessing()
        self.config = get_config()

    def process(self, data: list[Data], **kwargs) -> list[Data]:
        result = data
        self.processor.filter_registration("Category", self.processor.filter_category)
        self.processor.filter_registration("Price", self.processor.filter_price)
        self.processor.filter_registration("Seller", self.processor.filter_seller)
        filter_info = []
        for strategy in self.strategies:
            if isinstance(strategy, FilterStrategy):
                print("ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ:")
                for category in self.config.categories:
                    print(f"\n  Категория '{category}':")
                    filtered = strategy.process(result, self.processor, key="Category", param=category)
                    filter_info.append(["Category", category, len(filtered)])

                print("ФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
                price_filtered = strategy.process(result, self.processor, key="Price", param=self.config.price_range)
                filter_info.append(["Price", self.config.price_range, len(price_filtered)])

                print("ФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
                seller_filtered = strategy.process(result, self.processor, key="Seller", param=self.config.seller)
                filter_info.append(["Seller", self.config.seller, len(seller_filtered)])
            elif isinstance(strategy, NormalizationStrategy):
                result = strategy.process(result, self.processor, **kwargs)
            elif isinstance(strategy, StatisticsStrategy):
                result = strategy.process(result, self.processor, info=filter_info)
        return result
