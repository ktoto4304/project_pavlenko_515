from .app import Application
from .config import get_config
from .processing_strategies import (
    CompositeStrategy,
    FilterStrategy,
    NormalizationStrategy,
    StatisticsStrategy,
)
from .sourcefactory import create_source


def main():
    """ТОчка входа."""
    config = get_config()
    source1 = create_source("demo", {"name": config.demo_source_name})
    source2 = create_source("file", {"filename": config.file_source_path, "name": config.file_source_name})
    sources = [source1, source2]
    strategy = CompositeStrategy([NormalizationStrategy(),FilterStrategy(),StatisticsStrategy()])
    app = Application(sources, strategy)
    app.run()
