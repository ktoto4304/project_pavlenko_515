import os

from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    """Конфигурация приложения."""
    _instance = None

    def __new__(cls):
        """Создает или возвращает существующий экземпляр."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Инициализация конфигурации."""
        if self._initialized:
            return
        self.demo_source_name = "Рынок Энергоносителей"
        self.file_source_name = "Биржа металлов"
        self.file_source_path = "source1.json"
        self.web_source_name = "Веб-парсер (Мировые цены)"
        self.web_parser_type = "alpha_vantage"
        self.web_source_path = "web_source_data.json"
        self.web_api_url = "https://www.alphavantage.co/query"
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.categories = ["нефть", "газ", "золото", "медь"]
        self.price_range = "1000.0-5000.0"
        self.seller = "Норникель"
        self.strategy_type = "composite"
        self.execution_mode = "processes"
        self.chunk_size = 50
        self.test_mode = False
        self.test_data_size = 10000
        self._initialized = True
        if not self.alpha_vantage_api_key:
            print("ВНИМАНИЕ: ALPHA_VANTAGE_API_KEY не найден в .env файле")

    def __str__(self):
        """Строковое представление конфигурации."""
        return f"AppConfig(demo='{self.demo_source_name}', \
            file='{self.file_source_name}', web='{self.web_source_name}')"

def get_config() -> AppConfig:
    """Возвращает глобальный экземпляр конфигурации."""
    return AppConfig()
