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
from .web_parsing import create_web_source_file


def main() -> None:
    """Точка входа."""
    config = get_config()
    if config.run_mode == "async":
        source1 = create_source("async_demo", {"name": config.demo_source_name, "delay": 0.1})
        source2 = create_source("async_file", {"filename": config.file_source_path, "name": config.file_source_name, "delay": 0.2})
        sources = [source1, source2]
        if os.path.exists(config.web_source_path):
            source3 = create_source("async_file", {"filename": config.web_source_path, "name": config.web_source_name, "delay": 0.2})
            sources.append(source3)
        strategy = CompositeStrategy([NormalizationStrategy(), FilterStrategy(), StatisticsStrategy()])
        app = Application([], strategy)
        for src in sources:
            app.add_async_source(src)
        asyncio.run(app.run_async())
    elif config.run_mode == "hybrid":
        source1 = create_source("async_demo", {"name": config.demo_source_name, "delay": 0})
        source2 = create_source("async_file", {"filename": config.file_source_path, "name": config.file_source_name, "delay": 0})
        sources = [source1, source2]
        if os.path.exists(config.web_source_path):
            source3 = create_source("async_file", {"filename": config.web_source_path, "name": config.web_source_name, "delay": 0})
            sources.append(source3)
        strategy = CompositeStrategy([NormalizationStrategy(), FilterStrategy(), StatisticsStrategy()])
        app = Application([], strategy)
        for src in sources:
            app.add_async_source(src)
        asyncio.run(app.run_hybrid())
    elif config.run_mode == "sync_delay":
        source1 = create_source("demo", {"name": config.demo_source_name})
        source2 = create_source("file", {"filename": config.file_source_path, "name": config.file_source_name})
        sources = [source1, source2]
        if os.path.exists(config.web_source_path):
            source3 = create_source("file", {"filename": config.web_source_path, "name": config.web_source_name})
            sources.append(source3)
        strategy = CompositeStrategy([NormalizationStrategy(), FilterStrategy(), StatisticsStrategy()])
        app = Application(sources, strategy)
        app.run_with_delay()
    else:
        source1 = create_source("demo", {"name": config.demo_source_name})
        source2 = create_source("file", {"filename": config.file_source_path, "name": config.file_source_name})
        sources = [source1, source2]
        web_file = create_web_source_file(config.web_api_url, config.web_source_path)
        if web_file and os.path.exists(web_file):
            source3 = create_source("file", {"filename": web_file, "name": config.web_source_name})
            sources.append(source3)
        strategy = CompositeStrategy([NormalizationStrategy(), FilterStrategy(), StatisticsStrategy()])
        app = Application(sources, strategy)
        app.run()
