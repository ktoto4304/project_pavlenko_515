from typing import Any

from .app import Application
from .config import get_config
from .data import Data
from .processing_strategies import (
    CompositeStrategy,
    FilterStrategy,
    NormalizationStrategy,
    StatisticsStrategy,
)
from .sourcefactory import create_source


class AppRunner:
    """Единая точка запуска приложения."""

    def __init__(self) -> None:
        self.config = get_config()

    def _build_app(self) -> Application:
        """Собирает Application с источниками и стратегией."""
        strategy = CompositeStrategy([
            NormalizationStrategy(),
            FilterStrategy(),
            StatisticsStrategy(),
        ])

        app = Application([], strategy)

        if self.config.run_mode in ("async", "hybrid"):
            source1 = create_source("async_demo", {
                "name": self.config.demo_source_name,
                "delay": 0.1,
            })
            source2 = create_source("async_file", {
                "filename": self.config.file_source_path,
                "name": self.config.file_source_name,
                "delay": 0.2,
            })
            app.add_async_source(source1)
            app.add_async_source(source2)
        else:
            source1 = create_source("demo", {
                "name": self.config.demo_source_name,
            })
            source2 = create_source("file", {
                "filename": self.config.file_source_path,
                "name": self.config.file_source_name,
            })
            app.sources = [source1, source2]

        return app
    @staticmethod
    def format_console_message(summary: dict[str, Any]) -> str:
        """Форматирует сводку для консольного вывода."""
        lines = [
            "=" * 60,
            "РЕЗУЛЬТАТЫ ОБРАБОТКИ",
            "=" * 60,
            f"Обработано записей: {summary['total_records']}",
            f"Общее время: {summary['total_time']} сек",
            f"Средняя цена: {summary['avg_price']}",
            "",
            f"Категории: {summary['categories']}",
            f"Продавцы: {summary['sellers']}",
        ]
        metrics = summary.get("metrics", {})
        if metrics:
            lines.append(f"\nМетрики веб-парсера: {metrics}")
        return "\n".join(lines)
    @staticmethod
    def format_summary(data: list[Data], total_time: float, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
        """Формирует структурированную сводку."""
        categories: dict[str, int] = {}
        sellers: dict[str, int] = {}
        total_price: float = 0.0

        for item in data:
            categories[item.name] = categories.get(item.name, 0) + 1
            sellers[item.seller.get_name] = sellers.get(item.seller.get_name, 0) + 1
            total_price += item.price

        return {
            "total_records": len(data),
            "total_time": round(total_time, 4),
            "categories": categories,
            "sellers": sellers,
            "avg_price": round(total_price / len(data), 2) if data else 0,
            "data": data,
            "metrics": metrics or {},
        }

    def print_summary(self, summary: dict[str, Any]) -> None:
        """Выводит сводку в консоль (для main.py)."""
        print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
        print(f"Обработано записей: {summary['total_records']}")
        print(f"Общее время: {summary['total_time']} сек")
        print(f"Средняя цена: {summary['avg_price']}")
        print(f"\nКатегории: {summary['categories']}")
        print(f"Продавцы: {summary['sellers']}")

        if summary["metrics"]:
            print(f"\nМетрики веб-парсера: {summary['metrics']}")

    def run_sync(self) -> dict[str, Any]:
        """Синхронный запуск. Возвращает сводку."""
        app = self._build_app()
        app.setup_web_source()
        data, total_time = app.run()
        return self.format_summary(data, total_time)

    def run_sync_with_delay(self) -> dict[str, Any]:
        """Синхронный запуск с задержками. Возвращает сводку."""
        app = self._build_app()
        app.setup_web_source()
        data, total_time = app.run_with_delay()
        return self.format_summary(data, total_time)

    async def run_async(self) -> dict[str, Any]:
        """Асинхронный запуск. Возвращает сводку с метриками."""
        app = self._build_app()
        app.setup_web_source()
        data, total_time = await app.run_async()

        metrics = {}
        for source in app.async_sources:
            if hasattr(source, "requests_total"):
                metrics[source.name] = {
                    "requests_total": source.requests_total,
                    "requests_ok": source.requests_ok,
                    "requests_failed": source.requests_failed,
                    "retries": source.retries,
                    "items_collected": source.items_collected,
                }

        return self.format_summary(data, total_time, metrics)

    async def run_hybrid(self) -> dict[str, Any]:
        """Гибридный запуск. Возвращает сводку с метриками."""
        app = self._build_app()
        app.setup_web_source()
        data, total_time = await app.run_hybrid()

        metrics = {}
        for source in app.async_sources:
            if hasattr(source, "requests_total"):
                metrics[source.name] = {
                    "requests_total": source.requests_total,
                    "requests_ok": source.requests_ok,
                    "requests_failed": source.requests_failed,
                    "retries": source.retries,
                    "items_collected": source.items_collected,
                }

        return self.format_summary(data, total_time, metrics)
