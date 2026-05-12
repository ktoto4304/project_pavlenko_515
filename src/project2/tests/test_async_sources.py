import pytest

from project2.data import AsyncDemoSource


class TestAsyncDemoSource:
    """Тесты AsyncDemoSource."""

    @pytest.mark.asyncio
    async def test_get_data_async_yields_all_items(self):
        """Асинхронный источник отдаёт все элементы."""
        source = AsyncDemoSource(name="test", delay=0.0)
        results = []
        async for item in source.get_data_async():
            results.append(item)
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_get_data_async_items_have_correct_structure(self):
        """Элементы имеют правильную структуру."""
        source = AsyncDemoSource(name="test", delay=0.0)
        async for item in source.get_data_async():
            assert item.name is not None
            assert item.price > 0
            assert item.seller.get_name is not None
            break
