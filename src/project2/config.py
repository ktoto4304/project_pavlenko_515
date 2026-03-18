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
        """Инициализация конфигурации (только один раз)."""
        if self._initialized:
            return
        self.demo_source_name = "Рынок Энергоносителей"
        self.file_source_name = "Биржа металлов"
        self.file_source_path = "source1.json"
        self.categories = ["нефть", "газ", "золото", "медь"]
        self.price_range = "1000.0-5000.0"
        self.seller = "Норникель"
        self.strategy_type = "composite"
        self._initialized = True

    def __str__(self):
        """Строковое представление конфигурации."""
        return f"AppConfig(demo='{self.demo_source_name}', file='{self.file_source_name}')"
def get_config() -> AppConfig:
    """Возвращает глобальный экземпляр конфигурации."""
    return AppConfig()
