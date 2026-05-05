import asyncio
import os

from .app import Application
from .config import get_config
from .processing_strategies import (
    CompositeStrategy,
    FilterStrategy,
    NormalizationStrategy,
    StatisticsStrategy,
)
from .sourcefactory import create_source


def main() -> None:
    """Точка входа."""
    config = get_config()
    if config.run_mode == "async":
        _run_async_mode(config)
    elif config.run_mode == "hybrid":
        _run_hybrid_mode(config)
    elif config.run_mode == "sync_delay":
        _run_sync_delay_mode(config)
    else:
        _run_sync_mode(config)


def _run_async_mode(config) -> None:
    """Асинхронный режим: все источники асинхронные, включая веб."""
    source1 = create_source("async_demo", {
        "name": config.demo_source_name, "delay": 0.1
    })
    source2 = create_source("async_file", {
        "filename": config.file_source_path,
        "name": config.file_source_name,
        "delay": 0.2,
    })
    strategy = CompositeStrategy([
        NormalizationStrategy(),
        FilterStrategy(),
        StatisticsStrategy(),
    ])
    app = Application([], strategy)
    app.add_async_source(source1)
    app.add_async_source(source2)
    asyncio.run(app.run_async())


def _run_hybrid_mode(config) -> None:
    """Гибридный режим: асинхронный сбор + обработка через executor."""
    source1 = create_source("async_demo", {
        "name": config.demo_source_name, "delay": 0
    })
    source2 = create_source("async_file", {
        "filename": config.file_source_path,
        "name": config.file_source_name,
        "delay": 0,
    })
    strategy = CompositeStrategy([
        NormalizationStrategy(),
        FilterStrategy(),
        StatisticsStrategy(),
    ])
    app = Application([], strategy)
    app.add_async_source(source1)
    app.add_async_source(source2)
    asyncio.run(app.run_hybrid())


def _run_sync_delay_mode(config) -> None:
    """Синхронный режим с задержками."""
    source1 = create_source("demo", {"name": config.demo_source_name})
    source2 = create_source("file", {
        "filename": config.file_source_path,
        "name": config.file_source_name,
    })
    sources = [source1, source2]
    if os.path.exists(config.web_source_path):
        source3 = create_source("file", {
            "filename": config.web_source_path,
            "name": config.web_source_name,
        })
        sources.append(source3)
    strategy = CompositeStrategy([
        NormalizationStrategy(),
        FilterStrategy(),
        StatisticsStrategy(),
    ])
    app = Application(sources, strategy)
    app.run_with_delay()


def _run_sync_mode(config) -> None:
    """Обычный синхронный режим."""
    source1 = create_source("demo", {"name": config.demo_source_name})
    source2 = create_source("file", {
        "filename": config.file_source_path,
        "name": config.file_source_name,
    })
    sources = [source1, source2]
    if os.path.exists(config.web_source_path):
        source3 = create_source("file", {
            "filename": config.web_source_path,
            "name": config.web_source_name,
        })
        sources.append(source3)
    strategy = CompositeStrategy([
        NormalizationStrategy(),
        FilterStrategy(),
        StatisticsStrategy(),
    ])
    app = Application(sources, strategy)
    app.run()
