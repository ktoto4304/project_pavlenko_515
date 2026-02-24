from .app import Application
from .data import DemoSource, FileSource
from .objectspace import CommodityProcessing


def main():
    """Точка входа."""
    source1 = DemoSource("Рынок энергоносителей")
    source2 = FileSource("source1.json", "Биржа металлов")
    proc = CommodityProcessing()
    sources = [source1,source2]
    app = Application(sources,proc)
    app.run()

