from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from project2.web_parsing.alphavantage_api import AlphaVantageParser, RateLimiter

SAMPLE_API_RESPONSE = {
    "Time Series (Daily)": {
        "2024-01-15": {
            "1. open": "100.0",
            "2. high": "105.0",
            "3. low": "98.0",
            "4. close": "102.5",
            "5. volume": "1000000",
        },
        "2024-01-16": {
            "1. open": "102.5",
            "2. high": "108.0",
            "3. low": "101.0",
            "4. close": "107.0",
            "5. volume": "1200000",
        },
    }
}

SAMPLE_ERROR_RESPONSE = {
    "Error Message": "Invalid API call. Please retry."
}

SAMPLE_NOTE_RESPONSE = {
    "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day."
}


class TestRateLimiter:
    """Тесты RateLimiter."""

    @pytest.mark.asyncio
    async def test_acquire_does_not_block_first_call(self):
        """Первый вызов acquire не блокирует."""
        limiter = RateLimiter(rate=10.0)
        await limiter.acquire()

    @pytest.mark.asyncio
    async def test_acquire_with_zero_rate(self):
        """Лимитер с rate=0 не блокирует."""
        limiter = RateLimiter(rate=0.0)
        await limiter.acquire()


class TestAlphaVantageParser:
    """Тесты AlphaVantageParser."""

    @pytest.fixture
    def parser(self):
        return AlphaVantageParser(
            api_key="test_key",
            source_name="test",
            max_concurrency=2,
            rate_per_second=100.0,
            max_attempts=2,
        )

    def test_init_sets_attributes(self, parser):
        """Парсер корректно инициализируется."""
        assert parser.api_key == "test_key"
        assert parser.name == "test"
        assert parser.requests_total == 0
        assert parser.requests_ok == 0
        assert parser.requests_failed == 0
        assert parser.retries == 0

    def test_parse_response_extracts_data(self, parser):
        """Разбор корректного JSON-ответа API."""
        result = parser._parse_response("XOM", "нефть", SAMPLE_API_RESPONSE)
        assert len(result) == 2
        assert result[0].name == "нефть"
        assert result[0].price == 102.5
        assert result[0].seller.get_name == "Global Market"
        assert result[0].seller.get_id == 999
        assert "XOM" in result[0].note

    def test_parse_response_empty_timeseries(self, parser):
        """Пустой Time Series — пустой результат."""
        response = {"Time Series (Daily)": {}}
        result = parser._parse_response("XOM", "нефть", response)
        assert len(result) == 0

    def test_parse_response_missing_timeseries(self, parser):
        """Отсутствие Time Series — пустой результат."""
        response = {"Other Data": {}}
        result = parser._parse_response("XOM", "нефть", response)
        assert len(result) == 0

    def test_parse_response_skips_zero_price(self, parser):
        """Записи с нулевой ценой пропускаются."""
        response = {
            "Time Series (Daily)": {
                "2024-01-15": {
                    "4. close": "0.0",
                },
                "2024-01-16": {
                    "4. close": "100.0",
                },
            }
        }
        result = parser._parse_response("XOM", "нефть", response)
        assert len(result) == 1
        assert result[0].price == 100.0

    def test_parse_response_handles_30_days_only(self, parser):
        """Берутся только первые 30 дней."""
        response = {
            "Time Series (Daily)": {
                f"2024-01-{i:02d}": {"4. close": "100.0"}
                for i in range(1, 32)
            }
        }
        result = parser._parse_response("XOM", "нефть", response)
        assert len(result) == 30

    def test_parse_retry_after_numeric(self, parser):
        """Разбор Retry-After в формате числа."""
        assert parser._parse_retry_after("30") == 30.0

    def test_parse_retry_after_empty(self, parser):
        """Пустой Retry-After — 5 секунд по умолчанию."""
        assert parser._parse_retry_after("") == 5.0

    def test_handle_success_valid_response(self, parser):
        """Успешный ответ 200."""
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_API_RESPONSE
        result = parser._handle_success("XOM", "нефть", mock_response)
        assert len(result) == 2
        assert parser.requests_ok == 1

    def test_handle_success_error_message(self, parser):
        """Ответ 200 с Error Message."""
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_ERROR_RESPONSE
        result = parser._handle_success("XOM", "нефть", mock_response)
        assert result is None
        assert parser.requests_failed == 1

    def test_handle_success_note_message(self, parser):
        """Ответ 200 с Note (лимит API)."""
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_NOTE_RESPONSE
        result = parser._handle_success("XOM", "нефть", mock_response)
        assert result is None
        assert parser.requests_failed == 1
        assert parser.server_limits == 1

    @pytest.mark.asyncio
    async def test_make_request_success(self, parser):
        """Успешный HTTP-запрос."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_API_RESPONSE

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await parser._make_request(mock_client, "XOM", "нефть", 1)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_make_request_client_error_4xx(self, parser):
        """Ошибка 4xx — возвращает None."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await parser._make_request(mock_client, "XOM", "нефть", 1)
        assert result is None
        assert parser.requests_failed == 1

    @pytest.mark.asyncio
    async def test_make_request_server_error_5xx_retry(self, parser):
        """Ошибка 5xx — возвращает None для повторной попытки."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await parser._make_request(mock_client, "XOM", "нефть", 1)
        assert result is None
        assert parser.retries == 1

    @pytest.mark.asyncio
    async def test_transport_error_backoff(self, parser):
        """Транспортная ошибка с backoff."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        result = await parser._make_request(mock_client, "XOM", "нефть", 1)
        assert result is None
        assert parser.retries == 1

    @pytest.mark.asyncio
    async def test_transport_error_final_attempt(self, parser):
        """Транспортная ошибка на последней попытке."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        result = await parser._make_request(mock_client, "XOM", "нефть", 3)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_data_async_yields_data(self, parser):
        """Потоковая отдача данных."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_API_RESPONSE

        mock_client_context = AsyncMock()
        mock_client_context.__aenter__.return_value = mock_client_context
        mock_client_context.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client_context):
            results = []
            async for item in parser.get_data_async():
                results.append(item)

        assert len(results) > 0
        assert parser.requests_total > 0
