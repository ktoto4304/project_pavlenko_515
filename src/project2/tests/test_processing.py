import pytest

from project2.data import Data
from project2.objectspace import CommodityProcessing


class TestCommodityProcessing:
    """Тесты CommodityProcessing."""

    @pytest.fixture
    def processor(self):
        return CommodityProcessing(name="test_processor")

    def test_normalize_lowercase(self, processor, sample_data_list):
        """Нормализация приводит названия к нижнему регистру."""
        test_data = Data(
            name="НЕФТЬ", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        result = list(processor.normalizing(iter([test_data])))
        assert result[0][0].name == "нефть"
        assert result[0][1] is True

    def test_normalize_already_lowercase(self, processor):
        """Уже строчное название не меняется."""
        test_data = Data(
            name="нефть", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        result = list(processor.normalizing(iter([test_data])))
        assert result[0][0].name == "нефть"
        assert result[0][1] is False

    def test_normalize_whitespace(self, processor):
        """Нормализация удаляет пробелы по краям."""
        test_data = Data(
            name="  нефть  ", seller_name="Лукойл", price=4500.0,
            seller_id=4, source="test"
        )
        result = list(processor.normalizing(iter([test_data])))
        assert result[0][0].name == "нефть"

    def test_filter_category_finds_match(self, processor, sample_data_list):
        """Фильтрация по категории находит совпадения."""
        result = list(processor.filter_category(iter(sample_data_list), "нефть"))
        assert len(result) == 2
        assert all(item.name == "нефть" for item in result)

    def test_filter_category_no_match(self, processor, sample_data_list):
        """Фильтрация по несуществующей категории возвращает пусто."""
        result = list(processor.filter_category(iter(sample_data_list), "уран"))
        assert len(result) == 0

    def test_filter_price_in_range(self, processor, sample_data_list):
        """Фильтрация по диапазону цен."""
        result = list(processor.filter_price(iter(sample_data_list), "1000.0-2000.0"))
        assert len(result) == 2
        assert all(1000.0 <= item.price <= 2000.0 for item in result)

    def test_filter_price_no_match(self, processor, sample_data_list):
        """Цена вне диапазона — пустой результат."""
        result = list(processor.filter_price(iter(sample_data_list), "100.0-200.0"))
        assert len(result) == 0

    def test_filter_price_invalid_format(self, processor, sample_data_list):
        """Некорректный формат диапазона — пустой результат."""
        result = list(processor.filter_price(iter(sample_data_list), "invalid"))
        assert len(result) == 0

    def test_filter_seller_finds_match(self, processor, sample_data_list):
        """Фильтрация по продавцу."""
        result = list(processor.filter_seller(iter(sample_data_list), "Газпром"))
        assert len(result) == 2
        assert all(item.seller.get_name == "Газпром" for item in result)

    def test_filter_seller_no_match(self, processor, sample_data_list):
        """Несуществующий продавец — пустой результат."""
        result = list(processor.filter_seller(iter(sample_data_list), "Неизвестный"))
        assert len(result) == 0

    def test_average_price(self, processor, sample_data_list):
        """Расчёт средней цены."""
        avg = processor.average_price(iter(sample_data_list))
        expected = sum(item.price for item in sample_data_list) / len(sample_data_list)
        assert avg == pytest.approx(expected)

    def test_average_price_empty(self, processor, empty_data_list):
        """Средняя цена пустого списка — ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError):
            processor.average_price(iter(empty_data_list))

    def test_register_filter_and_use(self, processor, sample_data_list):
        """Регистрация фильтра и его использование."""
        processor.filter_registration("Category", processor.filter_category)
        result = list(processor.filter("Category", iter(sample_data_list), "золото"))
        assert len(result) == 2

    def test_filter_unregistered_key_raises(self, processor, sample_data_list):
        """Обращение к незарегистрированному фильтру вызывает ошибку."""
        with pytest.raises(ValueError):
            list(processor.filter("Unknown", iter(sample_data_list), "test"))
