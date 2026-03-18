from abc import ABC, abstractmethod
from typing import Any

from .data import DemoSource, FileSource, Source


class SourceFactory(ABC):
    """Абстрактная фабрика для создания источников данных."""
    @abstractmethod
    def create_source(self, config: dict[str,Any]) -> Source:
        """Создает источник данных на основе конфигурации."""
        pass
class DemoSourceFactory(SourceFactory):
    """Фабрика для создания источников demo."""
    def create_source(self, config: dict[str,Any]) -> DemoSource:
        """Создает источник данных demo."""
        name = config["name"]
        return DemoSource(name)
class FileSourceFactory(SourceFactory):
    """Фабрика для создания источников file."""
    def create_source(self, config: dict[str,Any]) -> FileSource:
        """Создает источник данных file."""
        name = config["name"]
        filename = config["filename"]
        return FileSource(filename,name)
class FactoryRegister:
    """Регистрация фабрики."""
    def __init__(self):
        self._factories = {}
    def register(self,type: str, factory: SourceFactory) -> None:
        self._factories[type] = factory
    def create_source(self, type: str,config: dict[str, Any]) -> Source:
        return self._factories[type].create_source(config)
_default_registry = FactoryRegister()
_default_registry.register('demo', DemoSourceFactory())
_default_registry.register('file', FileSourceFactory())
def create_source(type: str,config: dict[str,Any]) -> Source:
    """Создает источник данных."""
    return _default_registry.create_source(type,config)
