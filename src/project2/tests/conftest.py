import pytest

from project2.data import Data


@pytest.fixture
def sample_data_list() -> list[Data]:
    """Набор тестовых данных для проверки фильтрации и статистики."""
    return [
        Data(name="нефть", seller_name="Лукойл", price=4500.0,
             seller_id=4, source="test"),
        Data(name="газ", seller_name="Газпром", price=1200.0,
             seller_id=2, source="test"),
        Data(name="золото", seller_name="Полюс", price=5000.0,
             seller_id=3, source="test"),
        Data(name="медь", seller_name="Норникель", price=3000.0,
             seller_id=1, source="test"),
        Data(name="нефть", seller_name="Роснефть", price=4200.0,
             seller_id=6, source="test"),
        Data(name="газ", seller_name="Газпром", price=1100.0,
             seller_id=2, source="test"),
        Data(name="медь", seller_name="Норникель", price=3100.0,
             seller_id=1, source="test"),
        Data(name="золото", seller_name="Полюс", price=5500.0,
             seller_id=3, source="test"),
    ]


@pytest.fixture
def empty_data_list() -> list[Data]:
    """Пустой список данных для проверки граничных случаев."""
    return []
