import asyncio
import random
import time
from collections.abc import AsyncIterator
from datetime import UTC

import httpx

from ..config import get_config
from ..data import AsyncSource, Data


class RateLimiter:
    """Token-bucket rate limiter для asyncio."""
    def __init__(self, rate: float) -> None:
        self._interval = 1.0 / rate if rate > 0 else 0.0
        self._lock = asyncio.Lock()
        self._next_time = 0.0

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = max(0.0, self._next_time - now)
            self._next_time = max(now, self._next_time) + self._interval
        if wait > 0:
            await asyncio.sleep(wait)


class AlphaVantageParser(AsyncSource):
    """Асинхронный потоковый источник с Alpha Vantage API."""
    def __init__(
        self,
        api_key: str,
        source_name: str = "Alpha Vantage",
        max_concurrency: int = 2,
        rate_per_second: float = 0.1,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        connect_timeout: float = 5.0,
        read_timeout: float = 15.0,
        write_timeout: float = 5.0,
        pool_timeout: float = 2.0,
    ) -> None:
        super().__init__(source_name, "async_web")
        self.api_key = api_key
        self.config = get_config()
        self.base_url = self.config.web_api_url

        self._sem = asyncio.Semaphore(max_concurrency)
        self._limiter = RateLimiter(rate_per_second)

        self.max_attempts = max_attempts
        self.base_delay = base_delay

        self.timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout,
        )
        self.symbols: dict[str, str] = {
            "XOM": "нефть",
            "FCX": "медь",
            "GDX": "золото",
            "SLV": "серебро",
            "UNG": "газ",
        }
        self.requests_total: int = 0
        self.requests_ok: int = 0
        self.requests_failed: int = 0
        self.retries: int = 0
        self.server_limits: int = 0
        self.items_collected: int = 0

    async def get_data_async(self) -> AsyncIterator[Data]:
        """Асинхронный поток данных из API."""
        print("АСИНХРОННЫЙ ВЕБ-ПАРСЕР")
        print(f"Символов: {len(self.symbols)}")
        print(f"Параллелизм: {self._sem._value}, частота: 1 запрос в {1.0 / self._limiter._interval:.0f} сек")
        print(f"Повторных попыток: {self.max_attempts}")
        print(f"Таймауты: connect={self.timeout.connect}s, read={self.timeout.read}s, "
              f"write={self.timeout.write}s, pool={self.timeout.pool}s\n")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [
                asyncio.create_task(self._fetch_symbol(client, sym, name))
                for sym, name in self.symbols.items()
            ]
            for coro in asyncio.as_completed(tasks):
                try:
                    items = await coro
                    if items:
                        for data_item in items:
                            self.items_collected += 1
                            yield data_item
                except asyncio.CancelledError:
                    print("[ERROR] Запрос завершился ошибкой")

        self._print_metrics()

    def _print_metrics(self) -> None:
        """Выводит итоговые метрики."""
        print(f"  Запросов всего:       {self.requests_total}")
        print(f"  Успешных:             {self.requests_ok}")
        print(f"  Неудачных:            {self.requests_failed}")
        print(f"  Повторов:             {self.retries}")
        print(f"  Серверных лимитов:    {self.server_limits}")
        print(f"  Собрано записей:      {self.items_collected}")

    async def _fetch_symbol(
        self, client: httpx.AsyncClient, symbol: str, name: str
    ) -> list[Data] | None:
        """Запрос одного символа с повторными попытками."""
        print(f"[СТАРТ] {name} ({symbol})")

        for attempt in range(1, self.max_attempts + 1):
            result = await self._make_request(client, symbol, name, attempt)
            if result is not None:
                return result

        self.requests_failed += 1
        print(f"[FAIL] {name} ({symbol}): попытки исчерпаны")
        return None

    async def _make_request(
        self, client: httpx.AsyncClient, symbol: str, name: str, attempt: int
    ) -> list[Data] | None:
        """Один HTTP-запрос с ограничениями и обработкой ошибок."""
        async with self._sem:
            await self._limiter.acquire()
            self.requests_total += 1

            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "compact",
            }

            try:
                response = await client.get(self.base_url, params=params)
                status = response.status_code
            except httpx.TransportError as exc:
                return await self._handle_transport_error(symbol, name, attempt, exc)

            if status == 200:
                return self._handle_success(symbol, name, response)

            if status in (429, 503):
                return await self._handle_rate_limit(symbol, name, attempt, response)

            if status >= 500:
                return await self._handle_server_error(symbol, name, attempt, status)

            if 400 <= status < 500:
                print(f"[CLIENT ERROR] {name} ({symbol}): {status}")
                self.requests_failed += 1
                return None

            self.requests_failed += 1
            return None

    def _handle_success(
        self, symbol: str, name: str, response: httpx.Response
    ) -> list[Data] | None:
        """Обрабатывает успешный ответ 200."""
        data = response.json()

        if "Error Message" in data:
            print(f"[API ERROR] {name} ({symbol}): {data['Error Message']}")
            self.requests_failed += 1
            return None

        if "Note" in data:
            print(f"[API LIMIT] {name} ({symbol}): превышена частота запросов")
            self.server_limits += 1
            self.requests_failed += 1
            return None

        self.requests_ok += 1
        items = self._parse_response(symbol, name, data)
        print(f"[OK] {name} ({symbol}): {len(items)} записей")
        return items

    def _parse_response(self, symbol: str, name: str, data: dict) -> list[Data]:
        """Разбирает JSON-ответ в список объектов Data."""
        time_series = data.get("Time Series (Daily)", {})
        result = []
        for date, values in list(time_series.items())[:30]:
            price = float(values.get("4. close", 0))
            if price <= 0:
                continue
            result.append(Data(
                name=name,
                seller_name="Global Market",
                price=round(price, 2),
                seller_id=999,
                source="Alpha Vantage",
                note=f"Символ: {symbol}, дата: {date}",
            ))
        return result

    async def _handle_transport_error(
        self, symbol: str, name: str, attempt: int, exc: Exception
    ) -> list[Data] | None:
        """Обработка транспортной ошибки с exponential backoff и jitter."""
        if attempt < self.max_attempts:
            delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, self.base_delay)
            print(f"[RETRY] {name} ({symbol}): транспортная ошибка, "
                  f"попытка {attempt}/{self.max_attempts}, ждём {delay:.1f}с")
            self.retries += 1
            await asyncio.sleep(delay)
            return None
        print(f"[TRANSPORT ERROR] {name} ({symbol}): {exc!r}")
        return None

    async def _handle_rate_limit(
        self, symbol: str, name: str, attempt: int, response: httpx.Response
    ) -> list[Data] | None:
        """Обработка 429/503 с учётом Retry-After."""
        wait = self._parse_retry_after(response.headers.get("Retry-After", ""))
        print(f"[{response.status_code}] {name} ({symbol}): "
              f"попытка {attempt}/{self.max_attempts}, ждём {wait:.1f}с")
        self.server_limits += 1
        await asyncio.sleep(wait)

        if attempt < self.max_attempts:
            self.retries += 1
            return None
        self.requests_failed += 1
        return None

    async def _handle_server_error(
        self, symbol: str, name: str, attempt: int, status: int
    ) -> list[Data] | None:
        """Обработка 5xx с exponential backoff и jitter."""
        if attempt < self.max_attempts:
            delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, self.base_delay)
            print(f"[RETRY] {name} ({symbol}): {status}, "
                  f"попытка {attempt}/{self.max_attempts}, ждём {delay:.1f}с")
            self.retries += 1
            await asyncio.sleep(delay)
            return None
        print(f"[SERVER ERROR] {name} ({symbol}): {status}")
        return None

    @staticmethod
    def _parse_retry_after(header: str) -> float:
        """Разбирает заголовок Retry-After в секунды."""
        header = header.strip()
        if not header:
            return 5.0
        if header.isdigit():
            return float(header)
        try:
            from datetime import datetime
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(header)
            delta = (dt - datetime.now(UTC)).total_seconds()
            return max(0.0, delta)
        except (TypeError, ValueError):
            return 5.0
