from ..config import get_config
from .alphavantage_api import AlphaVantageParser


class ParserFactory:
    """Фабрика веб-парсеров."""
    @staticmethod
    def create_parser(parser_type: str, **kwargs) -> "AlphaVantageParser | None":
        """Создаёт веб-парсер."""
        if parser_type == "alpha_vantage":
            api_key = kwargs.get("api_key")
            if not api_key:
                print("Alpha Vantage API ключ не настроен")
                return None
            config = get_config()
            return AlphaVantageParser(
                api_key=api_key,
                source_name=kwargs.get("source_name", "Alpha Vantage"),
                max_concurrency=config.web_max_concurrency,
                rate_per_second=config.web_rate_per_second,
                max_attempts=config.web_max_attempts,
                base_delay=config.web_base_delay,
                connect_timeout=config.web_connect_timeout,
                read_timeout=config.web_read_timeout,
                write_timeout=config.web_write_timeout,
                pool_timeout=config.web_pool_timeout,
            )
        print(f"Неизвестный тип парсера: {parser_type}")
        return None


_parser_factory = ParserFactory()


def create_web_parser(parser_type: str, **kwargs) -> "AlphaVantageParser | None":
    """Создаёт веб-парсер через фабрику."""
    return _parser_factory.create_parser(parser_type, **kwargs)
