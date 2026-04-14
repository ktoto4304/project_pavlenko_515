import json
import os
import time
from typing import Any

import requests

from ..config import get_config
from .abtract_pars import WebParser


class AlphaVantageParser(WebParser):
    """Парсер для Alpha Vantage API с задержками между запросами."""

    def __init__(self, api_key: str, source_name: str = "Alpha Vantage"):
        self.api_key = api_key
        self.source_name = source_name
        self.data: list[dict[str, Any]] | None = None
        self.config = get_config()
        self.base_url = self.config.web_api_url
        self.request_delay = 12

    def fetch_data(self) -> list[dict[str, Any]] | None:
        """Получает данные напрямую из API."""
        if os.path.exists(self.config.web_source_path):
            print("Используем существующий файл веб-источника")
            return self._load_existing_data()
        print("Запрос данных из Alpha Vantage API...")
        api_data = self._fetch_from_api()
        if api_data:
            processed_data = self._process_api_response(api_data)
            if processed_data:
                self.data = processed_data
                print(f"Получено {len(self.data)} записей из API")
                return self.data
            print("Не удалось обработать данные из API")
            return None
        print("ОШИБКА: API недоступен")
        return None

    def _fetch_from_api(self) -> dict[str, Any] | None:
        """Выполняет запросы к API со всеми символами и задержками."""
        symbols = {'XOM': 'нефть', 'FCX': 'медь', 'GDX': 'золото', 'SLV': 'серебро','UNG': 'газ'}
        all_data = {}
        for i, (symbol, commodity_name) in enumerate(symbols.items(), 1):
            print(f"\n[{i}/{len(symbols)}] Запрос данных для {commodity_name} ({symbol})...")
            params = {"function": "TIME_SERIES_DAILY","symbol": symbol, "apikey": self.api_key,"outputsize": "compact"}
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "Error Message" in data:
                print(f"Ошибка API для {symbol}: {data['Error Message']}")
                continue
            if "Note" in data:
                print(f"API ограничение для {symbol}: {data['Note']}")
                print(f"Ожидание {self.request_delay * 2} секунд...")
                time.sleep(self.request_delay * 2)
                response = requests.get(self.base_url, params=params, timeout=30)
                data = response.json()
                if "Error Message" in data or "Note" in data:
                    print("Повторный запрос также не удался")
                    continue
            if "Time Series (Daily)" in data:
                all_data[symbol] = data
                print(f"Успешно получены данные для {commodity_name}")
                time_series = data["Time Series (Daily)"]
                print(f"Получено {len(time_series)} дней данных")
            if i < len(symbols):
                print(f"Ожидание {self.request_delay} секунд перед следующим запросом...")
                time.sleep(self.request_delay)
        return all_data if all_data else None

    def _load_existing_data(self) -> list[dict[str, Any]] | None:
        """Загружает существующие данные из файла."""
        with open(self.config.web_source_path, encoding='utf-8') as f:
            data = []
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
            self.data = data
            print(f"Загружено {len(self.data)} записей из файла")
            return data

    def _process_api_response(self, data: dict) -> list[dict[str, Any]]:
        """Обрабатывает ответ API и преобразует в нужный формат."""
        all_data = []
        for symbol, content in data.items():
            commodity_name = self._get_commodity_name(symbol)
            if not commodity_name:
                print(f"Неизвестный символ: {symbol}")
                continue

            time_series = content.get("Time Series (Daily)", {})
            if not time_series:
                continue
            records_added = 0
            for date, values in list(time_series.items())[:30]:
                price = float(values.get("4. close", 0))
                if price > 0:
                    all_data.append({"name": commodity_name,"seller": "Global Market",
                        "seller_id": 999,"price": round(price, 2),
                        "note": f"{self.source_name}, символ: {symbol}, дата: {date}"})
                    records_added += 1
            print(f"Добавлено {records_added} записей для {commodity_name}")

        if not all_data:
            print("Не удалось получить данные из API")
            return []
        return all_data

    def _get_commodity_name(self, symbol: str) -> str:
        """Определяет название сырья по символу."""
        mapping = {'XOM': 'нефть', 'FCX': 'медь', 'GDX': 'золото', 'SLV': 'серебро','UNG': 'газ'}
        return mapping.get(symbol, '')

    def save_to_file(self, filename: str) -> bool:
        """Сохраняет данные в файл."""
        if not self.data:
            print("Нет данных для сохранения")
            return False
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            for item in self.data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        print(f"Данные сохранены в {filename}")
        commodities = {}
        for item in self.data:
            name = item['name']
            commodities[name] = commodities.get(name, 0) + 1
        return True
