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


def main():
    """Точка входа."""
    config = get_config()
    source1 = create_source("demo", {"name": config.demo_source_name})
    source2 = create_source("file", {"filename": config.file_source_path, "name": config.file_source_name})
    sources = [source1, source2]
    web_file = create_web_source_file(config.web_api_url, config.web_source_path)
    if web_file and os.path.exists(web_file):
        source3 = create_source("file", {"filename": web_file, "name": config.web_source_name})
        sources.append(source3)
    strategy = CompositeStrategy([NormalizationStrategy(),FilterStrategy(),StatisticsStrategy()])
    app = Application(sources, strategy)
    app.run()
