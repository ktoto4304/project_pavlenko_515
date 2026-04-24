from abc import ABC, abstractmethod
from typing import Any

from .data import AsyncDemoSource, AsyncFileSource, DemoSource, FileSource, Source


class SourceFactory(ABC):
    """Абстрактная фабрика для создания источников данных."""
    @abstractmethod
    def create_source(self, config: dict[str, Any]) -> Source:
        """Создает источник данных на основе конфигурации."""
        pass


class DemoSourceFactory(SourceFactory):
    """Фабрика для создания источников demo."""
    def create_source(self, config: dict[str, Any]) -> DemoSource:
        """Создает источник данных demo."""
        return DemoSource(config["name"])


class FileSourceFactory(SourceFactory):
    """Фабрика для создания источников file."""
    def create_source(self, config: dict[str, Any]) -> FileSource:
        """Создает источник данных file."""
        return FileSource(config["filename"], config["name"])


class AsyncDemoSourceFactory(SourceFactory):
    """Фабрика для создания асинхронных источников demo."""
    def create_source(self, config: dict[str, Any]) -> AsyncDemoSource:
        """Создает асинхронный источник данных demo."""
        return AsyncDemoSource(config["name"], config.get("delay", 0.1))


class AsyncFileSourceFactory(SourceFactory):
    """Фабрика для создания асинхронных источников file."""
    def create_source(self, config: dict[str, Any]) -> AsyncFileSource:
        """Создает асинхронный источник данных file."""
        return AsyncFileSource(config["filename"], config["name"], config.get("delay", 0.2))


class FactoryRegister:
    """Регистрация фабрик источников данных."""
    def __init__(self) -> None:
        """Инициализирует реестр фабрик."""
        self._factories: dict[str, SourceFactory] = {}

    def register(self, type: str, factory: SourceFactory) -> None:
        """Регистрирует фабрику для указанного типа источника."""
        self._factories[type] = factory

    def create_source(self, type: str, config: dict[str, Any]) -> Source:
        """Создает источник данных указанного типа."""
        return self._factories[type].create_source(config)


_default_registry = FactoryRegister()
_default_registry.register('demo', DemoSourceFactory())
_default_registry.register('file', FileSourceFactory())
_default_registry.register('async_demo', AsyncDemoSourceFactory())
_default_registry.register('async_file', AsyncFileSourceFactory())


def create_source(type: str, config: dict[str, Any]) -> Source:
    """Создает источник данных через реестр фабрик."""
    return _default_registry.create_source(type, config)