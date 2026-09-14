import pytest

from project2.data import Data
from project2.objectspace import CommodityProcessing
from project2.processing_strategies import (
    CompositeStrategy,
    FilterStrategy,
    NormalizationStrategy,
    StatisticsStrategy,
)


class TestNormalizationStrategy:
    """Тесты стратегии нормализации."""

    def test_process_normalizes_data(self):
        """Синхронная нормализация приводит названия к нижнему регистру."""
        strategy = NormalizationStrategy()
        processor = CommodityProcessing()
        data = [
            Data(name="НЕФТЬ", seller_name="A", price=100.0,
                 seller_id=1, source="t"),
            Data(name="ГАЗ", seller_name="B", price=200.0,
                 seller_id=2, source="t"),
        ]
        result = strategy.process(iter(data), processor)
        assert result[0].name == "нефть"
        assert result[1].name == "газ"

    @pytest.mark.asyncio
    async def test_process_async_normalizes_data(self):
        """Асинхронная нормализация работает."""
        strategy = NormalizationStrategy()
        processor = CommodityProcessing()
        data = [
            Data(name="НЕФТЬ", seller_name="A", price=100.0,
                 seller_id=1, source="t"),
        ]

        async def async_iter():
            for item in data:
                yield item

        result = await strategy.process_async(async_iter(), processor)
        assert result[0].name == "нефть"


class TestFilterStrategy:
    """Тесты стратегии фильтрации."""

    def test_process_filters_by_key(self):
        """Синхронная фильтрация."""
        strategy = FilterStrategy()
        processor = CommodityProcessing()
        processor.filter_registration("Category", processor.filter_category)
        data = [
            Data(name="нефть", seller_name="A", price=100.0,
                 seller_id=1, source="t"),
            Data(name="газ", seller_name="B", price=200.0,
                 seller_id=2, source="t"),
        ]
        result = strategy.process(
            iter(data), processor, key="Category", param="нефть"
        )
        assert len(result) == 1
        assert result[0].name == "нефть"

    def test_process_missing_key_raises(self):
        """Отсутствие ключа или параметра вызывает ошибку."""
        strategy = FilterStrategy()
        processor = CommodityProcessing()
        with pytest.raises(ValueError):
            strategy.process(iter([]), processor)


class TestStatisticsStrategy:
    """Тесты стратегии статистики."""

    def test_process_returns_list(self):
        """Стратегия статистики возвращает данные как список."""
        strategy = StatisticsStrategy()
        processor = CommodityProcessing()
        data = [
            Data(name="нефть", seller_name="A", price=100.0,
                 seller_id=1, source="t"),
        ]
        result = strategy.process(iter(data), processor)
        assert len(result) == 1


class TestCompositeStrategy:
    """Тесты композитной стратегии."""

    @pytest.fixture
    def strategy(self):
        return CompositeStrategy([
            NormalizationStrategy(),
            FilterStrategy(),
            StatisticsStrategy(),
        ])

    def test_process_full_pipeline(self, strategy):
        """Полный конвейер: нормализация + фильтрация + статистика."""
        data = [
            Data(name="НЕФТЬ", seller_name="Лукойл", price=4500.0,
                 seller_id=4, source="t"),
            Data(name="газ", seller_name="Газпром", price=1200.0,
                 seller_id=2, source="t"),
            Data(name="ЗОЛОТО", seller_name="Полюс", price=5000.0,
                 seller_id=3, source="t"),
        ]
        result = strategy.process(iter(data))
        assert len(result) == 3
        assert all(item.name == item.name.lower() for item in result)

    @pytest.mark.asyncio
    async def test_process_async_full_pipeline(self, strategy):
        """Асинхронный конвейер."""
        data = [
            Data(name="НЕФТЬ", seller_name="Лукойл", price=4500.0,
                 seller_id=4, source="t"),
        ]

        async def async_iter():
            for item in data:
                yield item

        result = await strategy.process_async(async_iter())
        assert len(result) == 1
