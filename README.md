# Project2 — анализ цен на сырьевые товары

Учебный проект: конвейер сбора и обработки данных о сырьевых товарах
(нефть, газ, золото, медь, никель, серебро, платина, алюминий) из нескольких
типов источников — синхронных, асинхронных и веб-API — с поддержкой
конкурентной обработки (потоки, процессы) и асинхронного выполнения.

## Возможности

- **Источники данных** (паттерн Factory):
  - `demo` — данные прямо в коде
  - `file` — чтение JSON-файла построчно
  - `async_demo`, `async_file` — асинхронные версии с имитацией I/O-задержек
  - `alpha_vantage` — веб-парсер с рейт-лимитером, retry и экспоненциальным backoff
- **Стратегии обработки** (паттерн Strategy + Composite):
  - нормализация названий (нижний регистр, trim)
  - фильтрация по категории, диапазону цен, продавцу
  - расчёт статистики
- **Режимы выполнения**:
  - `sequential` — последовательный
  - `threads` — через `ThreadPoolExecutor`
  - `processes` — через `ProcessPoolExecutor`
  - `async` — полностью асинхронный сбор и обработка
  - `hybrid` — асинхронный сбор + обработка в executor
- **Надёжность**: декоратор `handle_db_errors`, retry с backoff,
  обработка HTTP-ошибок (4xx, 5xx, timeout, connection error).
- **Тесты**: pytest + pytest-asyncio, моки `httpx`, покрытие фильтрации,
  стратегий, источников и веб-парсера.
- **Бенчмарк**: сравнение sequential / threads / processes
  на 1 000 / 5 000 / 10 000 записей.
- **Telegram-бот** на aiogram (`project2-bot`).

## Стек

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — менеджер пакетов и окружений
- `asyncio`, `httpx`, `requests`, `python-dotenv`, `aiogram`
- `pytest`, `pytest-asyncio`, `pytest-mock`
- `ruff` — линтер и форматтер

## Структура проекта

```
project_pavlenko_515/
├── src/
│   ├── decorators.py                # handle_db_errors (вне пакета — TODO)
│   └── project2/
│       ├── __init__.py
│       ├── app.py                   # Application — оркестратор сбора и обработки
│       ├── app_runner.py            # AppRunner — точка входа и форматирование сводки
│       ├── main.py                  # CLI-запуск (entry point: project2)
│       ├── config.py                # AppConfig (Singleton), чтение .env
│       ├── data.py                  # Data, Sellerinfo, Source, AsyncSource, реализации
│       ├── objectspace.py           # CommodityProcessing — фильтры и статистика
│       ├── processing_strategies.py # Strategy + Composite
│       ├── sourcefactory.py         # Factory для источников
│       ├── concurent_executor.py    # ConcurrentProcessor (threads/processes)
│       ├── task_manager.py          # TaskManager для hybrid-режима
│       ├── web_parsing/
│       │   ├── __init__.py
│       │   ├── alphavantage_api.py  # AlphaVantageParser + RateLimiter
│       │   └── parsfactory.py       # create_web_parser
│       ├── bot/
│       │   ├── __init__.py
│       │   └── bot.py               # Telegram-бот (entry point: project2-bot)
│       ├── test/                    # утилиты для бенчмарка (не pytest-тесты)
│       │   ├── benchmark.py
│       │   └── test_data_generator.py
│       └── tests/                   # pytest-тесты
│           ├── conftest.py
│           ├── test_async_sources.py
│           ├── test_app_runner.py
│           ├── test_data.py
│           ├── test_processing.py
│           ├── test_strategies.py
│           └── test_web_parser.py
├── Makefile
├── pyproject.toml
└── README.md
```

## Установка

Требуется Python 3.12+ и `uv`.

```bash
# Установить uv (если ещё нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Клонировать репозиторий
git clone git@gitlab.digital.mephi.ru:ktoto4304/project_pavlenko_515.git
cd project_pavlenko_515

# Установить зависимости и сам пакет в editable-режиме
make install
```

