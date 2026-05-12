import pytest

from project2.app_runner import AppRunner


class TestAppRunner:
    """Тесты AppRunner."""

    def test_format_summary_structure(self, sample_data_list):
        """Сводка имеет правильную структуру."""
        summary = AppRunner.format_summary(sample_data_list, 1.5)
        assert "total_records" in summary
        assert "total_time" in summary
        assert "categories" in summary
        assert "sellers" in summary
        assert "avg_price" in summary
        assert "data" in summary
        assert "metrics" in summary

    def test_format_summary_counts_categories(self, sample_data_list):
        """Правильный подсчёт категорий."""
        summary = AppRunner.format_summary(sample_data_list, 1.5)
        assert summary["total_records"] == 8
        assert summary["categories"]["нефть"] == 2
        assert summary["categories"]["газ"] == 2
        assert summary["categories"]["золото"] == 2
        assert summary["categories"]["медь"] == 2

    def test_format_summary_counts_sellers(self, sample_data_list):
        """Правильный подсчёт продавцов."""
        summary = AppRunner.format_summary(sample_data_list, 1.5)
        assert summary["sellers"]["Газпром"] == 2
        assert summary["sellers"]["Норникель"] == 2

    def test_format_summary_avg_price(self, sample_data_list):
        """Правильный расчёт средней цены."""
        summary = AppRunner.format_summary(sample_data_list, 1.5)
        expected = sum(item.price for item in sample_data_list) / 8
        assert summary["avg_price"] == pytest.approx(expected)

    def test_format_summary_empty_list(self, empty_data_list):
        """Сводка для пустого списка."""
        summary = AppRunner.format_summary(empty_data_list, 0.0)
        assert summary["total_records"] == 0
        assert summary["avg_price"] == 0

    def test_format_summary_with_metrics(self, sample_data_list):
        """Метрики передаются в сводку."""
        metrics = {"source": {"requests_total": 5}}
        summary = AppRunner.format_summary(sample_data_list, 1.5, metrics)
        assert summary["metrics"] == metrics

    def test_format_console_message_contains_info(self, sample_data_list):
        """Консольное сообщение содержит ключевую информацию."""
        summary = AppRunner.format_summary(sample_data_list, 1.5)
        message = AppRunner.format_console_message(summary)
        assert "РЕЗУЛЬТАТЫ" in message
        assert str(summary["total_records"]) in message
