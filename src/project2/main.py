from .app import Application
from .data import DemoSource, FileSource
from .objectspace import DataProcessing


def main():
    """Точка входа."""
    source1 = DemoSource("Рынок энергоносителей")
    source2 = FileSource("source1.json", "Биржа металлов")
    proc = DataProcessing()
    sources = [source1,source2]
    app = Application(sources,proc)
    app.run()

