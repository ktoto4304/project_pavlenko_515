import pytest

from project2.data import Data


class TestData:
    """Тесты создания и методов Data."""

    def test_create_valid_data(self):
        """Data создаётся с корректными значениями."""
        item = Data(
            name="нефть", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test", note="срочно"
        )
        assert item.name == "нефть"
        assert item.price == 4500.0
        assert item.seller.get_name == "Лукойл"
        assert item.seller.get_id == 4
        assert item.source == "test"
        assert item.note == "срочно"

    def test_create_data_default_note(self):
        """Data создаётся с примечанием по умолчанию."""
        item = Data(
            name="газ", seller_name="Газпром", price=1200.0,
            seller_id=2, source="test"
        )
        assert item.note == "Нет примечаний"

    def test_create_data_invalid_price_raises(self):
        """Отрицательная цена вызывает ValueError."""
        with pytest.raises(ValueError):
            Data(
                name="газ", seller_name="Газпром", price=-100.0,
                seller_id=2, source="test"
            )

    def test_create_data_zero_price_raises(self):
        """Нулевая цена вызывает ValueError."""
        with pytest.raises(ValueError):
            Data(
                name="газ", seller_name="Газпром", price=0.0,
                seller_id=2, source="test"
            )

    def test_create_data_invalid_name_type_raises(self):
        """Некорректный тип name вызывает TypeError."""
        with pytest.raises(TypeError):
            Data(
                name=123, seller_name="Газпром", price=1200.0,
                seller_id=2, source="test"
            )

    def test_create_data_invalid_price_type_raises(self):
        """Некорректный тип price вызывает TypeError."""
        with pytest.raises(TypeError):
            Data(
                name="газ", seller_name="Газпром", price="1200",
                seller_id=2, source="test"
            )

    def test_data_str_representation(self):
        """Строковое представление содержит название и цену."""
        item = Data(
            name="нефть", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        result = str(item)
        assert "нефть" in result
        assert "4500" in result
        assert "Лукойл" in result

    def test_data_comparison_by_price(self):
        """Сравнение Data идёт по цене."""
        cheap = Data(
            name="газ", seller_name="Газпром", price=1000.0,
            seller_id=2, source="test"
        )
        expensive = Data(
            name="нефть", seller_name="Лукойл", price=5000.0,
            seller_id=4, source="test"
        )
        assert cheap < expensive
        assert expensive > cheap
        assert cheap != expensive

    def test_data_equal_by_id(self):
        """Равные по id объекты не равны (разные uuid)."""
        item1 = Data(
            name="нефть", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        item2 = Data(
            name="нефть", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        assert item1 != item2
