import os

from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    """Конфигурация приложения."""
    _instance = None

    def __new__(cls) -> 'AppConfig':
        """Создает или возвращает существующий экземпляр."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Инициализация конфигурации."""
        if self._initialized:
            return
        self.demo_source_name: str = "Рынок Энергоносителей"
        self.file_source_name: str = "Биржа металлов"
        self.file_source_path: str = "source1.json"
        self.web_source_name: str = "Веб-парсер (Мировые цены)"
        self.web_parser_type: str = "alpha_vantage"
        self.web_source_path: str = "web_source_data.json"
        self.web_api_url: str = "https://www.alphavantage.co/query"
        self.alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.categories: list[str] = ["нефть", "газ", "золото", "медь"]
        self.price_range: str = "1000.0-5000.0"
        self.seller: str = "Норникель"
        self.strategy_type: str = "composite"
        self.execution_mode: str = "processes"
        self.chunk_size: int = 50
        self.test_mode: bool = False
        self.test_data_size: int = 10000
        self.run_mode: str = "hybrid"
        self.max_workers: int = 4
        self.hybrid_executor: str = "threads"
        self._initialized: bool = True
        if not self.alpha_vantage_api_key:
            print("ВНИМАНИЕ: ALPHA_VANTAGE_API_KEY не найден в .env файле")

    def __str__(self) -> str:
        """Строковое представление конфигурации."""
        return (f"AppConfig(demo='{self.demo_source_name}', "
                f"file='{self.file_source_name}', web='{self.web_source_name}')")


def get_config() -> AppConfig:
    """Возвращает глобальный экземпляр конфигурации."""
    return AppConfig()
