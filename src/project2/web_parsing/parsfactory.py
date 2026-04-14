
from .abtract_pars import WebParser
from .alphavantage_api import AlphaVantageParser


class ParserFactory:
    """Фабрика для создания веб-парсеров."""

    @staticmethod
    def create_parser(parser_type: str, **kwargs) -> WebParser | None:
        """Создает парсер указанного типа."""
        if parser_type == "alpha_vantage":
            api_key = kwargs.get("api_key")
            if not api_key:
                print("Alpha Vantage API ключ не настроен")
                return None
            return AlphaVantageParser(api_key, kwargs.get("source_name", "Alpha Vantage"))
        print(f"Неизвестный тип парсера: {parser_type}")
        return None
_parser_factory = ParserFactory()
def create_web_parser(parser_type: str, **kwargs) -> WebParser | None:
    """Создает веб-парсер."""
    return _parser_factory.create_parser(parser_type, **kwargs)
