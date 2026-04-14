from abc import ABC, abstractmethod
from collections.abc import Iterator

from .config import get_config
from .data import Data
from .objectspace import CommodityProcessing


class ProcessingStrategy(ABC):
    """Абстрактный базовый класс для всех стратегий обработки данных."""
    @abstractmethod
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        """Выполняет обработку данных согласно конкретной стратегии."""
        pass

class NormalizationStrategy(ProcessingStrategy):
    """Стратегия нормализации данных."""
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
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

class FilterStrategy(ProcessingStrategy):
    """Стратегия фильтрации данных."""
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
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

class StatisticsStrategy(ProcessingStrategy):
    """Стратегия расчета статистики."""
    def process(self, data_iterator: Iterator[Data], processor: CommodityProcessing,
                **kwargs) -> Iterator[Data]:
        print("ОБЩАЯ СТАТИСТИКА:")
        data_list = list(data_iterator)
        print(f"Количество записей: {len(data_list)}")
        source_name = {}
        for data in data_list:
            if data.source not in source_name.keys():
                source_name[data.source] = 1
            else:
                source_name[data.source] += 1
        for source_type, count in source_name.items():
            print(f"Записей из источника типа {source_type}: {count}.")
        for info in kwargs.get("info", []):
            print(f"После фильтрации по \"{info[0]}({info[1]})\": {info[2]}")
        avg_price = processor.average_price(iter(data_list))
        print(f"Средняя цена продуктов: {avg_price}")
        return iter(data_list)

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
                    filtered = list(strategy.process(iter(all_data),
                                            self.processor, key="Category", param=category))
                    filter_info.append(["Category", category, len(filtered)])
                print("\nФИЛЬТРАЦИЯ ПО ЦЕНЕ (1000 д.е.-5000 д.е.):")
                price_filtered = list(strategy.process(iter(all_data),
                                                self.processor, key="Price", param=self.config.price_range))
                filter_info.append(["Price", self.config.price_range, len(price_filtered)])
                print("\nФИЛЬТРАЦИЯ ПО ПРОДАВЦУ:")
                seller_filtered = list(strategy.process(iter(all_data),
                                                self.processor, key="Seller", param=self.config.seller))
                filter_info.append(["Seller", self.config.seller, len(seller_filtered)])
            elif isinstance(strategy, NormalizationStrategy):
                print("\nНОРМАЛИЗАЦИЯ:")
                normalized_data = list(strategy.process(iter(all_data), self.processor))
                if normalized_data:
                    all_data = normalized_data
            elif isinstance(strategy, StatisticsStrategy):
                all_data = list(strategy.process(iter(all_data), self.processor, info=filter_info))
        return iter(all_data)