## Настройка

Создай файл `.env` в корне проекта:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

Бесплатный ключ: https://www.alphavantage.co/support/#api-key

Если ключ не задан — приложение выведет предупреждение и продолжит работу
на demo- и file-источниках (веб-парсер будет пропущен).

## Запуск

```bash
make project        # основной запуск (режим задаётся в config.run_mode)
make bot            # запуск Telegram-бота
```

Режим работы переключается в `src/project2/config.py`:

```python
self.run_mode: str = "hybrid"           # sync | sync_delay | async | hybrid
self.execution_mode: str = "processes"  # sequential | threads | processes
self.hybrid_executor: str = "threads"   # threads | processes
```

### Пример вывода

```
ВНИМАНИЕ: ALPHA_VANTAGE_API_KEY не найден в .env файле

=== НАСТРОЙКА АСИНХРОННОГО ВЕБ-ПАРСЕРА ===
Alpha Vantage API ключ не настроен
ВНИМАНИЕ: не удалось создать веб-источник

Источник 'Рынок Энергоносителей': собрано 10 записей (асинхронно)
Источник 'Биржа металлов': собрано 50 записей (асинхронно)
Асинхронный сбор: 60 записей за 10.0377 сек
Гибридная обработка (потоков): 0.0017 сек
Общее время (hybrid): 10.0394 сек
РЕЗУЛЬТАТЫ ОБРАБОТКИ
Обработано записей: 60
Общее время: 10.0394 сек
Средняя цена: 3912.29

Категории: {'медь': 8, 'газ': 9, 'золото': 7, 'никель': 7, 'нефть': 8, 'серебро': 7, 'платина': 7, 'алюминий': 7}
Продавцы: {'Норникель': 24, 'Газпром': 8, 'Полюс': 12, 'Лукойл': 4, 'Русал': 9, 'Роснефть': 3}
```

## Тесты

```bash
make test           # pytest -v
make lint           # ruff check src/ --ignore T201
```

Тесты лежат в `src/project2/tests/`. Папка `src/project2/test/` содержит
утилиты для бенчмарка и **исключена** из сбора pytest через `testpaths`
в `pyproject.toml`.

## Бенчмарк

Сравнение производительности `sequential` / `threads` / `processes`
на 1 000, 5 000 и 10 000 записей:

```bash
uv run python -m project2.test.benchmark
```

Пример вывода:

```
======================================================================
БЕНЧМАРК ПРОИЗВОДИТЕЛЬНОСТИ
Сравнение sequential / threads / processes
======================================================================

--- 10000 записей ---
  Sequential: 1.2345 сек
  Threads:    0.8765 сек (x1.41)
  Processes:  0.5432 сек (x2.27)
```

## Архитектура

```
                ┌──────────────────────┐
                │     AppRunner        │
                └──────────┬───────────┘
                           │
                ┌──────────▼───────────┐
                │     Application      │
                └──┬────────────────┬──┘
                   │                │
        ┌──────────▼─────┐   ┌──────▼──────────────┐
        │ SourceFactory  │   │  CompositeStrategy  │
        │ (Factory)      │   │  (Strategy)         │
        └──┬─────────────┘   └──────┬──────────────┘
           │                        │
   ┌───────▼────────┐      ┌────────▼─────────┐
   │ Source /       │      │ Normalization    │
   │ AsyncSource    │      │ Filter           │
   │ (ABC)          │      │ Statistics       │
   └────────────────┘      └──────────────────┘
           │
   ┌───────▼──────────────────────────┐
   │ Demo, File, AsyncDemo, AsyncFile,│
   │ AlphaVantageParser               │
   └──────────────────────────────────┘
```

Ключевые паттерны:
- **Factory** — `SourceFactory` и `FactoryRegister` для создания источников
- **Strategy + Composite** — `ProcessingStrategy` и `CompositeStrategy`
- **Singleton** — `AppConfig.__new__`
- **Decorator** — `handle_db_errors` для обработки ошибок ввода-вывода
