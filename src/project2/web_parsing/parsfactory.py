from .alphavantage_api import AlphaVantageParser


class ParserFactory:
    """Фабрика для создания асинхронных веб-источников."""

    @staticmethod
    def create_parser(parser_type: str, **kwargs):
        """Создаёт парсер указанного типа."""
        if parser_type == "alpha_vantage":
            api_key = kwargs.get("api_key")
            if not api_key:
                print("Alpha Vantage API ключ не настроен")
                return None
            return AlphaVantageParser(
                api_key=api_key,
                source_name=kwargs.get("source_name", "Alpha Vantage"),
                max_concurrency=kwargs.get("max_concurrency", 2),
                rate_per_second=kwargs.get("rate_per_second", 0.1),
                max_attempts=kwargs.get("max_attempts", 3),
            )
        print(f"Неизвестный тип парсера: {parser_type}")
        return None


_parser_factory = ParserFactory()


def create_web_parser(parser_type: str, **kwargs):
    """Создаёт веб-парсер через фабрику."""
    return _parser_factory.create_parser(parser_type, **kwargs)
