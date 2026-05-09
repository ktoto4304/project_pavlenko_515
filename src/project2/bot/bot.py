import asyncio
import os
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

from ..app_runner import AppRunner

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

router = Router()
runner = AppRunner()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Запустить обработку"),
            KeyboardButton(text="⚡ Гибридный режим"),
        ],
        [
            KeyboardButton(text="❓ Помощь"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


def _format_telegram_message(summary: dict[str, Any]) -> str:
    """Форматирует сводку для отправки в Telegram."""
    lines = [
        "<b>Результат обработки</b>",
        "",
        f"Записей обработано: <b>{summary['total_records']}</b>",
        f"Время выполнения: <b>{summary['total_time']} сек</b>",
        f"Средняя цена: <b>{summary['avg_price']}</b>",
        "",
        "<b>По категориям:</b>",
    ]

    for name, count in summary["categories"].items():
        lines.append(f"  • {name}: {count}")

    lines.append("")
    lines.append("<b>По продавцам:</b>")

    for name, count in summary["sellers"].items():
        lines.append(f"  • {name}: {count}")

    metrics = summary.get("metrics", {})
    if metrics:
        lines.append("")
        lines.append("<b>Метрики веб-парсера:</b>")
        for source_name, source_metrics in metrics.items():
            lines.append(f"<i>{source_name}:</i>")
            lines.append(f"Запросов: {source_metrics['requests_total']}")
            lines.append(f"Успешно: {source_metrics['requests_ok']}")
            lines.append(f"Ошибок: {source_metrics['requests_failed']}")
            lines.append(f"Повторов: {source_metrics['retries']}")
            lines.append(f"Собрано записей: {source_metrics['items_collected']}")

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (сообщение сокращено)"
    return text


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """Обработчик команды /start — приветствие и показ клавиатуры."""
    await message.answer(
        "Привет! Я бот для обработки данных о сырьевых товарах.\n\n"
        "Используй кнопки ниже или команды:\n"
        "/run — асинхронная обработка\n"
        "/run_hybrid — гибридный режим\n"
        "/help — справка",
        reply_markup=main_keyboard,
    )


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_handler(message: Message) -> None:
    """Обработчик команд /help и кнопки Помощь — показывает справку."""
    await message.answer(
        "📋 <b>Справка</b>\n\n"
        "<b>Команды:</b>\n"
        "/start — приветствие\n"
        "/run — асинхронный сбор и обработка данных\n"
        "/run_hybrid — гибридный режим\n"
        "/help — эта справка\n\n"
        "<b>Источники данных:</b>\n"
        "• Демо-данные (встроенные)\n"
        "• Файл с данными биржи\n"
        "• Alpha Vantage API (веб-парсер)\n\n"
        "<b>Режим работы:</b> асинхронные запросы, ограничение нагрузки, "
        "устойчивая обработка ошибок.",
        parse_mode="HTML",
    )


@router.message(Command("run"))
@router.message(F.text == "📊 Запустить обработку")
async def run_handler(message: Message) -> None:
    """Запускает асинхронную обработку данных."""
    await message.answer(
        "⏳ Запускаю асинхронную обработку данных...",
        reply_markup=main_keyboard,
    )
    summary = await runner.run_async()
    text = _format_telegram_message(summary)
    await message.answer(text, parse_mode="HTML")


@router.message(Command("run_hybrid"))
@router.message(F.text == "⚡ Гибридный режим")
async def run_hybrid_handler(message: Message) -> None:
    """Запускает гибридную обработку данных."""
    await message.answer(
        "⏳ Запускаю гибридную обработку данных...",
        reply_markup=main_keyboard,
    )
    summary = await runner.run_hybrid()
    text = _format_telegram_message(summary)
    await message.answer(text, parse_mode="HTML")
@router.message()
async def unknown_message_handler(message: Message) -> None:
    """Обрабатывает любые сообщения, которые не попали в другие хендлеры."""
    await message.answer(
        "Я не знаю такой команды.\n\n"
        "Используй кнопки ниже или напиши /help для справки.",
        reply_markup=main_keyboard,
    )

def run_bot() -> None:
    """Синхронная точка входа для консольного запуска бота."""
    asyncio.run(main())


async def main() -> None:
    """Точка входа для запуска бота."""
    if not BOT_TOKEN:
        print("ОШИБКА: BOT_TOKEN не найден в .env файле")
        return
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("Бот запущен в режиме polling...")
    await dp.start_polling(bot)
